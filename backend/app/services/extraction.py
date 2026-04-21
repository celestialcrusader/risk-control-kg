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
from pathlib import Path
from typing import List

from app.schemas.obligation import ExtractedObligationsResponse, Obligation
from app.models import SemanticControl
from app.core.database import get_db_session

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
) -> List[Obligation]:
    """
    Extract atomic obligations from regulatory Markdown text.

    This is the main entry point for the semantic decomposition pipeline.
    It reads Markdown content, calls the configured LLM (vLLM or Ollama),
    validates the output against the Pydantic schema, and stores results
    in the PostgreSQL semantic_controls (Silver layer) table.

    Args:
        markdown_content: Regulatory Markdown text from the Bronze layer.
        source_document_id: Optional UUID string of the source document.

    Returns:
        List of validated Obligation objects. Returns an empty list if
        the input is empty/None or if the LLM API fails.
    """
    obligations, _ = _extract_obligations_with_storage(
        markdown_content, source_document_id=source_document_id,
    )
    return obligations


def _extract_obligations_with_storage(
    markdown_content: str,
    source_document_id=None,
) -> tuple:
    """
    Extract atomic obligations and track database storage status.

    Internal function that returns both the obligations list and a
    boolean indicating whether storage to semantic_controls succeeded.

    Args:
        markdown_content: Regulatory Markdown text from the Bronze layer.
        source_document_id: Optional UUID string of the source document.

    Returns:
        Tuple of (List[Obligation], bool) where the bool indicates
        whether DB storage succeeded.
    """
    # Handle empty or None input
    if not markdown_content or not markdown_content.strip():
        logger.info("Empty or None markdown content provided, returning empty list")
        return [], True

    try:
        # Call LLM to extract obligations
        raw_response = _call_llm(markdown_content)
    except Exception as e:
        logger.error("LLM API call failed: %s", e)
        return [], True

    # Parse and validate LLM response
    obligations = _parse_llm_response(raw_response)
    if not obligations:
        logger.warning("No obligations extracted or validation failed")
        return [], True

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
        "Extracted %d obligations from markdown (storage=%s)",
        len(obligations),
        storage_succeeded,
    )
    return obligations, storage_succeeded
