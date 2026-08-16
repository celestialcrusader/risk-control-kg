"""
TDD Unit Test for CFIX-104: Honest Degradation Signaling in NLI Engine.
"""

from unittest.mock import patch
import pytest
from app.services.nli_engine import NliSetTheoryEngine


def test_nli_engine_llm_success_metadata():
    """Verify LLM success path populates method='LLM_CLASSIFICATION'."""
    with patch("app.services.nli_engine._call_llm") as mock_llm:
        mock_llm.return_value = '{"relation": "SUPERSET_OF", "confidence": 0.92, "logits": {"SUPERSET_OF": 0.92}}'
        engine = NliSetTheoryEngine()
        res = engine.evaluate_pair("Premise text", "Hypothesis text")
        
        assert res.set_theory_relation == "SUPERSET_OF"
        assert res.metadata["method"] == "LLM_CLASSIFICATION"
        assert res.metadata["model"] == "LLM_PROXY"


def test_nli_engine_fallback_metadata_and_warning():
    """Verify LLM failure path sets method='KEYWORD_HEURISTIC_FALLBACK' and does NOT claim DeBERTa."""
    with patch("app.services.nli_engine._call_llm", side_effect=RuntimeError("vLLM connection refused")):
        engine = NliSetTheoryEngine()
        res = engine.evaluate_pair("Premise text with encrypt pii", "Hypothesis text with encrypt pii")
        
        assert res.set_theory_relation == "EQUIVALENT_TO"
        assert res.metadata["method"] == "KEYWORD_HEURISTIC_FALLBACK"
        assert res.metadata["model"] == "KEYWORD_HEURISTIC"
        assert "DeBERTa-v3" not in res.metadata.get("model", "")
