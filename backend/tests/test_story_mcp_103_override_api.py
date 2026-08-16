"""
TDD Unit and Integration Tests for STORY-MCP-103:
Auditor Override & Immutable Audit Log Endpoint
(POST /api/v1/mappings/{id}/override, GET /api/v1/audit-logs)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.rckg_nodes import ObligationFrameworkMapping, SemanticRelation, AssuranceCoverage


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_auditor_override_and_audit_log(client):
    # 1. Fetch a mapping to test override on
    db = SessionLocal()
    mapping = db.query(ObligationFrameworkMapping).first()
    assert mapping is not None
    mapping_id = str(mapping.id)
    old_rel = mapping.semantic_relation.value
    old_cov = mapping.assurance_coverage.value
    db.close()
    
    # 2. Submit auditor override
    override_payload = {
        "semantic_relation": "EQUIVALENT",
        "assurance_coverage": "FULL_COVERAGE",
        "auditor_id": "auditor-lead-007",
        "justification": "Verified comprehensive technical control equivalence during Q3 audit."
    }
    
    response = client.post(f"/api/v1/mappings/{mapping_id}/override", json=override_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["id"] == mapping_id
    assert res_data["semantic_relation"] == "EQUIVALENT"
    assert res_data["assurance_coverage"] == "FULL_COVERAGE"
    assert res_data["override_applied"] is True
    
    # 3. Query immutable audit logs
    audit_resp = client.get("/api/v1/audit-logs?event_type=MAPPING_AUDITOR_OVERRIDE")
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert audit_data["total"] >= 1
    
    # Verify latest audit log content
    latest_event = audit_data["items"][0]
    assert latest_event["event_type"] == "MAPPING_AUDITOR_OVERRIDE"
    assert latest_event["actor_id"] == "auditor-lead-007"
    assert latest_event["event_data"]["mapping_id"] == mapping_id
    assert latest_event["event_data"]["new_relation"] == "EQUIVALENT"
    assert latest_event["event_data"]["new_coverage"] == "FULL_COVERAGE"
    assert "Q3 audit" in latest_event["event_data"]["justification"]


def test_auditor_override_invalid_id(client):
    invalid_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "semantic_relation": "SUBSET_OF",
        "assurance_coverage": "PARTIAL_COVERAGE",
        "auditor_id": "auditor-lead-007",
        "justification": "Invalid test"
    }
    response = client.post(f"/api/v1/mappings/{invalid_id}/override", json=payload)
    assert response.status_code == 404
