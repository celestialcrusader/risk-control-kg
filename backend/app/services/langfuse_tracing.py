"""
Langfuse tracing helpers for OBSERV-1.

Provides extraction-specific Langfuse tracing functions with graceful
degradation. All functions use conditional Langfuse import and try/except
blocks so that Langfuse failures never break the extraction pipeline.

Pattern (same as judge.py and repair.py):
    try:
        from langfuse import Langfuse
    except ImportError:
        Langfuse = None

All public functions:
- Accept a trace_id parameter for cross-service linkage
- Return the trace_id on success, None on graceful degradation
- Never raise exceptions
"""

import logging
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Conditionally import langfuse; may not be installed
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
    logger.debug("langfuse not installed, observability logging will be skipped")


def extract_and_trace(
    markdown_content: str,
    prompt: str,
    completion: str,
    model_used: str,
    document_id: Optional[str] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Create a Langfuse trace and span for the extraction call.

    This is the main tracing entry point for the extraction pipeline.
    It creates a trace with a unique trace_id and a generation span
    containing the prompt, completion, and token usage.

    Args:
        markdown_content: The regulatory markdown being extracted.
        prompt: The full prompt sent to the LLM.
        completion: The raw JSON completion from the LLM.
        model_used: The model name used (e.g., "mistralai/Mistral-8B").
        document_id: Optional source document identifier.
        prompt_tokens: Optional count of input tokens.
        completion_tokens: Optional count of output tokens.

    Returns:
        Dict with trace_id and token usage on success, or None if
        Langfuse is unavailable or an error occurred.
    """
    if Langfuse is None:
        logger.debug("langfuse not installed, skipping extraction tracing")
        return None

    try:
        langfuse_client = Langfuse()
        trace_id = str(uuid.uuid4())

        with langfuse_client.trace(
            id=trace_id,
            name="extraction",
            input=prompt,
            metadata={
                "document_id": document_id,
                "model": model_used,
                "markdown_length": len(markdown_content),
            },
        ) as trace:
            trace.update_generation(
                name="extraction-prompt",
                input=prompt,
                output=completion,
                metadata={
                    "model": model_used,
                    "document_id": document_id,
                },
                usage={
                    "promptTokens": prompt_tokens,
                    "completionTokens": completion_tokens,
                    "totalTokens": (prompt_tokens or 0) + (completion_tokens or 0),
                },
            )

        result: Dict[str, Any] = {"trace_id": trace_id}
        if prompt_tokens is not None:
            result["prompt_tokens"] = prompt_tokens
        if completion_tokens is not None:
            result["completion_tokens"] = completion_tokens

        logger.info("Traced extraction trace_id=%s model=%s", trace_id, model_used)
        return result

    except Exception as e:
        logger.warning("Failed to trace extraction in Langfuse: %s", e)
        return None


def log_extraction_failure(
    trace_id: str,
    judge_feedback: str,
    repair_attempts: int,
    final_status: str,
    document_id: Optional[str] = None,
) -> None:
    """
    Log an extraction failure to Langfuse with judge feedback and repair info.

    Creates a separate failure trace that includes the original trace_id
    reference, judge feedback, and number of repair attempts.

    Args:
        trace_id: The original extraction trace_id for correlation.
        judge_feedback: The LLM-as-Judge feedback explaining what was wrong.
        repair_attempts: Number of repair attempts made before failure.
        final_status: Final status (e.g., "rejected", "repair").
        document_id: Optional source document identifier.
    """
    if Langfuse is None:
        logger.debug("langfuse not installed, skipping failure logging")
        return

    try:
        langfuse_client = Langfuse()

        with langfuse_client.trace(
            id=str(uuid.uuid4()),
            name="extraction-failure",
            input=judge_feedback,
            metadata={
                "original_trace_id": trace_id,
                "document_id": document_id,
                "repair_attempts": repair_attempts,
                "final_status": final_status,
            },
        ) as trace:
            trace.update_generation(
                name="failure-analysis",
                output=judge_feedback,
                metadata={
                    "repair_attempts": repair_attempts,
                    "final_status": final_status,
                    "original_trace_id": trace_id,
                },
            )

        logger.info(
            "Logged extraction failure to Langfuse original_trace_id=%s status=%s",
            trace_id,
            final_status,
        )

    except Exception as e:
        logger.warning("Failed to log extraction failure to Langfuse: %s", e)
