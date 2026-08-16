"""
TDD Unit and Integration Tests for STORY-MCP-101:
Canonical Query Endpoints (/api/v1/obligations, /api/v1/controls, /api/v1/crosswalk)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_get_obligations_paginated(client):
    response = client.get("/api/v1/obligations?framework=MAS-TRM&limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 10
    assert len(data["items"]) <= 10
    if len(data["items"]) > 0:
        first = data["items"][0]
        assert "obligation_id" in first
        assert "statement_text" in first
        assert "framework_name" in first


def test_get_controls_active_only(client):
    response = client.get("/api/v1/controls?framework=NIST-SP-800-53&active_only=true&limit=15")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    # Verify no withdrawn controls (e.g., RA-4 or SA-12)
    control_ids = [item["control_id"] for item in data["items"]]
    assert "NIST-RA-4" not in control_ids
    assert "NIST-SA-12" not in control_ids
    if len(data["items"]) > 0:
        first = data["items"][0]
        assert "control_id" in first
        assert "control_name" in first
        assert "control_text" in first


def test_get_crosswalk_filter_by_source(client):
    response = client.get("/api/v1/crosswalk?source_id=MAS-7.6.1")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    
    # Check that NIST-AC-5 is mapped with SUBSET_OF and FULL_COVERAGE
    ac5_match = next((item for item in data["items"] if item["target_id"] == "NIST-AC-5"), None)
    assert ac5_match is not None
    assert ac5_match["source_id"] == "MAS-7.6.1"
    assert ac5_match["semantic_relation"] == "SUBSET_OF"
    assert ac5_match["assurance_coverage"] == "FULL_COVERAGE"
    assert ac5_match["confidence_score"] > 0.70
    assert "rationale" in ac5_match
    assert "Covered:" in ac5_match["rationale"]


def test_get_crosswalk_filter_by_coverage_and_confidence(client):
    response = client.get("/api/v1/crosswalk?assurance_coverage=FULL_COVERAGE&min_confidence=0.80&limit=5")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["assurance_coverage"] == "FULL_COVERAGE"
        assert item["confidence_score"] >= 0.80
