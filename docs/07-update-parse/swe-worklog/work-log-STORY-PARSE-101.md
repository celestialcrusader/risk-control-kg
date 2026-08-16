# Work Log: [STORY-PARSE-101] Multi-Engine Document Router & Docling Integration

**Developer:** SWE Agent  
**Date:** 2026-08-12  
**Status:** READY_FOR_QA  
**Target Story:** [STORY-PARSE-101](file:///home/zackchow/coding/rckg/docs/07-update-parse/update-parse-sprint.md#story-parse-101-multi-engine-document-router--docling-integration)  

---

## 1. Executive Summary & Work Accomplished
Implemented page-level text coverage evaluation and Docling digital PDF parser integration in `backend/app/services/pdf_to_markdown.py`.
The evaluator inspects text characters per page using `PyMuPDF` (`fitz`), classifying digital native pages ($>95\%$ text) vs scanned raster image pages. Digital pages route to `DoclingConverter`, preserving text fidelity and Markdown table structures, while falling back to `PaddleOCR-VL-1.6` on port 8002 when appropriate.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| [`backend/app/services/pdf_to_markdown.py`](file:///home/zackchow/coding/rckg/backend/app/services/pdf_to_markdown.py) | [MODIFIED] | Added `evaluate_page_text_coverage()` and `DoclingConverter` |
| [`backend/tests/test_pdf_to_markdown.py`](file:///home/zackchow/coding/rckg/backend/tests/test_pdf_to_markdown.py) | [NEW] | TDD unit test suite for document router & Docling fallback |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_pdf_to_markdown.py`
- **Initial Failure Reason:** `ImportError: cannot import name 'evaluate_page_text_coverage'`.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/services/pdf_to_markdown.py`
- **Passing Verification:** `pytest backend/tests/test_pdf_to_markdown.py` passed with 2/2 tests passing.

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Extracted fallback logic into `DoclingConverter.convert()` to gracefully handle docling import errors.

## 4. Test Execution Evidence
```bash
$ python3 -m pytest backend/tests/test_pdf_to_markdown.py -v
========================== 2 passed in 0.20s ==========================
```

## 5. Notes for QA Reviewer
- Verified `evaluate_page_text_coverage` handling of missing files and fallback logic when `docling` library is missing.
