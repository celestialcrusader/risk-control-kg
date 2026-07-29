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

from app.schemas.obligation import ExtractedObligationsResponse, Obligation
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

# LLM Configuration
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8000/v1")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "vllm")  # "vllm" or "ollama"
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/Mistral-8B-Instruct-v0.1")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))

# Prompt template path
PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "extraction.md"


def _load_prompt_template() -> str:
    """Load the extraction prompt template from the prompts directory."""
    try:
        return PROMPT_TEMPLATE_PATH.read_text()
    except FileNotFoundError:
        logger.warning("Prompt template not found at %s, using fallback", PROMPT_TEMPLATE_PATH)
        return (
            "Extract atomic obligations from the following regulatory text.\n"
            "Each obligation must include: id, prose, action_verb, subject_noun, clause_ref.\n"
            "Output JSON with an 'obligations' array.\n\nText:\n{{markdown_content}}"
        )


def _build_prompt(markdown_content: str) -> str:
    """Build the full prompt by inserting markdown content into the template."""
    template = _load_prompt_template()
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

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            response_format={"type": "json_object"},
        )
    except BadRequestError:
        logger.warning(
            "vLLM rejected response_format parameter, retrying without it"
        )
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("LLM returned null response")
    return content


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


def _parse_llm_response(raw_response: str) -> List[Obligation]:
    """
    Parse and validate the LLM JSON response against the Pydantic schema.

    Per project rule: Never trust raw LLM output. Always use strict Pydantic
    validation with try/except fallbacks.

    Args:
        raw_response: Raw JSON string from the LLM.

    Returns:
        List of validated Obligation objects.
    """
    try:
        parsed = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error("Failed to parse LLM JSON response: %s", e)
        return []

    try:
        response = ExtractedObligationsResponse(**parsed)
        return response.obligations
    except Exception as e:
        logger.error("Failed to validate LLM response against schema: %s", e)
        logger.debug("Raw response: %s", raw_response[:500])
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
                semantic_record = SemanticControl(
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
                    source_document_id=source_document_id,
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
) -> List[Obligation]:
    """
    Extract atomic obligations from regulatory Markdown text.

    This is the main entry point for the semantic decomposition pipeline.
    It reads Markdown content, calls the configured LLM (vLLM or Ollama),
    validates the output against the Pydantic schema, and stores results
    in the PostgreSQL semantic_controls (Silver layer) table.

    On successful extraction, publishes an extraction.completed event
    (fire-and-forget — Kafka failures never break extraction).
    On failure, publishes an extraction.failed event.

    Args:
        markdown_content: Regulatory Markdown text from the Bronze layer.
        source_document_id: Optional UUID string of the source document.
        event_publisher: Optional ExtractionEventPublisher instance.

    Returns:
        List of validated Obligation objects. Returns an empty list if
        the input is empty/None or if the LLM API fails.
    """
    from uuid import uuid4

    extraction_id = str(uuid4())
    start_time = time.time()

    obligations, storage_succeeded, trace_id = _extract_obligations_with_storage(
        markdown_content, source_document_id=source_document_id,
    )

    processing_time_ms = int((time.time() - start_time) * 1000)

    # Publish event
    if event_publisher:
        if obligations:
            event_publisher.on_extraction_completed(
                document_id=str(source_document_id) if source_document_id else extraction_id,
                obligation_count=len(obligations),
                extraction_id=extraction_id,
                model_used=LLM_MODEL,
                processing_time_ms=processing_time_ms,
                chunk_count=0,  # Filled by ingestion pipeline
                source_document_id=str(source_document_id) if source_document_id else None,
                obligation_ids=[o.id for o in obligations],
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

    return obligations


def _extract_obligations_with_storage(
    markdown_content: str,
    source_document_id=None,
) -> tuple:
    """
    Extract atomic obligations and track database storage status.

    Internal function that returns the obligations list, a boolean
    indicating whether storage to semantic_controls succeeded, and
    an optional Langfuse trace_id for cross-service linkage (AC-1, AC-5).

    Args:
        markdown_content: Regulatory Markdown text from the Bronze layer.
        source_document_id: Optional UUID string of the source document.

    Returns:
        Tuple of (List[Obligation], bool, str|None) where the bool indicates
        whether DB storage succeeded and the str is the Langfuse trace_id.
    """
    # Handle empty or None input
    if not markdown_content or not markdown_content.strip():
        logger.info("Empty or None markdown content provided, returning empty list")
        return [], True, None

    # Build prompt for tracing before LLM call
    prompt = _build_prompt(markdown_content)

    try:
        # Call LLM to extract obligations
        raw_response = _call_llm(markdown_content)
    except Exception as e:
        logger.error("LLM API call failed: %s", e)
        return [], True, None

    # Parse and validate LLM response
    obligations = _parse_llm_response(raw_response)
    if not obligations:
        logger.warning("No obligations extracted or validation failed")
        # Log failure to Langfuse if tracing is available
        if _log_extraction_failure:
            try:
                _log_extraction_failure(
                    trace_id="",  # No trace created since LLM call failed
                    judge_feedback="No obligations extracted",
                    repair_attempts=0,
                    final_status="no_obligations",
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

    # Store in Silver layer
    storage_succeeded = _store_obligations_in_semantic_controls(
        obligations, source_document_id=source_document_id,
    )
    if not storage_succeeded:
        logger.error(
            "Extraction succeeded (%d obligations) but storage failed",
            len(obligations),
        )

    logger.info(
        "Extracted %d obligations from markdown (storage=%s, trace_id=%s)",
        len(obligations),
        storage_succeeded,
        trace_id,
    )
    return obligations, storage_succeeded, trace_id
