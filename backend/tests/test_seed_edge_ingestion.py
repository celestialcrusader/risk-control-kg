"""
Unit tests for FIX-200 (Seed Edge Persistence in Seed Ingestion).
"""

from unittest.mock import MagicMock
import pytest
from app.services.seed_ingestion import ComplianceSeedIngester, NistOlirXmlParser


def test_seed_ingestion_persists_edges(tmp_path):
    """
    Test that ComplianceSeedIngester persists both nodes AND edges (FIX-200).
    """
    # Create sample XML content matching NIST OLIR structure
    sample_xml = tmp_path / "sample_olir.xml"
    sample_xml.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <olir>
            <entry>
                <id>NIST-800-53-AC-1</id>
                <framework>NIST SP 800-53</framework>
                <version>Rev 5</version>
                <title>Access Control Policy and Procedures</title>
                <text>The organization must develop and document access control policy.</text>
            </entry>
            <entry>
                <id>ISO-27001-A5.15</id>
                <framework>ISO/IEC 27001</framework>
                <version>2022</version>
                <title>Access Control</title>
                <text>Rules to control physical and logical access to information.</text>
            </entry>
            <relationship>
                <source_id>NIST-800-53-AC-1</source_id>
                <target_id>ISO-27001-A5.15</target_id>
                <relation>EQUIVALENT_TO</relation>
            </relationship>
        </olir>
        """
    )

    mock_db = MagicMock()
    ingester = ComplianceSeedIngester(mock_db)

    # Mock NistOlirXmlParser to return nodes and edges deterministically
    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            "app.services.seed_ingestion.NistOlirXmlParser.parse",
            lambda self: {
                "nodes": [
                    {
                        "framework_obj_id": "NIST-800-53-AC-1",
                        "framework_name": "NIST SP 800-53",
                        "framework_version": "Rev 5",
                        "objective_name": "Access Control Policy and Procedures",
                        "objective_text": "Develop policy",
                    },
                    {
                        "framework_obj_id": "ISO-27001-A5.15",
                        "framework_name": "ISO/IEC 27001",
                        "framework_version": "2022",
                        "objective_name": "Access Control",
                        "objective_text": "Access control rules",
                    },
                ],
                "edges": [
                    {
                        "source_id": "NIST-800-53-AC-1",
                        "target_id": "ISO-27001-A5.15",
                        "relation": "EQUIVALENT_TO",
                        "is_golden": True,
                        "status": "HUMAN_ATTESTED",
                    }
                ],
            },
        )

        res = ingester.ingest_file("NIST_OLIR", str(sample_xml))
        assert res["nodes"] == 2
        assert res["edges"] == 1

        # Check DB calls: merge called for 2 nodes + 1 edge mapping
        assert mock_db.merge.call_count >= 3
