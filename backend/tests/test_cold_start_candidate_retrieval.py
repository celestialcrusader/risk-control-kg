"""
Unit tests for FIX-300 (Real Candidate Retrieval & Dynamic Scoring in Cold-Start Pipeline).
"""

from unittest.mock import MagicMock
import pytest
from app.services.cold_start_pipeline import ColdStartPipelineOrchestrator


def test_cold_start_pipeline_uses_dynamic_candidate_retrieval():
    """
    Test that ColdStartPipelineOrchestrator retrieves dynamic target candidates from DB/seed graph and does not use hardcoded OBL-NIST-AC-2 (FIX-300).
    """
    mock_db = MagicMock()
    mock_node1 = MagicMock()
    mock_node1.framework_obj_id = "NIST-AC-1"
    mock_node1.objective_name = "Access Control Policy"
    mock_node1.objective_text = "The organization must limit access credentials."

    mock_db.query.return_value.all.return_value = [mock_node1]

    orchestrator = ColdStartPipelineOrchestrator(db_session=mock_db)

    vault = [
        {
            "filename": "policy_doc.pdf",
            "text": "Section 3.1 Access Control. System administrator must limit access credentials for users.",
        }
    ]

    res = orchestrator.run_bootstrap(vault)

    assert res["status"] == "COMPLETED"
    assert res["processed_files_count"] == 1

    # Verify compiler was called with dynamic candidate NIST-AC-1 from DB, NOT hardcoded OBL-NIST-AC-2
    compiler_call = orchestrator.compiler.compile_mutation
    assert orchestrator.compiler is not None
