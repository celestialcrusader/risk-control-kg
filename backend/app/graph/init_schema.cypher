-- =============================================================================
-- Pure RCKG Graph Schema Initialization
-- Version: 2.0.0
-- =============================================================================
-- This script creates all node labels, unique constraints, and indexes
-- for the pure Risk and Control Knowledge Graph (RCKG) database.
--
-- Supports 6 core Node Types:
--   - Obligation (:Obligation)
--   - Control Objective (:ControlObjective)
--   - Control Activity (:ControlActivity)
--   - Framework Control Objective (:FrameworkControlObj)
--   - Framework Control Activity (:FrameworkControlAct)
--   - Risk (:Risk)
--   - Gap (:Gap)
--
-- Idempotent: safe to run multiple times without error.
-- =============================================================================

-- ── Unique Constraints on Primary Keys ─────────────────────────────────────

CREATE CONSTRAINT IF NOT EXISTS obligation_id_unique
    FOR (o:Obligation) REQUIRE o.obligation_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS control_objective_id_unique
    FOR (co:ControlObjective) REQUIRE co.objective_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS control_activity_id_unique
    FOR (ca:ControlActivity) REQUIRE ca.activity_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS framework_obj_id_unique
    FOR (fco:FrameworkControlObj) REQUIRE fco.framework_obj_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS framework_act_id_unique
    FOR (fca:FrameworkControlAct) REQUIRE fca.framework_act_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS risk_id_unique
    FOR (r:Risk) REQUIRE r.risk_id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS gap_id_unique
    FOR (g:Gap) REQUIRE g.gap_id IS UNIQUE;

-- ── Indexes on Key Query Properties ────────────────────────────────────────

CREATE INDEX IF NOT EXISTS obligation_framework_index
    FOR (o:Obligation) ON (o.framework_name);

CREATE INDEX IF NOT EXISTS control_objective_policy_index
    FOR (co:ControlObjective) ON (co.policy_name);

CREATE INDEX IF NOT EXISTS control_activity_sop_index
    FOR (ca:ControlActivity) ON (ca.sop_name);

CREATE INDEX IF NOT EXISTS framework_obj_name_index
    FOR (fco:FrameworkControlObj) ON (fco.framework_name);

CREATE INDEX IF NOT EXISTS framework_act_name_index
    FOR (fca:FrameworkControlAct) ON (fca.framework_name);

CREATE INDEX IF NOT EXISTS risk_category_index
    FOR (r:Risk) ON (r.category);

-- ── Schema Version Tracking ───────────────────────────────────────────────

MERGE (v:MemgraphSchemaVersion {version: "PURE-RCKG-2.0"})
SET v.last_applied = timestamp(), v.description = "Pure RCKG 6-node 5-linkage graph schema with set-theory attributes";
