"""
TDD Unit Test for CFIX-200: LLM-Powered 6-Facet Extractor.
"""

from unittest.mock import patch
import pytest
from app.services.facet_extractor import DeJureFacetExtractor


def test_facet_extractor_llm_success_path():
    """Verify LLM extraction populates all 6 facets and sets extraction_method='LLM'."""
    llm_json = '{"action_verb": "report", "subject_noun": "data breach incidents", "domain_facet": "IncidentResponse", "modality_facet": "MANDATORY", "target_role_facet": "COMPLIANCE_OFFICER", "control_nature": "DETECTIVE"}'

    with patch("app.services.extraction._call_llm", return_value=llm_json):
        extractor = DeJureFacetExtractor()
        facets = extractor.extract_facets("In the event of a data breach, the compliance officer must report incidents within 24 hours.")
        
        assert facets["action_verb"] == "report"
        assert facets["subject_noun"] == "data breach incidents"
        assert facets["domain_facet"] == "IncidentResponse"
        assert facets["control_nature"] == "DETECTIVE"
        assert facets["extraction_method"] == "LLM"


def test_facet_extractor_fallback_path():
    """Verify LLM failure falls back to regex and sets extraction_method='REGEX_FALLBACK'."""
    with patch("app.services.extraction._call_llm", side_effect=RuntimeError("vLLM offline")):
        extractor = DeJureFacetExtractor()
        facets = extractor.extract_facets("System administrator must encrypt pii data.")
        
        assert facets["action_verb"] == "encrypt"
        assert facets["domain_facet"] == "DATA_PROTECTION"
        assert facets["extraction_method"] == "REGEX_FALLBACK"
