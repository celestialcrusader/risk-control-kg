"""
SQLAlchemy ORM Models for Pure RCKG Graph Entities & Set-Theory Linkages

Defines the 6 core graph node types and 5 explicit linkage relationship tables
storing mathematical set-theory classifications (EQUIVALENT_TO, SUPERSET_OF,
SUBSET_OF, INTERSECTS_WITH, NO_RELATIONSHIP) as specified in 06-delta.md.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    Enum as SQLEnum,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from backend.app.models import Base


# =============================================================================
# Set-Theory & Gap Enumerations
# =============================================================================

class SetTheoryRelation(str, Enum):
    """
    Formal Set-Theory Relationship Semantics for Graph Linkages:
    - EQUIVALENT_TO (≡): Full 1:1 match (A = B)
    - SUPERSET_OF (⊃): Source completely covers target + surplus (A ⊃ B)
    - SUBSET_OF (⊂): Partial coverage; gap flagged (A ⊂ B)
    - CONTINGENT_SATISFIES (cond): Satisfies target ONLY IF operational conditions met
    - INTERSECTS_WITH (∩): Partial overlap; review flagged (A ∩ B ≠ ∅)
    - NO_RELATIONSHIP (∅): Disjoint; critical gap flagged (A ∩ B = ∅)
    """
    EQUIVALENT_TO = "EQUIVALENT_TO"
    SUPERSET_OF = "SUPERSET_OF"
    SUBSET_OF = "SUBSET_OF"
    CONTINGENT_SATISFIES = "CONTINGENT_SATISFIES"
    INTERSECTS_WITH = "INTERSECTS_WITH"
    NO_RELATIONSHIP = "NO_RELATIONSHIP"



class GapSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GapState(str, Enum):
    NEW = "NEW"
    IN_REMEDIATION = "IN_REMEDIATION"
    REMEDIATED = "REMEDIATED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


# =============================================================================
# 1. Core Domain Entity Node Models
# =============================================================================

class ObligationNode(Base):
    """
    Regulatory / Statutory Mandate Clause (e.g. EU AI Act Art 10.1, DORA Art 6).
    Source: Regulatory Documents.
    """
    __tablename__ = "obligations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    obligation_id = Column(String(255), nullable=False, unique=True, index=True)
    framework_name = Column(String(255), nullable=False, index=True)
    framework_version = Column(String(50))
    statement_text = Column(Text, nullable=False)
    action_verb = Column(String(100), index=True)
    subject_noun = Column(String(255), index=True)
    source_document_id = Column(UUID(as_uuid=True))
    section_reference = Column(String(512))
    
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_obligation_framework", "framework_name", "framework_version"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "obligation_id": self.obligation_id,
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "statement_text": self.statement_text,
            "action_verb": self.action_verb,
            "subject_noun": self.subject_noun,
            "source_document_id": str(self.source_document_id) if self.source_document_id else None,
            "section_reference": self.section_reference,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ControlObjectiveNode(Base):
    """
    High-Level Internal Corporate Governance / Policy Target.
    Source: Corporate Policy Documents.
    """
    __tablename__ = "control_objectives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    objective_id = Column(String(255), nullable=False, unique=True, index=True)
    policy_name = Column(String(255), nullable=False, index=True)
    policy_version = Column(String(50))
    objective_name = Column(String(512), nullable=False)
    objective_text = Column(Text, nullable=False)
    owner = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_objective_policy", "policy_name", "policy_version"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "objective_id": self.objective_id,
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
            "objective_name": self.objective_name,
            "objective_text": self.objective_text,
            "owner": self.owner,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ControlActivityNode(Base):
    """
    Concrete Procedural Step, SOP, Standard, or Technical Configuration.
    Source: Process Docs, SOPs, Standards, User Guides, Instruction Manuals.
    """
    __tablename__ = "control_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    activity_id = Column(String(255), nullable=False, unique=True, index=True)
    sop_name = Column(String(255), nullable=False, index=True)
    sop_version = Column(String(50))
    activity_name = Column(String(512), nullable=False)
    activity_text = Column(Text, nullable=False)
    implementation_method = Column(String(100), default="AUTOMATED")  # AUTOMATED, MANUAL, HYBRID

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_activity_sop", "sop_name", "sop_version"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "activity_id": self.activity_id,
            "sop_name": self.sop_name,
            "sop_version": self.sop_version,
            "activity_name": self.activity_name,
            "activity_text": self.activity_text,
            "implementation_method": self.implementation_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FrameworkControlObjectiveNode(Base):
    """
    Standardized Benchmark Control Objective.
    Source: Industry Standards (ISO 27001, NIST AI RMF, NIST CSF, IM8).
    """
    __tablename__ = "framework_control_objectives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    framework_obj_id = Column(String(255), nullable=False, unique=True, index=True)
    framework_name = Column(String(255), nullable=False, index=True)  # e.g., 'NIST AI RMF'
    framework_version = Column(String(50))
    objective_name = Column(String(512), nullable=False)
    objective_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_framework_obj_name", "framework_name", "framework_version"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "framework_obj_id": self.framework_obj_id,
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "objective_name": self.objective_name,
            "objective_text": self.objective_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FrameworkControlActivityNode(Base):
    """
    Standardized Benchmark Granular Control Activity.
    Source: Industry Standards Implementation Guidance (NIST SP 800-53, IM8 Clauses).
    """
    __tablename__ = "framework_control_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    framework_act_id = Column(String(255), nullable=False, unique=True, index=True)
    framework_name = Column(String(255), nullable=False, index=True)  # e.g., 'NIST SP 800-53'
    framework_version = Column(String(50))
    activity_name = Column(String(512), nullable=False)
    activity_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_framework_act_name", "framework_name", "framework_version"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "framework_act_id": self.framework_act_id,
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "activity_name": self.activity_name,
            "activity_text": self.activity_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RiskNode(Base):
    """
    Inherent or Operational Threat/Vulnerability.
    Source: Enterprise Risk Inventories & Threat Catalogs.
    """
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    risk_id = Column(String(255), nullable=False, unique=True, index=True)
    risk_name = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="OPERATIONAL", index=True)
    severity_level = Column(String(50), default="MEDIUM", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "risk_id": self.risk_id,
            "risk_name": self.risk_name,
            "description": self.description,
            "category": self.category,
            "severity_level": self.severity_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class GapNode(Base):
    """
    Unmitigated Compliance Gap generated when set relation is SUBSET_OF, INTERSECTS_WITH, or NO_RELATIONSHIP.
    """
    __tablename__ = "gaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    gap_id = Column(String(255), nullable=False, unique=True, index=True)
    target_entity_type = Column(String(100), nullable=False, index=True)  # e.g., 'Obligation', 'ControlObjective'
    target_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    severity = Column(SQLEnum(GapSeverity), default=GapSeverity.MEDIUM, nullable=False)
    state = Column(SQLEnum(GapState), default=GapState.NEW, nullable=False, index=True)
    due_date = Column(DateTime(timezone=True))
    reviewer_id = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "gap_id": self.gap_id,
            "target_entity_type": self.target_entity_type,
            "target_entity_id": str(self.target_entity_id),
            "set_theory_relation": self.set_theory_relation.value if self.set_theory_relation else None,
            "severity": self.severity.value if self.severity else None,
            "state": self.state.value if self.state else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "reviewer_id": self.reviewer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MappingStatus(str, Enum):
    PROBABILISTIC_AI = "PROBABILISTIC_AI"
    HUMAN_ATTESTED = "HUMAN_ATTESTED"


class ShortCircuitAuditLog(Base):
    """
    Audit log for facet disjoint short-circuited candidate pairs.
    Prevents silent false negatives by tracking short-circuited evaluations for random sampling.
    """
    __tablename__ = "short_circuit_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_entity_type = Column(String(100), nullable=False, index=True)
    source_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_entity_type = Column(String(100), nullable=False, index=True)
    target_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    disjoint_reason = Column(Text, nullable=False)
    is_sampled_for_audit = Column(String(10), default="FALSE", index=True)
    audit_result = Column(String(50))  # e.g., 'CONFIRMED_DISJOINT', 'FALSE_NEGATIVE_CORRECTED'

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =============================================================================
# 2. Explicit 5-Linkage Set-Theory Relationship Tables
# =============================================================================

class RiskControlObjectiveMapping(Base):

    """Linkage 1: Risk <---> Control Objective (MITIGATES)"""
    __tablename__ = "risk_control_objective_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risks.id"), nullable=False, index=True)
    control_objective_id = Column(UUID(as_uuid=True), ForeignKey("control_objectives.id"), nullable=False, index=True)
    
    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    condition_clause = Column(Text)
    condition_confidence = Column(String(10), default="0.00")
    confidence_score = Column(String(10), default="0.00")
    logic_judge_score = Column(String(10), default="0.00")
    technical_judge_score = Column(String(10), default="0.00")
    status = Column(SQLEnum(MappingStatus), default=MappingStatus.PROBABILISTIC_AI, nullable=False)
    is_golden_assertion = Column(String(10), default="FALSE", index=True)
    model_version = Column(String(100))
    prompt_version = Column(String(100))
    embedding_model = Column(String(100))
    attested_by = Column(String(255))
    attested_at = Column(DateTime(timezone=True))
    reverted_by = Column(String(255))
    reverted_at = Column(DateTime(timezone=True))
    revert_reason = Column(Text)
    rationale = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("risk_id", "control_objective_id", name="uq_risk_obj_mapping"),
    )


class ObligationControlObjectiveMapping(Base):
    """Linkage 2: Obligation <---> Control Objective (SATISFIES)"""
    __tablename__ = "obligation_control_objective_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    obligation_id = Column(UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False, index=True)
    control_objective_id = Column(UUID(as_uuid=True), ForeignKey("control_objectives.id"), nullable=False, index=True)

    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    condition_clause = Column(Text)
    condition_confidence = Column(String(10), default="0.00")
    confidence_score = Column(String(10), default="0.00")
    logic_judge_score = Column(String(10), default="0.00")
    technical_judge_score = Column(String(10), default="0.00")
    status = Column(SQLEnum(MappingStatus), default=MappingStatus.PROBABILISTIC_AI, nullable=False)
    is_golden_assertion = Column(String(10), default="FALSE", index=True)
    model_version = Column(String(100))
    prompt_version = Column(String(100))
    embedding_model = Column(String(100))
    attested_by = Column(String(255))
    attested_at = Column(DateTime(timezone=True))
    reverted_by = Column(String(255))
    reverted_at = Column(DateTime(timezone=True))
    revert_reason = Column(Text)
    rationale = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("obligation_id", "control_objective_id", name="uq_ob_obj_mapping"),
    )


class ControlObjectiveActivityMapping(Base):
    """Linkage 3: Control Objective <---> Control Activity (OPERATIONALIZED_BY)"""
    __tablename__ = "control_objective_activity_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    control_objective_id = Column(UUID(as_uuid=True), ForeignKey("control_objectives.id"), nullable=False, index=True)
    control_activity_id = Column(UUID(as_uuid=True), ForeignKey("control_activities.id"), nullable=False, index=True)

    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    condition_clause = Column(Text)
    condition_confidence = Column(String(10), default="0.00")
    confidence_score = Column(String(10), default="0.00")
    logic_judge_score = Column(String(10), default="0.00")
    technical_judge_score = Column(String(10), default="0.00")
    status = Column(SQLEnum(MappingStatus), default=MappingStatus.PROBABILISTIC_AI, nullable=False)
    is_golden_assertion = Column(String(10), default="FALSE", index=True)
    model_version = Column(String(100))
    prompt_version = Column(String(100))
    embedding_model = Column(String(100))
    attested_by = Column(String(255))
    attested_at = Column(DateTime(timezone=True))
    reverted_by = Column(String(255))
    reverted_at = Column(DateTime(timezone=True))
    revert_reason = Column(Text)
    rationale = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("control_objective_id", "control_activity_id", name="uq_obj_act_mapping"),
    )


class ControlObjectiveFrameworkMapping(Base):
    """Linkage 4: Control Objective <---> Framework Control Objective (CROSSWALKS_TO_OBJ)"""
    __tablename__ = "control_objective_framework_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    control_objective_id = Column(UUID(as_uuid=True), ForeignKey("control_objectives.id"), nullable=False, index=True)
    framework_objective_id = Column(UUID(as_uuid=True), ForeignKey("framework_control_objectives.id"), nullable=False, index=True)

    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    condition_clause = Column(Text)
    condition_confidence = Column(String(10), default="0.00")
    confidence_score = Column(String(10), default="0.00")
    logic_judge_score = Column(String(10), default="0.00")
    technical_judge_score = Column(String(10), default="0.00")
    status = Column(SQLEnum(MappingStatus), default=MappingStatus.PROBABILISTIC_AI, nullable=False)
    is_golden_assertion = Column(String(10), default="FALSE", index=True)
    model_version = Column(String(100))
    prompt_version = Column(String(100))
    embedding_model = Column(String(100))
    attested_by = Column(String(255))
    attested_at = Column(DateTime(timezone=True))
    reverted_by = Column(String(255))
    reverted_at = Column(DateTime(timezone=True))
    revert_reason = Column(Text)
    rationale = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("control_objective_id", "framework_objective_id", name="uq_obj_fw_mapping"),
    )


class ControlActivityFrameworkMapping(Base):
    """Linkage 5: Control Activity <---> Framework Control Activity (CROSSWALKS_TO_ACT)"""
    __tablename__ = "control_activity_framework_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    control_activity_id = Column(UUID(as_uuid=True), ForeignKey("control_activities.id"), nullable=False, index=True)
    framework_activity_id = Column(UUID(as_uuid=True), ForeignKey("framework_control_activities.id"), nullable=False, index=True)

    set_theory_relation = Column(SQLEnum(SetTheoryRelation), nullable=False)
    condition_clause = Column(Text)
    condition_confidence = Column(String(10), default="0.00")
    confidence_score = Column(String(10), default="0.00")
    logic_judge_score = Column(String(10), default="0.00")
    technical_judge_score = Column(String(10), default="0.00")
    status = Column(SQLEnum(MappingStatus), default=MappingStatus.PROBABILISTIC_AI, nullable=False)
    is_golden_assertion = Column(String(10), default="FALSE", index=True)
    model_version = Column(String(100))
    prompt_version = Column(String(100))
    embedding_model = Column(String(100))
    attested_by = Column(String(255))
    attested_at = Column(DateTime(timezone=True))
    reverted_by = Column(String(255))
    reverted_at = Column(DateTime(timezone=True))
    revert_reason = Column(Text)
    rationale = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


from sqlalchemy import JSON


class GraphOutboxLog(Base):
    """Transactional Outbox table for synchronous PostgreSQL / Memgraph dual-write atomicity."""
    __tablename__ = "graph_outbox_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    primitive = Column(String(50), nullable=False)
    payload = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, PROCESSED, FAILED
    retry_count = Column(String(10), default="0")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))




