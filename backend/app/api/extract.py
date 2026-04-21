"""API router for obligation extraction (EXTRACT-1)."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.extraction import _extract_obligations_with_storage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["extraction"])


class ExtractionRequest(BaseModel):
    """Request body for the extraction endpoint."""

    markdown_content: str = Field(
        description="Regulatory Markdown text from the Bronze layer.",
        examples=["# Section 3: Access Control\n\nThe organization must limit..."],
    )
    source_document_id: str = Field(
        default=None,
        description="Optional UUID string of the source document to link extracted obligations to.",
    )


class ExtractionResponse(BaseModel):
    """Response body for the extraction endpoint."""

    obligation_count: int = Field(description="Number of obligations extracted.")
    obligations: list[dict] = Field(description="List of extracted obligation objects.")
    storage_succeeded: bool = Field(
        description="Whether database storage of the extracted obligations succeeded."
    )


@router.post("", response_model=ExtractionResponse)
def extract_obligations_endpoint(request: ExtractionRequest):
    """
    Extract atomic rule units from regulatory Markdown text.

    Accepts Markdown content, calls the configured LLM (vLLM or Ollama),
    validates the output against the Pydantic schema, and stores results
    in the PostgreSQL semantic_controls (Silver layer) table.

    **Acceptance Criteria:**
    - AC-1: Accepts markdown content via POST body and returns extracted obligations
    - AC-2: Returns obligation objects with all required fields (id, prose, action_verb,
      subject_noun, clause_ref)
    - AC-3: Optionally links obligations to a source document via source_document_id
    - AC-4: Returns storage success/failure status for observability
    - AC-5: Rejects empty markdown with HTTP 400

    POST /api/v1/extract
    """
    if not request.markdown_content or not request.markdown_content.strip():
        raise HTTPException(
            status_code=400,
            detail="markdown_content must not be empty or whitespace-only.",
        )

    try:
        source_doc_id = None
        if request.source_document_id:
            source_doc_id = request.source_document_id

        obligations, storage_succeeded = _extract_obligations_with_storage(
            markdown_content=request.markdown_content,
            source_document_id=source_doc_id,
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {e}",
        )

    return ExtractionResponse(
        obligation_count=len(obligations),
        obligations=[o.model_dump() for o in obligations],
        storage_succeeded=storage_succeeded,
    )
