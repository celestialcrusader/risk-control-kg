"""
Unit Tests for NIST SP 800-53 Rev 5 OSCAL YAML Parser (STORY-FOUNDATION-101).
"""

import pytest
import os
from pathlib import Path
from app.services.parsers.oscal_parser import OscalYamlCatalogParser


SAMPLE_OSCAL_YAML = """
catalog:
  uuid: 5ba2a3ba-1aa2-47d8-ad69-5beef7372b98
  metadata:
    title: NIST SP 800-53 Rev 5.2.0
    version: 5.2.0
    oscal-version: 1.1.3
  groups:
    - id: ac
      title: Access Control
      controls:
        - id: ac-1
          title: Policy and Procedures
          parts:
            - id: ac-1_smt
              name: statement
              prose: The organization develops, documents, and disseminates access control policies.
        - id: ac-2
          title: Account Management
          parts:
            - id: ac-2_smt
              name: statement
              prose: The organization manages information system accounts.
          controls:
            - id: ac-2.1
              title: Automated System Account Management
              parts:
                - id: ac-2.1_smt
                  name: statement
                  prose: The organization employs automated mechanisms to support account management.
"""


@pytest.fixture
def sample_oscal_file(tmp_path):
    f = tmp_path / "sample_oscal.yaml"
    f.write_text(SAMPLE_OSCAL_YAML)
    return str(f)


def test_oscal_parser_extracts_objectives_and_activities(sample_oscal_file):
    """Verify OSCAL parser extracts top-level controls as objectives and sub-controls as activities."""
    parser = OscalYamlCatalogParser(sample_oscal_file)
    result = parser.parse()

    assert "objectives" in result
    assert "activities" in result
    assert "edges" in result

    # Check Objectives
    objectives = result["objectives"]
    assert len(objectives) == 2
    ac1 = next(o for o in objectives if o["framework_obj_id"] == "NIST-AC-1")
    assert ac1["objective_name"] == "Policy and Procedures"
    assert "access control policies" in ac1["objective_text"]

    ac2 = next(o for o in objectives if o["framework_obj_id"] == "NIST-AC-2")
    assert ac2["objective_name"] == "Account Management"

    # Check Activities (Enhancements)
    activities = result["activities"]
    assert len(activities) == 1
    ac2_1 = activities[0]
    assert ac2_1["framework_act_id"] == "NIST-AC-2.1"
    assert ac2_1["activity_name"] == "Automated System Account Management"
    assert "automated mechanisms" in ac2_1["activity_text"]

    # Check Edges (Parent-child hierarchy)
    edges = result["edges"]
    assert len(edges) == 1
    assert edges[0]["source_id"] == "NIST-AC-2"
    assert edges[0]["target_id"] == "NIST-AC-2.1"
    assert edges[0]["relation"] == "REFINES"


def test_real_nist_oscal_yaml_catalog_parse():
    """Verify parsing of the actual data/test-docs/NIST_SP-800-53_rev5_catalog.yaml file."""
    real_path = "data/test-docs/NIST_SP-800-53_rev5_catalog.yaml"
    if not os.path.exists(real_path):
        pytest.skip(f"{real_path} not found")

    parser = OscalYamlCatalogParser(real_path)
    result = parser.parse()

    assert len(result["objectives"]) >= 200
    assert len(result["activities"]) >= 500
    assert len(result["edges"]) >= 500

    # Verify specific controls
    ac2 = next((o for o in result["objectives"] if "AC-2" in o["framework_obj_id"]), None)
    assert ac2 is not None
    assert "Account Management" in ac2["objective_name"]

