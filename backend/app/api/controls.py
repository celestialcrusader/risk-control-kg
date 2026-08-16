"""
Control mappings query API router for MVP2 (MVP2-303).
"""

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ControlMappingResponse(BaseModel):
    obligation_id: str
    obligation_prose: str
    framework_name: str
    set_theory_relation: str
    confidence_score: float
    judge_status: str  # APPROVED | PENDING_HITL_REVIEW | PENDING_JUDGE_REVIEW


from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.rckg_nodes import GraphOutboxLog


@router.get("/controls/{control_id}/mappings", response_model=List[ControlMappingResponse])
def get_control_mappings(control_id: str, db: Session = Depends(get_db)):
    """
    GET /api/controls/{control_id}/mappings (REMED-103)
    Returns all obligation mappings for a specified control from database outbox log.
    """
    outbox_entries = db.query(GraphOutboxLog).all()

    results = []
    for entry in outbox_entries:
        payload = entry.payload or {}
        t_id = payload.get("target_id") or payload.get("target_node_id") or ""
        if t_id == control_id:
            results.append(
                ControlMappingResponse(
                    obligation_id=payload.get("source_id") or payload.get("source_node_id") or "OBL-UNKNOWN",
                    obligation_prose=payload.get("source_text") or payload.get("prose") or "Extracted obligation text",
                    framework_name=payload.get("framework") or "NIST-800-53",
                    set_theory_relation=payload.get("set_theory_relation") or payload.get("relation_type") or "EQUIVALENT_TO",
                    confidence_score=float(payload.get("confidence_score", 0.90)),
                    judge_status=entry.status,
                )
            )
    return results
