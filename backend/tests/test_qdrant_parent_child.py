"""
Unit & Integration Test Suite for STORY-PARSE-105: Qdrant Parent-Child Vector Indexing & Hydration.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.services.qdrant_service import QdrantParentChildService


def test_search_and_hydrate_parent_clauses():
    """Verify vector search on child chunks returns hydrated parent context."""
    mock_client = MagicMock()
    mock_hit = MagicMock()
    mock_hit.score = 0.92
    mock_hit.payload = {
        "clause_id": "MAS-TRM-3.1.2a",
        "parent_clause_id": "MAS-TRM-3.1.2",
        "text": "(a) Hardware token requirement.",
        "legal_status": "ACTIVE"
    }
    mock_client.search.return_value = [mock_hit]

    service = QdrantParentChildService(client=mock_client)
    
    with patch.object(service, "_fetch_parent_clause_text", return_value="Section 3.1.2 Administrative Access Controls"):
        results = service.search_and_hydrate_parent_clauses(query_vector=[0.1] * 4096, limit=1)
        assert len(results) == 1
        assert results[0]["child_clause_id"] == "MAS-TRM-3.1.2a"
        assert results[0]["parent_clause_id"] == "MAS-TRM-3.1.2"
        assert "Section 3.1.2 Administrative Access Controls" in results[0]["retrieved_context"]
