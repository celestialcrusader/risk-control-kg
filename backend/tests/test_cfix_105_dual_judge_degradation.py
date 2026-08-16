"""
TDD Unit Test for CFIX-105: Dual-Judge LLM Evaluation & Arithmetic Degradation Signaling.
"""

from unittest.mock import patch
import pytest
from app.services.dual_judge_async import AsynchronousDualJudgeService


def test_dual_judge_llm_success():
    """Verify LLM success uses LLM scores and rationale."""
    with patch("app.services.dual_judge_async._call_llm") as mock_llm:
        mock_llm.return_value = '{"logic_score": 0.95, "technical_score": 0.90, "verdict": "APPROVED", "rationale": "Strong semantic alignment"}'
        service = AsynchronousDualJudgeService()
        service.enqueue_pair_for_audit("S-1", "T-1", "SATISFIES", confidence_score=0.80)
        
        results = service.evaluate_pending_audits()
        assert len(results) == 1
        res = results[0]
        assert res.logic_judge_score == 0.95
        assert res.technical_judge_score == 0.90
        assert res.verdict == "APPROVED"
        assert res.rationale == "Strong semantic alignment"


def test_dual_judge_arithmetic_fallback():
    """Verify LLM failure degrades to arithmetic with [ARITHMETIC_FALLBACK] rationale."""
    with patch("app.services.dual_judge_async._call_llm", side_effect=RuntimeError("vLLM offline")):
        service = AsynchronousDualJudgeService()
        service.enqueue_pair_for_audit("S-1", "T-1", "SATISFIES", confidence_score=0.80)
        
        results = service.evaluate_pending_audits()
        assert len(results) == 1
        res = results[0]
        assert res.logic_judge_score == 0.68
        assert res.technical_judge_score == 0.64
        assert res.verdict == "REJECTED"
        assert res.rationale.startswith("[ARITHMETIC_FALLBACK]")
        assert "LLM unavailable" in res.rationale
