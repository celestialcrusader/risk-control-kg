"""
TDD Unit Test for CFIX-301: Structured Degradation Logging.
"""

from unittest.mock import patch
import pytest
from app.core.observability import log_degradation_event


def test_log_degradation_event_schema():
    """Verify log_degradation_event returns valid structured payload schema."""
    payload = log_degradation_event(
        service="NliEngine",
        method_used="KEYWORD_HEURISTIC_FALLBACK",
        error=RuntimeError("vLLM connection refused"),
        context={"premise": "encrypt data", "hypothesis": "data encrypted"},
    )
    
    assert payload["event"] == "LLM_DEGRADATION"
    assert payload["service"] == "NliEngine"
    assert payload["method_used"] == "KEYWORD_HEURISTIC_FALLBACK"
    assert "vLLM connection refused" in payload["error"]
    assert "timestamp" in payload
    assert payload["context"]["premise"] == "encrypt data"
