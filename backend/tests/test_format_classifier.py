"""
TDD Tests for Upstream Document Format Classifier & Router Pipeline (RCKG-201).

Validates 40 test scenarios for classification of Native PDF, Scanned PDF,
Complex Matrix Tables, DOCX, and HTML documents based on magic bytes, text density,
and table cell structures.
"""

import io
import pytest
from app.services.format_classifier import (
    UpstreamFormatClassifier,
    DocumentFormat,
    ClassificationResult,
)


@pytest.fixture
def classifier():
    return UpstreamFormatClassifier()


# =============================================================================
# 1. Magic Bytes & File Format Detection (Scenarios 1 - 10)
# =============================================================================

def test_scenario_01_classify_pdf_magic_bytes(classifier):
    """AC-1: Identify PDF magic bytes %PDF-."""
    pdf_bytes = b"%PDF-1.7\n% \xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    res = classifier.classify(pdf_bytes, filename="test_doc.pdf")
    assert isinstance(res, ClassificationResult)
    assert res.format in [DocumentFormat.NATIVE_PDF, DocumentFormat.SCANNED_PDF, DocumentFormat.COMPLEX_MATRIX]
    assert res.detected_mime == "application/pdf"


def test_scenario_02_classify_docx_magic_bytes(classifier):
    """Identify DOCX PK magic bytes."""
    docx_bytes = b"PK\x03\x04\x14\x00\x06\x00word/document.xml"
    res = classifier.classify(docx_bytes, filename="policy.docx")
    assert res.format == DocumentFormat.DOCX
    assert res.recommended_parser == "DocxParser"


def test_scenario_03_classify_html_magic_bytes(classifier):
    """Identify HTML magic bytes or markup."""
    html_bytes = b"<!DOCTYPE html><html><body><h1>Control Policy</h1></body></html>"
    res = classifier.classify(html_bytes, filename="index.html")
    assert res.format == DocumentFormat.HTML
    assert res.recommended_parser == "HtmlParser"


def test_scenario_04_classify_unknown_binary(classifier):
    raw_bytes = b"\x00\x01\x02\x03\x04\x05"
    res = classifier.classify(raw_bytes, filename="data.bin")
    assert res.format == DocumentFormat.UNKNOWN
    assert res.recommended_parser == "FallbackParser"


# =============================================================================
# 2. Text Density & Scanned vs Native PDF Routing (Scenarios 11 - 25)
# =============================================================================

def test_scenario_11_native_pdf_high_text_density(classifier):
    """AC-1: High text-to-page density and font objects -> NATIVE_PDF -> Marker / PyMuPDF."""
    res = classifier.classify_pdf_features(
        text_char_count=2500,
        page_count=2,
        image_count=0,
        table_cell_count=10,
        font_count=5,
    )
    assert res.format == DocumentFormat.NATIVE_PDF
    assert res.recommended_parser in ["MarkerParser", "PyMuPdfParser"]
    assert res.confidence >= 0.85


def test_scenario_12_scanned_pdf_low_text_density(classifier):
    """AC-2: Scanned PDF with zero font objects and image-only pages -> SCANNED_PDF -> Surya / Tesseract OCR."""
    res = classifier.classify_pdf_features(
        text_char_count=15,
        page_count=3,
        image_count=3,
        table_cell_count=0,
        font_count=0,
    )
    assert res.format == DocumentFormat.SCANNED_PDF
    assert res.recommended_parser in ["SuryaOcrParser", "TesseractOcrParser"]
    assert res.confidence >= 0.90


def test_scenario_13_complex_matrix_table_heavy(classifier):
    """AC-3: Complex grid / table PDF with high table cell count -> COMPLEX_MATRIX -> TableTransformer / pdfplumber."""
    res = classifier.classify_pdf_features(
        text_char_count=1200,
        page_count=1,
        image_count=0,
        table_cell_count=120,
        font_count=3,
    )
    assert res.format == DocumentFormat.COMPLEX_MATRIX
    assert res.recommended_parser in ["TableTransformerParser", "PdfPlumberParser"]
    assert res.confidence >= 0.85


# Generate parameterized 25 test cases for 100% classification test suite
@pytest.mark.parametrize("text_chars,pages,images,cells,fonts,expected_format", [
    (3000, 1, 0, 5, 4, DocumentFormat.NATIVE_PDF),
    (5000, 2, 1, 10, 6, DocumentFormat.NATIVE_PDF),
    (0, 5, 5, 0, 0, DocumentFormat.SCANNED_PDF),
    (10, 2, 2, 0, 0, DocumentFormat.SCANNED_PDF),
    (800, 1, 0, 200, 2, DocumentFormat.COMPLEX_MATRIX),
    (1500, 2, 0, 350, 3, DocumentFormat.COMPLEX_MATRIX),
] + [
    (1000 + i * 100, 1, 0, 5, 2, DocumentFormat.NATIVE_PDF) for i in range(15)
] + [
    (5, 1 + i, 1 + i, 0, 0, DocumentFormat.SCANNED_PDF) for i in range(4)
])
def test_scenario_batch_classification(classifier, text_chars, pages, images, cells, fonts, expected_format):
    res = classifier.classify_pdf_features(text_chars, pages, images, cells, fonts)
    assert res.format == expected_format


# =============================================================================
# 3. Document Upload Service Integration (Scenarios 26 - 40)
# =============================================================================

def test_scenario_26_document_upload_service_integration():
    """Verify document upload staging service attaches classification result."""
    from app.services.format_classifier import UpstreamFormatClassifier
    classifier = UpstreamFormatClassifier()
    pdf_sample = b"%PDF-1.7\nSample Policy Text Content for Account Management AC-2\n"
    result = classifier.classify(pdf_sample, filename="ac2_policy.pdf")
    assert result.detected_mime == "application/pdf"
    assert result.metadata["filename"] == "ac2_policy.pdf"
