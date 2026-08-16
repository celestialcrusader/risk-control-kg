"""
TDD Unit/Integration Test for REMED-102: Synchronous Dual-Judge Gating & GraphOutboxLog Audit Columns.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.models.rckg_nodes import GraphOutboxLog
from app.services.memgraph_service import MemgraphService
from app.services.graph_compiler import GraphMutationDiff, ClosedSetPrimitive
from app.services.dual_judge_async import DualJudgeAuditResult


def test_remed_102_graph_outbox_log_columns():
    """Verify GraphOutboxLog model has judge_logic_score and judge_technical_score columns."""
    outbox = GraphOutboxLog()
    assert hasattr(outbox, "judge_logic_score")
    assert hasattr(outbox, "judge_technical_score")


@patch("app.services.dual_judge_async.AsynchronousDualJudgeService.evaluate_single")
def test_remed_102_enqueue_and_execute_holds_low_judge_score(mock_evaluate_single):
    """Verify mutation with logic_score < 0.95 sets status PENDING_HITL_REVIEW and skips Memgraph."""
    mock_evaluate_single.return_value = DualJudgeAuditResult(
        source_id="OBL-001",
        target_id="OBJ-001",
        logic_judge_score=0.80,  # Below 0.95 threshold
        technical_judge_score=1.00,
        verdict="REJECTED",
        rationale="Logic confidence too low",
    )

    mock_db = MagicMock()
    mock_conn = MagicMock()
    service = MemgraphService(db_session=mock_db, memgraph_connection=mock_conn)

    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_EDGE,
        source_node_id="OBL-001",
        target_node_id="OBJ-001",
        confidence_score=0.85,
        set_theory_relation="EQUIVALENT_TO",
    )

    outbox_entry = service.enqueue_and_execute(mutation)

    assert outbox_entry.status == "PENDING_HITL_REVIEW"
    assert outbox_entry.judge_logic_score == 0.80
    assert outbox_entry.judge_technical_score == 1.00
    # Memgraph cursor execute should NOT have been called
    mock_conn.cursor.return_value.execute.assert_not_called()


@patch("app.services.dual_judge_async.AsynchronousDualJudgeService.evaluate_single")
def test_remed_102_enqueue_and_execute_holds_failing_judge_llm(mock_evaluate_single):
    """Verify failing/unavailable Judge LLM sets status PENDING_JUDGE_REVIEW and skips Memgraph."""
    mock_evaluate_single.side_effect = RuntimeError("LLM Judge offline")

    mock_db = MagicMock()
    mock_conn = MagicMock()
    service = MemgraphService(db_session=mock_db, memgraph_connection=mock_conn)

    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_EDGE,
        source_node_id="OBL-002",
        target_node_id="OBJ-002",
        confidence_score=0.85,
        set_theory_relation="EQUIVALENT_TO",
    )

    outbox_entry = service.enqueue_and_execute(mutation)

    assert outbox_entry.status == "PENDING_JUDGE_REVIEW"
    mock_conn.cursor.return_value.execute.assert_not_called()
