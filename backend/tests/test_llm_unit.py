import pytest
from unittest.mock import MagicMock, patch
import httpx
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Trying to import LLMClient - will fail initially
try:
    from app.core.llm import LLMClient, LLMException
except ImportError:
    LLMClient = None
    LLMException = None

@pytest.fixture
def mock_httpx_post():
    with patch('httpx.post') as mock_post:
        yield mock_post

def test_llm_client_initialization():
    """Test that LLMClient initializes with correct default base_url"""
    if LLMClient is None:
        pytest.fail("LLMClient not implemented")
        
    client = LLMClient(base_url="http://localhost:11434", model="qwen2.5:14b")
    assert client.base_url == "http://localhost:11434"
    assert client.model == "qwen2.5:14b"

def test_generate_text_success(mock_httpx_post):
    """Test successful text generation"""
    if LLMClient is None:
        pytest.fail("LLMClient not implemented")

    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "I am a helpful AI."}
    mock_httpx_post.return_value = mock_response

    client = LLMClient()
    response = client.generate("Who are you?")
    
    assert response == "I am a helpful AI."
    # Verify correct payload was sent
    mock_httpx_post.assert_called_once()
    args, kwargs = mock_httpx_post.call_args
    assert kwargs['json']['model'] == client.model
    assert kwargs['json']['prompt'] == "Who are you?"
    assert kwargs['json']['stream'] is False

def test_generate_text_api_failure(mock_httpx_post):
    """Test handling of 500 API error"""
    if LLMClient is None:
        pytest.fail("LLMClient not implemented")

    # Mock failure response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_httpx_post.return_value = mock_response

    client = LLMClient()
    
    with pytest.raises(LLMException) as excinfo:
        client.generate("Trigger error")
    
    assert "Ollama API Error" in str(excinfo.value)
