"""
TDD Unit Tests for STORY-MCP-203:
MCP Resources, Prompts & Contextual Audit Templates
"""
import pytest
from app.mcp_server.server import (
    get_governance_summary_resource,
    get_true_gaps_resource,
    audit_crosswalk_review,
    gap_remediation_planner
)


def test_mcp_governance_summary_resource():
    text = get_governance_summary_resource()
    assert isinstance(text, str)
    assert "Pure RCKG Governance Status" in text
    assert "Total MAS TRM Obligations: 85" in text
    assert "Active NIST SP 800-53 Controls: 294" in text


def test_mcp_true_gaps_resource():
    text = get_true_gaps_resource()
    assert isinstance(text, str)
    assert "Category B: Retail Consumer Mandates" in text
    assert "MAS-14.3.3.a" in text
    assert "MAS-14.4.2" in text


def test_mcp_audit_crosswalk_review_prompt():
    prompt = audit_crosswalk_review("MAS-7.6.1")
    assert isinstance(prompt, str)
    assert "MAS-7.6.1" in prompt
    assert "query_crosswalk_mapping" in prompt
    assert "override_crosswalk_mapping" in prompt


def test_mcp_gap_remediation_planner_prompt():
    prompt = gap_remediation_planner()
    assert isinstance(prompt, str)
    assert "get_compliance_gaps" in prompt
    assert "Category B" in prompt
    assert "RACI" in prompt
