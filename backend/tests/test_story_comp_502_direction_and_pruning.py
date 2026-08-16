"""
TDD Tests for STORY-COMP-502: Directional Containment Calibrator & Superficial OVERLAPS Pruning Gate.
"""

import pytest
from app.services.coverage_verifier import AtomicCoverageVerifier


def test_directional_containment_ac5_segregation():
    """AC-502.1: Verify narrow software release segregation (MAS-7.6.1) is SUBSET_OF broad NIST-AC-5."""
    verifier = AtomicCoverageVerifier()

    mas_7_6_1 = "The Financial Institution must enforce segregation of duties in the software release process to prevent any single individual from developing, compiling, and moving software codes between environments."
    nist_ac_5 = "NIST-AC-5 Separation of Duties: Define system access authorizations to support separation of duties and document separation of duties."

    sem_rel, ass_cov, rationale = verifier.verify_and_gate(
        source_id="MAS-7.6.1",
        target_id="NIST-AC-5",
        source_text=mas_7_6_1,
        target_text=nist_ac_5,
        raw_sem_rel="SUPERSET_OF",  # Erraneously labeled as superset
        raw_ass_cov="FULL_COVERAGE",
    )
    # Narrow source requirement in a broader organizational control is SUBSET_OF (A ⊆ B)
    assert sem_rel == "SUBSET_OF"
    assert ass_cov == "FULL_COVERAGE"


def test_prune_superficial_overlaps_sc8_config_review():
    """AC-502.2: Verify superficial overlap between configuration review (MAS-7.2.2) and transmission encryption (NIST-SC-8) is pruned to NONE."""
    verifier = AtomicCoverageVerifier()

    mas_7_2_2 = "The Financial Institution must review and verify hardware and software configuration information regularly."
    nist_sc_8 = "NIST-SC-8 Transmission Confidentiality and Integrity: Protect the confidentiality and integrity of transmitted information."

    sem_rel, ass_cov, rationale = verifier.verify_and_gate(
        source_id="MAS-7.2.2",
        target_id="NIST-SC-8",
        source_text=mas_7_2_2,
        target_text=nist_sc_8,
        raw_sem_rel="OVERLAPS",
        raw_ass_cov="NO_COVERAGE",
    )
    assert sem_rel == "NONE"
    assert ass_cov == "NO_COVERAGE"
