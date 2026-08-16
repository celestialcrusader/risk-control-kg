"""
TDD Unit Test for CFIX-203: Seed Ingestion Node Type Distinction (Objective vs Activity).
"""

from unittest.mock import MagicMock
import pytest
from app.services.seed_ingestion import ComplianceSeedIngester
from app.models import FrameworkControlObjectiveNode, FrameworkControlActivityNode


def test_seed_ingester_distinguishes_base_controls_and_enhancements():
    """Verify base controls like 'AC-2' become FrameworkControlObjectiveNode and enhancements like 'AC-2(1)' become FrameworkControlActivityNode."""
    mock_db = MagicMock()
    ingester = ComplianceSeedIngester(db_session=mock_db)

    parsed_data = {
        "nodes": [
            {
                "framework_obj_id": "AC-2",
                "framework_name": "NIST SP 800-53",
                "framework_version": "Rev 5",
                "objective_name": "Account Management",
                "objective_text": "Manage system accounts.",
            },
            {
                "framework_obj_id": "AC-2(1)",
                "framework_name": "NIST SP 800-53",
                "framework_version": "Rev 5",
                "objective_name": "Automated System Account Management",
                "objective_text": "Employ automated mechanisms to manage accounts.",
            },
        ],
        "edges": [],
    }

    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.services.seed_ingestion.NistOlirXmlParser.parse", lambda self: parsed_data)
        res = ingester.ingest_file("NIST_OLIR", "dummy_file.xml")

        assert res["nodes"] == 2
        # Check merged models
        merged_args = [call.args[0] for call in mock_db.merge.call_args_list]
        obj_nodes = [n for n in merged_args if isinstance(n, FrameworkControlObjectiveNode)]
        act_nodes = [n for n in merged_args if isinstance(n, FrameworkControlActivityNode)]

        assert len(obj_nodes) == 1
        assert obj_nodes[0].framework_obj_id == "AC-2"

        assert len(act_nodes) == 1
        assert act_nodes[0].framework_act_id == "AC-2(1)"
