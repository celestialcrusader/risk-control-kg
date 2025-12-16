import pytest
import sys
import os
from neo4j.exceptions import ClientError

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

def test_read_only_enforcement(db):
    """
    TDD Mandate: Test that read-only client prevents write operations.
    """
    if not db:
        return

    # Method doesn't exist yet -> AttributeError (RED)
    
    # 1. Simple Read should work
    result = db.execute_read("RETURN 1 as val")
    assert result[0]['val'] == 1
    
    # 2. Write should fail
    # We attempt to write inside a read transaction
    with pytest.raises(ClientError) as excinfo:
        db.execute_read("CREATE (n:Risk {name: 'Should Fail'})")
    
    # Neo4j throws "Writing in read access mode not allowed."
    assert "access mode" in str(excinfo.value).lower() or "read" in str(excinfo.value).lower()
