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

def test_approvals_lifecycle(db):
    if not db:
        return

    # 1. Setup Data - Create a DRAFT node
    setup_query = """
    MERGE (r:Risk {name: 'Draft Risk', description: 'Pending review', status: 'DRAFT'})
    RETURN elementId(r) as eid
    """
    res = db.execute_write(setup_query, {}, action="TEST_SETUP")
    eid = res[0]['eid']

    try:
        # 2. GET /api/approvals - Verify it appears
        response = client.get("/api/approvals")
        assert response.status_code == 200
        data = response.json()
        
        # Check if our draft is in the list
        found = next((item for item in data if item['id'] == eid), None)
        assert found is not None
        assert found['properties']['status'] == 'DRAFT'
        
        # 3. PUT /api/approvals/{id} - Update Description
        update_payload = {"description": "Updated Description"}
        resp_update = client.put(f"/api/approvals/{eid}", json=update_payload)
        assert resp_update.status_code == 200
        
        # Verify update in DB
        check_query = f"MATCH (n) WHERE elementId(n) = '{eid}' RETURN n.description as desc"
        res_check = db.execute_read(check_query)
        assert res_check[0]['desc'] == "Updated Description"
        
        # 4. POST /api/approvals/{id}/approve - Approve
        resp_approve = client.post(f"/api/approvals/{eid}/approve")
        assert resp_approve.status_code == 200
        
        # Verify status change
        status_check = f"MATCH (n) WHERE elementId(n) = '{eid}' RETURN n.status as status"
        res_status = db.execute_read(status_check)
        assert res_status[0]['status'] == "APPROVED"
        
        # 5. GET /api/approvals - Verify it GONE from list
        response_final = client.get("/api/approvals")
        data_final = response_final.json()
        found_final = next((item for item in data_final if item['id'] == eid), None)
        assert found_final is None

    finally:
        # Cleanup
        db.execute_write(f"MATCH (n) WHERE elementId(n) = '{eid}' DETACH DELETE n", {}, action="CLEANUP")
