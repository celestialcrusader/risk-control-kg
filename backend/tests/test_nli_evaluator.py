"""
Unit Tests for Production NLI Evaluator & Set-Theory Cross-Encoder (STORY-MAINT-103).
"""

import pytest
from app.services.nli_evaluator import NliBatchCrosswalkEvaluator, SetTheoryEvaluation


def test_nli_evaluator_classifies_semantic_equivalence():
    """Verify evaluator assigns EQUIVALENT_TO when requirements match closely."""
    evaluator = NliBatchCrosswalkEvaluator()

    mas_clause = "A financial institution must implement multi-factor authentication for all privileged users."
    nist_control = "The organization enforces multi-factor authentication for privileged accounts."

    res = evaluator.evaluate_pair(mas_clause, nist_control)

    assert isinstance(res, SetTheoryEvaluation)
    assert res.relation in ("EQUIVALENT_TO", "SUPERSET_OF")
    assert res.confidence >= 0.80


def test_nli_evaluator_detects_no_relationship():
    """Verify evaluator assigns NO_RELATIONSHIP when topics are completely unrelated."""
    evaluator = NliBatchCrosswalkEvaluator()

    mas_clause = "Financial institutions must maintain physical security perimeters around data centers."
    nist_control = "The organization enforces cryptographic algorithms for digital signatures."

    res = evaluator.evaluate_pair(mas_clause, nist_control)

    assert res.relation == "NO_RELATIONSHIP"
    assert res.confidence <= 0.35
