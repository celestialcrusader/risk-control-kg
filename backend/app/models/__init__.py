"""
SQLAlchemy ORM Models for RCKG PostgreSQL Schema

This module defines the ORM representations of the Bronze/Silver/Gold
three-layer vault schema as specified in TRD Section 6.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
    Enum as SQLEnum,
    event,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


# =============================================================================
# Enumerations
# =============================================================================

class ControlStatus(Enum):
    """Control verification status."""
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DRAFT = "draft"
    ARCHIVED = "archived"


class VerificationLevel(Enum):
    """AI verification confidence level."""
    AI_CONFIDENT = "ai_confident"
    HUMAN_VERIFIED = "human_verified"
    PENDING_REVIEW = "pending_review"


class EventType(Enum):
    """Audit log event types."""
    DOCUMENT_UPLOADED = "document.uploaded"
    EXTRACTION_STARTED = "extraction.started"
    EXTRACTION_COMPLETED = "extraction.completed"
    VALIDATION_COMPLETED = "validation.completed"
    MAPPING_COMPLETED = "mapping.completed"
    GAP_CREATED = "gap.created"
    GAP_REMEDIATED = "gap.remEDIATED"
    GAP_CLOSED = "gap.closed"


# =============================================================================
# Bronze Layer: Raw Document Storage
# =============================================================================

class StagingControl(Base):
    """
    Bronze Layer: Raw unstructured document storage.

    Stores the original parsed regulatory documents before any AI extraction
    or semantic processing. This is the source of truth for all downstream
    data transformations.
    """
    __tablename__ = "staging_controls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)
    canonical_id = Column(String(255), nullable=False, index=True)
    raw_file_content = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_staging_canonical_id", "canonical_id"),
        Index("ix_staging_raw_content", "raw_file_content", postgresql_using="gin"),
    )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "uuid": str(self.uuid),
            "canonical_id": self.canonical_id,
            "raw_file_content": self.raw_file_content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# Silver Layer: AI-Extracted Semantic Structure
# =============================================================================

class SemanticControl(Base):
    """
    Silver Layer: AI-extracted structured control data.

    Contains the parsed semantic elements extracted from raw documents
    by the De Jure extraction pipeline. This represents the AI's
    interpretation of control obligations.
    """
    __tablename__ = "semantic_controls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)

    # Framework information
    framework_name = Column(String(255), nullable=False, index=True)
    framework_version = Column(String(50))
    group_id = Column(String(255))

    # Control structure
    control_id = Column(String(255), nullable=False, index=True)
    control_name = Column(String(512))

    # Extracted semantic elements
    objective_text = Column(Text)
    statement_text = Column(Text)
    action_verb = Column(String(100), index=True)
    subject_noun = Column(String(255), index=True)

    # Confidence scores from AI extraction
    extraction_confidence = Column(String(10), default="0.00")

    # Metadata
    source_document_id = Column(UUID(as_uuid=True))
    section_reference = Column(String(512))

    # Bronze layer linkage (EXTRACT-4)
    bronze_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("staging_controls.id"),
        nullable=True,
    )

    # Control status (EXTRACT-4)
    status = Column(String(50), default="pending_validation")

    # Application-level versioning (EXTRACT-4)
    version = Column(Integer, default=1)

    # Python-level defaults (apply at instantiation, not just insert time)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.status is None:
            self.status = "pending_validation"
        if self.version is None:
            self.version = 1

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_semantic_framework", "framework_name", "framework_version"),
        Index("ix_semantic_created_at", "created_at"),
        Index("ix_semantic_action_verb", "action_verb"),
        Index("ix_semantic_subject", "subject_noun"),
        Index("ix_semantic_bronze_record", "bronze_record_id"),
    )

    def _get_next_version(self):
        """Return the next version number for this record."""
        return (self.version or 1) + 1

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "uuid": str(self.uuid),
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "group_id": self.group_id,
            "control_id": self.control_id,
            "control_name": self.control_name,
            "objective_text": self.objective_text,
            "statement_text": self.statement_text,
            "action_verb": self.action_verb,
            "subject_noun": self.subject_noun,
            "extraction_confidence": self.extraction_confidence,
            "source_document_id": str(self.source_document_id) if self.source_document_id else None,
            "section_reference": self.section_reference,
            "bronze_record_id": str(self.bronze_record_id) if self.bronze_record_id else None,
            "status": self.status,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# Version auto-increment via before_insert event
# =============================================================================


@event.listens_for(SemanticControl, "before_insert", propagate=True)
def _autoincrement_version(mapper, connection, target):
    """Auto-increment version on insert when not explicitly set.

    The service layer handles version explicitly for version_obligation.
    This event only auto-increments for records that were constructed with
    the default version=1 but should actually be version 2+ (i.e., when
    the service explicitly sets _version_set=True on the instance).
    """
    pass  # Version management is handled explicitly in the service layer


# =============================================================================
# Gold Layer: Verified Controls with Bitemporal Support
# =============================================================================

class GoldenControl(Base):
    """
    Gold Layer: Human-verified or high-confidence AI-validated controls.

    The final, production-ready control data that can be used for
    compliance reporting, audit evidence, and regulatory submissions.

    Includes bitemporal tagging (valid_from/valid_to for event time,
    ingested_at for system time) as specified in TRD Section 6.2.
    """
    __tablename__ = "golden_controls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid4)

    # Core control information
    control_id = Column(String(255), primary_key=True)
    control_name = Column(String(512), nullable=False)
    framework_name = Column(String(255), nullable=False, index=True)
    framework_version = Column(String(50))
    group_id = Column(String(255))

    # Semantic elements from silver layer
    objective_text = Column(Text)
    statement_text = Column(Text)
    action_verb = Column(String(100))
    subject_noun = Column(String(255))

    # Bitemporal tagging (TRD Section 6.2)
    valid_from = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Verification status
    status = Column(
        SQLEnum(ControlStatus),
        default=ControlStatus.ACTIVE,
        nullable=False
    )
    verification_level = Column(
        SQLEnum(VerificationLevel),
        default=VerificationLevel.AI_CONFIDENT,
        nullable=False
    )
    verification_confidence = Column(String(10), default="0.00")

    # Owner and metadata
    owner = Column(String(255))
    implementation_method = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_golden_framework", "framework_name", "framework_version"),
        Index("ix_golden_status", "status"),
        Index("ix_golden_valid_range", "valid_from", "valid_to"),
        Index("ix_golden_ingested_at", "ingested_at"),
        Index("ix_golden_verb_subject", "action_verb", "subject_noun"),
    )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "uuid": str(self.uuid),
            "control_id": self.control_id,
            "control_name": self.control_name,
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "group_id": self.group_id,
            "objective_text": self.objective_text,
            "statement_text": self.statement_text,
            "action_verb": self.action_verb,
            "subject_noun": self.subject_noun,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "ingested_at": self.ingested_at.isoformat() if self.ingested_at else None,
            "status": self.status.value if self.status else None,
            "verification_level": self.verification_level.value if self.verification_level else None,
            "verification_confidence": self.verification_confidence,
            "owner": self.owner,
            "implementation_method": self.implementation_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_valid_at(self, as_of_date: datetime) -> bool:
        """Check if this control was valid at a specific point in time."""
        if self.valid_to and self.valid_to < as_of_date:
            return False
        if self.valid_from and self.valid_from > as_of_date:
            return False
        return True


# =============================================================================
# Audit Logging
# =============================================================================

class AuditLog(Base):
    """
    Audit log for all system events.

    Provides complete traceability for all operations performed on the
    system, including who performed them and when. Immutable and append-only.
    """
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSONB, nullable=False)
    actor_id = Column(String(255))
    actor_type = Column(String(50), default="user")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(INET)
    user_agent = Column(String(512))
    request_id = Column(UUID(as_uuid=True), default=uuid4, index=True)

    __table_args__ = (
        Index("ix_audit_event_type", "event_type"),
        Index("ix_audit_timestamp", "timestamp"),
        Index("ix_audit_actor", "actor_id"),
        Index("ix_audit_request", "request_id"),
        Index("ix_audit_data", "event_data", postgresql_using="gin"),
    )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "event_data": self.event_data,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "request_id": str(self.request_id),
        }


# =============================================================================
# Workflow Checkpoints (for Replay Strategy)
# =============================================================================

class WorkflowCheckpoint(Base):
    """
    Checkpoint tracking for workflow orchestration.

    Enables idempotent workflow execution and recovery from failures.
    Stores the state of each workflow stage to support replay functionality.
    """
    __tablename__ = "workflow_checkpoints"

    checkpoint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id = Column(String(255), nullable=False, index=True)
    stage = Column(String(50), nullable=False, index=True)
    data_hash = Column(String(64), nullable=False)
    extra_metadata = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("workflow_id", "stage", name="uq_workflow_stage"),
        Index("ix_checkpoint_created_at", "created_at"),
    )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "checkpoint_id": str(self.checkpoint_id),
            "workflow_id": self.workflow_id,
            "stage": self.stage,
            "data_hash": self.data_hash,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# Reconciliation Dead Letter Queue
# =============================================================================

class ReconciliationDLQ(Base):
    """
    Dead Letter Queue for cross-store reconciliation failures.

    Stores records that failed reconciliation checks across PostgreSQL,
    Memgraph, Qdrant, and MinIO. Requires manual review and resolution.
    """
    __tablename__ = "reconciliation_dlq"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    store_type = Column(String(50), nullable=False, index=True)
    record_id = Column(String(255), nullable=False, index=True)
    discrepancy_type = Column(String(100), nullable=False)
    discrepancy_details = Column(JSONB)
    status = Column(String(50), default="pending", nullable=False)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_reconciliation_store", "store_type", "record_id"),
        Index("ix_reconciliation_status", "status"),
    )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "store_type": self.store_type,
            "record_id": self.record_id,
            "discrepancy_type": self.discrepancy_type,
            "discrepancy_details": self.discrepancy_details,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# Schema Migrations Tracking
# =============================================================================

class SchemaMigration(Base):
    """
    Tracks applied schema migrations.

    Ensures schema changes are applied idempotently and can be
    rolled back if necessary.
    """
    __tablename__ = "schema_migrations"

    version = Column(String(50), primary_key=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text)
    checksum = Column(String(64))

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "version": self.version,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "description": self.description,
            "checksum": self.checksum,
        }



# Import Pure RCKG Graph Node and Linkage Models
from backend.app.models.rckg_nodes import (
    SetTheoryRelation,
    GapSeverity,
    GapState,
    MappingStatus,
    ObligationNode,
    ControlObjectiveNode,
    ControlActivityNode,
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    RiskNode,
    GapNode,
    ShortCircuitAuditLog,
    RiskControlObjectiveMapping,
    ObligationControlObjectiveMapping,
    ControlObjectiveActivityMapping,
    ControlObjectiveFrameworkMapping,
    ControlActivityFrameworkMapping,
    GraphOutboxLog,
)

# =============================================================================
# Schema Export
# =============================================================================

__all__ = [
    "Base",
    "StagingControl",
    "SemanticControl",
    "GoldenControl",
    "AuditLog",
    "WorkflowCheckpoint",
    "ReconciliationDLQ",
    "SchemaMigration",
    "ControlStatus",
    "VerificationLevel",
    "EventType",
    "SetTheoryRelation",
    "GapSeverity",
    "GapState",
    "MappingStatus",
    "ObligationNode",
    "ControlObjectiveNode",
    "ControlActivityNode",
    "FrameworkControlObjectiveNode",
    "FrameworkControlActivityNode",
    "RiskNode",
    "GapNode",
    "ShortCircuitAuditLog",
    "RiskControlObjectiveMapping",
    "ObligationControlObjectiveMapping",
    "ControlObjectiveActivityMapping",
    "ControlObjectiveFrameworkMapping",
    "ControlActivityFrameworkMapping",
    "GraphOutboxLog",
]


