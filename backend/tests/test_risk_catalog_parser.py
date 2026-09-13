"""
Unit Tests for Pure Risk Catalog Ingestion Parser (STORY-FOUNDATION-103).
"""

import pytest
import os
import openpyxl
from app.services.parsers.risk_catalog_parser import RiskCatalogParser


@pytest.fixture
def sample_risk_file(tmp_path):
    f = tmp_path / "sample_risk_db.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AI Risk Database v4"
    ws.append(["Banner Line 1", None, None])
    ws.append(["Banner Line 2", None, None])
    ws.append(["Title", "QuickRef", "Ev_ID", "Paper_ID", "Cat_ID", "SubCat_ID", "AddEv_ID", "Category level"])
    ws.append(["Model Inversion Attack on LLMs", "Carlini2023", "01.01.00", "1", "SEC", "PRV", None, "Technical"])
    ws.append(["Data Poisoning in Training Pipelines", "Biggio2022", "01.02.00", "2", "SEC", "INT", None, "Technical"])

    wb.save(str(f))
    return str(f)


def test_risk_catalog_parser_extracts_risk_nodes(sample_risk_file):
    """Verify RiskCatalogParser extracts structured risk dictionaries."""
    parser = RiskCatalogParser(sample_risk_file)
    risks = parser.parse()

    assert len(risks) == 2
    r1 = risks[0]
    assert r1["risk_id"] == "RISK-01.01.00"
    assert "Model Inversion Attack" in r1["risk_name"]
    assert r1["category"] == "Technical"

    r2 = risks[1]
    assert r2["risk_id"] == "RISK-01.02.00"
    assert "Data Poisoning" in r2["risk_name"]


def test_real_ai_risk_database_excel_parsing():
    """Verify parsing of actual data/test-docs/AI risk database.xlsx."""
    real_path = "data/test-docs/AI risk database.xlsx"
    if not os.path.exists(real_path):
        pytest.skip(f"{real_path} not found")

    parser = RiskCatalogParser(real_path)
    risks = parser.parse()

    assert len(risks) >= 100
    assert any("TASRA" in r["risk_name"] or "Risk" in r["risk_name"] or len(r["risk_name"]) > 5 for r in risks)
