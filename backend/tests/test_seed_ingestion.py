"""
TDD Integration Tests for Open-Source Compliance Seed Ingestion (RCKG-101).

Validates NistOlirXmlParser, CcmExcelParser, and ComplianceSeedIngester
according to docs/03-mvp/nist-olir-schema-mapping.md.
"""

import tempfile
import xml.etree.ElementTree as ET
import pytest
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.models.rckg_nodes import (
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    ControlObjectiveFrameworkMapping,
    SetTheoryRelation,
)


SAMPLE_NIST_OLIR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<OLIRDataExport xmlns="http://csrc.nist.gov/ns/olir/1.0">
  <InformativeReference id="REF-NIST-ISO-001">
    <FocalDocument>
      <DocumentIdentifier>NIST SP 800-53</DocumentIdentifier>
      <SectionIdentifier>AC-2</SectionIdentifier>
      <Identifier>NIST-800-53-AC-2</Identifier>
      <Title>Account Management</Title>
      <Description>The organization manages information system accounts.</Description>
    </FocalDocument>
    <ReferencedDocument>
      <DocumentIdentifier>ISO/IEC 27001</DocumentIdentifier>
      <SectionIdentifier>A.5.15</SectionIdentifier>
      <Identifier>ISO-27001-A.5.15</Identifier>
      <Title>Access Control</Title>
      <Description>Rules to control physical and logical access shall be established.</Description>
    </ReferencedDocument>
    <MappingRationale>
      <RelationshipType>EQUIVALENT_TO</RelationshipType>
      <Strength>1.0</Strength>
    </MappingRationale>
  </InformativeReference>
</OLIRDataExport>
"""


@pytest.fixture
def temp_nist_xml_file():
    """Fixture creating temporary NIST OLIR XML file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(SAMPLE_NIST_OLIR_XML)
        temp_path = f.name

    yield temp_path

    # Teardown
    Path(temp_path).unlink(missing_ok=True)


def test_nist_olir_xml_parser(temp_nist_xml_file):
    """AC-1: Verify NistOlirXmlParser extracts focal and referenced elements."""
    from backend.app.services.seed_ingestion import NistOlirXmlParser

    parser = NistOlirXmlParser(temp_nist_xml_file)
    parsed = parser.parse()

    assert "nodes" in parsed
    assert "edges" in parsed
    assert len(parsed["nodes"]) == 2
    assert len(parsed["edges"]) == 1

    focal_node = next(n for n in parsed["nodes"] if n["framework_obj_id"] == "NIST-800-53-AC-2")
    assert focal_node["framework_name"] == "NIST SP 800-53"
    assert focal_node["objective_name"] == "Account Management"

    edge = parsed["edges"][0]
    assert edge["source_id"] == "NIST-800-53-AC-2"
    assert edge["target_id"] == "ISO-27001-A.5.15"
    assert edge["relation"] == SetTheoryRelation.EQUIVALENT_TO.value
    assert edge["is_golden"] is True
    assert edge["status"] == "HUMAN_ATTESTED"


def test_compliance_seed_ingester(temp_nist_xml_file, db_session):
    """AC-3 & AC-4: Verify ComplianceSeedIngester writes framework nodes and edges to DB."""
    from backend.app.services.seed_ingestion import ComplianceSeedIngester

    ingester = ComplianceSeedIngester(db_session=db_session)
    stats = ingester.ingest_file(source_type="NIST_OLIR", file_path=temp_nist_xml_file)

    assert stats["nodes"] == 2
    assert stats["edges"] == 1

    # Verify PostgreSQL DB records created
    nodes = db_session.query(FrameworkControlObjectiveNode).all()
    assert len(nodes) == 2

    nist_node = db_session.query(FrameworkControlObjectiveNode).filter_by(framework_obj_id="NIST-800-53-AC-2").first()
    assert nist_node is not None
    assert nist_node.framework_name == "NIST SP 800-53"
    assert nist_node.objective_name == "Account Management"
