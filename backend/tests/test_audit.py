import pytest
import sys
import os
import uuid
from neo4j.time import DateTime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Database

@pytest.fixture(scope="module")
def db():
    db = Database()
    try:
        db.connect()
    except Exception:
        pytest.skip("Neo4j not available")
        return None
    yield db
    db.close()

def test_audit_logging_mechanism(db):
    """
    TDD Mandate: Assert that every successful write creates an immutable audit log entry.
    """
    if not db:
        return

    # Define inputs
    risk_id = str(uuid.uuid4())
    user_id = "user_123"
    action = "CREATE_RISK"
    
    query = "CREATE (n:Risk {id: $id, name: 'Audit Risk'})"
    params = {"id": risk_id}
    
    # 1. Execute write with audit (Method to be implemented)
    # If this method doesn't exist, it will raise AttributeError (RED)
    db.execute_write(query, params, user=user_id, action=action)
    
    # 2. Verify AuditLog node exists
    # We assume AuditLog is linked to the created node, OR just exists with properties
    # Let's simple check for AuditLog with matching action and user
    
    audit_check = """
    MATCH (a:AuditLog)
    WHERE a.user = $user AND a.action = $action
    RETURN a
    """
    
    results = db.query(audit_check, {"user": user_id, "action": action})
    
    assert len(results) > 0
    log_entry = results[0]['a']
    assert log_entry['user'] == user_id
    assert log_entry['action'] == action
    assert 'timestamp' in log_entry
    
    # Cleanup
    db.query("MATCH (n:Risk {id: $id}) DETACH DELETE n", {"id": risk_id})
    db.query("MATCH (a:AuditLog {action: $action}) DETACH DELETE a", {"action": action})
