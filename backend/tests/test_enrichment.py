import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Database
from app.core.knowledge import KnowledgeExtractor, ExtractedKnowledge, ExtractedEntity
from app.ingest.enricher import GraphEnricher
from app.core.oscal import Control, Property

@pytest.fixture(scope="module")
def db():
    db = Database()
    try:
        db.connect()
        db.apply_constraints()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")
        return None
    yield db
    db.close()

def test_graph_enrichment(db):
    if not db:
        return

    # 1. Setup Data
    # Create the requirement first
    req_id = "req-test-enrich"
    db.execute_write(
        "MERGE (r:Requirement {id: $id})", 
        {"id": req_id}, 
        action="TEST_SETUP"
    )
    
    control = Control(id=req_id, title="Test Req", props=[Property(name="description", value="...")])
    
    # 2. Mock Extractor
    mock_extractor = MagicMock(spec=KnowledgeExtractor)
    mock_extractor.extract_from_control.return_value = ExtractedKnowledge(
        entities=[
            ExtractedEntity(name="Data Leakage", type="Risk", description="Leak of data"),
            ExtractedEntity(name="Encryption", type="Control", description="Cipher stuff")
        ],
        summary="Summary"
    )
    
    # 3. Enrich
    enricher = GraphEnricher(db, mock_extractor)
    enricher.enrich_control(control)
    
    # 4. Verify Risk
    risks = db.execute_read(
        "MATCH (r:Risk {name: 'Data Leakage'})-[:MENTIONED_IN]->(req:Requirement {id: $id}) RETURN r",
        {"id": req_id}
    )
    assert len(risks) == 1
    assert risks[0]['r']['description'] == "Leak of data"
    
    # 5. Verify Control (should be a :Control node linked to Requirement)
    # Note: :Control label is also used for OSCAL Control, but here it's an entity type.
    # Our Ontology allows this overlapping, as it's a semantic tagging.
    ctrls = db.execute_read(
        "MATCH (c:Control {name: 'Encryption'})-[:MENTIONED_IN]->(req:Requirement {id: $id}) RETURN c",
        {"id": req_id}
    )
    assert len(ctrls) == 1
    
    # Cleanup
    db.execute_write("MATCH (n:Requirement {id: $id}) DETACH DELETE n", {"id": req_id}, action="CLEANUP")
    db.execute_write("MATCH (n:Risk {name: 'Data Leakage'}) DETACH DELETE n", {}, action="CLEANUP")
    db.execute_write("MATCH (n:Control {name: 'Encryption'}) DETACH DELETE n", {}, action="CLEANUP")
