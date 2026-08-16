"""
TDD Unit & Integration Test for CFIX-101: GraphRevert API Dependency Wiring.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_revert_endpoint_returns_503_when_memgraph_unavailable():
    """Verify POST /api/v1/extract/graph/revert returns 503 if Memgraph driver is unavailable."""
    with patch("app.core.memgraph.get_memgraph_driver", return_value=None):
        response = client.post(
            "/api/v1/extract/graph/revert",
            json={
                "diff_id": "DIFF-101",
                "auditor_id": "AUDITOR-01",
                "revert_reason": "Testing 503 fallback",
            },
        )
        assert response.status_code == 503
        assert "Memgraph connection unavailable" in response.json()["detail"]


def test_revert_endpoint_executes_with_live_connections():
    """Verify POST /api/v1/extract/graph/revert passes db and memgraph driver to service."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    with patch("app.core.memgraph.get_memgraph_driver", return_value=mock_driver):
        with patch("app.services.graph_revert_service.GraphRevertService.execute_revert") as mock_exec:
            mock_exec.return_value = MagicMock(model_dump=lambda: {"status": "REVERTED", "diff_id": "DIFF-101"})
            
            response = client.post(
                "/api/v1/extract/graph/revert",
                json={
                    "diff_id": "DIFF-101",
                    "auditor_id": "AUDITOR-01",
                    "revert_reason": "Testing success path",
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "REVERTED"
            assert mock_exec.called
