import pytest
import sys
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.llm import LLMClient, LLMException

def is_ollama_reachable():
    """Check if Ollama is actually running before running the test"""
    # Try localhost first (local shell execution)
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        # Simple health check or tag list
        response = requests.get(f"{url}/api/tags", timeout=1)
        return response.status_code == 200
    except Exception:
        return False

@pytest.mark.skipif(not is_ollama_reachable(), reason="Ollama is not reachable at default URL. Requires docker-compose up.")
def test_ollama_real_connectivity():
    """
    TDD Mandate: Integration Test (Red/Green)
    Test connectivity to the Ollama API, asserting a successful response structure.
    """
    client = LLMClient() # Auto-picks env var or localhost
    
    # Simple prompt
    try:
        # Note: 'tinyllama' or 'llama3' must be pulled. 
        # We'll rely on the docker-compose setup or user instructions to pull a model.
        # If model doesn't exist, Ollama usually auto-pulls or errors.
        # For test stability, we might want to check what models exist, but let's try a generate.
        response = client.generate("Say 'Hello Integration'.")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # We don't check exact text because LLMs are non-deterministic, 
        # but we check we got *something* back.
        
    except LLMException as e:
        # If specifically model is missing, we can maybe tolerate it if connection worked,
        # but strictly the story asks for "successful response structure".
        pytest.fail(f"LLM Integration failed: {str(e)}")
