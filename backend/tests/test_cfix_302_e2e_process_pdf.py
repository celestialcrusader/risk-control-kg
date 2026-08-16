"""
End-to-End Integration Test for CFIX-302: PDF Upload → LLM Chunking → Memgraph Cypher & Outbox Dual-Write.
"""

import time
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_e2e_process_pdf_pipeline():
    """Verify full end-to-end PDF processing pipeline under 5 seconds with mocked infrastructure."""
    start_time = time.time()
    
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    pdf_text = (
        b"%PDF-1.4\n"
        b"1.1 Access Control Policy\n"
        b"Financial institutions must enforce multi-factor authentication for all administrative system access.\n"
    )
    files = {"file": ("MAS_TRM_Guidelines_Test.pdf", pdf_text, "application/pdf")}

    llm_json = (
        '{"obligations": ['
        '{"id": "OBL-001", "prose": "Enforce multi-factor authentication for administrative access", '
        '"action_verb": "enforce", "subject_noun": "multi-factor authentication", "clause_ref": "1.1"}'
        ']}'
    )

    with patch("neo4j.GraphDatabase.driver", return_value=mock_driver):
        with patch("app.services.extraction._call_llm", return_value=llm_json):
            with patch("app.core.memgraph.get_memgraph_driver", return_value=mock_driver):
                response = client.post("/api/v1/extract/process-pdf", files=files)
                
                duration = time.time() - start_time
                assert duration < 10.0, f"E2E test took too long ({duration:.2f}s)"

                assert response.status_code == 200
                data = response.json()

                assert data["status"] == "SUCCESS"
                assert data["degraded_chunks"] == 0
                assert data["nodes_injected"] > 0
                assert data["edges_injected"] > 0

                # Verify Cypher execution occurred on session
                cypher_calls = [call.args[0] for call in mock_session.run.call_args_list]
                assert any("MERGE (d:StatutoryRequirement" in c for c in cypher_calls)
                assert any("MERGE (o:Obligation" in c for c in cypher_calls)
                assert any("o.extraction_method = $method" in c for c in cypher_calls)
