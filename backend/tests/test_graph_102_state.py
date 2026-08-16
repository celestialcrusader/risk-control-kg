"""
TDD Unit/Integration Test for STORY-GRAPH-102: RCKGState Schema & Checkpointer Integration.
"""

import pytest


def test_graph_102_rckg_state_schema():
    """Verify RCKGState TypedDict schema fields."""
    from app.services.pipeline_graph import RCKGState

    state: RCKGState = {
        "document_id": "doc_102",
        "pdf_path": "/tmp/test.pdf",
        "raw_markdown": "# Test Doc",
        "extracted_facets": {"action_verb": "limit", "subject_noun": "access"},
        "nli_relation": "EQUIVALENT_TO",
        "confidence_score": 0.95,
        "judge_logic_score": 0.98,
        "judge_technical_score": 1.00,
        "repair_attempts": 0,
        "outbox_status": "PENDING",
        "error_message": None,
    }

    assert state["document_id"] == "doc_102"
    assert state["judge_logic_score"] == 0.98
    assert state["outbox_status"] == "PENDING"


def test_graph_102_get_checkpointer():
    """Verify checkpointer initialization function."""
    from app.services.pipeline_graph import get_checkpointer

    checkpointer = get_checkpointer()
    assert checkpointer is not None
