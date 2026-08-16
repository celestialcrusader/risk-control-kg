"""
TDD Unit Test for CFIX-300: Governance Engine Pipeline Integration with MemgraphService.
"""

from unittest.mock import MagicMock, patch
import pytest
from app.services.memgraph_service import MemgraphService
from app.services.graph_compiler import ClosedSetPrimitive, GraphMutationDiff
from app.services.governance_engine import GraphRegressionError


def test_governance_blocks_golden_assertion_revert():
    """Verify MemgraphService raises GraphRegressionError when attempting to deprecate a pinned Golden Assertion."""
    mock_db = MagicMock()
    service = MemgraphService(db_session=mock_db, memgraph_connection=MagicMock())
    
    # Register golden assertion in governance engine
    service.governance_engine.register_golden_assertion("OBJ-100", "OBL-100", "EQUIVALENT_TO")

    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.DEPRECATE_EDGE,
        source_node_id="OBJ-100",
        target_node_id="OBL-100",
        set_theory_relation="EQUIVALENT_TO",
        confidence_score=0.95,
    )

    with pytest.raises(GraphRegressionError, match="Golden Assertion regression detected"):
        service.enqueue_and_execute(mutation)


def test_governance_blocks_ontology_mutation():
    """Verify ontology mutations are blocked with GOVERNANCE_BLOCKED status."""
    mock_db = MagicMock()
    service = MemgraphService(db_session=mock_db, memgraph_connection=MagicMock())

    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_NODE,
        source_node_id="NODE-1",
        target_node_id="NODE-1",
        confidence_score=0.95,
        metadata={"action": "ALTER_ONTOLOGY_SCHEMA"},
    )

    entry = service.enqueue_and_execute(mutation)
    assert entry.status == "GOVERNANCE_BLOCKED"
