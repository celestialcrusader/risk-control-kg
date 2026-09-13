# Work Log: [REMED-103] Wire Live Database Storage to Gap Query & Reasoning Trace APIs

**Developer:** SWE Agent  
**Date:** 2026-08-09  
**Status:** READY_FOR_QA  
**Target Story:** [REMED-103](docs/05-mvp-2/gaps-to-mvp.md#remed-103-wire-live-database-storage-to-gap-query--reasoning-trace-apis)  

---

## 1. Executive Summary & Work Accomplished
Completely eliminated legacy in-memory mock dictionaries (`_GAPS_STORE` and `_MAPPINGS_STORE`) from `backend/app/api/gaps.py` and `backend/app/api/controls.py`. Refactored `GET /api/v1/gaps`, `GET /api/v1/gaps/{gap_id}/trace`, and `GET /api/v1/controls/{control_id}/mappings` to query live database records (`GapNode`, `AuditLog`, `GraphOutboxLog`) via FastAPI's `db: Session = Depends(get_db)` dependency. Severity filtering and provenance trace assembly now operate directly against database storage.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/api/gaps.py` | [MODIFY] | Removed `_GAPS_STORE` mock list and connected `/gaps` and `/gaps/{id}/trace` to database queries |
| `backend/app/api/controls.py` | [MODIFY] | Removed `_MAPPINGS_STORE` mock dict and connected `/controls/{id}/mappings` to `GraphOutboxLog` queries |
| `backend/app/models/rckg_nodes.py` | [MODIFY] | Added `source_obligation_id`, `source_obligation_text`, `target_control_text`, `clause_citation`, and `framework` columns to `GapNode` |
| `backend/tests/test_remed_103_db_query_apis.py` | [NEW] | TDD unit and integration tests for live database query APIs |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_remed_103_db_query_apis.py`
- **Initial Failure Reason:** `_GAPS_STORE` and `_MAPPINGS_STORE` still existed, and API responses were not reading from database fixtures.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/api/gaps.py`, `backend/app/api/controls.py`
- **Passing Verification:** Implemented `db.query(GapNode)` and `db.query(GraphOutboxLog)` endpoints. `pytest backend/tests/test_remed_103_db_query_apis.py` passed with 100% success (5 passed).

### 2. REFACTOR Phase
- **Refactoring Applied:** Extracted payload parameter extraction in `controls.py` and handled missing trace items with graceful 404/defaults.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_remed_103_db_query_apis.py -v
==================== 5 passed, 1 warning in 0.32s ====================
```

## 5. Notes for QA Reviewer
- Verified that deleting `_GAPS_STORE` and `_MAPPINGS_STORE` does not break any existing routes.
- Confirmed database filtering by severity (`?severity=HIGH`) works cleanly.
