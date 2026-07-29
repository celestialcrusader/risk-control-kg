"""
Pydantic schemas for the LLM-as-Judge quality evaluation system.

Defines the canonical schema for judge criteria scores and judgments
that evaluate extracted obligations across metadata accuracy, legal
definition alignment, and rule semantics.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Judgment(BaseModel):
    """Complete judgment for an extracted obligation."""

    metadata_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Score for metadata accuracy (0.0-1.0).",
    )
    legal_alignment: float = Field(
        ge=0.0,
        le=1.0,
        description="Score for legal definition alignment (0.0-1.0).",
    )
    semantics: float = Field(
        ge=0.0,
        le=1.0,
        description="Score for rule semantics (0.0-1.0).",
    )
    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Average of the three criterion scores.",
    )
    status: Literal["approved", "repair"] = Field(
        description='Overall judgment status: "approved" if all criteria >= 0.80, "repair" otherwise.',
    )
    feedback: str = Field(
        description="Detailed explanation of what was good or what needs fixing.",
    )


class JudgmentResponse(BaseModel):
    """Response wrapper for the judge judgment."""

    judgment: Judgment
