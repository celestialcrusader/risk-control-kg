"""
TDD Tests for Phase 2 Graphiti Incremental Semantic Change Detector & Mutation Diff Engine (RCKG-401).
"""

import pytest
from app.services.graphiti_engine import (
    GraphitiSemanticChangeDetector,
    GraphitiDiffResult,
)


@pytest.fixture
def change_detector():
    return GraphitiSemanticChangeDetector(current_release="v1.0.0")


def test_graphiti_incremental_change_detection_and_supersede_diff(change_detector):
    """AC-1, AC-2, AC-3: Detects modified clauses, generates SUPERSEDE_NODE diffs, and increments release tag."""
    existing_nodes = [
        {"node_id": "OBL-101", "content": "Passwords must be at least 8 characters.", "version": "v1.0.0"},
        {"node_id": "OBL-102", "content": "Data backups must occur weekly.", "version": "v1.0.0"},
    ]

    new_clauses = [
        {"clause_id": "CLS-NEW-01", "content": "Passwords must be at least 16 characters with MFA enabled.", "target_node_id": "OBL-101"},
        {"clause_id": "CLS-NEW-02", "content": "Data backups must occur weekly.", "target_node_id": "OBL-102"},
    ]

    diff_result = change_detector.compute_mutation_diff(existing_nodes, new_clauses)

    assert isinstance(diff_result, GraphitiDiffResult)
    assert diff_result.next_release == "v1.1.0 [GRAPHITI_DIFF]"
    assert len(diff_result.mutations) == 1
    mutation = diff_result.mutations[0]
    assert mutation["action"] == "SUPERSEDE_NODE"
    assert mutation["target_node_id"] == "OBL-101"
    assert "valid_to" in mutation
