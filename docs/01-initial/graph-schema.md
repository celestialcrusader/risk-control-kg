# Graph Schema — RCKG

**Story**: INFRA-9 (Memgraph Schema Initialization)

## Overview

This document describes the Memgraph graph schema for the RCKG compliance platform. The schema is initialized via the Python module `app.graph.schema` which executes a Cypher script and loads SHACL shape definitions.

## Node Labels (8)

| Label | Key Property | Purpose |
|---|---|---|
| `Obligation` | `obligation_id` | Core compliance obligations |
| `Control` | `control_id` | Specific controls |
| `Regulation` | `document_id` | Source regulatory documents |
| `Gap` | `gap_id` | Identified compliance gaps |
| `Risk` | `risk_id` | Associated risks |
| `Evidence` | `evidence_id` | Compliance evidence artifacts |
| `ThirdParty` | `third_party_id` | Third-party entities |
| `ControlEffectiveness` | `effectiveness_id` | Control assessment results |

## Unique Constraints

Each label has a unique constraint on its primary key property:

| Label | Constraint Name | Property |
|---|---|---|
| `Obligation` | `obligation_id_unique` | `obligation_id` |
| `Control` | `control_id_unique` | `control_id` |
| `Regulation` | `regulation_document_id_unique` | `document_id` |
| `Gap` | `gap_id_unique` | `gap_id` |
| `Risk` | `risk_id_unique` | `risk_id` |
| `Evidence` | `evidence_id_unique` | `evidence_id` |
| `ThirdParty` | `third_party_id_unique` | `third_party_id` |
| `ControlEffectiveness` | `effectiveness_id_unique` | `effectiveness_id` |

## Indexes

Secondary indexes are created on `framework_id` for query performance. Unique constraint properties are automatically indexed by Memgraph and do not need separate indexes.

| Label | Property | Type |
|---|---|---|
| `Obligation` | `framework_id` | Secondary |
| `Control` | `framework_id` | Secondary |

## SHACL Shapes

Shape definitions live in `/backend/app/shapes/` as `.ttl` (Turtle RDF) files. Each node label has exactly one shape file defining its structure:

| Shape File | Target Label |
|---|---|
| `obligation.ttl` | `Obligation` |
| `control.ttl` | `Control` |
| `regulation.ttl` | `Regulation` |
| `gap.ttl` | `Gap` |
| `risk.ttl` | `Risk` |
| `evidence.ttl` | `Evidence` |
| `third_party.ttl` | `ThirdParty` |
| `control_effectiveness.ttl` | `ControlEffectiveness` |

SHACL shapes are loaded by `app.graph.schema.init_schema()` via the Memgraph SHACL extension.

## Schema Versioning

Schema version is tracked via a `MemgraphSchemaVersion` node in Memgraph itself:

```cypher
MERGE (v:MemgraphSchemaVersion {version: "INFRA-9"})
SET v.last_applied = timestamp(), v.description = "...";
```

The `check_health()` function reads this node to report the current schema version.

## Initialization

```python
from app.graph.schema import init_schema

result = init_schema()
# Returns: {"labels": N, "constraints": N, "indexes": N,
#           "shacl_loaded": [...], "shacl_count": N,
#           "version": "INFRA-9", "applied_at": "...", "status": "success"}
```

The script at `app/graph/init_schema.cypher` contains the raw Cypher statements and can be run independently via the Memgraph shell.

## Health Check

`GET /api/v1/graph/health` returns the current schema state:

```json
{
  "schema_version": "INFRA-9",
  "labels": 8,
  "indexes": 2,
  "constraints": 8,
  "shacl_loaded": true,
  "status": "healthy"
}
```

Status values: `healthy` (labels + version present), `degraded` (version present but labels missing), `unknown` (nothing available).

## Idempotency

All Cypher statements use `IF NOT EXISTS` or `MERGE`, making the initialization safe to run multiple times.
