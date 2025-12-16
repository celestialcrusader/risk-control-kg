import pytest
from pydantic import BaseModel, Field
from unittest.mock import MagicMock, patch
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.llm import LLMClient, LLMException

# Define a test Pydantic model
class RiskExtraction(BaseModel):
    risk_id: str = Field(..., description="Unique identifier for the risk")
    description: str = Field(..., description="Detailed description of the risk")
    severity: str = Field(..., description="High, Medium, or Low")

@pytest.fixture
def mock_httpx_post():
    with patch('httpx.post') as mock_post:
        yield mock_post

def test_generate_structured_success(mock_httpx_post):
    """
    TDD Mandate: Test that the LLMClient can take a Pydantic model and return a valid instance.
    """
    # Mock successful JSON response from LLM
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_data = {
        "risk_id": "R-001",
        "description": "Data leakage via unencrypted channel",
        "severity": "High"
    }
    # LLM might return it as a stringified JSON in the 'response' field
    mock_response.json.return_value = {"response": json.dumps(mock_data)}
    mock_httpx_post.return_value = mock_response

    client = LLMClient()
    
    # This method 'generate_structured' does not exist yet -> FAILURE EXPECTED
    result = client.generate_structured("Extract risk from text.", response_model=RiskExtraction)
    
    assert isinstance(result, RiskExtraction)
    assert result.risk_id == "R-001"
    assert result.severity == "High"

def test_generate_structured_validation_error(mock_httpx_post):
    """Test handling of invalid schema from LLM"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Missing required 'severity' field
    mock_data = {
        "risk_id": "R-002",
        "description": "Missing severity"
    }
    mock_response.json.return_value = {"response": json.dumps(mock_data)}
    mock_httpx_post.return_value = mock_response

    client = LLMClient()
    
    with pytest.raises(LLMException) as excinfo:
        client.generate_structured("Extract risk.", response_model=RiskExtraction)
    
    assert "Validation Error" in str(excinfo.value)
