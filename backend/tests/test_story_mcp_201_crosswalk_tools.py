"""
TDD Unit Tests for STORY-MCP-201:
FastMCP Server Architecture & Crosswalk Tool Implementation
"""
from app.mcp_server.server import (
    query_obligations,
    query_controls,
    query_crosswalk_mapping
)


def test_mcp_query_obligations():
    result = query_obligations(framework="MAS-TRM", limit=5)
    assert "total" in result
    assert len(result["items"]) <= 5
    assert any("MAS" in item["obligation_id"] for item in result["items"])


def test_mcp_query_controls_active():
    result = query_controls(active_only=True, limit=10)
    assert "total" in result
    assert result["total"] == 294
    # Ensure withdrawn controls are not present
    ctrl_ids = [item["framework_obj_id"] for item in result["items"]]
    assert "NIST-RA-4" not in ctrl_ids
    assert "NIST-SA-12" not in ctrl_ids


def test_mcp_query_crosswalk_mapping():
    result = query_crosswalk_mapping(source_id="MAS-7.6.1")
    assert "items" in result
    assert len(result["items"]) >= 1
    mapping = result["items"][0]
    assert mapping["target_id"] == "NIST-AC-5"
    assert mapping["semantic_relation"] == "SUBSET_OF"
    assert mapping["assurance_coverage"] == "FULL_COVERAGE"
    assert "rationale" in mapping
