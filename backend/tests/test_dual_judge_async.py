"""
TDD Tests for Asynchronous 70B Dual-Judge Audit Service & KTO/DPO Preference Worker (RCKG-304).
"""

import pytest
from app.services.dual_judge_async import (
    AsynchronousDualJudgeService,
    PreferenceAccumulatorWorker,
    DualJudgeAuditResult,
)


@pytest.fixture
def judge_service():
    return AsynchronousDualJudgeService()


@pytest.fixture
def preference_worker():
    return PreferenceAccumulatorWorker(target_threshold=5)


def test_dual_judge_async_evaluation(judge_service):
    """AC-1 & AC-2: Enqueue candidate pairs and evaluate Logic & Technical Judge scores."""
    judge_service.enqueue_pair_for_audit(
        source_id="REQ-101",
        target_id="OBL-202",
        relation_type="EQUIVALENT_TO",
        confidence_score=0.92,
    )

    results = judge_service.evaluate_pending_audits()

    assert len(results) == 1
    res = results[0]
    assert isinstance(res, DualJudgeAuditResult)
    assert res.logic_judge_score >= 0.0
    assert res.technical_judge_score >= 0.0
    assert res.verdict in ["APPROVED", "REJECTED"]


def test_preference_accumulator_worker_retrain_trigger(preference_worker):
    """AC-3 & AC-4: Accumulate preference pairs and fire KTO/DPO retraining trigger when threshold reached."""
    # Accumulate 4 pairs (below threshold 5)
    for i in range(4):
        triggered = preference_worker.add_preference_pair(
            chosen_pair={"source": f"REQ-{i}", "target": f"OBL-{i}"},
            rejected_pair={"source": f"REQ-{i}", "target": f"OBL-BAD-{i}"},
            score=0.95,
        )
        assert triggered is False

    # Add 5th pair -> threshold reached
    triggered = preference_worker.add_preference_pair(
        chosen_pair={"source": "REQ-5", "target": "OBL-5"},
        rejected_pair={"source": "REQ-5", "target": "OBL-BAD-5"},
        score=0.96,
    )
    assert triggered is True
    assert preference_worker.total_accumulated >= 5
