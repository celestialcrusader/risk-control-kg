"""
Unit Tests for Configurable Multi-Sheet Excel Compliance Matrix Parser (STORY-FOUNDATION-102).
"""

import pytest
import os
import openpyxl
from app.services.parsers.excel_matrix_parser import ConfigurableExcelParser


@pytest.fixture
def sample_excel_file(tmp_path):
    f = tmp_path / "sample_matrix.xlsx"
    wb = openpyxl.Workbook()
    
    # Sheet 1: Banner row + data
    ws1 = wb.active
    ws1.title = "Access Controls"
    ws1.append(["BANNER METADATA", "CONFIDENTIAL", None])
    ws1.append(["Control ID", "Control Name", "Description"])
    ws1.append(["AC-01", "Access Policy", "The organization maintains access policy."])
    ws1.append(["AC-02", "MFA Enforcement", "The organization enforces MFA."])

    # Sheet 2: Data directly
    ws2 = wb.create_sheet(title="Audit Controls")
    ws2.append(["Control ID", "Control Name", "Description"])
    ws2.append(["AU-01", "Audit Logging", "The organization logs audit events."])

    wb.save(str(f))
    return str(f)


def test_configurable_excel_parser_custom_offset_and_columns(sample_excel_file):
    """Verify parser handles custom header row offset and column mappings."""
    parser = ConfigurableExcelParser(
        file_path=sample_excel_file,
        framework_name="SAMPLE_FW",
        framework_version="v1",
        id_col="Control ID",
        title_col="Control Name",
        text_col="Description",
        header_row_offset=2,
        sheets=["Access Controls"],
    )
    result = parser.parse()
    nodes = result["nodes"]

    assert len(nodes) == 2
    assert nodes[0]["framework_obj_id"] == "SAMPLE_FW:AC-01"
    assert nodes[0]["objective_name"] == "Access Policy"
    assert "access policy" in nodes[0]["objective_text"]

    assert nodes[1]["framework_obj_id"] == "SAMPLE_FW:AC-02"


def test_configurable_excel_parser_multisheet_traversal(sample_excel_file):
    """Verify parser traverses all sheets when sheets=['*']."""
    parser = ConfigurableExcelParser(
        file_path=sample_excel_file,
        framework_name="SAMPLE_FW",
        framework_version="v1",
        id_col="Control ID",
        title_col="Control Name",
        text_col="Description",
        header_row_offset=2,
        sheets=["*"],
    )
    result = parser.parse()
    nodes = result["nodes"]

    assert len(nodes) >= 2
    sheet_categories = {n["sheet_category"] for n in nodes}
    assert "Access Controls" in sheet_categories


def test_real_aicm_excel_parsing():
    """Verify parsing of real aicm.xlsx in test-docs folder."""
    real_path = "data/test-docs/aicm.xlsx"
    if not os.path.exists(real_path):
        pytest.skip(f"{real_path} not found")

    parser = ConfigurableExcelParser(
        file_path=real_path,
        framework_name="CSA_AICM",
        framework_version="v1.0.3",
        id_col="Control ID",
        title_col="Control Title",
        text_col="Control Specification",
        header_row_offset=3,
    )
    result = parser.parse()
    nodes = result["nodes"]
    assert len(nodes) >= 50
    # Verify sample control
    first_node = nodes[0]
    assert "CSA_AICM:" in first_node["framework_obj_id"]
    assert len(first_node["objective_text"]) > 10


def test_real_audit_toolkit_excel_parsing():
    """Verify parsing of Artificial Intelligence Audit Toolkit_Workbook.xlsx."""
    real_path = "data/test-docs/Artificial Intelligence Audit Toolkit_Workbook.xlsx"
    if not os.path.exists(real_path):
        pytest.skip(f"{real_path} not found")

    parser = ConfigurableExcelParser(
        file_path=real_path,
        framework_name="AI_AUDIT_TOOLKIT",
        framework_version="1.0",
        id_col="Control Number",
        title_col="Control Name",
        text_col="AI-Specific Description",
        header_row_offset=1,
    )
    result = parser.parse()
    nodes = result["nodes"]
    assert len(nodes) >= 30
    assert "AI_AUDIT_TOOLKIT:ADR-DM-01" in [n["framework_obj_id"] for n in nodes]


def test_real_aivtf_excel_parsing():
    """Verify parsing of 11-sheet aivtf-excel.xlsx."""
    real_path = "data/test-docs/aivtf-excel.xlsx"
    if not os.path.exists(real_path):
        pytest.skip(f"{real_path} not found")

    parser = ConfigurableExcelParser(
        file_path=real_path,
        framework_name="AIVTF",
        framework_version="1.0",
        id_col="Transparency",  # First column in sheet
        title_col="Transparency",
        text_col="Transparency",
        header_row_offset=1,
        sheets=["*"],
    )
    result = parser.parse()
    nodes = result["nodes"]
    assert len(nodes) >= 10
    categories = {n["sheet_category"] for n in nodes}
    assert len(categories) >= 5

