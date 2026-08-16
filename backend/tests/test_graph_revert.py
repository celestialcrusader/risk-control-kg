"""
TDD Tests for Bitemporal Graph Revert Endpoint & Audit Trail Service (RCKG-403).
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.api.extract import router as extract_router
from app.services.graph_revert_service import GraphRevertService, RevertResult

app = FastAPI()
app.include_router(extract_router, prefix="/api/v1")
client = TestClient(app)


def test_graph_revert_service_execution():
    """AC-1, AC-2, AC-3: Execute revert operation and attach audit trail metadata."""
    revert_service = GraphRevertService(current_release="v1.1.0")

    result = revert_service.execute_revert(
        diff_id="DIFF-8921",
        auditor_id="AUDITOR-007",
        revert_reason="False positive edge reclassification detected during compliance review",
    )

    assert isinstance(result, RevertResult)
    assert result.status == "REVERTED"
    assert result.auditor_id == "AUDITOR-007"
    assert result.release_tag == "v1.2.0 [REVERT DIFF-8921]"
    assert result.reverted_at is not None


def test_graph_revert_api_endpoint():
    """AC-1: REST endpoint POST /api/v1/graph/revert executes revert operation."""
    payload = {
        "diff_id": "DIFF-8921",
        "auditor_id": "AUDITOR-007",
        "revert_reason": "False positive edge reclassification detected during compliance review",
    }
    response = client.post("/api/v1/graph/revert", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REVERTED"
    assert "release_tag" in data
