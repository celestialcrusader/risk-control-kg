import pytest
from app.services.extraction import LLM_MODEL, LLM_ENDPOINT

def test_extraction_qwen3_config():
    assert LLM_MODEL == "Qwen/Qwen3-30B-A3B"
    assert LLM_ENDPOINT == "http://localhost:8000/v1"
