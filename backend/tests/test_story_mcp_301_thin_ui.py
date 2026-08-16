"""
TDD Unit & Integration Tests for STORY-MCP-301, 302, 303:
Thin Human Governance & Reviewer UI
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_ui_index_served(client):
    response = client.get("/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html = response.text
    
    # Story MCP-301 elements (Dashboard & Heatmap)
    assert "Pure RCKG Governance Portal" in html
    assert "Executive Dashboard" in html
    assert "chapter-heatmap" in html
    assert "gaps-table-body" in html
    
    # Story MCP-302 elements (Matrix & Override Modal)
    assert "Crosswalk Matrix" in html
    assert "matrix-table-body" in html
    assert "override-modal" in html
    assert "override-justification" in html
    
    # Story MCP-303 elements (Playground & Audit Log Viewer)
    assert "NLI Playground" in html
    assert "play-source" in html
    assert "play-target" in html
    assert "Audit Logs" in html
    assert "audit-table-body" in html


def test_static_assets_served(client):
    css_res = client.get("/static/styles.css")
    assert css_res.status_code == 200
    assert "--bg-primary" in css_res.text
    
    js_res = client.get("/static/app.js")
    assert js_res.status_code == 200
    assert "loadDashboardData" in js_res.text
    assert "openOverrideModal" in js_res.text
