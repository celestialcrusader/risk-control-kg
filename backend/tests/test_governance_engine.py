"""
TDD Tests for Dual-Tier Governance Engine & Golden Assertions Compiler Gate (RCKG-402).
"""

import pytest
from app.services.governance_engine import (
    DualTierGovernanceEngine,
    GovernanceValidationResult,
    GraphRegressionError,
)


@pytest.fixture
def governance_engine():
    engine = DualTierGovernanceEngine()
    engine.register_golden_assertion(
        source_id="NIST-800-53-AU-2",
        target_id="ISO-27001-A.8.15",
        relation_type="EQUIVALENT_TO",
    )
    return engine


def test_governance_block_ontology_mutation(governance_engine):
    """AC-1: Blocks ontology schema mutations and requires Human Committee sign-off."""
    mutation = {"action": "ADD_NODE_TYPE", "node_type": "CUSTOM_REGULATORY_FACET"}
    res = governance_engine.validate_mutation(mutation)

    assert isinstance(res, GovernanceValidationResult)
    assert res.is_allowed is False
    assert res.status == "NEEDS_HUMAN_GOVERNANCE_SIGN_OFF"


def test_governance_golden_assertion_regression_check(governance_engine):
    """AC-2: Contradicting a pinned golden assertion raises GraphRegressionError."""
    mutation = {
        "action": "DEPRECATE_EDGE",
        "source_id": "NIST-800-53-AU-2",
        "target_id": "ISO-27001-A.8.15",
        "relation_type": "EQUIVALENT_TO",
    }
    with pytest.raises(GraphRegressionError, match="Golden Assertion regression detected"):
        governance_engine.validate_mutation(mutation)


def test_governance_instance_mutation_allowed(governance_engine):
    """AC-3: Instance mutations auto-pass governance gates when rules & assertions pass."""
    mutation = {
        "action": "SUPERSEDE_NODE",
        "source_id": "OBL-501",
        "target_id": "OBL-502",
        "relation_type": "SUBSET_OF",
    }
    res = governance_engine.validate_mutation(mutation)

    assert res.is_allowed is True
    assert res.status == "AUTO_COMMIT_APPROVED"
