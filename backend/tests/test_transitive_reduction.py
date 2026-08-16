"""
Unit Tests for Transitive Reduction & Graph Pruning Engine (STORY-MAINT-102).
"""

import pytest
from app.services.transitive_reduction import TransitiveReductionEngine, GraphEdge


def test_transitive_reduction_identifies_redundant_triangles():
    """Verify engine detects redundant transitive edges when direct edge exists."""
    engine = TransitiveReductionEngine()

    # Graph Topology:
    # A -> B (0.90)
    # B -> C (0.90)
    # A -> C (0.75 - Indirect Inferred / Weaker)
    # Direct A -> C (0.95 - Golden)
    edges = [
        GraphEdge(source_id="A", target_id="B", relation="EQUIVALENT_TO", confidence=0.90, is_golden=True),
        GraphEdge(source_id="B", target_id="C", relation="EQUIVALENT_TO", confidence=0.90, is_golden=True),
        GraphEdge(source_id="A", target_id="C", relation="EQUIVALENT_TO", confidence=0.75, is_golden=False),
    ]

    prune_plan = engine.identify_prunable_edges(edges)

    assert len(prune_plan["redundant_edges"]) == 1
    redundant = prune_plan["redundant_edges"][0]
    assert redundant.source_id == "A"
    assert redundant.target_id == "C"
    assert redundant.is_golden is False


def test_transitive_shortcut_collapse():
    """Verify shortcut collapse generates direct EQUIVALENT_TO edge when chain is confident."""
    engine = TransitiveReductionEngine(shortcut_threshold=0.80)

    edges = [
        GraphEdge(source_id="MAS-6.1", target_id="NIST-AC-2", relation="EQUIVALENT_TO", confidence=0.95),
        GraphEdge(source_id="NIST-AC-2", target_id="CIS-5.1", relation="EQUIVALENT_TO", confidence=0.90),
    ]

    shortcuts = engine.generate_transitive_shortcuts(edges)

    assert len(shortcuts) == 1
    sc = shortcuts[0]
    assert sc.source_id == "MAS-6.1"
    assert sc.target_id == "CIS-5.1"
    assert sc.relation == "EQUIVALENT_TO"
    assert sc.confidence == pytest.approx(0.855, 0.01)  # 0.95 * 0.90
