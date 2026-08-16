"""
Unit tests for FIX-204 (Persist Golden Assertions to PostgreSQL DB in DualTierGovernanceEngine).
"""

from unittest.mock import MagicMock
import pytest
from app.services.governance_engine import DualTierGovernanceEngine


def test_register_golden_assertion_persists_to_db():
    """
    Test that DualTierGovernanceEngine.register_golden_assertion persists ORM records to PostgreSQL (FIX-204).
    """
    mock_db = MagicMock()
    engine = DualTierGovernanceEngine(db_session=mock_db)

    engine.register_golden_assertion("CO-101", "OBL-202", "SATISFIES")

    assert ("CO-101", "OBL-202", "SATISFIES") in engine._golden_assertions
    # Verify DB merge/add and commit were executed
    assert mock_db.commit.called, "db_session.commit() should be called when registering golden assertion"


def test_load_golden_assertions_from_db():
    """
    Test loading golden assertions from PostgreSQL database (FIX-204).
    """
    mock_db = MagicMock()
    mock_mapping = MagicMock()
    mock_mapping.control_objective_id = "CO-300"
    mock_mapping.framework_objective_id = "OBL-400"
    mock_mapping.set_theory_relation.name = "SATISFIES"

    mock_db.query.return_value.filter.return_value.all.return_value = [mock_mapping]

    engine = DualTierGovernanceEngine(db_session=mock_db)
    count = engine.load_golden_assertions()

    assert count == 1
    assert ("CO-300", "OBL-400", "SATISFIES") in engine._golden_assertions
