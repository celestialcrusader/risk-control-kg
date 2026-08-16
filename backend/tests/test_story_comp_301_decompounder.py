"""
TDD Tests for STORY-COMP-301: Multi-Intent Clause Decompounder & Precision Query Expansion.
"""

import pytest
from app.services.clause_decompounder import ClauseDecompounder


def test_clause_decompounder_atomic_extraction():
    """AC-301.1: Verify decomposition of compound multi-threat clauses into atomic sub-queries."""
    decompounder = ClauseDecompounder()

    # Test compound web application & infrastructure security clause (MAS-14.1.3)
    text_14_1_3 = (
        "The Financial Institution must implement appropriate security controls to protect online financial services "
        "and applications against common cyber attacks such as SQL injection, cross-site scripting, "
        "man-in-the-middle attacks, denial-of-service, and malware."
    )
    sub_queries = decompounder.decompose(text_14_1_3)
    assert len(sub_queries) >= 3
    # Verify key technical sub-intents are extracted
    joined = " ".join(sub_queries).lower()
    assert "injection" in joined or "input validation" in joined
    assert "denial-of-service" in joined or "dos" in joined or "availability" in joined
    assert "malware" in joined or "malicious code" in joined


def test_clause_decompounder_single_intent_passthrough():
    """Verify simple single-mandate clause returns a single clean query."""
    decompounder = ClauseDecompounder()
    simple_text = "The Financial Institution must evaluate its exposure to technology risks."
    sub_queries = decompounder.decompose(simple_text)
    assert len(sub_queries) == 1
    assert "exposure to technology risks" in sub_queries[0].lower()


def test_clause_decompounder_secure_comm_channel():
    """Verify secure communications channel mandate (MAS-14.1.2) generates transmission security keywords."""
    decompounder = ClauseDecompounder()
    text_14_1_2 = "The Financial Institution must establish secure communication channels to protect the confidentiality and integrity of customer sensitive data transmitted over the internet."
    sub_queries = decompounder.decompose(text_14_1_2)
    assert any("transmission" in q.lower() or "communication" in q.lower() or "confidentiality" in q.lower() for q in sub_queries)
