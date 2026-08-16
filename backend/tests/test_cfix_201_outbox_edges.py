"""
TDD Unit & Integration Test for CFIX-201: Outbox Dual-Write for ALL process-pdf Graph Mutations.
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_process_pdf_routes_all_mutations_through_outbox():
    """Verify that process-pdf enqueues outbox logs for both nodes AND edges via MemgraphService."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    pdf_bytes = b"%PDF-1.4 Section 3.1 Access Control. System administrator must limit access credentials."
    files = {"file": ("test_doc.pdf", pdf_bytes, "application/pdf")}
    llm_json = '{"obligations": [{"id": "OBL-1", "prose": "Must limit access", "action_verb": "limit", "subject_noun": "access", "clause_ref": "Section 3.1"}]}'

    with patch("neo4j.GraphDatabase.driver", return_value=mock_driver):
        with patch("app.services.extraction._call_llm", return_value=llm_json):
            with patch("app.services.memgraph_service.MemgraphService.enqueue_and_execute") as mock_enqueue:
                response = client.post("/api/v1/extract/process-pdf", files=files)
                assert response.status_code == 200
                # Must be called for ADD_NODE and ADD_EDGE mutations
                assert mock_enqueue.called
                calls = mock_enqueue.call_args_list
                # Check that both node and edge primitives were enqueued
                primitives = [call.args[0].primitive.value for call in calls]
                assert "ADD_NODE" in primitives
                assert "ADD_EDGE" in primitives
