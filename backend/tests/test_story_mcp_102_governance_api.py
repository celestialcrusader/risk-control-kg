"""
TDD Unit and Integration Tests for STORY-MCP-102:
Governance, Gap Analytics & Realtime Evaluation Endpoints
(/api/v1/gaps, /api/v1/coverage/summary, /api/v1/evaluation/realtime)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_get_gaps_categorized(client):
    response = client.get("/api/v1/gaps?framework=MAS-TRM")
    assert response.status_code == 200
    data = response.json()
    assert "category_a_unmatched" in data
    assert "category_b_retail_mandates" in data
    assert "total_true_gaps" in data
    
    # Category B must include the retail consumer mandates
    cat_b_ids = [item["obligation_id"] for item in data["category_b_retail_mandates"]]
    assert "MAS-14.3.3.a" in cat_b_ids
    assert "MAS-14.3.3.b" in cat_b_ids
    assert "MAS-14.4.2" in cat_b_ids
    assert "MAS-14.4.3" in cat_b_ids
    
    for item in data["category_b_retail_mandates"]:
        assert "audit_root_cause" in item
        assert "statement_text" in item


def test_get_coverage_summary(client):
    response = client.get("/api/v1/coverage/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_obligations" in data
    assert "active_controls" in data
    assert "total_linkages" in data
    assert "coverage_rates" in data
    assert "full_coverage_pct" in data["coverage_rates"]
    assert "partial_coverage_pct" in data["coverage_rates"]
    assert "no_coverage_pct" in data["coverage_rates"]
    assert "chapter_breakdown" in data
    assert len(data["chapter_breakdown"]) > 0
    assert data["total_obligations"] == 85
    assert data["active_controls"] == 294


def test_post_evaluation_realtime(client):
    payload = {
        "source_text": "The Financial Institution must enforce segregation of duties in the software release process.",
        "target_text": "NIST-AC-5 Separation of Duties: Define system access authorizations to support separation of duties."
    }
    response = client.post("/api/v1/evaluation/realtime", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "semantic_relation" in data
    assert "assurance_coverage" in data
    assert "confidence_score" in data
    assert "rationale" in data
    assert data["confidence_score"] > 0.5
