"""
Unit tests for FIX-304 (Connect GraphRAG Export to Live Memgraph Query).
"""

from unittest.mock import MagicMock
import pytest
from app.services.graphrag_translator import GraphRAGTranslationService


def test_graphrag_export_queries_memgraph_when_nodes_none():
    """
    Test that GraphRAGTranslationService queries live Memgraph when nodes is None (FIX-304).
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        ({"node_id": "OBL-101", "type": "Obligation", "title": "MFA Enforcement"}, {"source_id": "OBL-101", "target_id": "CO-202", "relation_type": "SATISFIES", "confidence": 0.92}, {"node_id": "CO-202", "type": "ControlObjective", "title": "Access Control"}),
    ]

    service = GraphRAGTranslationService(memgraph_connection=mock_conn)
    payload = service.export_subgraph(nodes=None, edges=None)

    assert mock_cursor.execute.called, "Memgraph query execute should be called when nodes=None"
    assert payload.metadata["total_entities"] > 0
    assert any(e["id"] == "OBL-101" for e in payload.entities)
