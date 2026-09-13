import pytest
from fastapi.testclient import TestClient
import sys
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Database

client = TestClient(app)

# Dummy simple CSV
CSV_CONTENT = "nist_ctrl_id,ctrl_grp,ctrl_txt\nAC-99,Test Group,Description of test control"

@pytest.fixture(scope="module")
def db_conn():
    db = Database()
    try:
        db.connect()
        db.apply_constraints()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")
        return None
    yield db
    db.close()
    
    # Clean up uploads
    if os.path.exists("/home/rckg/coding/rckg/data/uploads/test.csv"):
        os.remove("/home/rckg/coding/rckg/data/uploads/test.csv")

def test_ingest_api(db_conn):
    if not db_conn:
        return

    # 1. Create dummy file
    with open("test.csv", "w", encoding='cp1252') as f:
        f.write(CSV_CONTENT)
        
    try:
        with open("test.csv", "rb") as f:
            # 2. Call API
            response = client.post("/api/ingest/", files={"file": ("test.csv", f, "text/csv")})
            
        # 3. Assertions
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        print(f"DEBUG: Response Data: {data}")
        assert data["status"] == "success"
        assert data["filename"] == "test.csv"
        assert data["controls_processed"] > 0, "No controls were processed!"
        
        # 4. Verify in DB
        # AC-99 should exist
        all_nodes = db_conn.execute_read("MATCH (n) RETURN labels(n), n.id, n.title")
        print(f"DEBUG: All Nodes: {all_nodes}")
        
        res = db_conn.execute_read("MATCH (r:Requirement {id: 'AC-99'})<-[:DEFINES]-(f:Framework) RETURN r")
        assert len(res) == 1
        assert "description" in res[0]['r']['description'].lower()
        
    finally:
        if os.path.exists("test.csv"):
            os.remove("test.csv")
            
    # Cleanup DB
    db_conn.execute_write("MATCH (r:Requirement {id: 'AC-99'}) DETACH DELETE r", {}, action="CLEANUP")
