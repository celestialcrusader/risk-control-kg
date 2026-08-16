# Work Log: [FIX-103] Wire Multi-Prompt LLM Extraction into extraction.py with Document-Type Routing

**Developer:** SWE Agent  
**Date:** 2026-07-31  
**Status:** READY_FOR_QA  
**Target Story:** [FIX-103](file:///home/zackchow/coding/rckg/docs/04-deepdive/real-mvp.md#fix-103-wire-multi-prompt-llm-extraction-into-extractionpy-with-document-type-routing)  

---

## 1. Executive Summary & Work Accomplished
Wired multi-prompt template routing and multi-type schema parsing into `backend/app/services/extraction.py`:
1. Updated `_load_prompt_template(document_type)` to dispatch to `extraction.md` for STATUTORY/REGULATORY_GUIDELINE, `extraction_control_objective.md` for ENTERPRISE_POLICY, and `extraction_control_activity.md` for PROCEDURE_SOP.
2. Updated `_parse_llm_response(raw_response, document_type)` to parse and validate `ControlObjective` objects for policy documents and `ControlActivity` objects for SOP documents.
3. Added `document_type` to `ExtractionRequest` in `backend/app/api/extract.py`.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/extraction.py` | [MODIFY] | Added multi-prompt template map, document_type routing, and Pydantic schema parsing |
| `backend/app/api/extract.py` | [MODIFY] | Added `document_type` to `ExtractionRequest` and passed through to service |
| `backend/tests/test_extraction_multi_type.py` | [NEW] | TDD Unit tests for multi-prompt routing and schema parsing |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_extraction_multi_type.py`
- **Initial Failure Reason:** `_load_prompt_template()` and `_parse_llm_response()` did not accept `document_type`, and `ExtractionRequest` lacked `document_type` field.

### 🟢 GREEN Phase
- **Implementation Files:** `backend/app/services/extraction.py`, `backend/app/api/extract.py`
- **Passing Verification:** `pytest backend/tests/test_extraction_multi_type.py -v` passed (4/4 passed).

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Extracted `PROMPT_TEMPLATE_MAP` lookup dictionary; gracefully handled case-insensitivity on document type parameter.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_extraction_multi_type.py -v
========================== 4 passed in 0.11s ==========================
```

## 5. Notes for QA Reviewer
- Test with valid JSON responses for all 3 document types to ensure validation works as expected.
