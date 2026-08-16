"""
Unit and Integration tests for STORY-COMP-203: Hybrid Candidate Retriever (Dense + BM25 Top-15 Recall Net).
"""
import pytest
import numpy as np
from app.services.hybrid_retriever import HybridCandidateRetriever


class MockControl:
    def __init__(self, framework_obj_id: str, objective_name: str, objective_text: str):
        self.framework_obj_id = framework_obj_id
        self.objective_name = objective_name
        self.objective_text = objective_text


def mock_embedder(texts):
    """Deterministic mock embedder creating unit vectors."""
    vectors = []
    for t in texts:
        v = np.zeros(64)
        for i, ch in enumerate(t[:64]):
            v[i] = ord(ch) % 10
        norm = np.linalg.norm(v)
        if norm > 0:
            v = v / norm
        vectors.append(v)
    return np.array(vectors)


def test_hybrid_retriever_initialization():
    """Verify hybrid retriever builds BM25 and vector stores."""
    controls = [
        MockControl("NIST-AC-1", "Access Control Policy", "Develop and document access control policy..."),
        MockControl("NIST-IA-2", "Identification and Authentication (Organizational Users)", "The system uniquely identifies and authenticates organizational users and implements multi-factor authentication (MFA)..."),
        MockControl("NIST-CA-2", "Control Assessments", "Conduct an assessment of the security and privacy controls..."),
    ]
    retriever = HybridCandidateRetriever(controls, mock_embedder)
    assert len(retriever.controls) == 3


def test_hybrid_retrieval_mfa_canonical_match():
    """Verify short query 'The organization must enforce MFA' finds NIST-IA-2 in top results."""
    controls = [
        MockControl("NIST-AC-1", "Access Control Policy", "Develop and document access control policy..."),
        MockControl("NIST-IA-2", "Identification and Authentication", "The system implements multi-factor authentication MFA for privileged and non-privileged access..."),
        MockControl("NIST-CA-2", "Control Assessments", "Conduct independent assessments of controls..."),
        MockControl("NIST-SI-2", "Flaw Remediation", "Identify, report, and correct information system flaws..."),
        MockControl("NIST-SC-7", "Boundary Protection", "Monitor and control communications at external boundary..."),
    ]
    retriever = HybridCandidateRetriever(controls, mock_embedder)
    results = retriever.retrieve_top_k("The organization must enforce MFA", top_k=3)
    
    assert len(results) > 0
    top_ids = [c.framework_obj_id for c, sim, meta in results]
    assert "NIST-IA-2" in top_ids
    # NIST-IA-2 should be #1 or #2 due to strong BM25 keyword match on MFA
    assert top_ids[0] == "NIST-IA-2"


def test_hybrid_retrieval_top_k_parameter():
    """Verify retriever returns requested top_k results."""
    controls = [
        MockControl(f"NIST-CTL-{i}", f"Control {i}", f"Description of control {i} with security requirements...")
        for i in range(20)
    ]
    retriever = HybridCandidateRetriever(controls, mock_embedder)
    results = retriever.retrieve_top_k("security requirements", top_k=15)
    assert len(results) == 15
