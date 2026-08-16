import pytest
from app.services.embedding_sync import EMBEDDING_MODEL_NAME, EMBEDDING_DIM

def test_embedding_config():
    assert EMBEDDING_MODEL_NAME == "Qwen/Qwen3-Embedding-8B"
    assert EMBEDDING_DIM == 4096
