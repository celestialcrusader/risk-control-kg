"""
Test main FastAPI application startup and root endpoint.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_main_app_root_and_routes():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "Pure RCKG Engine"
    assert data["status"] == "HEALTHY"
