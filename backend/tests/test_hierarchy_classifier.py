"""
Unit Tests for 3-Tier Multi-Framework Hierarchy Classifier (STORY-FOUNDATION-105).
"""

import pytest
from app.services.parsers.hierarchy_classifier import HierarchyClassifier


def test_hierarchy_classifier_tier1_regex():
    """Verify Tier 1: Regex patterns for NIST, CIS, ISO, PCI."""
    classifier = HierarchyClassifier()

    # NIST Enhancements
    assert classifier.classify("AC-2(1)") == "ACTIVITY"
    assert classifier.classify("IA-5(2)") == "ACTIVITY"
    assert classifier.classify("AC-2") == "OBJECTIVE"

    # CIS Safeguards
    assert classifier.classify("Safeguard 6.5") == "ACTIVITY"
    assert classifier.classify("CIS Safeguard 3.1") == "ACTIVITY"
    assert classifier.classify("Control 6") == "OBJECTIVE"

    # ISO Clauses
    assert classifier.classify("A.5.15.1") == "ACTIVITY"
    assert classifier.classify("A.5") == "OBJECTIVE"

    # PCI DSS
    assert classifier.classify("8.3.1") == "ACTIVITY"
    assert classifier.classify("8.3") == "OBJECTIVE"


def test_hierarchy_classifier_tier2_dot_depth():
    """Verify Tier 2: Dot-depth heuristics for custom/unrecognized standards."""
    classifier = HierarchyClassifier()

    assert classifier.classify("MAS-5.1.1") == "ACTIVITY"
    assert classifier.classify("MAS-5.1") == "OBJECTIVE"
    assert classifier.classify("SECTION-1.2.3.4") == "ACTIVITY"


def test_hierarchy_classifier_tier3_facet_context():
    """Verify Tier 3: Disambiguating verbs like 'approve' using target_role and control_nature."""
    classifier = HierarchyClassifier()

    # High-level governance intent -> OBJECTIVE
    gov_facets = {
        "action_verb": "approve",
        "target_role_facet": "BOARD_OF_DIRECTORS",
        "control_nature": "GOVERNANCE",
    }
    assert classifier.classify("POL-APPROVAL", "The Board shall approve the policy.", gov_facets) == "OBJECTIVE"

    # Operational ticket action -> ACTIVITY
    op_facets = {
        "action_verb": "approve",
        "target_role_facet": "SYSTEM_ADMINISTRATOR",
        "control_nature": "PREVENTATIVE",
    }
    assert classifier.classify("SOP-APPROVAL", "The admin must approve access requests.", op_facets) == "ACTIVITY"
