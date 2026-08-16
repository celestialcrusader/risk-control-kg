"""
TDD Unit & Integration Test for CFIX-102: GraphRAG Export API Dependency Wiring & Live Driver Execution.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_graphrag_endpoint_returns_503_when_memgraph_unavailable():
    """Verify GET /api/v1/extract/graph/graphrag-export returns 503 if Memgraph is offline."""
    with patch("app.core.memgraph.get_memgraph_driver", return_value=None):
        response = client.get("/api/v1/extract/graph/graphrag-export")
        assert response.status_code == 503
        assert "Memgraph connection unavailable for GraphRAG export" in response.json()["detail"]


def test_graphrag_endpoint_executes_with_live_driver_and_removes_hardcoded_mocks():
    """Verify GET /api/v1/extract/graph/graphrag-export uses live driver query and does NOT return mock REG-01."""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.run.return_value = []

    with patch("app.core.memgraph.get_memgraph_driver", return_value=mock_driver):
        response = client.get("/api/v1/extract/graph/graphrag-export")
        assert response.status_code == 200
        data = response.json()
        assert "entities" in data
        assert "relationships" in data
        # Ensure hardcoded fake nodes REG-01 and POL-01 are completely gone when no DB nodes exist
        node_ids = [e["id"] for e in data["entities"]]
        assert "REG-01" not in node_ids
        assert "POL-01" not in node_ids
