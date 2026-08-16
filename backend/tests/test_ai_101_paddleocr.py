import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_to_markdown import convert_pdf_to_markdown, PaddleOCRVLConverter

def test_paddleocr_primary_success(tmp_path):
    pdf_file = tmp_path / "test_doc.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock content")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "# Header\nTest markdown content"}}],
        "confidence": 0.95,
    }

    with patch("requests.post", return_value=mock_resp), \
         patch("app.services.pdf_to_markdown.get_minio_storage"):
        result = convert_pdf_to_markdown(str(pdf_file), "doc_123")
        assert result["converter_used"] == "paddleocr-vl-1.6"
        assert result["confidence_score"] == 0.95
