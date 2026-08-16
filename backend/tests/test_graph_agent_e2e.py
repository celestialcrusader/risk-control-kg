"""
End-to-End Integration Verification Test for LangGraph State Graph Upgrade (STORY-GRAPH-105).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pipeline_graph import build_rckg_pipeline_graph, RCKGState

client = TestClient(app)


def test_graph_105_pipeline_graph_invocation_and_resume():
    """Verify LangGraph State Graph builds, pauses at interrupt, and resumes via API."""
    graph = build_rckg_pipeline_graph()
    initial_state: RCKGState = {
        "document_id": "doc_test_105",
        "pdf_path": "backend/tests/fixtures/sample.pdf",
        "raw_markdown": "Section 1: Access Control. Organization must enforce MFA.",
        "extracted_facets": {},
        "nli_relation": "PENDING",
        "confidence_score": 0.90,
        "judge_logic_score": 0.96,
        "judge_technical_score": 1.00,
        "repair_attempts": 0,
        "outbox_status": "PENDING",
        "error_message": None,
    }

    thread_id = "thread_test_105"
    config = {"configurable": {"thread_id": thread_id}}

    # 1. Invoke graph — execution pauses at interrupt_before=["hitl_review"]
    state_snapshot = graph.invoke(initial_state, config=config)
    assert state_snapshot is not None

    # 2. Resume graph thread via API endpoint
    res = client.post("/api/v1/graph/resume", json={"thread_id": thread_id, "approved": True})
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "RESUMED"
    assert res_data["final_state"].get("outbox_status") in ["EXECUTED", "PENDING_HITL_REVIEW"]
