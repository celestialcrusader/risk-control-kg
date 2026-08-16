"""
Unit tests for FIX-101 (LLM_ENDPOINT Port Collision & Import Path Inconsistency).
"""

import os
import importlib
import pytest


def test_llm_endpoint_default_port_not_8000():
    """
    Test that default LLM_ENDPOINT port is not 8000 (prevents self-referencing FastAPI server).
    """
    import app.services.extraction as ext_module

    if "LLM_ENDPOINT" not in os.environ:
        assert ":8000" not in ext_module.LLM_ENDPOINT, f"LLM_ENDPOINT default {ext_module.LLM_ENDPOINT} collides with FastAPI port 8000"
    else:
        import inspect
        source = inspect.getsource(ext_module)
        assert 'LLM_ENDPOINT", "http://localhost:8000/v1"' not in source


def test_llm_endpoint_env_var_override(monkeypatch):
    """
    QA Edge Case: Verify setting LLM_ENDPOINT env var properly overrides default.
    """
    custom_endpoint = "http://custom-vllm:9000/v1"
    monkeypatch.setenv("LLM_ENDPOINT", custom_endpoint)
    import app.services.extraction as ext_module
    importlib.reload(ext_module)

    assert ext_module.LLM_ENDPOINT == custom_endpoint


def test_extract_api_bootstrap_import_path():
    """
    Test that app.api.extract does not use 'backend.app.services' prefix.
    """
    import inspect
    import app.api.extract as extract_api

    source = inspect.getsource(extract_api)
    assert "from backend.app.services" not in source, "Found 'backend.app.services' import in extract.py"
