-- =============================================================================
-- RCKG Graph Schema Initialization
-- Version: 1.0.0
-- =============================================================================
-- This script creates all node labels, unique constraints, and indexes
-- for the RCKG compliance graph database. It is idempotent: safe to run
-- multiple times without error.
--
-- SHACL shapes are loaded separately via the Python init_schema() module
-- in app.graph.schema._load_shacl_shapes().
-- =============================================================================

-- ── Unique Constraints on Primary Keys ─────────────────────────────────────

CREATE CONSTRAINT IF NOT EXISTS obligation_id_unique
    FOR (o:Obligation) REQUIRE o.obligation_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS control_id_unique
    FOR (c:Control) REQUIRE c.control_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS regulation_document_id_unique
    FOR (r:Regulation) REQUIRE r.document_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS gap_id_unique
    FOR (g:Gap) REQUIRE g.gap_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS risk_id_unique
    FOR (r:Risk) REQUIRE r.risk_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS evidence_id_unique
    FOR (e:Evidence) REQUIRE e.evidence_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS third_party_id_unique
    FOR (t:ThirdParty) REQUIRE t.third_party_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS effectiveness_id_unique
    FOR (ce:ControlEffectiveness) REQUIRE ce.effectiveness_id IS UNIQUE;

-- ── Indexes on Key Query Properties ────────────────────────────────────────
-- Note: unique constraints already index the constrained property, so
-- only framework_id indexes are needed here (not covered by constraints).

CREATE INDEX IF NOT EXISTS obligation_framework_index
    FOR (o:Obligation) ON (o.framework_id);

CREATE INDEX IF NOT EXISTS control_framework_index
    FOR (c:Control) ON (c.framework_id);

-- ── Schema Version Tracking ───────────────────────────────────────────────

MERGE (v:MemgraphSchemaVersion {version: "INFRA-9"})
SET v.last_applied = timestamp(), v.description = "Initial graph schema: 8 labels, unique constraints, indexes, SHACL shapes";
