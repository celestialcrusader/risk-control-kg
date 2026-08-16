"""
Unit tests for FIX-305 (LLM-Proxied Dual-Judge Service).
"""

from unittest.mock import patch
import pytest
from app.services.dual_judge_async import AsynchronousDualJudgeService


@patch("app.services.dual_judge_async._call_llm")
def test_dual_judge_uses_llm_evaluation(mock_call_llm):
    """
    Test that AsynchronousDualJudgeService uses LLM evaluation instead of arithmetic conf * 1.02 / 0.98 scaling (FIX-305).
    """
    mock_call_llm.return_value = '{"logic_score": 0.92, "technical_score": 0.88, "verdict": "APPROVED", "rationale": "High semantic overlap"}'

    service = AsynchronousDualJudgeService()
    service.enqueue_pair_for_audit("CO-101", "OBL-202", "SATISFIES", confidence_score=0.75)

    results = service.evaluate_pending_audits()

    assert len(results) == 1
    res = results[0]
    assert res.logic_judge_score == 0.92
    assert res.technical_judge_score == 0.88
    assert res.verdict == "APPROVED"
    assert mock_call_llm.called, "LLM should be called for dual-judge evaluation"
