import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ingest.loader import OSCALGraphLoader
from app.ingest.adapters.csa_ccm import CSACCMAdapter
from app.ingest.adapters.nist_csv import NISTCSVAdapter
from app.core.database import Database

SAMPLE_CCM_PATH = "data/raw/oscal/primary-dataset.json"
SAMPLE_NIST_PATH = "data/raw/csv/sp800-53r5-control-catalog.csv"

@pytest.fixture(scope="module")
def db():
    db = Database()
    try:
        db.connect()
        # Ensure constraints are applied for the test
        db.apply_constraints()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")
        return None
    yield db
    db.close()

@pytest.mark.skipif(not os.path.exists(SAMPLE_CCM_PATH), reason="CCM Sample not found")
def test_loader_ccm_ingestion(db):
    if not db:
        return
        
    # 1. Adapt
    adapter = CSACCMAdapter()
    catalog = adapter.to_oscal(SAMPLE_CCM_PATH)
    
    # 2. Load
    loader = OSCALGraphLoader(db)
    loader.load_catalog(catalog)
    
    # 3. Verify Framework
    res = db.execute_read("MATCH (f:Framework {id: 'CLOUD-CONTROLS-MATRIX'}) RETURN f")
    assert len(res) == 1
    
    # 4. Verify Requirement (e.g., A&A-01)
    res = db.execute_read("MATCH (r:Requirement {id: 'A&A-01'})<-[:DEFINES]-(f:Framework) RETURN r")
    assert len(res) == 1
    assert res[0]['r']['title'] == "Audit and Assurance Policy and Procedures"

@pytest.mark.skipif(not os.path.exists(SAMPLE_NIST_PATH), reason="NIST Sample not found")
def test_loader_nist_ingestion(db):
    if not db:
        return
        
    # 1. Adapt
    adapter = NISTCSVAdapter()
    catalog = adapter.to_oscal(SAMPLE_NIST_PATH)
    
    # 2. Load
    loader = OSCALGraphLoader(db)
    loader.load_catalog(catalog)
    
    # 3. Verify Framework
    res = db.execute_read("MATCH (f:Framework {id: 'NIST-SP-800-53-REV-5'}) RETURN f")
    assert len(res) == 1
    
    # 4. Verify Requirement (e.g., AC-1)
    res = db.execute_read("MATCH (r:Requirement {id: 'AC-1'})<-[:DEFINES]-(f:Framework) RETURN r")
    assert len(res) == 1
    assert "access control policy" in res[0]['r']['description']
