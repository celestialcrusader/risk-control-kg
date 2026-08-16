"""
TDD Unit/Integration Test for STORY-GRAPH-103: State Graph Nodes Construction.
"""

import pytest


def test_graph_103_node_functions():
    """Verify node functions exist and update state correctly."""
    from app.services.pipeline_graph import (
        parse_pdf_node,
        extract_facets_node,
        nli_classify_node,
        dual_judge_eval_node,
        repair_loop_node,
        commit_outbox_node,
        hitl_review_node,
        RCKGState,
    )

    state: RCKGState = {
        "document_id": "doc_103",
        "pdf_path": "backend/tests/fixtures/sample.pdf",
        "raw_markdown": "Section 1 Access Control MFA",
        "extracted_facets": {"action_verb": "limit", "subject_noun": "access"},
        "nli_relation": "PENDING",
        "confidence_score": 0.90,
        "judge_logic_score": 0.80,
        "judge_technical_score": 1.00,
        "repair_attempts": 0,
        "outbox_status": "PENDING",
        "error_message": None,
    }

    # Test parse_pdf_node fallback
    pdf_res = parse_pdf_node(state)
    assert "raw_markdown" in pdf_res

    # Test extract_facets_node
    facets_res = extract_facets_node(state)
    assert "extracted_facets" in facets_res

    # Test nli_classify_node
    nli_res = nli_classify_node(state)
    assert "nli_relation" in nli_res

    # Test dual_judge_eval_node
    judge_res = dual_judge_eval_node(state)
    assert "judge_logic_score" in judge_res
    assert "judge_technical_score" in judge_res

    # Test repair_loop_node
    repair_res = repair_loop_node(state)
    assert repair_res["repair_attempts"] == 1

    # Test commit_outbox_node
    commit_res = commit_outbox_node(state)
    assert commit_res["outbox_status"] == "EXECUTED"

    # Test hitl_review_node
    hitl_res = hitl_review_node(state)
    assert hitl_res["outbox_status"] == "PENDING_HITL_REVIEW"
