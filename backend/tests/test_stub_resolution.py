"""
Unit Tests for Stub Node Resolution & Graph Self-Healing Engine (STORY-FOUNDATION-106).
"""

import pytest
from app.services.memgraph_service import MemgraphService, GraphMutationDiff, ClosedSetPrimitive


def test_stub_node_generation_and_self_healing():
    """Verify stub node creation and late-binding resolution logic."""
    service = MemgraphService()

    # Step 1: Create a Stub Node representing an unresolved crosswalk target
    stub_diff = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_NODE,
        source_node_id="NIST-AC-2",
        target_node_id="NIST-AC-2",
        confidence_score=0.5,
        metadata={
            "label": "FrameworkControlObj",
            "framework_obj_id": "NIST-AC-2",
            "framework_name": "NIST SP 800-53",
            "objective_name": "NIST-AC-2 (Stub Reference)",
            "objective_text": "",
            "node_status": "STUB_UNRESOLVED",
        },
    )
    cypher_stub, params_stub = service.render_cypher_and_params(stub_diff)
    assert params_stub["node_status"] == "STUB_UNRESOLVED"
    assert "STUB_UNRESOLVED" in cypher_stub

    # Step 2: Later Ingestion resolves the Stub Node with full metadata
    resolved_diff = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_NODE,
        source_node_id="NIST-AC-2",
        target_node_id="NIST-AC-2",
        confidence_score=1.0,
        metadata={
            "label": "FrameworkControlObj",
            "framework_obj_id": "NIST-AC-2",
            "framework_name": "NIST SP 800-53",
            "objective_name": "Account Management",
            "objective_text": "The organization manages information system accounts.",
            "node_status": "RESOLVED",
        },
    )
    cypher_resolved, params_resolved = service.render_cypher_and_params(resolved_diff)
    assert params_resolved["objective_name"] == "Account Management"
    assert params_resolved["node_status"] == "RESOLVED"

