"""
TDD Tests for STORY-COMP-403: Dynamic Bayesian Confidence Calibrator & Structured 4-Part Rationale Standard.
"""

import pytest
from app.services.confidence_calibrator import compute_dynamic_confidence, format_structured_rationale


def test_dynamic_confidence_variance():
    """AC-403.1: Confidence score must vary continuously based on dense similarity and token alignment."""
    conf1 = compute_dynamic_confidence(
        base_llm_conf=0.85,
        dense_sim=0.74,
        source_text="The Financial Institution must enforce segregation of duties in software release.",
        target_text="NIST-AC-5 Separation of Duties: Define access authorizations to support separation of duties.",
    )
    conf2 = compute_dynamic_confidence(
        base_llm_conf=0.85,
        dense_sim=0.48,
        source_text="The Financial Institution must adopt a defence-in-depth approach.",
        target_text="NIST-RA-9 Criticality Analysis: Perform criticality analysis on system components.",
    )
    # The two confidences must NOT both be exactly 0.85 and must differ realistically
    assert conf1 != conf2
    assert 0.60 <= conf1 <= 0.99
    assert 0.60 <= conf2 <= 0.99
    assert conf1 > conf2  # Strong match has higher confidence than weak match


def test_structured_4part_rationale_format():
    """AC-403.2: Rationale must follow structured 4-part audit format."""
    rationale = format_structured_rationale(
        source_id="MAS-7.5.7",
        target_id="NIST-AU-4",
        source_text="The Financial Institution must enable logging facility to record activities during change process.",
        target_text="NIST-AU-4 Audit Log Storage Capacity",
        sem_rel="SUBSET_OF",
        ass_cov="PARTIAL_COVERAGE",
        covered_elements=["Audit log storage infrastructure"],
        missing_elements=["Requirement to log activities during software change execution"],
        conclusion_text="AU-4 ensures log repository capacity but does not enforce event capture during software changes.",
    )

    assert "MAS Requirement:" in rationale
    assert "NIST Control:" in rationale
    assert "Gap Analysis:" in rationale
    assert "Assurance Conclusion:" in rationale
