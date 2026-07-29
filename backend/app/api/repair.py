"""API router for the iterative repair endpoint (EXTRACT-3).

Re-submits low-scoring obligations to the LLM with judge feedback,
so that extraction quality improves automatically before committing
to the Silver layer.
"""

import logging

from fastapi import APIRouter, HTTPException
from typing import Optional

from pydantic import BaseModel, Field

from app.services.repair import repair_obligation

logger = logging.getLogger(__name__)

router = APIRouter(tags=["repair"])

DEFAULT_MAX_ATTEMPTS = 3


class RepairRequest(BaseModel):
    """Request body for the repair endpoint."""

    obligation: dict = Field(
        description="Extracted obligation object to repair.",
        examples=[{
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
        }],
    )
    judgment_feedback: str = Field(
        description="Judge feedback explaining what needs to be fixed.",
        examples=["The action_verb should include the modal verb 'shall'."],
    )
    original_markdown: str = Field(
        description="Original regulatory Markdown text for context.",
        examples=["# Section 3: Access Control\n\nThe organization must limit..."],
    )
    max_attempts: int = Field(
        default=DEFAULT_MAX_ATTEMPTS,
        description="Maximum number of repair attempts (default: 3).",
    )
    trace_id: str = Field(
        default="",
        description="Langfuse trace_id from the extraction endpoint for trace linkage.",
    )


class RepairResponse(BaseModel):
    """Response body for the repair endpoint."""

    obligation: Optional[dict] = Field(
        default=None,
        description="The repaired obligation, or null if rejected.",
    )
    status: str = Field(
        description="Repair outcome: 'repaired', 'rejected', or 'original_kept'.",
    )
    attempts: int = Field(
        description="Number of repair attempts made.",
    )


@router.post("", response_model=RepairResponse)
def repair_obligation_endpoint(request: RepairRequest):
    """
    Re-submit a low-scoring obligation to the LLM with judge feedback.

    Calls the repair service which iteratively retries up to max_attempts
    times. Returns the repaired obligation, final status, and attempt count.

    **Acceptance Criteria:**
    - AC-1: Accepts obligation, feedback, and markdown via POST body
    - AC-2: Returns 'repaired' when a valid repair is produced
    - AC-3: Returns 'rejected' when all attempts fail
    - AC-4: Returns 'original_kept' when feedback is empty
    - AC-5: Supports configurable max_attempts (default 3)
    - AC-6: Response includes attempt count for observability

    POST /api/v1/repair
    """
    max_attempts = request.max_attempts

    try:
        parent_trace_id = request.trace_id if request.trace_id else None
        obligation, status, attempts_made = repair_obligation(
            obligation=request.obligation,
            judgment_feedback=request.judgment_feedback,
            original_markdown=request.original_markdown,
            max_attempts=max_attempts,
            parent_trace_id=parent_trace_id,
        )
    except Exception as e:
        logger.error("Repair failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Repair failed: {e}",
        )

    return RepairResponse(
        obligation=obligation.model_dump() if obligation else None,
        status=status,
        attempts=attempts_made,
    )
