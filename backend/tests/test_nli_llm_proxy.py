"""
Unit tests for FIX-301 (LLM-Proxied NLI Classification in NliSetTheoryEngine).
"""

from unittest.mock import patch
import pytest
from app.services.nli_engine import NliSetTheoryEngine


@patch("app.services.nli_engine._call_llm")
def test_nli_engine_calls_llm_for_classification(mock_call_llm):
    """
    Test that NliSetTheoryEngine uses LLM classification for arbitrary text pairs (FIX-301).
    """
    mock_call_llm.return_value = '{"relation": "SUPERSET_OF", "confidence": 0.91, "logits": {"SUPERSET_OF": 0.91, "EQUIVALENT_TO": 0.05}}'

    engine = NliSetTheoryEngine()
    premise = "System log management policy requires capturing administrative activity."
    hypothesis = "SOP-101 requires recording admin logins."

    result = engine.evaluate_pair(premise, hypothesis)

    assert result.set_theory_relation == "SUPERSET_OF"
    assert result.confidence_score == 0.91
    assert mock_call_llm.called, "LLM should be called for NLI classification"
