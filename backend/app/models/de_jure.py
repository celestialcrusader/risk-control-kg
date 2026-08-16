"""
De Jure Regulatory Models & Schemas for RCKG.
Includes temporal status and supersession metadata.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DeJureObligation(BaseModel):
    obligation_id: str = Field(..., description="Unique clause/obligation identifier")
    text: str = Field(..., description="Verbatim clause text")
    legal_status: str = Field(default="ACTIVE", description="ACTIVE | AMENDED | SUPERSEDED | CANCELLED")
    effective_date: Optional[str] = Field(default=None, description="ISO Date string (YYYY-MM-DD)")
    expiry_date: Optional[str] = Field(default=None, description="ISO Date string (YYYY-MM-DD)")
    parent_clause_id: Optional[str] = Field(default=None, description="Parent clause identifier")
    supersedes_clause_id: Optional[str] = Field(default=None, description="Superseded clause identifier")
    source_authority: Optional[str] = Field(default="MAS", description="Issuing authority")
    source_doc: Optional[str] = Field(default=None, description="Source document title")
