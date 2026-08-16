"""
TDD Unit Test for CFIX-106: process-pdf Extraction Degradation & Node Provenance Property.
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_process_pdf_status_degraded_when_all_llm_calls_fail():
    """Verify process-pdf returns status='DEGRADED' when LLM fails for all chunks."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    pdf_bytes = b"%PDF-1.4 Section 3.1 Access Control. System administrator must limit access credentials."
    files = {"file": ("test_doc.pdf", pdf_bytes, "application/pdf")}

    with patch("neo4j.GraphDatabase.driver", return_value=mock_driver):
        with patch("app.services.extraction._call_llm", side_effect=RuntimeError("vLLM down")):
            response = client.post("/api/v1/extract/process-pdf", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "DEGRADED"
            assert data["degraded_chunks"] > 0
            assert "used regex fallback" in data["message"]


def test_process_pdf_status_success_when_llm_succeeds():
    """Verify process-pdf returns status='SUCCESS' and degraded_chunks=0 when LLM succeeds."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    pdf_bytes = b"%PDF-1.4 Section 3.1 Access Control. System administrator must limit access credentials."
    files = {"file": ("test_doc.pdf", pdf_bytes, "application/pdf")}
    llm_json = '{"obligations": [{"id": "OBL-1", "prose": "Must limit access", "action_verb": "limit", "subject_noun": "access", "clause_ref": "Section 3.1"}]}'

    with patch("neo4j.GraphDatabase.driver", return_value=mock_driver):
        with patch("app.services.extraction._call_llm", return_value=llm_json):
            response = client.post("/api/v1/extract/process-pdf", files=files)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "SUCCESS"
            assert data["degraded_chunks"] == 0
