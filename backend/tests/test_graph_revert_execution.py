"""
Unit tests for FIX-303 (Live Memgraph Cypher Execution in GraphRevertService).
"""

from unittest.mock import MagicMock
import pytest
from app.services.graph_revert_service import GraphRevertService


def test_graph_revert_executes_cypher_and_updates_db():
    """
    Test that GraphRevertService executes Cypher query on Memgraph and updates DB ORM records (FIX-303).
    """
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    service = GraphRevertService(db_session=mock_db, memgraph_connection=mock_conn)

    res = service.execute_revert(
        diff_id="DIFF-8921",
        auditor_id="AUDITOR-01",
        revert_reason="False positive crosswalk relationship",
    )

    assert res.status == "REVERTED"
    assert res.diff_id == "DIFF-8921"
    # Verify Memgraph Cypher execution
    assert mock_cursor.execute.called, "Memgraph Cypher execute should be called to revert edge"
    # Verify DB commit
    assert mock_db.commit.called, "DB session commit should be called"
