"""
TDD Tests for STORY-COMP-402: Retail Banking Customer Gap Classifier & Canonical MFA IA-2 Binding.
"""

import pytest
from app.services.coverage_verifier import AtomicCoverageVerifier
from app.services.clause_decompounder import ClauseDecompounder


def test_retail_customer_gap_detected():
    """AC-402.1: Verify retail customer notification mandates (e.g. MAS-14.3.3.a) are flagged as true regulatory gaps."""
    verifier = AtomicCoverageVerifier()

    mas_14_3_3_a = "The Financial Institution must notify its customers immediately upon discovery of unauthorized transactions or security breaches."
    nist_si_4 = "NIST-SI-4 Information System Monitoring: Monitor the information system to detect attacks and indicators of potential compromise."

    sem_rel, ass_cov, rationale = verifier.verify_and_gate(
        source_id="MAS-14.3.3.a",
        target_id="NIST-SI-4",
        source_text=mas_14_3_3_a,
        target_text=nist_si_4,
        raw_sem_rel="OVERLAPS",
        raw_ass_cov="PARTIAL_COVERAGE",
    )
    assert ass_cov == "NO_COVERAGE"
    assert "retail customer" in rationale.lower() or "customer" in rationale.lower()


def test_canonical_mfa_ia2_binding_in_decompounder():
    """AC-402.2: Verify ClauseDecompounder maps MFA login clauses to canonical IA-2 queries."""
    decompounder = ClauseDecompounder()
    mas_mfa = "The Financial Institution must deploy multi-factor authentication at login for all online financial services."

    queries = decompounder.decompose(mas_mfa)
    combined = " ".join(queries).lower()
    assert "multi-factor authentication" in combined or "mfa" in combined
    assert "ia-2" in combined or "identification and authentication" in combined
