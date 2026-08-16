"""
TDD Unit Tests for Elasticsearch BM25 Sparse Search Service with Network Hop Buffer (RCKG-301).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from app.services.retrieval.bm25_service import Bm25SparseSearchService, Bm25SearchResult


@pytest.fixture
def bm25_service():
    return Bm25SparseSearchService(es_url="http://localhost:9200", index_name="rckg_nodes_bm25")


def test_bm25_search_query_formatting_and_response(bm25_service):
    """AC-1: Query BM25 index and return top candidate IDs with relevance scores."""
    # Seed in-memory fallback index
    bm25_service.index_documents([
        {"node_id": "OBL-101", "content": "System administrator must limit user access credentials."},
        {"node_id": "OBL-102", "content": "Data protection officer must encrypt all PII databases."},
        {"node_id": "OBL-103", "content": "Security team must review access logs quarterly."},
    ])

    res = bm25_service.search(query_text="access credentials", top_k=10)

    assert isinstance(res, Bm25SearchResult)
    assert len(res.candidate_ids) >= 1
    assert "OBL-101" in res.candidate_ids
    assert res.total_hits > 0


def test_bm25_search_15s_network_hop_timeout_handling(bm25_service):
    """AC-2: Incorporate 15-second network hop buffer and fallback gracefully on timeout."""
    with patch.object(bm25_service, "_execute_es_http_query", side_effect=TimeoutError("Network hop timeout after 15s")):
        res = bm25_service.search(query_text="encryption policy", top_k=10, timeout_sec=15.0)

        assert isinstance(res, Bm25SearchResult)
        assert res.metadata.get("fallback_triggered") is True
        assert res.metadata.get("timeout_sec") == 15.0
