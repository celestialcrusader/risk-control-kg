"""
TDD Unit Test for CFIX-204: neo4j Driver Session Interface in GraphRAG & Revert Services.
"""

from unittest.mock import MagicMock
import pytest
from app.services.graphrag_translator import GraphRAGTranslationService
from app.services.graph_revert_service import GraphRevertService


def test_graphrag_translator_uses_driver_session_without_cursor():
    """Verify GraphRAGTranslationService executes via driver.session() without raising AttributeError for cursor."""
    mock_driver = MagicMock(spec=["session"])
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_session.run.return_value = []

    service = GraphRAGTranslationService(memgraph_connection=mock_driver)
    payload = service.export_subgraph()
    
    assert mock_driver.session.called
    assert mock_session.run.called
    assert isinstance(payload.entities, list)


def test_graph_revert_uses_driver_session_without_cursor():
    """Verify GraphRevertService executes via driver.session() without raising AttributeError for cursor."""
    mock_driver = MagicMock(spec=["session"])
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    service = GraphRevertService(memgraph_connection=mock_driver)
    res = service.execute_revert("DIFF-204", "AUDITOR-1", "Testing driver session")
    
    assert mock_driver.session.called
    assert mock_session.run.called
    assert res.status == "REVERTED"
