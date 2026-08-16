"""
Unit tests for FIX-306 (Semantic Similarity in Graphiti Change Detector).
"""

import pytest
from app.services.graphiti_engine import GraphitiSemanticChangeDetector


def test_graphiti_ignores_minor_whitespace_and_formatting_changes():
    """
    Test that GraphitiSemanticChangeDetector ignores minor whitespace/formatting changes (high similarity >= 0.90) and does not emit SUPERSEDE_NODE (FIX-306).
    """
    detector = GraphitiSemanticChangeDetector()

    existing_nodes = [
        {"node_id": "OBL-01", "content": "Multi-factor authentication must be enforced for administrative access."}
    ]

    # New clause with minor whitespace formatting change only
    new_clauses = [
        {"target_node_id": "OBL-01", "clause_id": "CLS-01", "content": "Multi-factor authentication  must be enforced   for administrative access. "}
    ]

    result = detector.compute_mutation_diff(existing_nodes, new_clauses)

    # Minor formatting change should NOT trigger SUPERSEDE_NODE
    assert len(result.mutations) == 0, f"Expected 0 mutations for minor whitespace change, got: {result.mutations}"


def test_graphiti_emits_supersede_for_meaningful_semantic_change():
    """
    Test that GraphitiSemanticChangeDetector emits SUPERSEDE_NODE when semantic content changes significantly (similarity < 0.90) (FIX-306).
    """
    detector = GraphitiSemanticChangeDetector()

    existing_nodes = [
        {"node_id": "OBL-01", "content": "Multi-factor authentication must be enforced for administrative access."}
    ]

    # New clause with significant policy change (passkeys mandatory)
    new_clauses = [
        {"target_node_id": "OBL-01", "clause_id": "CLS-02", "content": "FIDO2 hardware passkeys and biometric authentication must be mandatory for all database administrators."}
    ]

    result = detector.compute_mutation_diff(existing_nodes, new_clauses)

    assert len(result.mutations) == 1
    assert result.mutations[0]["action"] == "SUPERSEDE_NODE"
    assert result.mutations[0]["target_node_id"] == "OBL-01"
