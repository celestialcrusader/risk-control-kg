"""
Pydantic schemas for obligation extraction.

Defines the canonical schema for atomic rule units extracted from
regulatory text by the De Jure semantic decomposition pipeline.

Per TRD Section 7.4, each obligation must include:
- id: Unique identifier for the obligation
- prose: The full text of the extracted obligation
- action_verb: The primary action verb (e.g., "must", "shall", "must limit")
- subject_noun: The primary subject noun phrase
- clause_ref: Reference to the source clause (e.g., "Section 3.1")
- effective_date: Optional date when the obligation takes effect
- section_ref: Optional parent section reference
- clause_hierarchy: Optional structured hierarchy data
"""

from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator


class ClauseHierarchy(BaseModel):
    """Structured hierarchy data for nested regulatory clauses."""

    parent: str = Field(description="Parent section name")
    level: int = Field(description="Hierarchy depth level")
    path: str = Field(description="Dot-separated path, e.g., '3.1' or '100.b.2'")


class Obligation(BaseModel):
    """
    Atomic rule unit extracted from regulatory text.

    Each obligation represents a discrete, structured node in the
    knowledge graph that can be queried, validated, and traced back
    to its source regulatory text.
    """

    id: str = Field(description="Unique obligation identifier, e.g., 'AC-1' or '100b1'")
    prose: str = Field(description="Full text of the obligation")
    action_verb: str = Field(description="Primary action verb or verb phrase")
    subject_noun: str = Field(description="Primary subject noun phrase")
    clause_ref: str = Field(description="Reference to the source clause, e.g., 'Section 3.1'")
    effective_date: Optional[str] = Field(
        default=None,
        description="Optional date when the obligation takes effect (ISO 8601 format)",
    )
    section_ref: Optional[str] = Field(
        default=None,
        description="Optional parent section reference, e.g., 'Section 3' or 'Title 12'",
    )
    clause_hierarchy: Optional[ClauseHierarchy] = Field(
        default=None,
        description="Optional structured hierarchy data for nested clauses",
    )

    model_config = {"use_enum_values": False}


class ExtractedObligationsResponse(BaseModel):
    """
    Response wrapper for the LLM extraction output.

    The LLM returns a JSON object with an 'obligations' key containing
    an array of obligation objects. This model validates that structure
    and converts each item into a proper Obligation instance.
    """

    obligations: list[Obligation] = Field(
        description="List of validated obligation objects",
    )
