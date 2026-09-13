# Work Log: [CFIX-104] Eliminate Silent LLM Fallback in NLI Engine — Require Explicit Degradation

**Developer:** SWE Agent  
**Date:** 2026-08-02  
**Status:** READY_FOR_QA  
**Target Story:** [CFIX-104](docs/04-deepdive/claude-remediation-sprint.md#cfix-104-eliminate-silent-llm-fallback-in-nli-engine--require-explicit-degradation)  

---

## 1. Executive Summary & Work Accomplished
Updated `NliSetTheoryEngine.evaluate_pair()` to provide truthful metadata and explicit degradation logging. On LLM success, `metadata["method"]` is set to `"LLM_CLASSIFICATION"` and `metadata["model"]` is `"LLM_PROXY"`. On LLM failure, `logger.warning()` is emitted with the premise/hypothesis and error reason, and `metadata["method"]` is set to `"KEYWORD_HEURISTIC_FALLBACK"` with `metadata["model"] = "KEYWORD_HEURISTIC"`. The misleading `"DeBERTa-v3"` claim was completely removed from the fallback path.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/nli_engine.py` | MODIFIED | Added explicit metadata methods and degradation warning logging |
| `backend/tests/test_cfix_104_nli_degradation.py` | [NEW] | TDD unit test verifying metadata on LLM success and fallback |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_cfix_104_nli_degradation.py`
- **Initial Failure Reason:** `KeyError: 'method'` because metadata was missing method tracking.

### 🟢 GREEN Phase
- **Implementation:** Added `method` and truthful `model` metadata keys to both success and fallback paths.
- **Passing Verification:** `pytest backend/tests/test_cfix_104_nli_degradation.py` passed 100%.

### 🔵 REFACTOR Phase
- Cleaned up exception logger warning formatting to truncate long text snippets safely.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_cfix_104_nli_degradation.py -v
========================== 2 passed in 0.02s ==========================
```

## 5. Notes for QA Reviewer
- Verified `metadata["method"] == "LLM_CLASSIFICATION"` when LLM responds.
- Verified `metadata["method"] == "KEYWORD_HEURISTIC_FALLBACK"` and `DeBERTa` is absent when LLM fails.
