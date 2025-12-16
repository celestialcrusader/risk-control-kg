import pytest
import sys
import os
import uuid
from neo4j.exceptions import ClientError, ConstraintError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Database

@pytest.fixture(scope="module")
def db():
    db = Database()
    try:
        db.connect()
        # Verify connection
        db.query("RETURN 1")
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")
        return None
    
    yield db
    db.close()

def test_ontology_uniqueness_constraints(db):
    """
    TDD Mandate: Verify that creating duplicate nodes violates constraints.
    We need unique IDs for Risk, Control, and Framework.
    """
    if not db:
        return
        
    # Ensure constraints are applied (or are SUPPOSED to be)
    db.apply_constraints()
    
    unique_id = str(uuid.uuid4())
    
    # 1. Create first node
    db.query("CREATE (n:Risk {id: $id, name: 'Risk 1'})", {"id": unique_id})
    
    # 2. Try to create duplicate - SHOULD FAIL if constraints exist
    try:
        with pytest.raises(ClientError) as excinfo:
            db.query("CREATE (n:Risk {id: $id, name: 'Risk 2'})", {"id": unique_id})
        
        # Check if it is specifically a ConstraintValidationFailed error
        # exact error code depends on Neo4j version, usually Neo.ClientError.Schema.ConstraintValidationFailed
        assert "ConstraintValidationFailed" in excinfo.value.code or "ConstraintViolation" in str(excinfo.value)
        
    finally:
        # Cleanup
        db.query("MATCH (n:Risk {id: $id}) DETACH DELETE n", {"id": unique_id})

def test_mandatory_labels_and_props(db):
    """
    TDD Mandate: Verify we can store core relationships.
    """
    if not db:
        return

    # Just a smoke test for the relationship query logic
    risk_id = str(uuid.uuid4())
    ctrl_id = str(uuid.uuid4())
    
    db.query(
        """
        CREATE (r:Risk {id: $rid})
        CREATE (c:Control {id: $cid})
        CREATE (c)-[:MITIGATES]->(r)
        """, 
        {"rid": risk_id, "cid": ctrl_id}
    )
    
    result = db.query(
        "MATCH (c:Control)-[:MITIGATES]->(r:Risk) WHERE c.id = $cid RETURN r.id as risk_id",
        {"cid": ctrl_id}
    )
    assert len(result) == 1
    assert result[0]['risk_id'] == risk_id
    
    # Cleanup
    db.query("MATCH (n) WHERE n.id IN [$rid, $cid] DETACH DELETE n", {"rid": risk_id, "cid": ctrl_id})
