"""
Unit tests for FIX-203 (Prevent NO_RELATIONSHIP Edge Pollution in Graph Compiler).
"""

import pytest
from app.services.graph_compiler import RuleBasedGraphCompiler


def test_graph_compiler_returns_empty_when_no_relationship():
    """
    Test that RuleBasedGraphCompiler returns empty mutations list (no ADD_EDGE with NO_RELATIONSHIP) when cosine similarity is between 0.30 and 0.70 (FIX-203).
    """
    compiler = RuleBasedGraphCompiler()

    source_node = {
        "node_id": "CO-001",
        "action_verb": "review",
        "subject_noun": "logs",
    }
    target_node = {
        "node_id": "OBL-999",
        "action_verb": "encrypt",
        "subject_noun": "passwords",
    }

    # Similarity 0.50 does not satisfy relationship criteria and should NOT generate NO_RELATIONSHIP edge mutation
    mutations = compiler.compile_mutation(source_node, target_node, cosine_sim=0.50)

    no_rel_edges = [m for m in mutations if m.relationship_type == "NO_RELATIONSHIP"]
    assert len(no_rel_edges) == 0, f"Expected 0 NO_RELATIONSHIP edge mutations, got {len(no_rel_edges)}: {no_rel_edges}"
    assert len(mutations) == 0, f"Expected 0 total mutations for moderate non-matching similarity, got {len(mutations)}: {mutations}"
