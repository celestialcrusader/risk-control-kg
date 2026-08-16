"""
TDD Tests for STORY-COMP-302: Genuinely Decoupled Two-Dimensional Dual-Judge & Anti-Heuristic Gatekeeper.
"""

import pytest
from app.services.nli_evaluator import NliBatchCrosswalkEvaluator, TwoDimensionalEvaluation


def test_anti_heuristic_gatekeeper_caps_fallback():
    """AC-302.1: Heuristic fallback must NEVER assign EQUIVALENT, FULL_COVERAGE, or confidence > 0.35."""
    evaluator = NliBatchCrosswalkEvaluator(llm_endpoint="http://non-existent-endpoint:9999/v1")

    # Pass clauses that share words (e.g. access, privacy) that previously triggered heuristic 0.95 EQUIVALENT
    source = "The Financial Institution must establish security controls for data caching on mobile devices."
    target = "NIST-PM-20 Public Privacy Website: Maintain a public website about the organization's privacy program."

    res = evaluator.evaluate_pair(source, target)
    assert res.semantic_relation != "EQUIVALENT"
    assert res.assurance_coverage != "FULL_COVERAGE"
    assert res.confidence <= 0.35
    assert "heuristic" in res.rationale.lower() or "unverified" in res.rationale.lower()


def test_orthogonal_two_dimensional_evaluations_preserved():
    """AC-302.2: Ensure genuine 2D orthogonality without deterministic overwrite."""
    # Test valid non-trivial orthogonal combination: OVERLAPS + FULL_COVERAGE
    e1 = TwoDimensionalEvaluation(
        semantic_relation="OVERLAPS",
        assurance_coverage="FULL_COVERAGE",
        confidence=0.88,
        rationale="Specific technical mandate in MAS is fully satisfied by the broader NIST control mechanisms.",
    )
    assert e1.semantic_relation == "OVERLAPS"
    assert e1.assurance_coverage == "FULL_COVERAGE"

    # Test valid non-trivial orthogonal combination: SUBSET_OF + PARTIAL_COVERAGE
    e2 = TwoDimensionalEvaluation(
        semantic_relation="SUBSET_OF",
        assurance_coverage="PARTIAL_COVERAGE",
        confidence=0.85,
        rationale="NIST control is structurally broader but leaves specific MAS operational mandate unaddressed.",
    )
    assert e2.semantic_relation == "SUBSET_OF"
    assert e2.assurance_coverage == "PARTIAL_COVERAGE"
