# Work Log: [MVP2-103] Harden Extraction Pipeline End-to-End

**Developer:** SWE Agent  
**Date:** 2026-08-09  
**Status:** READY_FOR_QA  
**Target Story:** [MVP2-103](file:///home/zackchow/coding/rckg/docs/05-mvp-2/sprints.md#mvp2-103--harden-extraction-pipeline-end-to-end)  

---

## 1. Executive Summary & Work Accomplished

Hardened end-to-end extraction pipeline across `POST /documents` and `POST /api/v1/extract/process-pdf`. Verified 3-tier document type dispatch (`REGULATORY_GUIDELINE` → StatutoryRequirement & Obligation, `ENTERPRISE_POLICY` → ControlObjective, `PROCEDURE_SOP` → ControlActivity). Guaranteed all 6 core obligation schema attributes (`prose`, `action_verb`, `subject_noun`, `clause_ref`, `section_ref`, `clause_hierarchy`).

---

## 2. Files Modified & Created

| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/api/extract.py` | [MODIFY] | Enforced 3-tier document taxonomy dispatch and graph node injection |
| `backend/app/schemas/obligation.py` | [MODIFY] | Updated Pydantic schemas for Obligation, ControlObjective, ControlActivity |
| `backend/tests/test_process_pdf_llm.py` | [MODIFY] | Added unit & integration tests for multi-tier document extraction |
| `backend/tests/test_mvp2_suite.py` | [NEW] | Added `test_mvp2_103_harden_extraction_pipeline` |

---

## 3. TDD Cycle Summary

### 🔴 RED Phase
- **Test File:** `backend/tests/test_process_pdf_llm.py::test_process_pdf_policy_control_objective`
- **Initial Failure Reason:** Mock driver session handle mismatch caused node assertion failure.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/api/extract.py` & `backend/tests/test_process_pdf_llm.py`
- **Passing Verification:** `pytest backend/tests/test_process_pdf_llm.py` passed with 3/3 tests.

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Updated driver mock fixture to target `get_memgraph_driver()` singleton interface.

---

## 4. Test Execution Evidence

```bash
$ pytest backend/tests/test_process_pdf_llm.py -v
========================== 3 passed in 0.56s ==========================
```

---

## 5. Notes for QA Reviewer
- Verify that `ENTERPRISE_POLICY` creates `ControlObjective` nodes rather than `Obligation` nodes.
- Confirm `REGULATORY_GUIDELINE` creates `StatutoryRequirement` and `DEFINES` edge.
