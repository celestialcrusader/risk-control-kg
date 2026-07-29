# UAT-09: Graph Schema Health and SHACL Validation

**Covers**: INFRA-9
**Type**: Infrastructure Health Check
**Effort**: ~5 minutes

## Objective

Verify that the Memgraph graph database is running, the schema labels/indexes/constraints are initialized, and SHACL shapes are loaded.

## Prerequisites

- UAT-01 passes (all infrastructure healthy, specifically Memgraph container)

## Steps

### Step 1: Check Memgraph Service Status

```bash
# Verify Memgraph container is running
docker-compose ps memgraph

# Check Memgraph is accepting connections
curl -s http://localhost:7687 | head -1 || echo "Bolt port not responding (expected for newer Memgraph versions)"

# Check Memgraph HTTP API
curl -s http://localhost:7444/version | python3 -m json.tool
```

**Expected**: Memgraph HTTP API returns version information.

### Step 2: Query Graph Schema Health via API

```bash
curl -s http://localhost:8000/api/v1/graph/health | python3 -m json.tool
```

**Expected Response**:
```json
{
  "schema_version": "1.0",
  "node_labels": ["Obligation", "Control", "Requirement", ...],
  "indexes": ["idx_obligation_control_id", ...],
  "constraints": ["constraint_obligation_control_id_unique", ...],
  "shacl_loaded": true,
  "shacl_shapes": [...],
  "health": "ok"
}
```

### Step 3: Verify Memgraph Schema Directly

```bash
# Query Memgraph for labels
docker exec -it $(docker-compose ps -q memgraph) mgconsole -f - << 'EOF'
SHOW LABELS;
EOF
```

**Expected**: List of node labels including Obligation, Control, Requirement.

```bash
# Query Memgraph for indexes
docker exec -it $(docker-compose ps -q memgraph) mgconsole -f - << 'EOF'
SHOW INDEXES;
EOF
```

**Expected**: Indexes on control_id, canonical_id fields.

### Step 4: Verify SHACL Shapes

```bash
# Check if SHACL shapes are loaded in Memgraph
docker exec -it $(docker-compose ps -q memgraph) mgconsole -f - << 'EOF'
MATCH (s:SHACL_Shape) RETURN count(s) AS shape_count;
EOF
```

**Expected**: shape_count > 0 (SHACL shapes loaded).

### Step 5: Verify Schema Initialization Script

```bash
# Check the schema init script exists
ls -la backend/app/graph/schema.py

# Verify it can be imported without error
python3 -c "from app.graph.schema import check_health; print('Schema module imports OK')"
```

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Memgraph service | HTTP API | Version info returned |
| 2 | Graph health API | Response structure | schema_version, node_labels, indexes, constraints, shacl_loaded=true |
| 3 | Node labels | mgconsole SHOW LABELS | Obligation, Control, Requirement labels present |
| 4 | Indexes | mgconsole SHOW INDEXES | Indexes on control_id, canonical_id |
| 5 | SHACL shapes | Shape count | shape_count > 0 |
| 6 | Schema module | Python import | Imports without error |

## Verification

- [ ] Memgraph HTTP API responds with version info
- [ ] Graph health endpoint returns valid schema report
- [ ] Node labels include required domain entities
- [ ] Indexes exist for fast lookups (control_id, canonical_id)
- [ ] SHACL shapes are loaded for data validation
- [ ] Schema module is importable

## Pass/Fail Criteria

- **PASS**: All 6 checks succeed — Memgraph is running, schema initialized, SHACL loaded
- **FAIL**: Any check fails — Memgraph may need schema re-initialization

## Schema Re-Initialization

If schema appears empty:
```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.graph.schema import initialize_schema

result = initialize_schema()
print(f"Initialization result: {result}")
PYEOF
```
