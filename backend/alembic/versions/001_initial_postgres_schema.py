"""Initial PostgreSQL schema with Bronze/Silver/Gold layers

Revision ID: 001_initial
Revises:
Create Date: 2026-04-15

This migration creates the complete three-layer vault schema as specified
in TRD Section 6, including:

- Bronze layer (staging_controls): Raw document storage
- Silver layer (semantic_controls): AI-extracted structured data
- Gold layer (golden_controls): Verified controls with bitemporal support
- Audit logging and workflow checkpoint tables
- Schema for reconciliation dead letter queue

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create all tables and indexes for the RCKG schema.
    This migration is idempotent - running it multiple times will succeed.
    """

    # ==========================================
    # Bronze Layer: Staging Controls
    # ==========================================
    op.create_table(
        "staging_controls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("canonical_id", sa.String(255), nullable=False),
        sa.Column("raw_file_content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
        sa.UniqueConstraint("canonical_id"),
    )

    op.create_index("ix_staging_canonical_id", "staging_controls", ["canonical_id"])
    op.create_index("ix_staging_created_at", "staging_controls", ["created_at"])
    op.create_index("ix_staging_raw_content", "staging_controls", ["raw_file_content"], postgresql_using="gin")

    # ==========================================
    # Silver Layer: Semantic Controls
    # ==========================================
    op.create_table(
        "semantic_controls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("framework_name", sa.String(255), nullable=False),
        sa.Column("framework_version", sa.String(50), nullable=True),
        sa.Column("group_id", sa.String(255), nullable=True),
        sa.Column("control_id", sa.String(255), nullable=False),
        sa.Column("control_name", sa.String(512), nullable=True),
        sa.Column("objective_text", sa.Text(), nullable=True),
        sa.Column("statement_text", sa.Text(), nullable=True),
        sa.Column("action_verb", sa.String(100), nullable=True),
        sa.Column("subject_noun", sa.String(255), nullable=True),
        sa.Column("extraction_confidence", sa.String(10), nullable=True),
        sa.Column("source_document_id", sa.UUID(), nullable=True),
        sa.Column("section_reference", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
        sa.UniqueConstraint("control_id"),
    )

    op.create_index("ix_semantic_control_id", "semantic_controls", ["control_id"])
    op.create_index("ix_semantic_framework", "semantic_controls", ["framework_name", "framework_version"])
    op.create_index("ix_semantic_created_at", "semantic_controls", ["created_at"])
    op.create_index("ix_semantic_action_verb", "semantic_controls", ["action_verb"])
    op.create_index("ix_semantic_subject", "semantic_controls", ["subject_noun"])

    # ==========================================
    # Gold Layer: Golden Controls with Bitemporal Support
    # ==========================================
    op.create_table(
        "golden_controls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("control_id", sa.String(255), nullable=False),
        sa.Column("control_name", sa.String(512), nullable=False),
        sa.Column("framework_name", sa.String(255), nullable=False),
        sa.Column("framework_version", sa.String(50), nullable=True),
        sa.Column("group_id", sa.String(255), nullable=True),
        sa.Column("objective_text", sa.Text(), nullable=True),
        sa.Column("statement_text", sa.Text(), nullable=True),
        sa.Column("action_verb", sa.String(100), nullable=True),
        sa.Column("subject_noun", sa.String(255), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("verification_level", sa.String(50), nullable=False, server_default="ai_confident"),
        sa.Column("verification_confidence", sa.String(10), nullable=True),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("implementation_method", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id", "control_id"),
        sa.UniqueConstraint("uuid"),
        sa.CheckConstraint("status IN ('active', 'superseded', 'draft', 'archived')", name="chk_golden_status"),
        sa.CheckConstraint("verification_level IN ('ai_confident', 'human_verified', 'pending_review')", name="chk_golden_verification_level"),
    )

    op.create_index("ix_golden_framework", "golden_controls", ["framework_name", "framework_version"])
    op.create_index("ix_golden_status", "golden_controls", ["status"])
    op.create_index("ix_golden_valid_range", "golden_controls", ["valid_from", "valid_to"])
    op.create_index("ix_golden_ingested_at", "golden_controls", ["ingested_at"])
    op.create_index("ix_golden_verb_subject", "golden_controls", ["action_verb", "subject_noun"])

    # ==========================================
    # Audit Log Table
    # ==========================================
    op.create_table(
        "audit_log",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("actor_id", sa.String(255), nullable=True),
        sa.Column("actor_type", sa.String(50), nullable=True, server_default="user"),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("ip_address", sa.Inet(), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_audit_event_type", "audit_log", ["event_type"])
    op.create_index("ix_audit_timestamp", "audit_log", ["timestamp"])
    op.create_index("ix_audit_actor", "audit_log", ["actor_id"])
    op.create_index("ix_audit_request", "audit_log", ["request_id"])
    op.create_index("ix_audit_data", "audit_log", ["event_data"], postgresql_using="gin")

    # ==========================================
    # Workflow Checkpoints Table
    # ==========================================
    op.create_table(
        "workflow_checkpoints",
        sa.Column("checkpoint_id", sa.UUID(), nullable=False),
        sa.Column("workflow_id", sa.String(255), nullable=False),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("data_hash", sa.String(64), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("checkpoint_id"),
        sa.UniqueConstraint("workflow_id", "stage", name="uq_workflow_stage"),
    )

    op.create_index("ix_checkpoint_workflow", "workflow_checkpoints", ["workflow_id"])
    op.create_index("ix_checkpoint_stage", "workflow_checkpoints", ["stage"])

    # ==========================================
    # Reconciliation DLQ Table
    # ==========================================
    op.create_table(
        "reconciliation_dlq",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("store_type", sa.String(50), nullable=False),
        sa.Column("record_id", sa.String(255), nullable=False),
        sa.Column("discrepancy_type", sa.String(100), nullable=False),
        sa.Column("discrepancy_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('pending', 'acknowledged', 'resolved', 'archived')", name="chk_recon_status"),
    )

    op.create_index("ix_reconciliation_store", "reconciliation_dlq", ["store_type", "record_id"])
    op.create_index("ix_reconciliation_status", "reconciliation_dlq", ["status"])

    # ==========================================
    # Schema Migrations Tracking Table
    # ==========================================
    op.create_table(
        "schema_migrations",
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("version"),
    )

    # ==========================================
    # Insert initial schema version
    # ==========================================
    op.execute(
        """
        INSERT INTO schema_migrations (version, description)
        VALUES ('001_initial', 'Initial Bronze/Silver/Gold schema with bitemporal support')
        ON CONFLICT (version) DO NOTHING
        """
    )

    # ==========================================
    # Create update trigger function
    # ==========================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """)

    # Apply triggers to tables with updated_at
    for table_name in ["staging_controls", "semantic_controls", "golden_controls", "audit_log", "workflow_checkpoints", "reconciliation_dlq"]:
        op.execute(f"""
            CREATE TRIGGER update_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)


def downgrade() -> None:
    """
    Drop all tables and related objects.
    This is the inverse of the upgrade function.
    """

    # Drop triggers and function
    op.execute("DROP TRIGGER IF EXISTS update_reconciliation_dlq_updated_at ON reconciliation_dlq")
    op.execute("DROP TRIGGER IF EXISTS update_workflow_checkpoints_updated_at ON workflow_checkpoints")
    op.execute("DROP TRIGGER IF EXISTS update_audit_log_updated_at ON audit_log")
    op.execute("DROP TRIGGER IF EXISTS update_golden_controls_updated_at ON golden_controls")
    op.execute("DROP TRIGGER IF EXISTS update_semantic_controls_updated_at ON semantic_controls")
    op.execute("DROP TRIGGER IF EXISTS update_staging_controls_updated_at ON staging_controls")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables in reverse order (dependencies first)
    op.drop_table("schema_migrations")
    op.drop_table("reconciliation_dlq")
    op.drop_table("workflow_checkpoints")
    op.drop_table("audit_log")
    op.drop_table("golden_controls")
    op.drop_table("semantic_controls")
    op.drop_table("staging_controls")
