"""
TDD Tests for Parameterized Cypher Builders and Dual-Write Atomicity (RCKG-104).
"""

import pytest
from backend.app.graph.rckg_queries import RCKGCypherBuilder
from backend.app.services.graph_compiler import ClosedSetPrimitive, GraphMutationDiff


def test_cypher_builder_supersede_node():
    """AC-2: SUPERSEDE_NODE Cypher template sets valid_to and links old node with [:SUPERSEDES]."""
    cypher = RCKGCypherBuilder.build_supersede_node_cypher()
    assert "valid_to" in cypher
    assert ":SUPERSEDES" in cypher
    assert "$old_node_id" in cypher
    assert "$new_node_id" in cypher


def test_cypher_builder_create_gap():
    """AC-1: CREATE_GAP Cypher template creates Gap node and links source and target."""
    cypher = RCKGCypherBuilder.build_create_gap_mutation_cypher()
    assert "MERGE (g:Gap" in cypher or "CREATE (g:Gap" in cypher
    assert "DIRECT_GAP_TO" in cypher or "HAS_GAP" in cypher
    assert "$source_node_id" in cypher
    assert "$target_node_id" in cypher


def test_cypher_builder_reclassify_and_deprecate_edge():
    """AC-1: Cypher templates for edge reclassification and deprecation."""
    reclassify_cypher = RCKGCypherBuilder.build_reclassify_edge_cypher()
    assert "set_theory_relation" in reclassify_cypher

    deprecate_cypher = RCKGCypherBuilder.build_deprecate_edge_cypher()
    assert "status = 'DEPRECATED'" in deprecate_cypher or "DEPRECATED" in deprecate_cypher


def test_memgraph_service_execute_mutation(db_session):
    """AC-1 & AC-3: MemgraphService maps GraphMutationDiff to parameterized execution and outbox logging."""
    from backend.app.services.memgraph_service import MemgraphService

    service = MemgraphService(db_session=db_session)
    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_EDGE,
        source_node_id="OBJ-001",
        target_node_id="OBL-001",
        relationship_type="SATISFIES",
        set_theory_relation="EQUIVALENT_TO",
        confidence_score=0.95,
    )

    outbox_entry = service.enqueue_and_execute(mutation)
    assert outbox_entry is not None
    assert outbox_entry.status == "PROCESSED"
    assert outbox_entry.primitive == "ADD_EDGE"


def test_memgraph_service_supersede_node_execution(db_session):
    """AC-2 & AC-4: Test dual-write atomicity for SUPERSEDE_NODE primitive."""
    from backend.app.services.memgraph_service import MemgraphService

    service = MemgraphService(db_session=db_session)
    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.SUPERSEDE_NODE,
        source_node_id="OBJ-OLD-01",
        target_node_id="OBJ-NEW-01",
        confidence_score=1.0,
        metadata={"reason": "Policy version upgrade"},
    )

    outbox_entry = service.enqueue_and_execute(mutation)
    assert outbox_entry.status == "PROCESSED"
    assert outbox_entry.payload["target_node_id"] == "OBJ-NEW-01"
