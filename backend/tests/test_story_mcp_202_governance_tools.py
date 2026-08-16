"""
TDD Unit Tests for STORY-MCP-202:
Governance Analytics, Gap Inspection & Realtime Evaluation MCP Tools
"""
import pytest
from app.mcp_server.server import (
    get_coverage_analytics,
    get_compliance_gaps,
    evaluate_compliance_crosswalk,
    override_crosswalk_mapping
)
from app.core.database import SessionLocal
from app.models.rckg_nodes import ObligationFrameworkMapping


def test_mcp_get_coverage_analytics():
    result = get_coverage_analytics()
    assert "total_obligations" in result
    assert "active_controls" in result
    assert "total_linkages" in result
    assert "rates" in result
    assert result["total_obligations"] == 85
    assert result["active_controls"] == 294
    assert result["rates"]["full_coverage_pct"] > 0


def test_mcp_get_compliance_gaps():
    result = get_compliance_gaps(framework="MAS-TRM")
    assert "total_true_gaps" in result
    assert "category_a_unmatched" in result
    assert "category_b_retail_mandates" in result
    
    cat_b_ids = [item["obligation_id"] for item in result["category_b_retail_mandates"]]
    assert "MAS-14.3.3.a" in cat_b_ids
    assert "MAS-14.3.3.b" in cat_b_ids
    assert "MAS-14.4.2" in cat_b_ids
    assert "MAS-14.4.3" in cat_b_ids


def test_mcp_evaluate_compliance_crosswalk():
    source_text = "The Financial Institution must enforce segregation of duties in the software release process."
    target_text = "NIST-AC-5 Separation of Duties: Define system access authorizations to support separation of duties."
    
    result = evaluate_compliance_crosswalk(source_text, target_text, source_id="MAS-7.6.1", target_id="NIST-AC-5")
    assert "semantic_relation" in result
    assert "assurance_coverage" in result
    assert "confidence_score" in result
    assert "rationale" in result
    assert result["semantic_relation"] == "SUBSET_OF"
    assert result["assurance_coverage"] == "FULL_COVERAGE"


def test_mcp_override_crosswalk_mapping():
    db = SessionLocal()
    mapping = db.query(ObligationFrameworkMapping).first()
    assert mapping is not None
    m_id = str(mapping.id)
    db.close()
    
    result = override_crosswalk_mapping(
        mapping_id=m_id,
        semantic_relation="EQUIVALENT",
        assurance_coverage="FULL_COVERAGE",
        auditor_id="mcp-agent-auditor",
        justification="MCP tool automated audit adjustment."
    )
    assert result["override_applied"] is True
    assert result["semantic_relation"] == "EQUIVALENT"
    assert result["assurance_coverage"] == "FULL_COVERAGE"
    assert result["auditor_id"] == "mcp-agent-auditor"
