from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.llm import LLMClient
from app.core.oscal import Control

class ExtractedEntity(BaseModel):
    name: str
    type: str = Field(..., description="One of: Risk, Control, Definition, Actor, System")
    description: str

class ExtractedKnowledge(BaseModel):
    entities: List[ExtractedEntity] = []
    summary: str

class KnowledgeExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def extract_from_control(self, control: Control) -> ExtractedKnowledge:
        """
        Uses LLM to extract entities from a Control (which represents a document chunk).
        """
        # Find description prop
        text = "No content"
        for p in control.props:
            if p.name == "description":
                text = p.value
                break
                
        if len(text) < 50: # Skip very short chunks
            return ExtractedKnowledge(entities=[], summary="Skipped (too short)")

        prompt = f"""
        Analyze the following text from a compliance document:
        
        "{text[:2000]}"... (truncated)
        
        Extract the key entities mentioned. Focus on:
        - Specific Risks mentioned.
        - Specific Control definitions.
        - Key Terms (Definitions).
        
        Provide a brief summary of the text as well.
        """
        
        try:
            return self.llm.generate_structured(prompt, ExtractedKnowledge)
        except Exception as e:
            # Fallback or log
            print(f"Extraction failed: {e}")
            return ExtractedKnowledge(entities=[], summary="Extraction Failed")
