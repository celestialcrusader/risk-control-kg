# INFRA-9: Memgraph Schema Initialization

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: infrastructure, graph, memgraph

---

## User Story

> As a **backend developer**, I want Memgraph to have its schema (node labels, indexes, constraints, SHACL shapes) pre-initialized, so that graph writes in subsequent sprints have a defined structure to validate against.

---

## Context and Background

The CTO review identified that no story defined who creates the graph schema between starting Memgraph (INFRA-1) and writing nodes (CROSSWALK-4). This story fills that gap.

Memgraph requires node labels, indexes, unique constraints, and SHACL shapes to be defined before data can be written with confidence. Without this schema initialization, subsequent ingestion and crosswalk stories have no structural guarantees.

---

## Acceptance Criteria

1. Given Memgraph is running, when the schema initialization script executes, then all node labels are created: `Obligation`, `Control`, `Regulation`, `Gap`, `Risk`, `Evidence`, `ThirdParty`, `ControlEffectiveness`
2. Given the schema is applied, when indexes are verified, then indexes exist on key properties: `obligation_id`, `control_id`, `framework_id`, `document_id`
3. Given the schema is applied, when constraints are verified, then unique constraints exist on primary keys
4. SHACL shapes are loaded from `/backend/app/shapes/` into Memgraph's SHACL extension
5. Schema version is tracked in `memgraph_schema_versions` system table
6. Schema initialization is idempotent (can be run multiple times without error)

---

## Definition of Done

- [ ] Cypher schema initialization script in `/backend/app/graph/init_schema.cypher`
- [ ] SHACL shapes loaded into Memgraph
- [ ] Schema health check endpoint `/api/v1/graph/health`
- [ ] Documentation in `docs/01-initial/graph-schema.md`
- [ ] All acceptance criteria verified
- [ ] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- **Blocked by**: INFRA-1 (Memgraph must be running), INFRA-2 (PostgreSQL schema)
- **Blocks**: CROSSWALK-4, INGEST-5

---

## Technical Notes

### Node Labels (8 total)

| Label | Key Properties | Purpose |
|---|---|---|
| `Obligation` | `obligation_id`, `framework_id` | Core compliance obligations |
| `Control` | `control_id`, `framework_id` | Specific controls |
| `Regulation` | `document_id` | Source regulatory documents |
| `Gap` | `gap_id` | Identified compliance gaps |
| `Risk` | `risk_id` | Associated risks |
| `Evidence` | `evidence_id` | Compliance evidence artifacts |
| `ThirdParty` | `third_party_id` | Third-party entities |
| `ControlEffectiveness` | `effectiveness_id` | Control assessment results |

### Example Cypher

```cypher
-- Create labels and unique constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (o:Obligation) REQUIRE o.obligation_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Control) REQUIRE c.control_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (r:Regulation) REQUIRE r.document_id IS UNIQUE;

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS FOR (o:Obligation) ON (o.framework_id);
CREATE INDEX IF NOT EXISTS FOR (c:Control) ON (c.framework_id);
```

### SHACL Extension

- Use Memgraph's SHACL extension: `CALL shacl.load_shapes_from_file('/path/to/shapes.ttl')`
- Shape files in `/backend/app/shapes/` as `.ttl` files

### Schema Migrations

- Store schema metadata in PostgreSQL `schema_migrations` table (already defined in INFRA-2)
- Track version and application timestamp

### Health Check

- Endpoint: `GET /api/v1/graph/health`
- Returns: labels count, indexes count, schema version, SHACL loaded status
