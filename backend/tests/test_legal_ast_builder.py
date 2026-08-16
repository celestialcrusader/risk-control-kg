"""
Unit & Integration Test Suite for STORY-PARSE-103: Legal Numbering Regex State Machine (LegalHierarchyBuilder).
"""

import pytest
from app.services.legal_ast_builder import LegalHierarchyBuilder


def test_legal_hierarchy_builder_nested_structure():
    """Verify state stack hierarchy building for 3.1.2(a)(i)."""
    blocks = [
        "3. ACCESS CONTROL",
        "3.1 Multi-Factor Authentication",
        "3.1.2 Administrative Accounts",
        "(a) System administrators must use hardware tokens.",
        "(i) Tokens must be FIPS 140-3 validated.",
        "4. SYSTEM MONITORING",
    ]

    builder = LegalHierarchyBuilder()
    nodes = builder.process_elements(blocks)

    assert len(nodes) == 6
    assert nodes[0]["clause_id"] == "3."
    assert nodes[0]["level"] == "section"
    assert nodes[0]["parent_clause_id"] is None

    assert nodes[1]["clause_id"] == "3.1"
    assert nodes[1]["parent_clause_id"] == "3."

    assert nodes[2]["clause_id"] == "3.1.2"
    assert nodes[2]["parent_clause_id"] == "3.1"

    assert nodes[3]["clause_id"] == "a" or nodes[3]["clause_id"] == "(a)"
    assert nodes[3]["parent_clause_id"] == "3.1.2"

    assert nodes[4]["clause_id"] == "i" or nodes[4]["clause_id"] == "(i)"
    assert nodes[4]["parent_clause_id"] == nodes[3]["clause_id"]

    # Pop stack on new section 4.
    assert nodes[5]["clause_id"] == "4."
    assert nodes[5]["parent_clause_id"] is None


def test_legal_hierarchy_builder_empty():
    """Verify empty text blocks processing."""
    builder = LegalHierarchyBuilder()
    assert builder.process_elements([]) == []
