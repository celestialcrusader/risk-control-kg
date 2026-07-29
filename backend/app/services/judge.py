"""
LLM-as-Judge quality evaluation service for EXTRACT-2.

Evaluates extracted obligations across three quality criteria:
  1. Metadata Accuracy (0.0-1.0): Are action_verb, subject_noun, clause_ref correct?
  2. Legal Definition Alignment (0.0-1.0): Does it align with compliance terminology?
  3. Rule Semantics (0.0-1.0): Is the intent preserved without semantic loss?

Threshold: >= 0.80 passes (approved), < 0.80 flagged for repair.

Pipeline:
1. Load prompt template from prompts/judge.md
2. Build prompt with obligation JSON and original markdown
3. Call Ollama (llama3.1) for evaluation
4. Parse and validate LLM JSON response against Pydantic schema
5. Score results to Langfuse (graceful degradation if unavailable)
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.schemas.judge import Judgment, JudgmentResponse

logger = logging.getLogger(__name__)

# Conditionally import langfuse; may not be installed
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
    logger.debug("langfuse not installed, observability logging will be skipped")

# LLM Configuration
OLLAMA_MODEL = "llama3.1"
OLLAMA_TEMPERATURE = 0.3

# Prompt template path
PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "judge.md"

# Quality threshold: all criteria must meet this score to be "approved"
THRESHOLD = 0.80

# Fallback prompt used when template file is not found
FALLBACK_PROMPT = """
Evaluate the following extracted obligation for quality.
Score each criterion from 0.0 to 1.0.

Obligation: {{obligation_json}}
Original Text: {{original_markdown}}

Criteria:
1. Metadata Accuracy: Are action_verb, subject_noun, clause_ref correct?
2. Legal Definition Alignment: Does it align with compliance terminology?
3. Rule Semantics: Is the intent preserved without loss?

