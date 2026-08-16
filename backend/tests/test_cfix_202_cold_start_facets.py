"""
TDD Unit Test for CFIX-202: Dynamic Candidate Facet Extraction in Cold-Start Pipeline.
"""

from unittest.mock import MagicMock, patch
import pytest
from app.services.cold_start_pipeline import ColdStartPipelineOrchestrator


def test_cold_start_pipeline_extracts_dynamic_candidate_facets():
    """Verify ColdStartPipelineOrchestrator calls facet extractor for candidates dynamically instead of hardcoding facets."""
    mock_db = MagicMock()
    mock_node = MagicMock()
    mock_node.framework_obj_id = "NIST-IA-2"
    mock_node.objective_name = "Multi-Factor Authentication"
    mock_node.objective_text = "The organization shall implement multi-factor authentication for network access."
    mock_db.query.return_value.all.return_value = [mock_node]

    orchestrator = ColdStartPipelineOrchestrator(db_session=mock_db)
    
    extracted_facets = {
        "action_verb": "implement",
        "subject_noun": "multi-factor authentication",
        "domain_facet": "AccessControl",
        "modality_facet": "MANDATORY",
        "target_role_facet": "SYSTEM_ADMINISTRATOR",
        "control_nature": "PREVENTATIVE",
        "extraction_method": "LLM",
    }

    with patch.object(orchestrator.facet_extractor, "extract_facets", return_value=extracted_facets) as mock_extract:
        vault = [{"filename": "policy.pdf", "text": "Organizations must enforce access control."}]
        res = orchestrator.run_bootstrap(vault)
        
        assert res["status"] == "COMPLETED"
        assert mock_extract.called
        # Verify candidate passed to facet extractor was objective_text
        calls = [call.args[0] for call in mock_extract.call_args_list]
        assert mock_node.objective_text in calls
