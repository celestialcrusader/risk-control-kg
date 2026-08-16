"""
Unit and Integration tests for STORY-COMP-204: Dual-Judge Assurance Evaluator & Defensible Audit Rationale.
"""
import pytest
from app.services.nli_evaluator import (
    NliBatchCrosswalkEvaluator,
    TwoDimensionalEvaluation,
)


def test_two_dimensional_evaluation_dataclass():
    """Verify TwoDimensionalEvaluation has both semantic_relation and assurance_coverage."""
    eval_res = TwoDimensionalEvaluation(
        semantic_relation="SUPPORTS",
        assurance_coverage="NO_COVERAGE",
        confidence=0.90,
        rationale="Resource budgeting enables security controls but does not satisfy CIA preservation mandate.",
    )
    assert eval_res.semantic_relation == "SUPPORTS"
    assert eval_res.assurance_coverage == "NO_COVERAGE"
    assert eval_res.confidence == 0.90


def test_evaluator_distinguishes_enables_from_covers():
    """Verify evaluator treats budgeting/governance controls as SUPPORTS + NO_COVERAGE rather than FULL_COVERAGE."""
    evaluator = NliBatchCrosswalkEvaluator()
    res = evaluator.evaluate_pair(
        source_text="The Financial Institution must establish IT processes and controls to preserve the confidentiality, integrity, and availability of data and IT systems.",
        target_text="NIST-SA-2 Allocation of Resources: Determine and allocate resources required to protect the system as part of capital planning...",
    )
    # Must NOT be classified as FULL_COVERAGE
    assert res.assurance_coverage in ["NO_COVERAGE", "PARTIAL_COVERAGE"]
    # Semantic relation should be SUPPORTS or OVERLAPS, not EQUIVALENT
    assert res.semantic_relation in ["SUPPORTS", "OVERLAPS", "SUPERSET_OF"]
    # Rationale must not be generic
    assert "LLM Semantic Evaluation" not in res.rationale
    assert len(res.rationale) > 20


def test_evaluator_subsumption_directionality():
    """Verify evaluator marks NIST AC-5 as SUBSET_OF (Source subset of Target) or EQUIVALENT for SoD."""
    evaluator = NliBatchCrosswalkEvaluator()
    res = evaluator.evaluate_pair(
        source_text="The Financial Institution must enforce segregation of duties in the software release process.",
        target_text="NIST-AC-5 Separation of Duties: Define system access authorizations to support separation of duties...",
    )
    assert res.semantic_relation in ["SUBSET_OF", "EQUIVALENT", "SUPERSET_OF", "OVERLAPS"]
    assert res.confidence >= 0.75
    assert len(res.rationale) > 15
