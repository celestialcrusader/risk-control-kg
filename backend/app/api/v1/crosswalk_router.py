"""
FastAPI Router for Canonical Crosswalk Query Endpoints (STORY-MCP-101)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, cast, Float

from app.core.database import get_db
from app.models.rckg_nodes import ObligationNode, FrameworkControlObjectiveNode, ObligationFrameworkMapping, SemanticRelation, AssuranceCoverage
from app.models import AuditLog
from app.schemas.crosswalk_api import (
    ObligationItem, ObligationListResponse,
    ControlItem, ControlListResponse,
    CrosswalkEdgeItem, CrosswalkListResponse,
    AuditorOverrideRequest, AuditorOverrideResponse,
    AuditLogItem, AuditLogListResponse
)

router = APIRouter(prefix="", tags=["Canonical Crosswalk API"])

WITHDRAWN_NIST_IDS = {
    "NIST-AC-9", "NIST-AC-13", "NIST-AC-15", "NIST-AT-5", "NIST-AU-13", "NIST-AU-15",
    "NIST-CA-4", "NIST-CM-13", "NIST-CP-5", "NIST-IA-13", "NIST-IR-10", "NIST-MA-1",
    "NIST-MP-8", "NIST-PE-7", "NIST-PE-11", "NIST-PE-12", "NIST-PE-19", "NIST-PL-3",
    "NIST-PS-9", "NIST-RA-4", "NIST-SA-6", "NIST-SA-7", "NIST-SA-12", "NIST-SA-13",
    "NIST-SA-14", "NIST-SA-18", "NIST-SA-19", "NIST-SC-6", "NIST-SC-9", "NIST-SI-9"
}


@router.get("/obligations", response_model=ObligationListResponse)
def get_obligations(
    framework: Optional[str] = Query(None, description="Framework name (e.g. MAS-TRM)"),
    search: Optional[str] = Query(None, description="Keyword search in statement text"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(ObligationNode)
    if framework:
        query = query.filter(ObligationNode.framework_name == framework)
    if search:
        query = query.filter(ObligationNode.statement_text.ilike(f"%{search}%"))
    
    total = query.count()
    items_db = query.order_by(ObligationNode.obligation_id).offset(offset).limit(limit).all()
    
    items = []
    for item in items_db:
        chap = None
        if item.obligation_id.startswith("MAS-"):
            parts = item.obligation_id.replace("MAS-", "").split(".")
            if parts:
                chap = f"Chapter {parts[0]}"
        items.append(ObligationItem(
            id=str(item.id),
            obligation_id=item.obligation_id,
            statement_text=item.statement_text or "",
            framework_name=item.framework_name or "MAS-TRM",
            chapter=chap,
            section=item.section_identifier
        ))
    
    return ObligationListResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/controls", response_model=ControlListResponse)
def get_controls(
    framework: Optional[str] = Query(None, description="Framework name (e.g. NIST-SP-800-53)"),
    active_only: bool = Query(True, description="Exclude purged/withdrawn controls"),
    search: Optional[str] = Query(None, description="Keyword search in control name/text"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(FrameworkControlObjectiveNode)
    if framework:
        query = query.filter(FrameworkControlObjectiveNode.framework_name == framework)
    if active_only:
        query = query.filter(~FrameworkControlObjectiveNode.framework_obj_id.in_(WITHDRAWN_NIST_IDS))
        query = query.filter(FrameworkControlObjectiveNode.objective_text != None)
        query = query.filter(FrameworkControlObjectiveNode.objective_text != "")
    if search:
        query = query.filter(
            (FrameworkControlObjectiveNode.objective_name.ilike(f"%{search}%")) |
            (FrameworkControlObjectiveNode.objective_text.ilike(f"%{search}%"))
        )
    
    total = query.count()
    items_db = query.order_by(FrameworkControlObjectiveNode.framework_obj_id).offset(offset).limit(limit).all()
    
    items = []
    for item in items_db:
        items.append(ControlItem(
            id=str(item.id),
            control_id=item.framework_obj_id,
            control_name=item.objective_name or "",
            control_text=item.objective_text or "",
            framework_name=item.framework_name or "NIST-SP-800-53",
            is_active=item.framework_obj_id not in WITHDRAWN_NIST_IDS
        ))
    
    return ControlListResponse(total=total, limit=limit, offset=offset, items=items)


@router.get("/crosswalk", response_model=CrosswalkListResponse)
def get_crosswalk(
    source_id: Optional[str] = Query(None, description="Filter by source obligation ID (e.g. MAS-7.6.1)"),
    target_id: Optional[str] = Query(None, description="Filter by target control ID (e.g. NIST-AC-5)"),
    semantic_relation: Optional[SemanticRelation] = Query(None, description="Filter by semantic relation"),
    assurance_coverage: Optional[AssuranceCoverage] = Query(None, description="Filter by assurance coverage"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = (
        db.query(ObligationFrameworkMapping, ObligationNode, FrameworkControlObjectiveNode)
        .join(ObligationNode, ObligationFrameworkMapping.obligation_id == ObligationNode.id)
        .join(FrameworkControlObjectiveNode, ObligationFrameworkMapping.framework_objective_id == FrameworkControlObjectiveNode.id)
    )
    
    if source_id:
        query = query.filter(ObligationNode.obligation_id == source_id)
    if target_id:
        query = query.filter(FrameworkControlObjectiveNode.framework_obj_id == target_id)
    if semantic_relation:
        query = query.filter(ObligationFrameworkMapping.semantic_relation == semantic_relation)
    if assurance_coverage:
        query = query.filter(ObligationFrameworkMapping.assurance_coverage == assurance_coverage)
    if min_confidence is not None:
        query = query.filter(cast(ObligationFrameworkMapping.confidence_score, Float) >= min_confidence)
    
    total = query.count()
    results = query.order_by(desc(ObligationFrameworkMapping.confidence_score)).offset(offset).limit(limit).all()
    
    items = []
    for mapping, obl, ctrl in results:
        items.append(CrosswalkEdgeItem(
            mapping_id=str(mapping.id),
            source_id=obl.obligation_id,
            source_text=obl.statement_text or "",
            source_framework=obl.framework_name or "MAS-TRM",
            target_id=ctrl.framework_obj_id,
            target_name=ctrl.objective_name or "",
            target_text=ctrl.objective_text or "",
            target_framework=ctrl.framework_name or "NIST-SP-800-53",
            semantic_relation=mapping.semantic_relation,
            assurance_coverage=mapping.assurance_coverage,
            confidence_score=float(mapping.confidence_score or 0.0),
            rationale=mapping.rationale or "",
            human_approved=False
        ))
    
    return CrosswalkListResponse(total=total, limit=limit, offset=offset, items=items)


@router.post("/mappings/{mapping_id}/override", response_model=AuditorOverrideResponse)
def override_mapping(
    mapping_id: str,
    req: AuditorOverrideRequest,
    db: Session = Depends(get_db)
):
    try:
        mapping = db.query(ObligationFrameworkMapping).filter(ObligationFrameworkMapping.id == mapping_id).first()
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid mapping ID format or mapping not found")

    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    obl = db.query(ObligationNode).filter(ObligationNode.id == mapping.obligation_id).first()
    ctrl = db.query(FrameworkControlObjectiveNode).filter(FrameworkControlObjectiveNode.id == mapping.framework_objective_id).first()

    old_rel = mapping.semantic_relation.value if hasattr(mapping.semantic_relation, "value") else str(mapping.semantic_relation)
    old_cov = mapping.assurance_coverage.value if hasattr(mapping.assurance_coverage, "value") else str(mapping.assurance_coverage)

    # Apply auditor override
    mapping.semantic_relation = req.semantic_relation
    mapping.assurance_coverage = req.assurance_coverage
    mapping.rationale = f"[AUDITOR OVERRIDE by {req.auditor_id}]: {req.justification} | Original: {mapping.rationale}"
    
    # Record immutable audit log
    audit_entry = AuditLog(
        event_type="MAPPING_AUDITOR_OVERRIDE",
        actor_id=req.auditor_id,
        actor_type="auditor",
        event_data={
            "mapping_id": mapping_id,
            "source_id": obl.obligation_id if obl else "",
            "target_id": ctrl.framework_obj_id if ctrl else "",
            "old_relation": old_rel,
            "new_relation": req.semantic_relation.value,
            "old_coverage": old_cov,
            "new_coverage": req.assurance_coverage.value,
            "justification": req.justification,
        }
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(mapping)

    return AuditorOverrideResponse(
        id=str(mapping.id),
        obligation_id=obl.obligation_id if obl else "",
        framework_obj_id=ctrl.framework_obj_id if ctrl else "",
        semantic_relation=mapping.semantic_relation,
        assurance_coverage=mapping.assurance_coverage,
        confidence_score=float(mapping.confidence_score or 1.0),
        rationale=mapping.rationale,
        override_applied=True,
        auditor_id=req.auditor_id,
        justification=req.justification
    )


@router.get("/audit-logs", response_model=AuditLogListResponse)
def get_audit_logs(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)

    total = query.count()
    records = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()

    items = [
        AuditLogItem(
            id=str(r.id),
            event_type=r.event_type,
            actor_id=r.actor_id,
            actor_type=r.actor_type,
            event_data=r.event_data or {},
            timestamp=r.timestamp.isoformat() if r.timestamp else None
        )
        for r in records
    ]

    return AuditLogListResponse(total=total, limit=limit, offset=offset, items=items)

