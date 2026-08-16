"""
TDD Unit/Integration Test for REMED-104: Complete Bitemporal Schema & Startup Endpoint Locality Check.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.models.rckg_nodes import ControlObjectiveNode, ControlActivityNode, RiskNode
from app.main import validate_llm_endpoint_locality


def test_remed_104_bitemporal_columns_on_all_nodes():
    """Verify ControlObjectiveNode, ControlActivityNode, and RiskNode have valid_from and valid_to columns."""
    obj = ControlObjectiveNode()
    act = ControlActivityNode()
    risk = RiskNode()

    assert hasattr(obj, "valid_from")
    assert hasattr(obj, "valid_to")
    assert hasattr(act, "valid_from")
    assert hasattr(act, "valid_to")
    assert hasattr(risk, "valid_from")
    assert hasattr(risk, "valid_to")


@patch("socket.gethostbyname")
@patch("app.main.logger")
def test_remed_104_llm_endpoint_locality_public_warning(mock_logger, mock_gethostbyname):
    """Verify validate_llm_endpoint_locality logs a WARNING when resolving to a public IP address."""
    mock_gethostbyname.return_value = "8.8.8.8"

    validate_llm_endpoint_locality()

    mock_logger.warning.assert_called_once()
    assert "public IP" in mock_logger.warning.call_args[0][0]


@patch("socket.gethostbyname")
@patch("app.main.logger")
def test_remed_104_llm_endpoint_locality_private_info(mock_logger, mock_gethostbyname):
    """Verify validate_llm_endpoint_locality logs INFO when resolving to a private/loopback IP address."""
    mock_gethostbyname.return_value = "127.0.0.1"

    validate_llm_endpoint_locality()

    mock_logger.info.assert_called_once()
    assert "verified private/local IP" in mock_logger.info.call_args[0][0]
