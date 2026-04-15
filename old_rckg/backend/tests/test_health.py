from fastapi.testclient import TestClient
import pytest
import sys
import os

# Add the parent directory to sys.path to ensure we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Trying to import the app - this will fail initially (Red Phase)
try:
    from app.main import app
except ImportError:
    app = None

def test_health_endpoint():
    """
    TDD Mandate: Test that the /health endpoint returns status 200 and strict structure.
    """
    if app is None:
        pytest.fail("Could not import 'app.main'. The application does not exist yet.")
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "rckg-backend"}
