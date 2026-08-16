"""
Unit & Integration Test Suite for STORY-PARSE-101: Multi-Engine Document Router & Docling Integration.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.services.pdf_to_markdown import (
    evaluate_page_text_coverage,
    DoclingConverter,
    convert_pdf_to_markdown,
)


def test_evaluate_page_text_coverage_file_not_found():
    """Verify FileNotFoundError raised when pdf file is missing."""
    with pytest.raises(FileNotFoundError):
        evaluate_page_text_coverage("non_existent_file.pdf")


def test_docling_converter_fallback(tmp_path):
    """Verify DoclingConverter falls back to PaddleOCR when docling fails."""
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy pdf content")

    with patch("app.services.pdf_to_markdown.PaddleOCRVLConverter") as mock_paddle:
        mock_instance = MagicMock()
        mock_instance.convert.return_value = MagicMock(markdown="# Fallback Markdown", confidence=0.85)
        mock_paddle.return_value = mock_instance

        converter = DoclingConverter()
        res = converter.convert(str(pdf_file))
        assert res.markdown == "# Fallback Markdown"
