-- RCKG PostgreSQL Schema Initialization
-- This script creates the Bronze/Silver/Gold three-layer vault schema
-- Run automatically on first container startup

-- ============================================
-- Enable UUID extension
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- Bronze Layer: Staging Controls (raw unstructured text)
-- ============================================
CREATE TABLE IF NOT EXISTS staging_controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),
    canonical_id VARCHAR(255) NOT NULL,
    raw_file_content JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Bronze layer
CREATE INDEX IF NOT EXISTS idx_staging_canonical_id ON staging_controls(canonical_id);
CREATE INDEX IF NOT EXISTS idx_staging_created_at ON staging_controls(created_at);
CREATE INDEX IF NOT EXISTS idx_staging_raw_content ON staging_controls USING GIN(raw_file_content);

-- ============================================
-- Silver Layer: Semantic Controls (AI-extracted structure)
-- ============================================
CREATE TABLE IF NOT EXISTS semantic_controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),

    -- Framework information
    framework_name VARCHAR(255) NOT NULL,
    framework_version VARCHAR(50),
    group_id VARCHAR(255),

    -- Control structure
    control_id VARCHAR(255) NOT NULL,
    control_name VARCHAR(512),

    -- Extracted semantic elements
    objective_text TEXT,
    statement_text TEXT,
    action_verb VARCHAR(100),
    subject_noun VARCHAR(255),

    -- Confidence scores from AI extraction
    extraction_confidence DECIMAL(3,2),

    -- Metadata
    source_document_id UUID,
    section_reference VARCHAR(512),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Silver layer
CREATE UNIQUE INDEX IF NOT EXISTS idx_semantic_control_id ON semantic_controls(control_id);
CREATE INDEX IF NOT EXISTS idx_semantic_framework ON semantic_controls(framework_name, framework_version);
CREATE INDEX IF NOT EXISTS idx_semantic_created_at ON semantic_controls(created_at);
CREATE INDEX IF NOT EXISTS idx_semantic_action_verb ON semantic_controls(action_verb);
CREATE INDEX IF NOT EXISTS idx_semantic_subject ON semantic_controls(subject_noun);

-- ============================================
-- Gold Layer: Golden Controls (human-verified or high-confidence AI)
-- ============================================
CREATE TABLE IF NOT EXISTS golden_controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uuid UUID UNIQUE DEFAULT uuid_generate_v4(),

    -- Core control information
    control_id VARCHAR(255) PRIMARY KEY,
    control_name VARCHAR(512) NOT NULL,
    framework_name VARCHAR(255) NOT NULL,
    framework_version VARCHAR(50),
    group_id VARCHAR(255),

    -- Semantic elements from silver layer
    objective_text TEXT,
    statement_text TEXT,
    action_verb VARCHAR(100),
    subject_noun VARCHAR(255),

    -- Bitemporal tagging (TRD Section 6.2)
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),

    -- Verification status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'superseded', 'draft', 'archived')),
    verification_level VARCHAR(50) DEFAULT 'ai_confident' CHECK (verification_level IN ('ai_confident', 'human_verified', 'pending_review')),
    verification_confidence DECIMAL(3,2),

    -- Owner and metadata
    owner VARCHAR(255),
    implementation_method VARCHAR(255),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Gold layer
CREATE INDEX IF NOT EXISTS idx_golden_framework ON golden_controls(framework_name, framework_version);
CREATE INDEX IF NOT EXISTS idx_golden_status ON golden_controls(status);
CREATE INDEX IF NOT EXISTS idx_golden_valid_range ON golden_controls(valid_from, valid_to);
CREATE INDEX IF NOT EXISTS idx_golden_ingested_at ON golden_controls(ingested_at);
CREATE INDEX IF NOT EXISTS idx_golden_verb_subject ON golden_controls(action_verb, subject_noun);

-- ============================================
-- Audit Log Table
-- ============================================
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    actor_id VARCHAR(255),
    actor_type VARCHAR(50) DEFAULT 'user',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    request_id UUID DEFAULT gen_random_uuid()
);

-- Indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_log(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_request ON audit_log(request_id);
CREATE INDEX IF NOT EXISTS idx_audit_data ON audit_log USING GIN(event_data);

-- ============================================
-- Workflow Checkpoints Table (for replay strategy)
-- ============================================
CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    checkpoint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id VARCHAR(255) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    data_hash VARCHAR(64) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workflow_id, stage)
);

-- Indexes for workflow checkpoints
CREATE INDEX IF NOT EXISTS idx_checkpoint_workflow ON workflow_checkpoints(workflow_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_stage ON workflow_checkpoints(stage);

-- ============================================
-- Reconciliation DLQ (Dead Letter Queue)
-- ============================================
CREATE TABLE IF NOT EXISTS reconciliation_dlq (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_type VARCHAR(50) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    discrepancy_type VARCHAR(100) NOT NULL,
    discrepancy_details JSONB,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'resolved', 'archived')),
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for reconciliation DLQ
CREATE INDEX IF NOT EXISTS idx_reconciliation_store ON reconciliation_dlq(store_type, record_id);
CREATE INDEX IF NOT EXISTS idx_reconciliation_status ON reconciliation_dlq(status);

-- ============================================
-- Schema Migrations Tracking
-- ============================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT,
    checksum VARCHAR(64)
);

-- Insert initial schema version
INSERT INTO schema_migrations (version, description)
VALUES ('1.0.0', 'Initial Bronze/Silver/Gold schema with bitemporal support')
ON CONFLICT (version) DO NOTHING;

-- ============================================
-- Function: Update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_staging_controls_updated_at BEFORE UPDATE ON staging_controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_semantic_controls_updated_at BEFORE UPDATE ON semantic_controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_golden_controls_updated_at BEFORE UPDATE ON golden_controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_log_updated_at BEFORE UPDATE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_checkpoints_updated_at BEFORE UPDATE ON workflow_checkpoints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reconciliation_dlq_updated_at BEFORE UPDATE ON reconciliation_dlq
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Create rckg user with appropriate permissions
-- ============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rckg') THEN
        CREATE ROLE rckg LOGIN PASSWORD 'rckg_secret_password';
    END IF;
END
$$;

-- ============================================
-- Grant permissions (after role exists)
-- ============================================
GRANT ALL PRIVILEGES ON DATABASE rckg_db TO rckg;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rckg;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rckg;
