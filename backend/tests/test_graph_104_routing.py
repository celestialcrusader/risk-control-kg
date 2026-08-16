"""
TDD Unit/Integration Test for STORY-GRAPH-104: Dynamic Routing Edges & HITL Interrupt Breakpoint.
"""

import pytest


def test_graph_104_routing_logic():
    """Verify route_after_judge conditional routing logic."""
    from app.services.pipeline_graph import route_after_judge, RCKGState

    state_approved: RCKGState = {
        "document_id": "doc_approved",
        "pdf_path": "",
        "raw_markdown": "",
        "extracted_facets": {},
        "nli_relation": "SATISFIES",
        "confidence_score": 0.95,
        "judge_logic_score": 0.96,
        "judge_technical_score": 1.00,
        "repair_attempts": 0,
        "outbox_status": "PENDING",
        "error_message": None,
    }
    assert route_after_judge(state_approved) == "commit_outbox"

    state_repair: RCKGState = {
        **state_approved,
        "judge_logic_score": 0.80,
        "repair_attempts": 1,
    }
    assert route_after_judge(state_repair) == "repair_loop"

    state_hitl: RCKGState = {
        **state_approved,
        "judge_logic_score": 0.80,
        "repair_attempts": 3,
    }
    assert route_after_judge(state_hitl) == "hitl_review"


def test_graph_104_build_pipeline_graph():
    """Verify state graph builds and compiles successfully."""
    from app.services.pipeline_graph import build_rckg_pipeline_graph

    graph = build_rckg_pipeline_graph()
    assert graph is not None
