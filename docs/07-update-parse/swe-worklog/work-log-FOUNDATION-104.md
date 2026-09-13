# Work Log: [STORY-FOUNDATION-104] Direct Public Baseline Graph Linkages & Schema Decoupling

**Developer:** SWE Agent  
**Date:** 2026-08-15  
**Status:** READY_FOR_QA  
**Target Story:** [STORY-FOUNDATION-104](docs/07-update-parse/sprint-plan-foundation-setup.md#story-foundation-104-direct-public-baseline-graph-linkages--schema-decoupling)  

---

## 1. Executive Summary & Work Accomplished
Decoupled the knowledge graph schema from requiring a mandatory client `ControlObjectiveNode (CO)`. Implemented direct public relationship ORM models (`ObligationFrameworkMapping`, `RiskFrameworkMapping`, and `FrameworkCrosswalkMapping`) in PostgreSQL and added parameterized Cypher builders for direct public baseline queries (`:CROSSWALKS_TO`, `:MITIGATED_BY`, `:ALIGNS_WITH`) in Memgraph.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/models/rckg_nodes.py` | [MODIFY] | Added `ObligationFrameworkMapping`, `RiskFrameworkMapping`, `FrameworkCrosswalkMapping` models |
| `backend/app/models/__init__.py` | [MODIFY] | Exported new mapping models in `__all__` |
| `backend/app/graph/rckg_queries.py` | [MODIFY] | Added Cypher builders for direct public baseline crosswalks |
| `backend/tests/test_public_baseline_linkages.py` | [NEW] | TDD Unit tests for direct public mapping creation |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_public_baseline_linkages.py`
- **Initial Failure Reason:** `ImportError: cannot import name 'ObligationFrameworkMapping' from 'app.models.rckg_nodes'`.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/models/rckg_nodes.py`, `backend/app/graph/rckg_queries.py`
- **Passing Verification:** `pytest backend/tests/test_public_baseline_linkages.py -v` passed 3/3 tests (100% success).

### 🔵 REFACTOR Phase
- Configured scoped table isolation in test fixture to prevent SQLite `JSONB` compilation errors on un-targeted tables.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_public_baseline_linkages.py -v
========================== 3 passed in 0.09s ==========================
```
