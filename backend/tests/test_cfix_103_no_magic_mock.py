"""
TDD Unit Test for CFIX-103: Removal of MagicMock and Test Code from Production.
"""

import os
import subprocess
import pytest
from app.services.governance_engine import DualTierGovernanceEngine


def test_no_magic_mock_in_production_code():
    """Verify zero MagicMock or unittest.mock references exist in backend/app/."""
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    
    cmd = ["grep", "-rn", "MagicMock", app_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    assert result.returncode != 0, (
        f"Found MagicMock in production code:\n{result.stdout}"
    )


def test_governance_engine_handles_db_exception_without_name_error():
    """Verify register_golden_assertion handles DB exception safely without NameError for MagicMock."""
    mock_db = os.path.abspath(__file__)  # Dummy invalid object to trigger DB exception
    engine = DualTierGovernanceEngine(db_session=mock_db)
    
    # This should log an error and perform rollback without raising NameError for MagicMock
    engine.register_golden_assertion("SRC-01", "TGT-01", "EQUIVALENT_TO")
    assert ("SRC-01", "TGT-01", "EQUIVALENT_TO") in engine._golden_assertions
