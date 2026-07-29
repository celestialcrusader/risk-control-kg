"""
Iterative Repair Loop service for EXTRACT-3.

Re-submits low-scoring obligations to the LLM with the judge's feedback,
so that extraction quality improves automatically before committing to
the Silver layer.

Pipeline:
1. Validate input (obligation, feedback, markdown)
2. Extract parent section context from original markdown
3. If feedback is empty, return original_kept
4. Build repair prompt from template + feedback + obligation + context
5. Call LLM (Ollama via _call_ollama, same pattern as extraction.py)
6. Parse and validate LLM output against Pydantic Obligation schema
7. Retry up to max_attempts times
8. On max attempts exceeded, send to dead-letter queue
9. Log each attempt to Langfuse
10. Return (obligation, status, attempts_made) where status is
    "repaired", "rejected", or "original_kept"
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from app.schemas.obligation import Obligation

logger = logging.getLogger(__name__)

# LLM Configuration
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8000/v1")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

# Prompt template path
PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "repair.md"

# Default max repair attempts
DEFAULT_MAX_ATTEMPTS = int(os.getenv("DEFAULT_MAX_REPAIR_ATTEMPTS", "3"))

# Conditionally import langfuse; may not be installed
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
    logger.debug("langfuse not installed, observability logging will be skipped")

# Fallback prompt used when template file is not found
FALLBACK_PROMPT = """
You are a regulatory compliance expert. Repair the following obligation extraction.

PARENT SECTION:
{{parent_section_heading}}

PRECEDING PARAGRAPHS:
{{preceding_paragraphs}}

ORIGINAL TEXT:
{{original_markdown}}

EXTRACTED OBLIGATION:
{{obligation_json}}

JUDGE FEEDBACK:
{{feedback}}

