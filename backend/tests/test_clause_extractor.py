"""
TDD Tests for De Jure Clause-Boundary Rule Unit Extractor (RCKG-203).
"""

import pytest
from app.services.hybrid_chunking import ClauseBoundaryExtractor, ClauseChunk


@pytest.fixture
def extractor():
    return ClauseBoundaryExtractor()


def test_clause_boundary_extractor_statutory_headers(extractor):
    """AC-1 & AC-2: Splits text strictly at legal section boundaries and retains section metadata."""
    sample_text = """
Article 14.1 Security of Processing
The controller and processor shall implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk.

Article 14.2 Encryption Requirements
Data at rest and in transit must be encrypted using AES-256 and TLS 1.3 algorithms.

Section 3.2 Account Provisioning
All user accounts must be approved by the designated SecOps manager prior to creation.
"""
    chunks = extractor.extract_clauses(sample_text)

    assert len(chunks) == 3
    for c in chunks:
        assert isinstance(c, ClauseChunk)
        assert len(c.chunk_text) > 0
        assert c.word_count > 0

    assert chunks[0].section_reference == "Article 14.1"
    assert "Security of Processing" in chunks[0].heading_title

    assert chunks[1].section_reference == "Article 14.2"
    assert "Encryption Requirements" in chunks[1].heading_title

    assert chunks[2].section_reference == "Section 3.2"
    assert "Account Provisioning" in chunks[2].heading_title


def test_clause_no_truncation_mid_sentence(extractor):
    """AC-3: Chunks never truncate mid-sentence or mid-clause."""
    sample_text = """
Clause 5.1 Access Review Procedure
The security administrator must review all access rights on a quarterly basis. Any stale accounts must be disabled immediately.
"""
    chunks = extractor.extract_clauses(sample_text)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.section_reference == "Clause 5.1"
    assert "quarterly basis." in chunk.chunk_text
    assert "disabled immediately." in chunk.chunk_text
