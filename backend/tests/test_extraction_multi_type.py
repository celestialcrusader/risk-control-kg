"""
Unit tests for FIX-103 (Multi-Prompt Routing and Multi-Type Parsing).
"""

import json
import pytest
from app.services.extraction import _load_prompt_template, _build_prompt, _parse_llm_response
from app.schemas.obligation import ControlObjective, ControlActivity, Obligation
from app.api.extract import ExtractionRequest


def test_load_prompt_template_routing():
    """
    Test prompt template loading for different document types.
    """
    stat_prompt = _load_prompt_template("REGULATORY_GUIDELINE")
    assert "atomic obligations" in stat_prompt.lower()

    pol_prompt = _load_prompt_template("ENTERPRISE_POLICY")
    assert "control_objectives" in pol_prompt

    sop_prompt = _load_prompt_template("PROCEDURE_SOP")
    assert "control_activities" in sop_prompt

    # Test case-insensitivity fallback
    lower_pol_prompt = _load_prompt_template("enterprise_policy")
    assert "control_objectives" in lower_pol_prompt


def test_parse_llm_response_control_objectives():
    """
    Test parsing control_objectives for ENTERPRISE_POLICY document_type.
    """
    raw_json = json.dumps({
        "control_objectives": [
            {
                "id": "POL-IAM-OBJ-01",
                "prose": "The Information Security Team shall establish multi-factor authentication controls to satisfy AccessControl.",
                "action_verb": "establish",
                "subject_noun": "Information Security Team",
                "domain_facet": "AccessControl",
                "clause_ref": "Section 4.1",
            }
        ]
    })
    results = _parse_llm_response(raw_json, document_type="ENTERPRISE_POLICY")
    assert len(results) == 1
    assert isinstance(results[0], ControlObjective)
    assert results[0].id == "POL-IAM-OBJ-01"
    assert results[0].domain_facet == "AccessControl"


def test_parse_llm_response_control_activities():
    """
    Test parsing control_activities for PROCEDURE_SOP document_type.
    """
    raw_json = json.dumps({
        "control_activities": [
            {
                "id": "SOP-IAM-ACT-01",
                "prose": "The System Administrator must execute quarterly user access reviews using IAM Portal.",
                "action_verb": "execute",
                "subject_noun": "System Administrator",
                "execution_type": "MANUAL",
                "frequency": "QUARTERLY",
                "clause_ref": "Step 4.2",
            }
        ]
    })
    results = _parse_llm_response(raw_json, document_type="PROCEDURE_SOP")
    assert len(results) == 1
    assert isinstance(results[0], ControlActivity)
    assert results[0].id == "SOP-IAM-ACT-01"
    assert results[0].execution_type == "MANUAL"
    assert results[0].frequency == "QUARTERLY"


def test_parse_llm_response_invalid_json_graceful():
    """
    QA Edge Case: Verify invalid JSON returns empty list without exception.
    """
    bad_json = "NOT_JSON_RESPONSE"
    assert _parse_llm_response(bad_json, document_type="ENTERPRISE_POLICY") == []
    assert _parse_llm_response(bad_json, document_type="PROCEDURE_SOP") == []


def test_extraction_request_document_type_field():
    """
    Test ExtractionRequest schema contains document_type field.
    """
    req = ExtractionRequest(
        markdown_content="# Section 1\nTest",
        document_type="ENTERPRISE_POLICY"
    )
    assert req.document_type == "ENTERPRISE_POLICY"
