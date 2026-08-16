"""
TDD Unit Tests for Pre-Cached ColBERTv2 Token Embedding VRAM MaxSim Reranker (RCKG-302).
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from app.services.retrieval.colbert_service import (
    ColBERTTokenCacheService,
    ColBERTReranker,
    ColBERTRerankResult,
)


@pytest.fixture
def cache_service():
    return ColBERTTokenCacheService(max_token_len=512)


@pytest.fixture
def reranker(cache_service):
    return ColBERTReranker(cache_service=cache_service)


def test_colbert_token_cache_precomputation(cache_service):
    """AC-1: ColBERTTokenCacheService pre-computes and caches token matrix representations."""
    node_id = "OBL-201"
    text = "Access control policies must enforce multi-factor authentication for administrative users."

    tokens = cache_service.get_or_compute_embeddings(node_id=node_id, text=text)

    assert tokens is not None
    assert len(tokens.shape) == 2  # (seq_len, embedding_dim)
    assert tokens.shape[1] == 128  # ColBERT v2 embedding dim = 128
    assert cache_service.has_cached(node_id) is True


def test_colbert_maxsim_reranking(reranker):
    """AC-2 & AC-3: ColBERTReranker executes MaxSim late-interaction scoring over pre-cached token matrices."""
    query_node = {
        "node_id": "REQ-101",
        "text": "User authentication requirements for privileged system access.",
    }
    candidates = [
        {"node_id": "OBL-201", "text": "Access control policies must enforce multi-factor authentication for administrative users."},
        {"node_id": "OBL-202", "text": "Data backup procedures must be executed every 24 hours."},
        {"node_id": "OBL-203", "text": "Privileged credentials shall be limited and audited."},
    ]

    result = reranker.rerank(query_node=query_node, candidate_nodes=candidates, top_k=2)

    assert isinstance(result, ColBERTRerankResult)
    assert len(result.ranked_candidate_ids) == 2
    assert result.ranked_candidate_ids[0] in ["OBL-201", "OBL-203"]
    assert result.latency_ms >= 0
    assert result.maxsim_scores[result.ranked_candidate_ids[0]] > result.maxsim_scores[result.ranked_candidate_ids[1]]
