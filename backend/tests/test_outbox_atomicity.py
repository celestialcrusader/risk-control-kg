"""
Unit tests for FIX-201 (Transaction Outbox Atomicity in MemgraphService) & REMED-102 (Dual-Judge Outbox Gate).
"""

from unittest.mock import patch, MagicMock
import pytest
from app.services.memgraph_service import MemgraphService
from app.services.graph_compiler import ClosedSetPrimitive, GraphMutationDiff
from app.services.dual_judge_async import DualJudgeAuditResult


def test_enqueue_and_execute_atomicity_memgraph_failure_causes_rollback():
    """
    Test that Memgraph execution failure triggers PostgreSQL rollback and does NOT commit PENDING entry (FIX-201).
    """
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Memgraph connection timeout")

    service = MemgraphService(db_session=mock_db, memgraph_connection=mock_conn)

    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_NODE,
        source_node_id="OBL-TEST-001",
        target_node_id="OBL-TEST-001",
        confidence_score=0.95,
    )

    mock_judge = MagicMock()
    mock_judge.evaluate_single.return_value = DualJudgeAuditResult(
        source_id="OBL-TEST-001",
        target_id="OBL-TEST-001",
        logic_judge_score=1.0,
        technical_judge_score=1.0,
        verdict="APPROVED",
    )

    with patch("app.services.dual_judge_async.AsynchronousDualJudgeService", return_value=mock_judge):
        with pytest.raises(Exception, match="Memgraph connection timeout"):
            service.enqueue_and_execute(mutation)

    # Verify PostgreSQL rollback was called when Memgraph failed
    mock_db.rollback.assert_called_once()
    # Verify DB commit was NOT called before Memgraph execution
    assert mock_db.commit.call_count == 0


def test_enqueue_and_execute_success_sets_executed_and_commits():
    """
    Test that successful execution sets status='EXECUTED' and commits DB (FIX-201).
    """
    mock_db = MagicMock()
    mock_conn = MagicMock()

    service = MemgraphService(db_session=mock_db, memgraph_connection=mock_conn)

    mutation = GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_NODE,
        source_node_id="OBL-TEST-002",
        target_node_id="OBL-TEST-002",
        confidence_score=0.95,
    )

    mock_judge = MagicMock()
    mock_judge.evaluate_single.return_value = DualJudgeAuditResult(
        source_id="OBL-TEST-002",
        target_id="OBL-TEST-002",
        logic_judge_score=1.0,
        technical_judge_score=1.0,
        verdict="APPROVED",
    )

    with patch("app.services.dual_judge_async.AsynchronousDualJudgeService", return_value=mock_judge):
        entry = service.enqueue_and_execute(mutation)

    assert entry.status == "EXECUTED"
    # Single atomic commit at the end after Memgraph success
    mock_db.commit.assert_called_once()
