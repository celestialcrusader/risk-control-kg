import pytest
from app.services.retrieval.colbert_service import RERANKER_MODEL_NAME

def test_reranker_qwen3_config():
    assert RERANKER_MODEL_NAME == "Qwen/Qwen3-Reranker-8B"