Output ONLY valid JSON with this structure:
{
  "id": "<obligation ID>",
  "prose": "<corrected obligation text>",
  "action_verb": "<corrected verb>",
  "subject_noun": "<corrected subject>",
  "clause_ref": "<corrected clause reference>"
}
"""

# ==============================================================================
# Context extraction
# ==============================================================================


def _extract_context(
    obligation: Union[Dict[str, Any], Any],
    original_markdown: str,
) -> Tuple[str, str]:
    """
    Extract parent section heading and 2 preceding paragraphs from markdown.

    Parses the obligation's clause_ref (e.g., "Section 3.1") to find the
    matching section heading in the original markdown, then includes the
    2 paragraphs preceding that section as context.

    Args:
        obligation: The extracted obligation (dict or Pydantic model).
        original_markdown: The original regulatory markdown text.

    Returns:
        A tuple of (parent_section_heading, preceding_paragraphs).
    """
    # Determine clause_ref
    if hasattr(obligation, "model_dump"):
        clause_ref = getattr(obligation, "clause_ref", "")
    else:
        clause_ref = obligation.get("clause_ref", "")

    if not clause_ref or not original_markdown.strip():
        return "", ""

    lines = original_markdown.split("\n")

    # Extract numeric section identifiers from clause_ref (e.g., "3.1" from "Section 3.1")
    ref_numbers = re.findall(r"(\d+(?:\.\d+)*)", clause_ref)

    def _heading_number(heading_text: str) -> str:
        """Extract the first numeric section identifier from a heading."""
        nums = re.findall(r"(\d+(?:\.\d+)*)", heading_text)
        return nums[0] if nums else ""

    # Search for the section heading matching the clause_ref
    # Pattern: "# Section 3.1" or "## 3.1" etc.
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            heading_text = stripped.lstrip("#").strip()
            heading_num = _heading_number(heading_text)

            # Match if clause_ref contains the same section number as the heading
            for ref_num in ref_numbers:
                if ref_num == heading_num:
                    # Found matching section
                    section_heading = line
                    # Collect 2 preceding paragraphs (skip blank lines)
                    preceding = []
                    for j in range(i - 1, -1, -1):
                        if len(preceding) >= 2:
                            break
                        if lines[j].strip():
                            preceding.append(lines[j].strip())
                    preceding_paragraphs = "\n".join(reversed(preceding))
                    return section_heading, preceding_paragraphs

    # Fallback: no matching section found, use first heading and preceding paragraphs
    first_heading = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            first_heading = line
            break

    preceding = []
    first_heading_idx = lines.index(first_heading) if first_heading else 0
    for j in range(first_heading_idx - 1, -1, -1):
        if len(preceding) >= 2:
            break
        if lines[j].strip():
            preceding.append(lines[j].strip())

    return first_heading, "\n".join(reversed(preceding))


# ==============================================================================
# DLQ (Dead-Letter Queue)
# ==============================================================================


def _send_to_dlq(obligation: Union[Dict[str, Any], Any], reason: str) -> None:
    """
    Move an obligation to the dead-letter queue after max repair attempts exceeded.

    Graceful degradation: if the extraction_dlq table does not exist in
    PostgreSQL, this function logs the rejection and continues without error.

    Args:
        obligation: The obligation that failed all repair attempts.
        reason: Reason for DLQ placement (e.g., "max_repair_attempts_exceeded").
    """
    obligation_id = ""
    if hasattr(obligation, "id"):
        obligation_id = obligation.id
    elif isinstance(obligation, dict):
        obligation_id = obligation.get("id", "unknown")

    original_text = ""
    if hasattr(obligation, "prose"):
        original_text = obligation.prose
    elif isinstance(obligation, dict):
        original_text = obligation.get("prose", "N/A")

    logger.warning(
        "DLQ: obligation=%s reason=%s original_text=%s",
        obligation_id,
        reason,
        original_text[:200] if original_text else "N/A",
    )

    # Attempt to write to the DLQ table if it exists
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        logger.debug("sqlalchemy not available, skipping DLQ table write")
        return

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rckg")

    try:
        engine = create_engine(db_url, pool_size=1, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO extraction_dlq "
                    "(obligation_id, original_text, feedback, attempt_count, reason, created_at) "
                    "VALUES (:obligation_id, :original_text, :feedback, :attempt_count, :reason, NOW())"
                ),
                {
                    "obligation_id": obligation_id,
                    "original_text": original_text,
                    "feedback": "",
                    "attempt_count": DEFAULT_MAX_ATTEMPTS,
                    "reason": reason,
                },
            )
            conn.commit()
        logger.info("Wrote DLQ record for obligation=%s reason=%s", obligation_id, reason)
    except Exception as e:
        # Table doesn't exist or other DB error — graceful degradation
        logger.warning(
            "DLQ table write failed (table may not exist yet): %s", e
        )


# ==============================================================================
# Langfuse logging
# ==============================================================================


def _log_attempt_to_langfuse(
    attempt_number: int,
    feedback: str,
    obligation: Union[Dict[str, Any], Any],
    status: str,
    parent_trace_id: Optional[str] = None,
) -> None:
    """
    Log a repair attempt to Langfuse for observability.

    Graceful degradation: if langfuse is not installed, this function is a no-op.

    Args:
        attempt_number: The attempt number (1-based).
        feedback: The judge feedback string.
        obligation: The obligation being repaired.
        status: The repair result status ("repaired", "rejected", etc.).
        parent_trace_id: Optional trace_id from the extraction trace for
            cross-service linkage (grandparent of repair trace).
    """
    if Langfuse is None:
        logger.debug("langfuse not installed, skipping repair attempt logging")
        return

    obligation_id = ""
    if hasattr(obligation, "id"):
        obligation_id = obligation.id
    elif isinstance(obligation, dict):
        obligation_id = obligation.get("id", "unknown")

    feedback_summary = feedback[:200] if feedback else ""

    try:
        langfuse_client = Langfuse()
        trace_id = f"repair-{obligation_id}-attempt-{attempt_number}"

        trace_kwargs: Dict[str, Any] = {
            "id": trace_id,
            "name": "obligation-repair-attempt",
        }
        if parent_trace_id:
            trace_kwargs["parent_observation_id"] = parent_trace_id

        with langfuse_client.trace(**trace_kwargs) as trace:
            trace.update_generation(
                name=f"repair-attempt-{attempt_number}",
                input=feedback_summary,
                metadata={
                    "obligation_id": obligation_id,
                    "attempt_number": attempt_number,
                    "feedback_summary": feedback_summary,
                    "status": status,
                },
            )
        logger.info(
            "Logged repair attempt %d to Langfuse trace_id=%s status=%s",
            attempt_number,
            trace_id,
            status,
        )
    except Exception as e:
        logger.warning("Failed to log repair attempt to Langfuse: %s", e)


# ==============================================================================
# Prompt building
# ==============================================================================


def _load_prompt_template() -> str:
    """Load the repair prompt template from the prompts directory."""
    try:
        return PROMPT_TEMPLATE_PATH.read_text()
    except FileNotFoundError:
        logger.warning(
            "Repair prompt template not found at %s, using fallback", PROMPT_TEMPLATE_PATH
        )
        return FALLBACK_PROMPT


def _build_prompt(
    obligation: Union[Dict[str, Any], Any],
    feedback: str,
    original_markdown: str,
    parent_section_heading: str = "",
    preceding_paragraphs: str = "",
) -> str:
    """
    Build the full repair prompt by inserting obligation, feedback, context,
    and original text into the template.

    Args:
        obligation: The extracted obligation (dict or Pydantic model).
        feedback: The judge feedback string describing what needs fixing.
        original_markdown: The original regulatory markdown text.
        parent_section_heading: Parent section heading extracted from markdown.
        preceding_paragraphs: 2 preceding paragraphs as context.

    Returns:
        Formatted prompt string ready for the LLM.
    """
    template = _load_prompt_template()

    obligation_json = json.dumps(
        obligation.model_dump() if hasattr(obligation, "model_dump") else obligation,
        indent=2,
    )

    return template.replace("{{obligation_json}}", obligation_json) \
                   .replace("{{feedback}}", feedback) \
                   .replace("{{original_markdown}}", original_markdown) \
                   .replace("{{parent_section_heading}}", parent_section_heading) \
                   .replace("{{preceding_paragraphs}}", preceding_paragraphs)


# ==============================================================================
# LLM calling
# ==============================================================================


def _call_llm(prompt: str) -> str:
    """
    Call the LLM for repair (uses Ollama in default configuration).

    Args:
        prompt: Formatted repair prompt.

    Returns:
        Raw JSON string response from the LLM.

    Raises:
        Exception: If the LLM API is unreachable.
    """
    if LLM_PROVIDER == "ollama":
        return _call_ollama(prompt)
    else:
        return _call_vllm(prompt)


def _call_vllm(prompt: str) -> str:
    """
    Call vLLM using the OpenAI-compatible API.

    Args:
        prompt: Formatted repair prompt.

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
        raise ValueError("LLM returned null response from repair")
    return content


