# Work Log: [FIX-101] Fix LLM_ENDPOINT Port Collision & Import Path Inconsistency

**Developer:** SWE Agent  
**Date:** 2026-07-31  
**Status:** READY_FOR_QA  
**Target Story:** [FIX-101](file:///home/zackchow/coding/rckg/docs/04-deepdive/real-mvp.md#fix-101-fix-llm_endpoint-port-collision--import-path-inconsistency)  

---

## 1. Executive Summary & Work Accomplished
1. Fixed default `LLM_ENDPOINT` port in `backend/app/services/extraction.py` from `http://localhost:8000/v1` to `http://localhost:8001/v1` to avoid self-call loop with FastAPI (which runs on port 8000).
2. Cleaned up all `from backend.app.services...` imports in `backend/app/api/extract.py` to use relative module path `from app.services...` to prevent import failures.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/extraction.py` | [MODIFY] | Changed default LLM_ENDPOINT port to 8001 |
| `backend/app/api/extract.py` | [MODIFY] | Updated imports from `backend.app.services` to `app.services` |
| `backend/tests/test_fix_101_config_and_imports.py` | [NEW] | TDD Unit test for port default and import paths |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_fix_101_config_and_imports.py`
- **Initial Failure Reason:** `LLM_ENDPOINT` default contained `:8000` port, and `extract.py` contained `from backend.app.services` statements.

### 🟢 GREEN Phase
- **Implementation Files:** `backend/app/services/extraction.py`, `backend/app/api/extract.py`
- **Passing Verification:** `pytest backend/tests/test_fix_101_config_and_imports.py -v` passed (2/2 passed).

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Consistent `app.services` imports across all endpoint handlers in `extract.py`.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_fix_101_config_and_imports.py -v
========================== 2 passed in 0.10s ==========================
```

## 5. Notes for QA Reviewer
- Confirm that setting `LLM_ENDPOINT` env var overrides the new 8001 default as expected.
