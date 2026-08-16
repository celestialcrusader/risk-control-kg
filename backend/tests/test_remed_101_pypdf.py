"""
TDD Unit/Integration Test for REMED-101: Live PDF Conversion Fallback using PyPDF.
"""

import os
import tempfile
import pytest
from app.services.pdf_to_markdown import _run_marker, MarkerFallbackConverter, convert_pdf_to_markdown

# Sample minimal 1-page PDF bytes with heading and text content
SAMPLE_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 75 >>\nstream\nBT /F1 12 Tf 100 700 Td (Section 1 Title) Tj ET\nBT /F1 12 Tf 100 650 Td (System must enforce access controls.) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000062 00000 n\n0000000125 00000 n\n0000000224 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n348\n%%EOF"


def test_remed_101_run_marker_live_pypdf_parsing():
    """Verify _run_marker extracts text and headings via pypdf without throwing RuntimeError."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(SAMPLE_PDF_BYTES)
        tmp_path = tmp.name

    try:
        result = _run_marker(tmp_path)
        assert result is not None
        assert result.confidence == 0.88
        assert len(result.headings) > 0
        assert "Section 1" in result.markdown or "Document Content" in result.markdown
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_remed_101_invalid_pdf_raises_value_error():
    """Verify invalid PDF content raises ValueError instead of RuntimeError."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"INVALID PDF BYTES")
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError) as exc_info:
            _run_marker(tmp_path)
        assert "Invalid PDF file structure" in str(exc_info.value)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
