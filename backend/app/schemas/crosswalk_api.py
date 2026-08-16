"""
Pydantic Schemas for Canonical REST API (Sprint P)
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.rckg_nodes import SemanticRelation, AssuranceCoverage


class ObligationItem(BaseModel):
    id: str
    obligation_id: str
    statement_text: str
    framework_name: str
    chapter: Optional[str] = None
    section: Optional[str] = None


class ObligationListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ObligationItem]


class ControlItem(BaseModel):
    id: str
    control_id: str
    control_name: str
    control_text: str
    framework_name: str
    is_active: bool = True


class ControlListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ControlItem]


class CrosswalkEdgeItem(BaseModel):
    mapping_id: str
    source_id: str
    source_text: str
    source_framework: str
    target_id: str
    target_name: str
    target_text: str
    target_framework: str
    semantic_relation: SemanticRelation
    assurance_coverage: AssuranceCoverage
    confidence_score: float
    rationale: str
    human_approved: bool = False
    override_reason: Optional[str] = None


class CrosswalkListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[CrosswalkEdgeItem]


class GapItem(BaseModel):
    obligation_id: str
    statement_text: str
    framework_name: str
    category: str
    audit_root_cause: str
    suggested_remediation: str


class CategorizedGapsResponse(BaseModel):
    total_true_gaps: int
    category_a_unmatched: List[GapItem]
    category_b_retail_mandates: List[GapItem]


class ChapterCoverageItem(BaseModel):
    chapter: str
    total_obligations: int
    fully_covered: int
    partially_covered: int
    uncovered: int
    coverage_pct: float


class CoverageRateBreakdown(BaseModel):
    full_coverage_pct: float
    partial_coverage_pct: float
    no_coverage_pct: float


class CoverageSummaryResponse(BaseModel):
    total_obligations: int
    active_controls: int
    total_linkages: int
    coverage_rates: CoverageRateBreakdown
    chapter_breakdown: List[ChapterCoverageItem]


class RealtimeEvaluationRequest(BaseModel):
    source_text: str = Field(..., min_length=5)
    target_text: str = Field(..., min_length=5)


class RealtimeEvaluationResponse(BaseModel):
    semantic_relation: SemanticRelation
    assurance_coverage: AssuranceCoverage
    confidence_score: float
    rationale: str


class AuditorOverrideRequest(BaseModel):
    semantic_relation: SemanticRelation
    assurance_coverage: AssuranceCoverage
    auditor_id: str = Field(..., min_length=2)
    justification: str = Field(..., min_length=5)


class AuditorOverrideResponse(BaseModel):
    id: str
    obligation_id: str
    framework_obj_id: str
    semantic_relation: SemanticRelation
    assurance_coverage: AssuranceCoverage
    confidence_score: float
    rationale: str
    override_applied: bool = True
    auditor_id: str
    justification: str


class AuditLogItem(BaseModel):
    id: str
    event_type: str
    actor_id: Optional[str] = None
    actor_type: Optional[str] = None
    event_data: dict
    timestamp: Optional[str] = None


class AuditLogListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[AuditLogItem]


