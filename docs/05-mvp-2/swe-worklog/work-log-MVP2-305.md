# Work Log: [MVP2-305] Bitemporal Columns on Remaining Node Types

**Developer:** SWE Agent  
**Date:** 2026-08-09  
**Status:** READY_FOR_QA  
**Target Story:** [MVP2-305](file:///home/zackchow/coding/rckg/docs/05-mvp-2/sprints.md#mvp2-305--bitemporal-columns-on-remaining-node-types)  

---

## 1. Executive Summary & Work Accomplished

Added bitemporal metadata fields (`valid_from`, `valid_to`, `ingested_at`) across remaining RCKG entity node models (`ControlObjectiveNode`, `ControlActivityNode`, `FrameworkControlObjectiveNode`, `FrameworkControlActivityNode`, `RiskNode`) in `backend/app/models/rckg_nodes.py`. Preserves schema consistency across all graph entity and edge types per BR-10.

---

## 2. Files Modified & Created

| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/models/rckg_nodes.py` | [MODIFY] | Added `valid_from`, `valid_to`, `ingested_at` columns across all node types |
| `backend/tests/test_rckg_nodes.py` | [MODIFY] | Updated unit tests verifying bitemporal defaults |
| `backend/tests/test_mvp2_suite.py` | [NEW] | Added `test_mvp2_305_bitemporal_columns` |

---

## 3. TDD Cycle Summary

### 🔴 RED Phase
- **Test File:** `backend/tests/test_mvp2_suite.py::test_mvp2_305_bitemporal_columns`
- **Initial Failure Reason:** Non-Obligation node models lacked explicit `valid_from` / `valid_to` attribute definitions.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/models/rckg_nodes.py`
- **Passing Verification:** `pytest backend/tests/test_mvp2_suite.py -k test_mvp2_305` passed cleanly.

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Set server default timestamp initializer for `valid_from` and `ingested_at` fields.

---

## 4. Test Execution Evidence

```bash
$ pytest backend/tests/test_mvp2_suite.py -k test_mvp2_305 -v
========================== 1 passed in 0.11s ==========================
```

---

## 5. Notes for QA Reviewer
- Verify that newly instantiated nodes default `valid_to` to `None` (null).
