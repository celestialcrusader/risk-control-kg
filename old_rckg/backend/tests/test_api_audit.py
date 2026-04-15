import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Database
from app.core.generator import AuditProgram, AuditStep

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    db = Database()
    try:
        db.connect()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")
        return None
    yield db
    db.close()

def test_audit_generator_api(db):
    if not db:
        return

    # 1. Setup Data
    setup_query = """
    MERGE (c:Control {id: 'AC-1', title: 'Access Control Policy', description: 'The organization develops and maintains an access control policy.'})
    """
    db.execute_write(setup_query, {}, action="TEST_SETUP")

    # 2. Mock LLM
    # We need to mock 'generate_structured' on the LLMClient instance created inside the router
    # Since router instantiates fresh deps, we patch the class.
    
    mock_program = AuditProgram(
        topic="Access Control",
        overview="Audit of AC policies.",
        audit_steps=[
            AuditStep(
                control_id="AC-1",
                control_title="Access Control Policy",
                test_objective="Verify policy exists.",
                test_steps=["Request policy", "Review dates"],
                expected_evidence=["Policy Document"]
            )
        ]
    )

    # Patch where it is imported/used in the router
    with patch("app.api.routers.audit.LLMClient") as MockLLMClass:
        mock_instance = MockLLMClass.return_value
        mock_instance.generate_structured.return_value = mock_program
        
        # 3. Call API
        payload = {"topic": "Access Control"}
        response = client.post("/api/audit/generate", json=payload)
        
        # 4. Assertions
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        print(f"DEBUG DATA: {data}")
        
        assert data["topic"] == "Access Control"
        assert len(data["audit_steps"]) == 1
        assert data["audit_steps"][0]["control_id"] == "AC-1"
        assert "Policy Document" in data["audit_steps"][0]["expected_evidence"]
        
    # Cleanup
    db.execute_write("MATCH (n:Control {id: 'AC-1'}) DETACH DELETE n", {}, action="CLEANUP")