def _call_ollama(prompt: str) -> str:
    """
    Call Ollama for the repair LLM request.

    Args:
        prompt: Formatted repair prompt.

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
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": LLM_TEMPERATURE},
    )

    content = response.get("message", {}).get("content")
    if content is None:
        raise ValueError("Ollama returned null response from repair")
    return content


# ==============================================================================
# Parsing
# ==============================================================================


def _parse_repair_response(raw_response: str) -> Optional[Obligation]:
    """
    Parse and validate the LLM repair JSON response against the Obligation schema.

    Per project rule: Never trust raw LLM output. Always use strict Pydantic
    validation with try/except fallbacks.

    Args:
        raw_response: Raw JSON string from the LLM repair.

    Returns:
        A validated Obligation instance, or None if parsing/validation fails.
    """
    try:
        parsed = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Failed to parse repair JSON response: %s", e)
        return None

    try:
        return Obligation(**parsed)
    except Exception as e:
        logger.warning("Failed to validate repair response against Obligation schema: %s", e)
        logger.debug("Raw repair response: %s", raw_response[:500])
        return None


# ==============================================================================
# Main entry point
# ==============================================================================


def repair_obligation(
    obligation: Union[Dict[str, Any], Any, None],
    judgment_feedback: str,
    original_markdown: str,
    max_attempts: Optional[int] = None,
    parent_trace_id: Optional[str] = None,
) -> Tuple[Optional[Obligation], str, int]:
    """
    Re-submit a low-scoring obligation to the LLM with the judge's feedback.

    This is the main entry point for the iterative repair loop. It validates
    input, extracts context, builds a repair prompt, calls the LLM, and
    retries up to max_attempts times until a valid obligation is produced or
    all attempts are exhausted.

    Args:
        obligation: The extracted obligation that needs repair (dict or Pydantic model).
        judgment_feedback: The feedback string from the LLM-as-Judge explaining what
            needs to be fixed.
        original_markdown: The original regulatory markdown text for context.
        max_attempts: Maximum number of repair attempts. Defaults to env var
            DEFAULT_MAX_REPAIR_ATTEMPTS or 3.
        parent_trace_id: Optional trace_id from the extraction trace for
            cross-service linkage (grandparent of repair traces).

    Returns:
        A tuple of (obligation, status, attempts_made) where:
        - obligation: The repaired Obligation instance, or None if rejected.
        - status: One of "repaired", "rejected", or "original_kept".
        - attempts_made: The actual number of LLM calls made.
    """
    if max_attempts is None:
        max_attempts = DEFAULT_MAX_ATTEMPTS

    # Early return for invalid input — return the original obligation if available
    if not obligation:
        logger.info("No obligation provided, returning original_kept")
        return None, "original_kept", 0

    if not judgment_feedback or not judgment_feedback.strip():
        logger.info("Empty feedback provided, returning original_kept")
        return obligation, "original_kept", 0

    if not original_markdown or not original_markdown.strip():
        logger.info("Empty original markdown provided, returning original_kept")
        return obligation, "original_kept", 0

    # Extract context once before the retry loop
    parent_section_heading, preceding_paragraphs = _extract_context(obligation, original_markdown)
    logger.debug(
        "Context extracted: heading=%s paragraphs=%d chars",
        parent_section_heading[:50] if parent_section_heading else "N/A",
        len(preceding_paragraphs),
    )

    last_obligation = None
    attempts_made = 0

    for attempt in range(1, max_attempts + 1):
        attempts_made = attempt
        logger.info("Repair attempt %d of %d", attempt, max_attempts)

        # Log this attempt to Langfuse before calling LLM
        _log_attempt_to_langfuse(
            attempt, judgment_feedback, obligation, "in_progress",
            parent_trace_id=parent_trace_id,
        )

        try:
            # Build and call LLM
            prompt = _build_prompt(
                obligation,
                judgment_feedback,
                original_markdown,
                parent_section_heading,
                preceding_paragraphs,
            )
            raw_response = _call_llm(prompt)
        except Exception as e:
            logger.warning("Repair attempt %d LLM call failed: %s", attempt, e)
            _log_attempt_to_langfuse(
                attempt, judgment_feedback, obligation, "llm_error",
                parent_trace_id=parent_trace_id,
            )
            last_obligation = None
            continue

        # Parse and validate
        repaired_obligation = _parse_repair_response(raw_response)

        if repaired_obligation is not None:
            logger.info(
                "Repair succeeded on attempt %d: id=%s",
                attempt,
                repaired_obligation.id,
            )
            _log_attempt_to_langfuse(
                attempt, judgment_feedback, repaired_obligation, "repaired",
                parent_trace_id=parent_trace_id,
            )
            return repaired_obligation, "repaired", attempts_made

        logger.warning(
            "Repair attempt %d produced invalid output, retrying...",
            attempt,
        )
        _log_attempt_to_langfuse(attempt, judgment_feedback, obligation, "invalid_output", parent_trace_id=parent_trace_id)
        last_obligation = None

    # All attempts exhausted
    logger.warning(
        "All %d repair attempts exhausted, sending to DLQ",
        max_attempts,
    )
    try:
        _send_to_dlq(obligation, "max_repair_attempts_exceeded")
    except Exception as e:
        logger.warning("DLQ call failed: %s", e)
    _log_attempt_to_langfuse(attempts_made, judgment_feedback, obligation, "rejected")
    return None, "rejected", attempts_made
