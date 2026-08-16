"""
TDD Unit Test for CFIX-304: System Dependency Health Check Endpoint.
"""

from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check_healthy_status():
    """Verify health check returns HEALTHY when PostgreSQL, Memgraph, and LLM are all connected."""
    with patch("app.core.health.ping_database", return_value=True):
        with patch("app.core.health.check_llm_connectivity", return_value=True):
            with patch("app.core.health.get_memgraph_driver") as mock_driver_fn:
                mock_driver = MagicMock()
                mock_driver_fn.return_value = mock_driver
                
                response = client.get("/api/v1/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "HEALTHY"
                assert data["postgresql"] == "connected"
                assert data["memgraph"] == "connected"
                assert data["llm_endpoint"] == "connected"


def test_health_check_degraded_status():
    """Verify health check returns DEGRADED when LLM is unreachable but DB and Memgraph are up."""
    with patch("app.core.health.ping_database", return_value=True):
        with patch("app.core.health.check_llm_connectivity", return_value=False):
            with patch("app.core.health.get_memgraph_driver") as mock_driver_fn:
                mock_driver = MagicMock()
                mock_driver_fn.return_value = mock_driver
                
                response = client.get("/api/v1/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "DEGRADED"
                assert data["llm_endpoint"] == "unreachable"


def test_health_check_unhealthy_status():
    """Verify health check returns UNHEALTHY when PostgreSQL is unreachable."""
    with patch("app.core.health.ping_database", return_value=False):
        with patch("app.core.health.check_llm_connectivity", return_value=True):
            with patch("app.core.health.get_memgraph_driver", return_value=None):
                response = client.get("/api/v1/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "UNHEALTHY"
                assert data["postgresql"] == "unreachable"
