import pytest
from unittest.mock import patch
from app.services.nli_engine import NliSetTheoryEngine, NLI_MODEL_NAME

def test_nli_modernbert_config():
    assert NLI_MODEL_NAME == "answerdotai/ModernBERT-large-NLI"

def test_nli_zero_keyword_fallback_on_failure():
    engine = NliSetTheoryEngine()
    # Mock LLM call failure
    with patch("app.services.nli_engine._call_llm", side_effect=RuntimeError("LLM unavailable")):
        # Premise contains "encrypt" and "pii" which previously triggered fake 0.95 confidence keyword fallback
        result = engine.evaluate_pair("encrypt pii data", "encrypt pii data")
        assert result.set_theory_relation == "PENDING_CLASSIFICATION"
        assert result.confidence_score == 0.0
        assert result.metadata["method"] == "FAILED"
