"""
TDD Tests for STORY-COMP-501: Dynamic Granular Element Extractor & Zero-Template 4-Part Rationale Engine.
"""

import pytest
from app.services.nli_evaluator import TwoDimensionalEvaluation
from app.services.confidence_calibrator import format_structured_rationale


def test_two_dimensional_evaluation_has_dynamic_element_fields():
    """AC-501.1: Verify TwoDimensionalEvaluation contains covered_mechanisms and missing_gaps fields."""
    eval_res = TwoDimensionalEvaluation(
        semantic_relation="SUBSET_OF",
        assurance_coverage="PARTIAL_COVERAGE",
        confidence=0.88,
        rationale="NIST-SC-13 provides cryptographic protection for transit.",
        covered_mechanisms="FIPS-validated cryptographic algorithms for data transmission",
        missing_gaps="Mandatory retail customer confirmation channel",
        comparative_justification="NIST-SC-13 enforces transit encryption but does not mandate retail alerting.",
    )
    assert eval_res.covered_mechanisms == "FIPS-validated cryptographic algorithms for data transmission"
    assert eval_res.missing_gaps == "Mandatory retail customer confirmation channel"


def test_zero_template_structured_rationale():
    """AC-501.2: Verify format_structured_rationale rejects static mail-merge templates."""
    rationale = format_structured_rationale(
        source_id="MAS-14.1.2",
        target_id="NIST-SC-13",
        source_text="The Financial Institution must secure communications channels to protect customer data.",
        target_text="NIST-SC-13 Cryptographic Protection: Implement cryptographic modules in accordance with applicable laws.",
        sem_rel="SUBSET_OF",
        ass_cov="PARTIAL_COVERAGE",
        covered_elements=["FIPS-validated cryptographic algorithms for communications protection"],
        missing_elements=["Specific retail banking customer advisory protocols"],
        conclusion_text="NIST-SC-13 enforces cryptographic controls on data in transit, satisfying the transmission security obligation of MAS-14.1.2.",
    )

    # Must contain dynamic elements
    assert "FIPS-validated cryptographic algorithms" in rationale
    assert "Specific retail banking customer advisory protocols" in rationale

    # Must NOT contain the prohibited mail-merge placeholders
    assert "Core technical controls and operational mechanisms" not in rationale
    assert "Framework-specific reporting workflows or external parameters" not in rationale
