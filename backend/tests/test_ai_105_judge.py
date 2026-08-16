import pytest
from app.services.judge import JUDGE_MODEL, JUDGE_ENDPOINT

def test_judge_qwen3_80b_config():
    assert JUDGE_MODEL == "Qwen/Qwen3-Next-80B-A3B"
    assert JUDGE_ENDPOINT == "http://localhost:8004/v1"
