"""
Unit & Integration Test Suite for STORY-PARSE-102: Singapore Statutes Online (SSO) HTML DOM Scraper & Parser.
"""

import pytest
from app.services.sso_scraper import parse_sso_html, SSOSectionNode


def test_parse_sso_html_provisions():
    """Verify parsing of HTML provNum, provTitle, and provBody elements."""
    sample_html = """
    <html>
      <body>
        <div class="prov1" id="pr1" data-anchor-id="sec-1">
          <span class="provNum">1.</span>
          <span class="provTitle">Short title and commencement</span>
          <div class="provBody">This Act may be cited as the Technology Risk Management Act.</div>
        </div>
        <div class="prov1" id="pr2" data-anchor-id="sec-2">
          <span class="provNum">2.</span>
          <span class="provTitle">Interpretation</span>
          <div class="provBody">In this Act, "financial institution" means any entity licensed by MAS.</div>
        </div>
      </body>
    </html>
    """
    nodes = parse_sso_html(sample_html)
    assert len(nodes) == 2
    assert nodes[0]["clause_id"] == "1."
    assert nodes[0]["title"] == "Short title and commencement"
    assert "Technology Risk Management Act" in nodes[0]["text"]
    assert nodes[0]["source_anchor"] == "pr1"

    assert nodes[1]["clause_id"] == "2."
    assert "financial institution" in nodes[1]["text"]


def test_parse_sso_html_empty():
    """Verify handling of empty HTML."""
    nodes = parse_sso_html("<html><body></body></html>")
    assert nodes == []