Output ONLY valid JSON with this structure:
{
  "metadata_accuracy": <float 0.0-1.0>,
  "legal_alignment": <float 0.0-1.0>,
  "semantics": <float 0.0-1.0>,
  "overall_score": <float 0.0-1.0>,
  "status": "approved" or "repair",
  "feedback": "<string explaining what was good or what needs fixing>"
}
"""


def _load_prompt_template() -> str:
    """Load the judge prompt template from the prompts directory."""
    try:
        return PROMPT_TEMPLATE_PATH.read_text()
    except FileNotFoundError:
        logger.warning(
            "Judge prompt template not found at %s, using fallback", PROMPT_TEMPLATE_PATH
        )
        return FALLBACK_PROMPT


def _build_prompt(obligation: Union[Dict[str, Any], Any], original_markdown: str) -> str:
    """
    Build the full prompt by inserting obligation and original text into the template.

    Args:
        obligation: The extracted obligation (dict or Pydantic model).
        original_markdown: The original regulatory markdown text.

    Returns:
        Formatted prompt string ready for the LLM.
    """
    template = _load_prompt_template()

    obligation_json = json.dumps(
        obligation.model_dump() if hasattr(obligation, "model_dump") else obligation,
        indent=2,
    )

    return template.replace("{{obligation_json}}", obligation_json) \
                   .replace("{{original_markdown}}", original_markdown)


def _call_ollama(prompt: str) -> str:
    """
    Call Ollama with llama3.1 to evaluate the obligation.

    Args:
        prompt: Formatted prompt with obligation and original text.

    Returns:
        Raw JSON string response from the LLM.

    Raises:
        Exception: If the Ollama API is unreachable or returns an error.
    """
    try:
        import ollama
    except ImportError:
        logger.warning(
            "ollama package not installed. Cannot call judge LLM. "
            "Install with: pip install ollama"
        )
        raise RuntimeError("ollama package not installed")

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": OLLAMA_TEMPERATURE},
    )

    content = response.get("message", {}).get("content")
    if content is None:
        raise ValueError("Ollama returned null response from judge evaluation")
    return content


def _call_llm(prompt: str) -> str:
    """
    Call the LLM for judge evaluation (uses Ollama).

    Args:
        prompt: Formatted prompt with obligation and original text.

    Returns:
        Raw JSON string response from the LLM.

    Raises:
        Exception: If the LLM API is unreachable or returns an error.
    """
    return _call_ollama(prompt)


def _parse_judgment(raw_response: str) -> JudgmentResponse:
    """
    Parse and validate the LLM JSON response against the Pydantic schema.

    Per project rule: Never trust raw LLM output. Always use strict Pydantic
    validation with try/except fallbacks.

    Args:
        raw_response: Raw JSON string from the LLM judge.

    Returns:
        A validated JudgmentResponse object.

    Raises:
        ValueError: If the response cannot be parsed or validated.
    """
    try:
        parsed = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"Failed to parse judge JSON response: {e}") from e

    try:
        return JudgmentResponse(**parsed)
    except Exception as e:
        raise ValueError(
            f"Failed to validate judge response against schema: {e}. "
            f"Raw response: {raw_response[:500]}"
        ) from e


def _score_in_langfuse(
    judgment_response: JudgmentResponse,
    parent_trace_id: Optional[str] = None,
) -> None:
    """
    Log judge scores to Langfuse for observability.

    Graceful degradation: if langfuse is not installed (Langfuse is None),
    this function is a no-op.

    Args:
        judgment_response: The validated judgment to log.
        parent_trace_id: Optional trace_id from the extraction trace for
            cross-service linkage. If provided, this judge trace is linked
            as a child of the extraction trace.
    """
    if Langfuse is None:
        logger.debug("langfuse not installed, skipping score logging")
        return

    try:
        langfuse_client = Langfuse()
        trace_id = str(uuid.uuid4())

        trace_kwargs: Dict[str, Any] = {
            "id": trace_id,
            "name": "obligation-judge-evaluation",
        }
        if parent_trace_id:
            trace_kwargs["parent_observation_id"] = parent_trace_id

        with langfuse_client.trace(**trace_kwargs) as trace:
            trace.update_generation(
                name="judge-scoring",
                input={
                    "metadata_accuracy": judgment_response.judgment.metadata_accuracy,
                    "legal_alignment": judgment_response.judgment.legal_alignment,
                    "semantics": judgment_response.judgment.semantics,
                    "overall_score": judgment_response.judgment.overall_score,
                    "status": judgment_response.judgment.status,
                },
                output=judgment_response.judgment.feedback,
            )
        logger.info("Logged judge scores to Langfuse trace_id=%s", trace_id)
    except Exception as e:
        logger.warning("Failed to log judge scores to Langfuse: %s", e)


def _default_judgment(reason: str) -> JudgmentResponse:
    """
    Create a default/rejected judgment for error cases.

    Used when the LLM response cannot be parsed or validated.

    Args:
        reason: Explanation of why the default judgment was created.

    Returns:
        A JudgmentResponse with low scores and repair status.
    """
    return JudgmentResponse(
        judgment=Judgment(
            metadata_accuracy=0.0,
            legal_alignment=0.0,
            semantics=0.0,
            overall_score=0.0,
            status="repair",
            feedback=f"Judgment unavailable: {reason}",
        )
    )


def judge_extraction(
    obligation: Union[Dict[str, Any], Any],
    original_markdown: str,
    parent_trace_id: Optional[str] = None,
) -> JudgmentResponse:
    """
    Evaluate an extracted obligation for quality using the LLM-as-Judge.

    This is the main entry point for the judge evaluation pipeline.
    It builds a prompt with the obligation and original text, calls Ollama
    (llama3.1) for evaluation, validates the response, and logs to Langfuse.

    Args:
        obligation: The extracted obligation (dict or Pydantic model).
        original_markdown: The original regulatory markdown text.
        parent_trace_id: Optional trace_id from the extraction trace for
            cross-service linkage.

    Returns:
        A JudgmentResponse with scores and status.
        Returns a default repair judgment if the LLM fails.
    """
    # Handle empty input
    if not original_markdown or not original_markdown.strip():
        logger.warning("Empty original_markdown provided, returning default judgment")
        return _default_judgment("Empty original markdown")

    try:
        # Build prompt
        prompt = _build_prompt(obligation, original_markdown)
        logger.debug("Judge prompt built (length=%d)", len(prompt))

        # Call LLM
        raw_response = _call_llm(prompt)
        logger.debug("Judge LLM response received (length=%d)", len(raw_response))

        # Parse and validate
        judgment_response = _parse_judgment(raw_response)

        # Independently compute status from criterion scores (never trust LLM status)
        scores = [
            judgment_response.judgment.metadata_accuracy,
            judgment_response.judgment.legal_alignment,
            judgment_response.judgment.semantics,
        ]
        computed_status = "approved" if all(s >= THRESHOLD for s in scores) else "repair"

        # Reconstruct the judgment with the computed status, preserving
        # the LLM's feedback and scores
        judgment_response.judgment.status = computed_status

        logger.info(
            "Judge evaluation complete: status=%s, overall=%.2f",
            judgment_response.judgment.status,
            judgment_response.judgment.overall_score,
        )

        # Log to Langfuse
        _score_in_langfuse(judgment_response, parent_trace_id=parent_trace_id)

        return judgment_response

    except Exception as e:
        logger.error("Judge evaluation failed: %s", e)
        return _default_judgment(str(e))
