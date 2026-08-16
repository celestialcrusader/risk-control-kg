"""
Unit & Integration Test Suite for STORY-PARSE-104: Memgraph Temporal Supersession Schema Upgrade.
"""

import pytest
from app.models.de_jure import DeJureObligation
from app.services.graphrag_translator import GraphRAGTranslator


def test_de_jure_obligation_temporal_fields():
    """Verify DeJureObligation schema supports legal_status and effective_date."""
    ob = DeJureObligation(
        obligation_id="MAS-TRM-3.1.2a",
        text="Implement multi-factor authentication",
        legal_status="ACTIVE",
        effective_date="2021-01-18",
        parent_clause_id="MAS-TRM-3.1.2",
        supersedes_clause_id="MAS-TRM-2013-3.1.2"
    )
    assert ob.legal_status == "ACTIVE"
    assert ob.effective_date == "2021-01-18"
    assert ob.supersedes_clause_id == "MAS-TRM-2013-3.1.2"


def test_generate_cypher_mutation_temporal_edges():
    """Verify generate_cypher_mutation emits HAS_SUBCLAUSE and SUPERSEDES statements."""
    translator = GraphRAGTranslator()
    facet_data = {
        "clause_id": "MAS-TRM-2021-3.1.2a",
        "text": "MFA requirement",
        "legal_status": "ACTIVE",
        "effective_date": "2021-01-18",
        "parent_clause_id": "MAS-TRM-2021-3.1.2",
        "supersedes_clause_id": "MAS-TRM-2013-3.1.2a"
    }
    cypher = translator.generate_cypher_mutation(facet_data)
    assert "HAS_SUBCLAUSE" in cypher
    assert "SUPERSEDES" in cypher
    assert "legal_status" in cypher
