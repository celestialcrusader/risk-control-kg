import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.llm import LLMClient
from app.core.knowledge import KnowledgeExtractor, ExtractedKnowledge
from app.core.oscal import Control, Property

@pytest.mark.integration
def test_knowledge_extraction_integration():
    """
    Test that KnowledgeExtractor can actually extract entities using the local LLM.
    """
    # 1. Setup
    try:
        llm = LLMClient()
        # Simple connectivity check
        llm.generate("Hello")
    except Exception:
        pytest.skip("Local LLM not available")
        return

    extractor = KnowledgeExtractor(llm)
    
    # 2. Create Dummy Control with compliance text
    text = """
    The organization must implement Multi-Factor Authentication (MFA) for all remote access.
    Failure to do so introduces significant Risk of unauthorized access.
    MFA is defined as using two or more distinct authentication factors.
    """
    
    control = Control(
        id="test-ctrl-1",
        title="MFA Requirement",
        props=[Property(name="description", value=text)]
    )
    
    # 3. Extract
    result = extractor.extract_from_control(control)
    
    # 4. Verify
    assert isinstance(result, ExtractedKnowledge)
    assert len(result.entities) > 0
    
    # Check for specific entities
    types = [e.type for e in result.entities]
    names = [e.name.lower() for e in result.entities]
    
    # We expect MFA / Multi-Factor Authentication (Control or Definition)
    # We expect Unauthorized Access (Risk)
    
    print(f"Extracted: {result.entities}")
    
    assert any("mfa" in n or "authentication" in n for n in names)
    # Note: LLM output is non-deterministic, but usually consistent on this simple text
