"""
TDD Unit Test for CFIX-205: Removal of Misleading DeBERTa Model Metadata.
"""

import os
import subprocess
import pytest
from app.services.nli_engine import NliSetTheoryEngine


def test_no_deberta_model_string_in_nli_result():
    """Verify NliResult metadata model key never returns DeBERTa on heuristic fallback."""
    engine = NliSetTheoryEngine()
    # Force fallback path (without mocking _call_llm, which raises exception when LLM is offline or invalid prompt)
    res = engine.evaluate_pair("System logging required", "Logs must be stored")
    
    assert res.metadata.get("model") != "DeBERTa-v3-CrossEncoder-Llama3.1-8B-Student"
    assert "DeBERTa" not in str(res.metadata.get("model", ""))
