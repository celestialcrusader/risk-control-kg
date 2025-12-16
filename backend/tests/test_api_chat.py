import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Database

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

def test_chat_api_endpoint(db):
    if not db:
        return

    # 1. Setup Data
    # Create a node that we can ask about
    setup_query = """
    MERGE (r:Risk {name: 'API_Auth_Failure', description: 'Risk of unauthorized access due to weak API authentication.'})
    """
    db.execute_write(setup_query, {}, action="TEST_SETUP")

    # 2. Mock GraphRAG (we don't want to rely on actual LLM for the unit test of the endpoint)
    # We want to ensure the endpoint calls the RAG service correctly.
    
    with patch("app.api.routers.chat.GraphRAG") as MockGraphRAG:
        instance = MockGraphRAG.return_value
        instance.query.return_value = {
            "response": "Authentication failure is a critical risk.",
            "sources": ["API_Auth_Failure"]
        }
        
        # 3. Call API
        payload = {"message": "What is the risk of auth failure?"}
        response = client.post("/api/chat/", json=payload)
        
        # 4. Assertions
        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        
        assert "response" in data
        assert data["response"] == "Authentication failure is a critical risk."
        assert "sources" in data
        assert "API_Auth_Failure" in data["sources"]
        
        # Verify RAG was called
        instance.query.assert_called_once()
        args, _ = instance.query.call_args
        assert "auth failure" in args[0].lower() # The user message

    # Cleanup
    db.execute_write("MATCH (n:Risk {name: 'API_Auth_Failure'}) DETACH DELETE n", {}, action="CLEANUP")
