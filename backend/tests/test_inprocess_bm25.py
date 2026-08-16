"""
Unit tests for FIX-302 (In-Process BM25 Sparse Search Service).
"""

import pytest
from app.services.retrieval.bm25_service import Bm25SparseSearchService


def test_bm25_in_process_search_scores_and_ranks():
    """
    Test that Bm25SparseSearchService computes real BM25 scores for indexed documents without raising unhandled RuntimeError (FIX-302).
    """
    service = Bm25SparseSearchService()

    docs = [
        {"node_id": "DOC-1", "content": "Multi-factor authentication must be enforced for administrative access."},
        {"node_id": "DOC-2", "content": "Database passwords must be stored using strong salt and hash algorithms."},
        {"node_id": "DOC-3", "content": "Multi-factor authentication (MFA) is required for remote user logins."},
    ]
    service.index_documents(docs)

    res = service.search("multi-factor authentication access", top_k=5)

    assert res.total_hits == 2
    assert "DOC-1" in res.candidate_ids
    assert "DOC-3" in res.candidate_ids
    # DOC-1 matches all 3 query terms (multi-factor, authentication, access) -> higher BM25 score than DOC-3
    assert res.candidate_ids[0] == "DOC-1"
    assert res.score_map["DOC-1"] > res.score_map["DOC-3"]
