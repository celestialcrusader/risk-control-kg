"""
TDD Tests for STORY-COMP-401: Atomic Coverage Verifier Gate & False FULL/EQUIVALENT Prevention.
"""

import pytest
from app.services.coverage_verifier import AtomicCoverageVerifier


def test_coverage_verifier_downgrades_storage_vs_logging():
    """AC-401.1: Verify AU-4 (storage capacity) does NOT satisfy MAS-7.5.7 (logging change activities) as FULL_COVERAGE."""
    verifier = AtomicCoverageVerifier()

    mas_7_5_7 = "The Financial Institution must enable a logging facility to record activities performed during the change process."
    nist_au_4 = "NIST-AU-4 Audit Log Storage Capacity: Allocate audit log storage capacity and configure system to prevent capacity exhaustion."

    # Even if LLM erroneously suggested FULL_COVERAGE, verifier must gate and downgrade to PARTIAL_COVERAGE
    sem_rel, ass_cov, rationale = verifier.verify_and_gate(
        source_id="MAS-7.5.7",
        target_id="NIST-AU-4",
        source_text=mas_7_5_7,
        target_text=nist_au_4,
        raw_sem_rel="SUBSET_OF",
        raw_ass_cov="FULL_COVERAGE",
    )
    assert ass_cov != "FULL_COVERAGE"
    assert ass_cov in ["PARTIAL_COVERAGE", "NO_COVERAGE"]
    assert "storage" in rationale.lower()


def test_coverage_verifier_downgrades_reporting_vs_lifecycle():
    """AC-401.2: Verify IR-6 (incident reporting) does NOT equal MAS-7.7.3.c (entire incident management lifecycle roles)."""
    verifier = AtomicCoverageVerifier()

    mas_7_7_3_c = "The Financial Institution must define roles and responsibilities for incident recording, analysis, escalation, decision-making, resolution, and monitoring."
    nist_ir_6 = "NIST-IR-6 Incident Reporting: Personnel report incidents and incident information is reported to authorities."

    sem_rel, ass_cov, rationale = verifier.verify_and_gate(
        source_id="MAS-7.7.3.c",
        target_id="NIST-IR-6",
        source_text=mas_7_7_3_c,
        target_text=nist_ir_6,
        raw_sem_rel="EQUIVALENT",
        raw_ass_cov="FULL_COVERAGE",
    )
    assert sem_rel != "EQUIVALENT"
    assert ass_cov != "FULL_COVERAGE"
    assert sem_rel in ["OVERLAPS", "SUBSET_OF"]


def test_coverage_verifier_media_storage_vs_mobile_sandbox():
    """Verify MP-7 (media use / portable storage) does NOT equal MAS-14.1.7 (mobile sandbox / jailbreak prevention)."""
    verifier = AtomicCoverageVerifier()

    mas_14_1_7 = "The Financial Institution must prohibit rooted or jailbroken devices from accessing mobile online banking applications unless protected by a containerized sandbox."
    nist_mp_7 = "NIST-MP-7 Media Use: Restrict the use of portable storage devices on organizational systems."

    sem_rel, ass_cov, rationale = verifier.verify_and_gate(
        source_id="MAS-14.1.7",
        target_id="NIST-MP-7",
        source_text=mas_14_1_7,
        target_text=nist_mp_7,
        raw_sem_rel="EQUIVALENT",
        raw_ass_cov="FULL_COVERAGE",
    )
    assert sem_rel in ["OVERLAPS", "NONE"]
    assert ass_cov == "NO_COVERAGE"
