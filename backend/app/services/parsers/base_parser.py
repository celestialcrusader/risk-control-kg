"""
Standardized BaseParser Abstract Interface for Multi-Parser Stack (RCKG-202).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel, Field


class ParseResult(BaseModel):
    markdown_text: str
    heading_count: int = 0
    table_count: int = 0
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseParser(ABC):
    """Abstract Base Class for specialized document parsers."""

    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str = "") -> ParseResult:
        """Parse raw file bytes into a structured ParseResult object."""
        pass
