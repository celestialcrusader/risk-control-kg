"""
TDD Tests for De Jure 6-Facet Extraction Service (RCKG-203b).
"""

import pytest
from app.services.facet_extractor import DeJureFacetExtractor


@pytest.fixture
def extractor():
    return DeJureFacetExtractor()


def test_extract_all_6_orthogonal_facets(extractor):
    """AC-1 & AC-2: Return a dictionary containing all 6 orthogonal facet keys with high accuracy."""
    clause_text = "The system administrator must encrypt all stored PII data to prevent unauthorized access."
    facets = extractor.extract_facets(clause_text)

    assert isinstance(facets, dict)
    required_keys = {
        "action_verb",
        "subject_noun",
        "domain_facet",
        "modality_facet",
        "target_role_facet",
        "control_nature",
    }
    assert required_keys.issubset(set(facets.keys()))

    assert facets["action_verb"] == "encrypt"
    assert facets["subject_noun"] in ["pii", "data", "pii data"]
    assert facets["modality_facet"] == "MANDATORY"
    assert facets["target_role_facet"] == "SYSTEM_ADMINISTRATOR"


def test_modality_facet_optional(extractor):
    """Verify RECOMMENDATION / OPTIONAL modality when 'should' is present instead of 'must'."""
    clause_text = "Organizations should review access logs on a monthly basis."
    facets = extractor.extract_facets(clause_text)

    assert facets["action_verb"] == "review"
    assert facets["modality_facet"] == "RECOMMENDED"


def test_compiler_integration_compatibility(extractor):
    """AC-3: Ensure extracted facets dict integrates with RuleBasedGraphCompiler."""
    from app.services.graph_compiler import RuleBasedGraphCompiler
    compiler = RuleBasedGraphCompiler()

    clause_1 = "Security officers shall limit user credentials to authorized personnel."
    clause_2 = "System admin must limit credentials for all active users."

    facets_1 = extractor.extract_facets(clause_1)
    facets_2 = extractor.extract_facets(clause_2)

    source_entity = {"node_id": "REQ-101", **facets_1}
    target_entity = {"node_id": "CTRL-202", **facets_2}

    mutations = compiler.compile_mutation(source_entity, target_entity, cosine_sim=0.92)
    assert len(mutations) > 0
    assert mutations[0].source_node_id == "REQ-101"
    assert mutations[0].target_node_id == "CTRL-202"
