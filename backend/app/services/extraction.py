"""
Semantic Decomposition Pipeline for EXTRACT-1.

Extracts atomic rule units from regulatory Markdown text using
Mistral 8B (via vLLM or Ollama) and stores results in the
PostgreSQL semantic_controls (Silver layer) table.

Pipeline:
1. Load prompt template from prompts/extraction.md
2. Call LLM API (vLLM primary, Ollama fallback) with markdown content
3. Parse and validate LLM JSON response against Pydantic schema
4. Store validated obligations in semantic_controls table
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import List, Optional

from app.schemas.obligation import ExtractedObligationsResponse, Obligation, ControlObjective, ControlActivity
from app.models import SemanticControl
from app.core.database import get_db_session
from app.services.extraction_event import ExtractionEventPublisher

# Tracing is optional; integrated into extraction flow
try:
    from app.services.langfuse_tracing import extract_and_trace as _extract_and_trace, log_extraction_failure as _log_extraction_failure  # noqa: F401
except ImportError:
    _extract_and_trace = None  # type: ignore[misc,assignment]
    _log_extraction_failure = None  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)

# LLM Configuration (AI-REQ-06)
LLM_ENDPOINT = os.getenv("MODEL_EXTRACTION_ENDPOINT", os.getenv("LLM_ENDPOINT", "http://localhost:8000/v1"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "vllm")  # "vllm" or "ollama"
LLM_MODEL = os.getenv("MODEL_EXTRACTION_NAME", os.getenv("LLM_MODEL", "nvidia/Qwen3.6-35B-A3B-NVFP4"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))

# Prompt template paths
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

PROMPT_TEMPLATE_MAP = {
    "REGULATORY_GUIDELINE": PROMPTS_DIR / "extraction.md",
    "STATUTORY": PROMPTS_DIR / "extraction.md",
    "ENTERPRISE_POLICY": PROMPTS_DIR / "extraction_control_objective.md",
    "PROCEDURE_SOP": PROMPTS_DIR / "extraction_control_activity.md",
}


def _load_prompt_template(document_type: str = "REGULATORY_GUIDELINE") -> str:
    """Load the extraction prompt template for the given document type."""
    template_path = PROMPT_TEMPLATE_MAP.get(
        document_type.upper(), PROMPT_TEMPLATE_MAP["REGULATORY_GUIDELINE"]
    )
    try:
        return template_path.read_text()
    except FileNotFoundError:
        logger.warning("Prompt template not found at %s, using fallback", template_path)
        return (
            "Extract atomic obligations from the following regulatory text.\n"
            "Each obligation must include: id, prose, action_verb, subject_noun, clause_ref.\n"
            "Output JSON with an 'obligations' array.\n\nText:\n{{markdown_content}}"
        )


def _build_prompt(markdown_content: str, document_type: str = "REGULATORY_GUIDELINE") -> str:
    """Build the full prompt by inserting markdown content into the template."""
    template = _load_prompt_template(document_type)
    return template.replace("{{markdown_content}}", markdown_content)


def _call_llm(markdown_content: str) -> str:
    """
    Call the configured LLM API to extract obligations from markdown content.

    Production: Uses OpenAI-compatible client for vLLM endpoint.
    Development: Falls back to Ollama client.

    Args:
        markdown_content: Regulatory Markdown text from the Bronze layer.

    Returns:
        Raw JSON string response from the LLM.

    Raises:
        Exception: If the LLM API is unreachable or returns an error.
    """
    prompt = _build_prompt(markdown_content)

    if LLM_PROVIDER == "ollama":
        return _call_ollama(prompt)
    else:
        return _call_vllm(prompt)


def _call_vllm(prompt: str) -> str:
    """
    Call vLLM using the OpenAI-compatible API.

    Tries with response_format first; falls back without it if the
    server rejects the parameter.

    Args:
        prompt: Formatted prompt with markdown content.

    Returns:
        Raw JSON string from the LLM.

    Raises:
        Exception: If the vLLM API is unreachable.
    """
    from openai import OpenAI, BadRequestError

    client = OpenAI(
        base_url=LLM_ENDPOINT,
        api_key=os.getenv("LLM_API_KEY", "not-required"),
    )

    system_instruction = (
        "You are a GRC compliance extraction engine. "
        "Extract atomic rule units as a JSON array."
    )
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
        temperature=LLM_TEMPERATURE,
        max_tokens=8192,
    )




    message = response.choices[0].message
    content = message.content
    if not content and hasattr(message, "reasoning") and message.reasoning:
        content = message.reasoning
    if not content and hasattr(message, "reasoning_content") and message.reasoning_content:
        content = message.reasoning_content

    if content is None:
        raise ValueError("LLM returned null response")

    # Clean markdown fences if present
    cleaned = content.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()



def _call_ollama(prompt: str) -> str:
    """
    Call Ollama for local development without GPU.

    Args:
        prompt: Formatted prompt with markdown content.

    Returns:
        Raw JSON string from the LLM.

    Raises:
        Exception: If the Ollama API is unreachable.
    """
    try:
        import ollama
    except ImportError:
        logger.warning(
            "ollama package not installed. Falling back to vLLM. "
            "Install with: pip install ollama"
        )
        return _call_vllm(prompt)

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": LLM_TEMPERATURE},
    )

    content = response.get("message", {}).get("content")
    if content is None:
        raise ValueError("Ollama returned null response")
    return content


def _parse_llm_response(raw_response: str, document_type: str = "REGULATORY_GUIDELINE") -> list:
    """
    Parse and validate the LLM JSON response against Pydantic schemas.
    """
    parsed = None
    try:
        parsed = json.loads(raw_response)
    except Exception:
        pass

    if parsed is None:
        import re
        list_match = re.search(r"\[.*\]", raw_response, re.DOTALL)
        dict_match = re.search(r"\{.*\}", raw_response, re.DOTALL)

        if list_match:
            try:
                parsed = json.loads(list_match.group(0))
            except Exception:
                pass
        if parsed is None and dict_match:
            try:
                parsed = json.loads(dict_match.group(0))
            except Exception:
                pass

    if parsed is None:
        logger.error("Failed to parse valid JSON from LLM response")
        return []

    doc_type_upper = document_type.upper()

    def _clean_dict(d: dict) -> dict:
        allowed = {"id", "prose", "action_verb", "subject_noun", "clause_ref", "effective_date", "section_ref", "clause_hierarchy", "clause_reference"}
        cleaned = {k: v for k, v in d.items() if k in allowed}
        if "clause_ref" not in cleaned and "id" in cleaned:
            cleaned["clause_ref"] = str(cleaned["id"])
        if "prose" not in cleaned:
            cleaned["prose"] = str(d.get("obligation", d.get("action", "Standard requirement.")))
        if "action_verb" not in cleaned:
            cleaned["action_verb"] = "must"
        if "subject_noun" not in cleaned:
            cleaned["subject_noun"] = str(d.get("responsible_party", d.get("actor", "Financial Institution")))
        if "id" not in cleaned:
            cleaned["id"] = "OBL-1"

        # Normalize prose to canonical active 3-tier GRC syntax if unformatted
        prose = str(cleaned["prose"]).strip()
        actor = str(cleaned["subject_noun"]).strip()
        if actor.lower() in ("fi", "the fi"):
            actor = "Financial Institution"
            cleaned["subject_noun"] = actor
        if not (prose.lower().startswith("the ") or prose.lower().startswith("a ") or prose.lower().startswith("an ")):
            actor_prefix = actor if actor.lower().startswith("the ") else f"The {actor}"
            cleaned["prose"] = f"{actor_prefix} must {prose[0].lower() + prose[1:]}"
        return cleaned

    if isinstance(parsed, list):
        validated = []
        for item in parsed:
            if isinstance(item, dict):
                try:
                    validated.append(Obligation(**_clean_dict(item)))
                except Exception as e:
                    logger.warning("Failed to validate item as Obligation: %s", e)
        return validated

    elif isinstance(parsed, dict):
        if doc_type_upper == "ENTERPRISE_POLICY":
            objs = parsed.get("control_objectives", [])
            validated = []
            for item in objs:
                try:
                    validated.append(ControlObjective(**item))
                except Exception as e:
                    logger.error("Failed to validate ControlObjective: %s", e)
            return validated

        elif doc_type_upper == "PROCEDURE_SOP":
            acts = parsed.get("control_activities", [])
            validated = []
            for item in acts:
                try:
                    validated.append(ControlActivity(**item))
                except Exception as e:
                    logger.error("Failed to validate ControlActivity: %s", e)
            return validated

        else:
            if "obligations" in parsed and isinstance(parsed["obligations"], list):
                validated = []
                for item in parsed["obligations"]:
                    if isinstance(item, dict):
                        try:
                            validated.append(Obligation(**_clean_dict(item)))
                        except Exception:
                            continue
                return validated
            elif any(k in parsed for k in ("prose", "id", "obligation")):
                try:
                    return [Obligation(**_clean_dict(parsed))]
                except Exception as e:
                    logger.error("Failed to validate single obligation dict: %s", e)
                    return []

    return []





def _store_obligations_in_semantic_controls(
    obligations: List[Obligation],
    source_document_id=None,
) -> bool:
    """
    Store validated obligations in the PostgreSQL semantic_controls table.

    Generates a unique UUID for each record's uuid column while storing
    the obligation id in the control_id column. Uses ON CONFLICT DO UPDATE
    to allow safe re-extraction without unique constraint violations.

    Args:
        obligations: List of validated Obligation objects to persist.
        source_document_id: Optional UUID string of the source document.

    Returns:
        True if storage succeeded, False if an exception occurred.
    """
    from uuid import uuid4

    try:
        with get_db_session() as session:
            for obligation in obligations:
                existing = (
                    session.query(SemanticControl)
                    .filter(SemanticControl.control_id == obligation.id)
                    .first()
                )
                valid_doc_id = source_document_id if (source_document_id and len(str(source_document_id)) == 36) else None

                if existing:
                    existing.objective_text = obligation.prose
                    existing.statement_text = obligation.prose
                    existing.action_verb = obligation.action_verb
                    existing.subject_noun = obligation.subject_noun
                    existing.section_reference = obligation.section_ref or obligation.clause_ref
                    if valid_doc_id:
                        existing.source_document_id = valid_doc_id
                else:
                    semantic_record = SemanticControl(
                        id=uuid4(),
                        uuid=uuid4(),
                        framework_name="de-jure",
                        framework_version="1.0",
                        control_id=obligation.id,
                        control_name=obligation.id,
                        objective_text=obligation.prose,
                        statement_text=obligation.prose,
                        action_verb=obligation.action_verb,
                        subject_noun=obligation.subject_noun,
                        section_reference=obligation.section_ref or obligation.clause_ref,
                        source_document_id=valid_doc_id,
                    )
                    session.add(semantic_record)


            session.commit()
            logger.info(
                "Stored %d obligations in semantic_controls",
                len(obligations),
            )
        return True
    except Exception as e:
        logger.error(
            "Failed to store %d obligations in semantic_controls: %s",
            len(obligations),
            e,
        )
        return False


def extract_obligations(
    markdown_content: str,
    source_document_id=None,
    event_publisher: Optional[ExtractionEventPublisher] = None,
    document_type: str = "REGULATORY_GUIDELINE",
) -> list:
    """
    Extract atomic rule units / control objectives / control activities from Markdown text.
    """
    from uuid import uuid4

    extraction_id = str(uuid4())
    start_time = time.time()

    extracted_items, storage_succeeded, trace_id = _extract_obligations_with_storage(
        markdown_content, source_document_id=source_document_id, document_type=document_type,
    )

    processing_time_ms = int((time.time() - start_time) * 1000)

    # Publish event
    if event_publisher:
        if extracted_items:
            event_publisher.on_extraction_completed(
                document_id=str(source_document_id) if source_document_id else extraction_id,
                obligation_count=len(extracted_items),
                extraction_id=extraction_id,
                model_used=LLM_MODEL,
                processing_time_ms=processing_time_ms,
                chunk_count=0,  # Filled by ingestion pipeline
                source_document_id=str(source_document_id) if source_document_id else None,
                obligation_ids=[getattr(o, "id", str(idx)) for idx, o in enumerate(extracted_items)],
            )
        else:
            event_publisher.on_extraction_failed(
                document_id=str(source_document_id) if source_document_id else extraction_id,
                extraction_id=extraction_id,
                error_reason="No obligations extracted or validation failed",
                model_used=LLM_MODEL,
                processing_time_ms=processing_time_ms,
                source_document_id=str(source_document_id) if source_document_id else None,
            )

    return extracted_items


def _extract_obligations_with_storage(
    markdown_content: str,
    source_document_id=None,
    document_type: str = "REGULATORY_GUIDELINE",
) -> tuple:
    """
    Extract atomic rule units/objectives/activities and track database storage status.
    """
    # Handle empty or None input
    if not markdown_content or not markdown_content.strip():
        logger.info("Empty or None markdown content provided, returning empty list")
        return [], True, None

    # Build prompt for tracing before LLM call
    prompt = _build_prompt(markdown_content, document_type=document_type)

    try:
        # Call LLM to extract items
        raw_response = _call_llm(prompt)
    except Exception as e:
        logger.error("LLM API call failed: %s", e)
        return [], True, None

    # Parse and validate LLM response
    extracted_items = _parse_llm_response(raw_response, document_type=document_type)
    if not extracted_items:
        logger.warning("No items extracted or validation failed")
        # Log failure to Langfuse if tracing is available
        if _log_extraction_failure:
            try:
                _log_extraction_failure(
                    trace_id="",  # No trace created since LLM call failed
                    judge_feedback="No items extracted",
                    repair_attempts=0,
                    final_status="no_items",
                    document_id=str(source_document_id) if source_document_id else None,
                )
            except Exception:
                pass
        return [], True, None

    # Trace the extraction call (AC-1, AC-2)
    trace_id = None
    if _extract_and_trace:
        try:
            trace_result = _extract_and_trace(
                markdown_content=markdown_content,
                prompt=prompt,
                completion=raw_response,
                model_used=LLM_MODEL,
                document_id=str(source_document_id) if source_document_id else None,
            )
            trace_id = trace_result.get("trace_id") if trace_result else None
        except Exception:
            logger.warning("Tracing failed, extraction continues")

    # Store in Silver layer if items are Obligations
    obligations = [item for item in extracted_items if isinstance(item, Obligation)]
    storage_succeeded = True
    if obligations:
        storage_succeeded = _store_obligations_in_semantic_controls(
            obligations, source_document_id=source_document_id,
        )

    logger.info(
        "Extracted %d items from markdown (storage=%s, trace_id=%s)",
        len(extracted_items),
        storage_succeeded,
        trace_id,
    )
    return extracted_items, storage_succeeded, trace_id
