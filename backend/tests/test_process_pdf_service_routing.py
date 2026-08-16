"""
Integration / Unit tests for FIX-202 (Route process-pdf through MemgraphService).
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.memgraph_service import MemgraphService

client = TestClient(app)


@patch("neo4j.GraphDatabase.driver")
@patch.object(MemgraphService, "enqueue_and_execute")
@patch("app.services.extraction._call_llm")
def test_process_pdf_routes_through_memgraph_service(mock_call_llm, mock_enqueue, mock_driver):
    """
    Test that process-pdf endpoint calls MemgraphService.enqueue_and_execute for graph mutations (FIX-202).
    """
    mock_call_llm.return_value = '{"obligations": [{"id": "OBL-01", "prose": "The organization must enforce MFA.", "action_verb": "enforce", "subject_noun": "organization", "clause_ref": "Section 3.1"}]}'

    mock_session = MagicMock()
    mock_driver.return_value.session.return_value.__enter__.return_value = mock_session

    pdf_bytes = b"%PDF-1.4 Section 3.1 Access Control\nThe organization must enforce MFA."
    files = {"file": ("test_trm_service.pdf", pdf_bytes, "application/pdf")}

    response = client.post("/api/v1/extract/process-pdf?document_type=REGULATORY_GUIDELINE", files=files)
    assert response.status_code == 200

    # Verify enqueue_and_execute was called for mutations
    assert mock_enqueue.called, "MemgraphService.enqueue_and_execute should be called for mutations"
