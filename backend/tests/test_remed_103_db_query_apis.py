"""
TDD Unit/Integration Test for REMED-103: DB-Backed Gap Query & Reasoning Trace APIs.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from app.models import AuditLog
from app.models.rckg_nodes import GapNode, GraphOutboxLog
import app.api.gaps as gaps_mod
import app.api.controls as controls_mod


@pytest.fixture
def client_with_db(db_session):
    """FastAPI TestClient with overridden get_db dependency to use isolated test DB session."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_remed_103_no_in_memory_stores_exist():
    """Verify legacy _GAPS_STORE and _MAPPINGS_STORE dictionaries are completely removed."""
    assert not hasattr(gaps_mod, "_GAPS_STORE"), "_GAPS_STORE mock dictionary must be removed"
    assert not hasattr(controls_mod, "_MAPPINGS_STORE"), "_MAPPINGS_STORE mock dictionary must be removed"


def test_remed_103_gaps_api_queries_database(client_with_db, db_session):
    """Verify GET /api/v1/gaps queries live database GapNode records."""
    gap1 = GapNode(
        gap_id="GAP-REMED-103-HIGH",
        severity="HIGH",
        source_obligation_id="OBL-103-A",
        source_obligation_text="System shall log all access.",
        target_control_text="Log user logins.",
        set_theory_relation="NO_RELATIONSHIP",
        clause_citation="AU-2",
        framework="NIST-800-53",
    )
    gap2 = GapNode(
        gap_id="GAP-REMED-103-MED",
        severity="MEDIUM",
        source_obligation_id="OBL-103-B",
        source_obligation_text="Encrypt keys using KMS.",
        target_control_text="Encrypt volume at rest.",
        set_theory_relation="SUBSET_OF",
        clause_citation="SC-28",
        framework="NIST-800-53",
    )
    db_session.add_all([gap1, gap2])
    db_session.commit()

    # Query all gaps
    res = client_with_db.get("/api/v1/gaps")
    assert res.status_code == 200
    data = res.json()
    gap_ids = [g["gap_id"] for g in data]
    assert "GAP-REMED-103-HIGH" in gap_ids
    assert "GAP-REMED-103-MED" in gap_ids

    # Query severity=HIGH filter
    res_high = client_with_db.get("/api/v1/gaps?severity=HIGH")
    assert res_high.status_code == 200
    data_high = res_high.json()
    assert all(g["severity"] == "HIGH" for g in data_high)
    assert any(g["gap_id"] == "GAP-REMED-103-HIGH" for g in data_high)
    assert not any(g["gap_id"] == "GAP-REMED-103-MED" for g in data_high)


def test_remed_103_gap_trace_api_returns_live_provenance(client_with_db, db_session):
    """Verify GET /api/v1/gaps/{id}/trace constructs trace from live DB tables."""
    gap = GapNode(
        gap_id="GAP-TRACE-TEST",
        severity="HIGH",
        source_obligation_id="OBL-TRACE-1",
        source_obligation_text="Multi-factor authentication must be enabled.",
        target_control_text="Basic password authentication.",
        set_theory_relation="NO_RELATIONSHIP",
        clause_citation="IA-2",
        framework="NIST-800-53",
    )
    outbox = GraphOutboxLog(
        primitive="CREATE_GAP",
        payload={
            "source_id": "OBL-TRACE-1",
            "target_id": "IA-2",
            "source_text": "Multi-factor authentication must be enabled.",
        },
        status="EXECUTED",
        judge_logic_score=0.98,
        judge_technical_score=1.00,
    )
    db_session.add_all([gap, outbox])
    db_session.commit()

    res = client_with_db.get("/api/v1/gaps/GAP-TRACE-TEST/trace")
    assert res.status_code == 200
    trace = res.json()
    assert trace["gap_id"] == "GAP-TRACE-TEST"
    assert trace["extracted_obligation"]["prose"] == "Multi-factor authentication must be enabled."
    assert trace["judge_scores"]["logic_score"] == 0.98
    assert trace["judge_scores"]["technical_score"] == 1.00


def test_remed_103_gap_trace_404_on_non_existent(client_with_db):
    """Verify 404 response on non-existent gap_id."""
    res = client_with_db.get("/api/v1/gaps/NON_EXISTENT_GAP_ID_999/trace")
    assert res.status_code == 404


def test_remed_103_control_mappings_api_queries_outbox(client_with_db, db_session):
    """Verify GET /api/v1/controls/{control_id}/mappings queries outbox entries."""
    outbox = GraphOutboxLog(
        primitive="ADD_EDGE",
        payload={
            "source_id": "OBL-MAP-01",
            "target_id": "CTRL-AC-2",
            "source_text": "Enforce MFA for all user logins.",
            "framework": "NIST-800-53",
            "set_theory_relation": "EQUIVALENT_TO",
            "confidence_score": 0.96,
        },
        status="APPROVED",
        judge_logic_score=0.97,
        judge_technical_score=1.00,
    )
    db_session.add(outbox)
    db_session.commit()

    res = client_with_db.get("/api/v1/controls/CTRL-AC-2/mappings")
    assert res.status_code == 200
    mappings = res.json()
    assert len(mappings) >= 1
    target_mapping = next((m for m in mappings if m["obligation_id"] == "OBL-MAP-01"), None)
    assert target_mapping is not None
    assert target_mapping["set_theory_relation"] == "EQUIVALENT_TO"
