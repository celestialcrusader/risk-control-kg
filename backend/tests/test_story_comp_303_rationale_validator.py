"""
TDD Tests for STORY-COMP-303: Defensible Comparative Rationale Generator & Tautology Rejection Filter.
"""

import pytest
from app.services.rationale_validator import validate_and_sanitize_rationale


def test_reject_tautological_rationales():
    """AC-303.1: Reject tautological strings that merely echo enum values or token metrics."""
    tautologies = [
        "Evaluated semantic relationship as OVERLAPS with PARTIAL_COVERAGE assurance level.",
        "Shared domain concepts (risk) with token overlap ratio of 0.43.",
        "LLM Cross-Framework Semantic Evaluation",
        "LLM Evaluation",
        "",
    ]
    for tautology in tautologies:
        is_valid, sanitized = validate_and_sanitize_rationale(
            tautology,
            source_id="MAS-7.6.1",
            target_id="NIST-AC-5",
            source_text="The Financial Institution must enforce segregation of duties in software release.",
            target_text="NIST-AC-5 Separation of Duties: Define access authorizations to support separation of duties.",
        )
        assert is_valid is False
        # Ensure sanitized fallback is comparative and context-aware
        assert "MAS-7.6.1" in sanitized or "segregation of duties" in sanitized.lower()


def test_accept_defensible_comparative_rationale():
    """AC-303.2: Accept granular comparative rationales that cite concrete mechanisms."""
    valid_rationale = (
        "NIST-AC-5 satisfies the core mandate of MAS-7.6.1 by requiring separation of system access "
        "authorizations, preventing developers from moving code to production without dual control."
    )
    is_valid, sanitized = validate_and_sanitize_rationale(
        valid_rationale,
        source_id="MAS-7.6.1",
        target_id="NIST-AC-5",
        source_text="The Financial Institution must enforce segregation of duties in software release.",
        target_text="NIST-AC-5 Separation of Duties",
    )
    assert is_valid is True
    assert sanitized == valid_rationale
