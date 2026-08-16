"""
Unit tests for ClauseBoundaryExtractor (FIX-100).
"""

import pytest
from app.services.hybrid_chunking import ClauseBoundaryExtractor


def test_clause_boundary_extractor_no_index_error():
    """
    Test that ClauseBoundaryExtractor parses clause headers without raising IndexError (FIX-100).
    """
    extractor = ClauseBoundaryExtractor()
    sample_text = (
        "Section 3.1 Access Control\n"
        "Financial institutions must enforce multi-factor authentication for administrative access.\n\n"
        "Section 4.2 Logging & Audit\n"
        "System logs shall record user activities."
    )
    # This should not raise IndexError: no such group
    chunks = extractor.extract_clauses(sample_text)
    assert len(chunks) == 2
    assert chunks[0].section_reference == "Section 3.1"
    assert chunks[0].heading_title == "Access Control"
    assert chunks[1].section_reference == "Section 4.2"
    assert chunks[1].heading_title == "Logging & Audit"


def test_clause_boundary_extractor_varied_headers():
    """
    QA Edge Case: Verify extraction across varied clause header formats (Article, Annex, numbering).
    """
    extractor = ClauseBoundaryExtractor()
    sample_text = (
        "Article 5 General Principles\n"
        "Data protection principles must be adhered to.\n\n"
        "Annex B BYOD Security\n"
        "BYOD policy requirements.\n\n"
        "9.1.5 Multi-Factor Authentication\n"
        "MFA must be implemented."
    )
    chunks = extractor.extract_clauses(sample_text)
    assert len(chunks) == 3
    assert chunks[0].section_reference == "Article 5"
    assert chunks[0].heading_title == "General Principles"
    assert chunks[1].section_reference == "Annex B"
    assert chunks[1].heading_title == "BYOD Security"
    assert chunks[2].section_reference == "9.1.5"
    assert chunks[2].heading_title == "Multi-Factor Authentication"
