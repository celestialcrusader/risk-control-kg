# Work Log: [MVP2-102] Eliminate Fabricated Extraction Fallback

**Developer:** SWE Agent  
**Date:** 2026-08-09  
**Status:** READY_FOR_QA  
**Target Story:** [MVP2-102](file:///home/zackchow/coding/rckg/docs/05-mvp-2/sprints.md#mvp2-102--eliminate-fabricated-extraction-fallback)  

---

## 1. Executive Summary & Work Accomplished

Eliminated fabricated obligation extraction regex fallback in `backend/app/services/extraction.py` and API pipeline. When LLM API call fails or returns unparseable content, the pipeline returns an empty list with `extraction_method: "FAILED"` metadata and logs a degradation event via `log_degradation_event()`. Prevents silent generation of fake compliance obligations.

---

## 2. Files Modified & Created

| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/extraction.py` | [MODIFY] | Enforced honest failure output when LLM is unavailable |
| `backend/tests/test_cfix_106_process_pdf_degradation.py` | [MODIFY] | Verified degradation event logging and non-fabrication |
| `backend/tests/test_mvp2_suite.py` | [NEW] | Added `test_mvp2_102_no_fabricated_fallback` |

---

## 3. TDD Cycle Summary

### 🔴 RED Phase
- **Test File:** `backend/tests/test_mvp2_suite.py::test_mvp2_102_no_fabricated_fallback`
- **Initial Failure Reason:** LLM failure path was silently fabricating synthetic obligations.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/services/extraction.py`
- **Passing Verification:** `pytest backend/tests/test_mvp2_suite.py -k test_mvp2_102` passed with 100% success.

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Standardized exception logging with structured observability metadata.

---

## 4. Test Execution Evidence

```bash
$ pytest backend/tests/test_mvp2_suite.py -k test_mvp2_102 -v
========================== 1 passed in 0.10s ==========================
```

---

## 5. Notes for QA Reviewer
- Verify that invalid JSON output from LLM returns empty list `[]` instead of raising unhandled exception.
- Confirm `log_degradation_event()` is dispatched with `service="Extraction"`.
