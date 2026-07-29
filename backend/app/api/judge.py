"""API router for the LLM-as-Judge quality evaluation endpoint (EXTRACT-2)."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.judge import judge_extraction
from app.schemas.judge import JudgmentResponse

logger = logging.getLogger(__name__)

# Maximum allowed length for original_markdown input
MAX_MARKDOWN_LENGTH = 100_000

router = APIRouter(tags=["judge"])


class JudgeRequest(BaseModel):
    """Request body for the judge endpoint."""

    obligation: dict = Field(
        description="Extracted obligation object to evaluate.",
        examples=[{
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
        }],
    )
    original_markdown: str = Field(
        description="Original regulatory Markdown text for context.",
        examples=["# Section 3: Access Control\n\nThe organization must limit..."],
    )
    trace_id: str = Field(
        default="",
        description="Langfuse trace_id from the extraction endpoint for trace linkage.",
    )


class JudgeResponse(BaseModel):
    """Response body for the judge endpoint."""

    judgment: dict = Field(
        description="Judge evaluation results including scores and status.",
    )


@router.post("", response_model=JudgeResponse)
def judge_extraction_endpoint(request: JudgeRequest):
    """
    Evaluate an extracted obligation for quality using the LLM-as-Judge.

    Scores the obligation across three criteria (metadata accuracy, legal
    alignment, rule semantics) using Ollama with Llama 3.1. Returns an
    approved or repair status with detailed feedback.

    **Acceptance Criteria:**
    - AC-1: Returns scores (0.0-1.0) for each of the three criteria
    - AC-2: Status is 'approved' when all criteria >= 0.80
    - AC-3: Status is 'repair' with feedback when any criterion < 0.80
    - AC-4: Uses Ollama (local dev) with Llama 3.1 model
    - AC-5: Output includes detailed feedback explaining scores
    - AC-6: Scores logged to Langfuse with trace_id

    POST /api/v1/judge
    """
    if not request.original_markdown or not request.original_markdown.strip():
        raise HTTPException(
            status_code=400,
            detail="original_markdown must not be empty or whitespace-only.",
        )

    if len(request.original_markdown) > MAX_MARKDOWN_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"original_markdown exceeds maximum length of {MAX_MARKDOWN_LENGTH} characters.",
        )

    try:
        parent_trace_id = request.trace_id if request.trace_id else None
        response = judge_extraction(
            obligation=request.obligation,
            original_markdown=request.original_markdown,
            parent_trace_id=parent_trace_id,
        )
    except Exception as e:
        logger.error("Judge evaluation failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Judge evaluation failed: {e}",
        )

    return JudgeResponse(judgment=response.judgment.model_dump())
