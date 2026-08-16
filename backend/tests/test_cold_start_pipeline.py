import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from fastapi.testclient import TestClient
from app.services.cold_start_pipeline import ColdStartPipelineOrchestrator



@pytest.fixture
def orchestrator(db_session):
    return ColdStartPipelineOrchestrator(db_session=db_session)


def test_cold_start_bootstrap_pipeline_5_sample_files(orchestrator):
    """AC-1 & AC-5: Ingest 5 sample files end-to-end and emit release manifest."""
    document_vault = [
        {
            "filename": "policy_access_control.pdf",
            "bytes": b"%PDF-1.7\nArticle 14.1 Access Provisioning\nSection 3.2 System Administrator must limit access credentials.",
            "text": "Article 14.1 Access Provisioning\nSection 3.2 System Administrator must limit access credentials.",
        },
        {
            "filename": "sop_encryption.pdf",
            "bytes": b"%PDF-1.7\nArticle 14.2 Encryption Requirements\nSystem Administrator must encrypt all stored PII data.",
            "text": "Article 14.2 Encryption Requirements\nSystem Administrator must encrypt all stored PII data.",
        },
        {
            "filename": "matrix_controls.csv",
            "bytes": b"Control ID,Control Name,Status\nAC-1,Policy,Active\nAC-2,Account Management,Active\n",
            "text": "Control ID,Control Name,Status\nAC-1,Policy,Active\nAC-2,Account Management,Active\n",
        },
        {
            "filename": "doc_audit.docx",
            "bytes": b"PK\x03\x04\x14\x00\x06\x00word/document.xml\nSection 5.1 Access Review\nAuditor must review user credentials quarterly.",
            "text": "Section 5.1 Access Review\nAuditor must review user credentials quarterly.",
        },
        {
            "filename": "index_overview.html",
            "bytes": b"<!DOCTYPE html><html><body>Article 1.0 Security Policy\nSecurity officer must monitor system logs.</body></html>",
            "text": "Article 1.0 Security Policy\nSecurity officer must monitor system logs.",
        },
    ]

    res = orchestrator.run_bootstrap(document_vault)

    assert isinstance(res, dict)
    assert res["status"] == "COMPLETED"
    assert "v1.0.0 [COLD_START_BOOTSTRAP]" in res["graph_release"]
    assert res["total_edges_created"] > 0
    assert res["processed_files_count"] == 5


def test_bootstrap_endpoint_api():
    """Verify POST /api/v1/extract/bootstrap endpoint."""
    from fastapi import FastAPI
    from app.api.extract import router as extract_router

    app = FastAPI()
    app.include_router(extract_router, prefix="/api/v1/extract")
    client = TestClient(app)




    payload = [
        {"filename": "test_policy.pdf", "content": "Article 1.0 Access Control Policy\nMust limit access."},
        {"filename": "test_sop.pdf", "content": "Section 2.0 Encryption Policy\nMust encrypt data."},
    ]

    response = client.post("/api/v1/extract/bootstrap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["processed_files_count"] == 2
