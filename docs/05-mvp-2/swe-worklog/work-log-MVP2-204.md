# Work Log: [MVP2-204] Facet Extractor LLM Hardening

**Developer:** SWE Agent  
**Date:** 2026-08-09  
**Status:** READY_FOR_QA  
**Target Story:** [MVP2-204](file:///home/zackchow/coding/rckg/docs/05-mvp-2/sprints.md#mvp2-204--facet-extractor-llm-hardening)  

---

## 1. Executive Summary & Work Accomplished

Hardened `DeJureFacetExtractor.extract_facets()` in `backend/app/services/facet_extractor.py`. Expanded regex verb fallback coverage to over 25 common compliance verbs (`enforce`, `restrict`, `authorize`, `audit`, `encrypt`, `monitor`, `provision`, `deactivate`, etc.). Marked degraded regex output with `extraction_method: "REGEX_DEGRADED"` and capped confidence at 0.30.

---

## 2. Files Modified & Created

| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/facet_extractor.py` | [MODIFY] | Expanded compliance verb dictionary and tagged degraded extraction method |
| `backend/tests/test_cfix_200_facet_llm.py` | [MODIFY] | Updated unit tests for facet extraction |
| `backend/tests/test_mvp2_suite.py` | [NEW] | Added `test_mvp2_204_facet_extractor_degraded` |

---

## 3. TDD Cycle Summary

### 🔴 RED Phase
- **Test File:** `backend/tests/test_mvp2_suite.py::test_mvp2_204_facet_extractor_degraded`
- **Initial Failure Reason:** Regex verb dictionary contained only 10 hardcoded verbs.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/services/facet_extractor.py`
- **Passing Verification:** `pytest backend/tests/test_mvp2_suite.py -k test_mvp2_204` passed with 100% success.

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Dynamic domain facet mapping based on action verb semantic clustering.

---

## 4. Test Execution Evidence

```bash
$ pytest backend/tests/test_mvp2_suite.py -k test_mvp2_204 -v
========================== 1 passed in 0.11s ==========================
```

---

## 5. Notes for QA Reviewer
- Verify that LLM path populates all 6 facets when available.
- Confirm regex fallback caps confidence score at 0.30.
