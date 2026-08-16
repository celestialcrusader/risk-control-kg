# Work Log: [RCKG-201] Upstream Document Format Classifier & Router Pipeline

**Developer:** SWE Agent  
**Date:** 2026-07-29  
**Status:** READY_FOR_QA  
**Target Story:** [RCKG-201](file:///home/zackchow/coding/rckg/docs/03-mvp/mvp-sprint.md#rckg-201-upstream-document-format-classifier--router-pipeline)  

---

## 1. Executive Summary & Work Accomplished

Implemented the `UpstreamFormatClassifier` engine in `backend/app/services/format_classifier.py` to automatically inspect incoming raw enterprise documents and route them to optimal specialized parser backends:
- `NATIVE_PDF` -> Marker / PyMuPDF
- `SCANNED_PDF` -> Surya / Tesseract OCR
- `COMPLEX_MATRIX` -> TableTransformer / pdfplumber
- `DOCX` -> python-docx
- `HTML` -> BeautifulSoup / HtmlParser

Integrated format classification inspection into the staging document upload workflow in `backend/app/services/document_upload.py`, populating audit log metadata with `detected_format` and `recommended_parser`.

---

## 2. Files Modified & Created

| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/format_classifier.py` | [NEW] | Implementation of `DocumentFormat`, `ClassificationResult`, and `UpstreamFormatClassifier` |
| `backend/app/services/document_upload.py` | [MODIFY] | Integrated format classifier inspection into upload staging audit logs |
| `backend/tests/test_format_classifier.py` | [NEW] | TDD test suite validating format classification across 33 test scenarios |

---

## 3. TDD Cycle Summary

### 🔴 RED Phase
- **Test File:** `backend/tests/test_format_classifier.py`
- **Initial Failure Reason:** `backend.app.services.format_classifier` module did not exist.

### 🟢 GREEN Phase
- **Implementation File:** `backend/app/services/format_classifier.py`
- **Passing Verification:** `pytest backend/tests/test_format_classifier.py -v` executed with 33/33 test scenarios passed (100% success).

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Passed `filename` into `classify_pdf_features()` metadata to ensure complete audit traceability.

---

## 4. Test Execution Evidence

```bash
$ pytest backend/tests/test_format_classifier.py -v
============================= test session starts ==============================
collected 33 items                                                             

backend/tests/test_format_classifier.py::test_scenario_01_classify_pdf_magic_bytes PASSED [  3%]
...
backend/tests/test_format_classifier.py::test_scenario_26_document_upload_service_integration PASSED [100%]

======================== 33 passed, 1 warning in 0.02s =========================
```

---

## 5. Notes for QA Reviewer
- Verified magic byte detection for `%PDF`, `PK\x03\x04` (DOCX), `<!DOC` (HTML).
- Verified text density and font object ratio heuristics differentiating digital native PDFs from scanned image PDFs and table-heavy matrices.
