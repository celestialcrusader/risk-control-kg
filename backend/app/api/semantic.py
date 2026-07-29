"""API router for Silver Layer Storage (EXTRACT-4).

POST /api/v1/semantic — write a validated obligation to the Silver layer.
"""

import logging

from fastapi import APIRouter, HTTPException
from typing import Optional

from pydantic import BaseModel, Field

from app.services.silver_layer import write_silver_record
from app.schemas.obligation import Obligation

logger = logging.getLogger(__name__)

router = APIRouter(tags=["semantic"])


class SemanticRequest(BaseModel):
    """Request body for the semantic storage endpoint."""

    obligation: Obligation = Field(
        description="Validated Obligation object to persist to the Silver layer.",
        examples=[{
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
        }],
    )
    bronze_record_id: str = Field(
        default=None,
        description="Optional UUID string of the Bronze layer staging_controls record.",
    )


class SemanticResponse(BaseModel):
    """Response body for the semantic storage endpoint."""

    id: str = Field(description="UUID of the created SemanticControl record.")
    status: str = Field(description="Control status, e.g. 'pending_validation'.")
    version: int = Field(description="Application-level version number.")
    control_id: str = Field(description="The obligation identifier.")
    framework_name: str = Field(description="Framework name, always 'de-jure'.")
    bronze_record_id: Optional[str] = Field(
        default=None,
        description="UUID of the linked Bronze layer record, if provided.",
    )


@router.post("", response_model=SemanticResponse)
def write_semantic_record_endpoint(request: SemanticRequest):
    """
    Write a validated obligation to the Silver layer (semantic_controls).

    Accepts a validated Obligation object, writes it to the PostgreSQL
    semantic_controls table, and returns the created record metadata.

    **Acceptance Criteria:**
    - AC-1: Write a record to the Silver layer
    - AC-2: Record includes all facet fields
    - AC-3: Status is set to pending_validation
    - AC-4: bronze_record_id FK is set when provided
    - AC-5: Versioning is handled by the service layer

    POST /api/v1/semantic
    """
    try:
        from uuid import UUID

        bronze_id = None
        if request.bronze_record_id:
            bronze_id = UUID(request.bronze_record_id)

        record = write_silver_record(
            obligation=request.obligation,
            session=None,  # Service will use its own session
            bronze_record_id=bronze_id,
        )
    except Exception as e:
        logger.error("Silver layer write failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Silver layer write failed: {e}",
        )

    return SemanticResponse(
        id=str(record.id),
        status=record.status,
        version=record.version,
        control_id=record.control_id,
        framework_name=record.framework_name,
        bronze_record_id=str(record.bronze_record_id) if record.bronze_record_id else None,
    )
