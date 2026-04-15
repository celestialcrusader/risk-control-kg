import pytest
from fastapi.testclient import TestClient
import sys
import os

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

def test_get_graph_visualization(db):
    if not db:
        return

    # 1. Setup Data
    # Create some nodes and relationships to visualize
    setup_query = """
    MERGE (n1:VisNode {id: 'v1', name: 'Node 1'})
    MERGE (n2:VisNode {id: 'v2', name: 'Node 2'})
    MERGE (n1)-[:CONNECTED_TO]->(n2)
    """
    db.execute_write(setup_query, {}, action="TEST_SETUP")

    # 2. Call API (filter to our test nodes to avoid noise from existing DB data)
    response = client.get("/api/graph?label=VisNode")
    
    # 3. Assertions
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    
    assert "nodes" in data
    assert "edges" in data
    
    # Find our nodes
    nodes = data["nodes"]
    ids = [n["data"]["id"] for n in nodes]
    assert "v1" in ids
    assert "v2" in ids
    
    # Check Edge
    edges = data["edges"]
    assert len(edges) >= 1
    # Check structure (Cytoscape assumes source/target in data)
    assert "source" in edges[0]["data"]
    assert "target" in edges[0]["data"]
    
    # Cleanup
    db.execute_write("MATCH (n:VisNode) DETACH DELETE n", {}, action="CLEANUP")
