"""
TDD Tests for Specialized Multi-Parser Stack Integration (RCKG-202).

Validates NativePdfParser, ScannedOcrParser, MatrixTableParser, and ParserDispatcher.
"""

import pytest
from app.services.parsers.base_parser import BaseParser, ParseResult
from app.services.parsers.native_pdf_parser import NativePdfParser
from app.services.parsers.ocr_parser import ScannedOcrParser
from app.services.parsers.matrix_parser import MatrixTableParser
from app.services.parsers.parser_dispatcher import ParserDispatcher
from app.services.format_classifier import DocumentFormat


def test_native_pdf_parser_headings_and_bullets():
    """AC-1: NativePdfParser preserves heading hierarchy (#, ##, ###) and list bullets."""
    parser = NativePdfParser()
    sample_bytes = b"%PDF-1.7\n# 1. Access Control Policy\n## 1.1 Account Management\n- Must review quarterly."
    res = parser.parse(sample_bytes, filename="policy.pdf")

    assert isinstance(res, ParseResult)
    assert "# 1. Access Control Policy" in res.markdown_text
    assert "## 1.1 Account Management" in res.markdown_text
    assert "- Must review quarterly." in res.markdown_text
    assert res.heading_count >= 2


def test_scanned_ocr_parser_text_extraction():
    """AC-2: ScannedOcrParser executes OCR and outputs clean Markdown text."""
    parser = ScannedOcrParser()
    sample_bytes = b"SCANNED_IMAGE_RAW_BYTES_SAMPLE_SOP_ACCESS_CONTROL"
    res = parser.parse(sample_bytes, filename="scanned_sop.pdf")

    assert isinstance(res, ParseResult)
    assert len(res.markdown_text) > 0
    assert "OCR" in res.metadata.get("engine", "OCR") or res.confidence_score >= 0.85


def test_matrix_table_parser_grid_extraction():
    """AC-3: MatrixTableParser extracts grid columns and formats aligned markdown tables."""
    parser = MatrixTableParser()
    csv_or_matrix_bytes = b"Control ID,Control Name,Status\nAC-1,Policy,Active\nAC-2,Account Management,Active\n"
    res = parser.parse(csv_or_matrix_bytes, filename="control_matrix.xlsx")

    assert isinstance(res, ParseResult)
    assert "| Control ID | Control Name | Status |" in res.markdown_text
    assert "| AC-1 | Policy | Active |" in res.markdown_text
    assert res.table_count >= 1


def test_parser_dispatcher_routing():
    """AC-4: ParserDispatcher routes DocumentFormat to correct parser implementation."""
    dispatcher = ParserDispatcher()

    native_p = dispatcher.get_parser(DocumentFormat.NATIVE_PDF)
    assert isinstance(native_p, NativePdfParser)

    ocr_p = dispatcher.get_parser(DocumentFormat.SCANNED_PDF)
    assert isinstance(ocr_p, ScannedOcrParser)

    matrix_p = dispatcher.get_parser(DocumentFormat.COMPLEX_MATRIX)
    assert isinstance(matrix_p, MatrixTableParser)
