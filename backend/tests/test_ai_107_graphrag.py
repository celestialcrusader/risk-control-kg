import pytest
from app.services.graphrag_translator import GRAPHRAG_MODEL_NAME, GRAPHRAG_ENDPOINT

def test_graphrag_qwen3_80b_config():
    assert GRAPHRAG_MODEL_NAME == "Qwen/Qwen3-Next-80B-A3B"
    assert GRAPHRAG_ENDPOINT == "http://localhost:8004/v1"
