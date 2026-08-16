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


class ClauseReferenceDetails(BaseModel):
    """Simplified reference details to map back to original source document."""

    document_identifier: str = Field(default="", description="Identifier of the document, e.g. 'NIST SP 800-53' or 'MAS TRM'")
    document_version: Optional[str] = Field(default=None, description="Version of the document, e.g. 'January 2021'")
    document_title: Optional[str] = Field(default=None, description="Title of the source document")
    clause_citation: Optional[str] = Field(default=None, description="Verbatim citation of the clause")
    clause_reference: Optional[str] = Field(default=None, description="Section, paragraph, or page reference")


class Obligation(BaseModel):
    """
    Atomic rule unit extracted from regulatory text (Tier 1 Statutory / Guideline requirement).
    Syntax: "The [Primary Actor] must [Action Verb] [Subject/Target] [Condition]."
    """

    id: str = Field(description="Unique obligation identifier, e.g., '3.1.1.a'")
    prose: str = Field(description="Imperative obligation statement")
    action_verb: str = Field(description="Primary active verb")
    subject_noun: str = Field(description="Primary actor or role performing the action")
    clause_ref: str = Field(description="Reference to the source clause, e.g., 'Section 3.1'")
    effective_date: Optional[str] = Field(
        default=None,
        description="Optional date when the obligation takes effect",
    )
    section_ref: Optional[str] = Field(
        default=None,
        description="Main section heading, e.g., 'Section 3'",
    )
    clause_hierarchy: Optional[ClauseHierarchy] = Field(
        default=None,
        description="Optional structured hierarchy data for nested clauses",
    )
    clause_reference: Optional[ClauseReferenceDetails] = Field(
        default=None,
        description="Detailed mapping back to original document citation",
    )

    model_config = {"use_enum_values": False}


class ControlObjective(BaseModel):
    """
    Enterprise Policy Control Objective (Tier 2 Policy Document requirement).
    Syntax: "The organization shall establish [Control Objective] to satisfy [Domain]."
    """

    id: str = Field(description="Control objective identifier, e.g., 'POL-IAM-OBJ-01'")
    prose: str = Field(description="Control objective statement")
    action_verb: str = Field(description="Primary active verb")
    subject_noun: str = Field(description="Target role or entity")
    domain_facet: str = Field(description="GRC Domain, e.g., AccessControl, Cryptography")
    clause_ref: str = Field(description="Policy section reference")
    clause_reference: Optional[ClauseReferenceDetails] = Field(default=None)


class ControlActivity(BaseModel):
    """
    SOP / Procedure Control Activity (Tier 3 SOP / Standard requirement).
    Syntax: "The [Operator/System] must execute [Technical Step] using [Tool/Setting]."
    """

    id: str = Field(description="Control activity identifier, e.g., 'SOP-IAM-ACT-01'")
    prose: str = Field(description="Technical instruction statement")
    action_verb: str = Field(description="Primary execution verb")
    subject_noun: str = Field(description="Primary operator, role, or automated script")
    execution_type: str = Field(default="MANUAL", description="AUTOMATED | MANUAL | SEMI_AUTOMATED")
    frequency: str = Field(default="CONTINUOUS", description="REALTIME | DAILY | MONTHLY | QUARTERLY")
    clause_ref: str = Field(description="SOP section or step reference")
    clause_reference: Optional[ClauseReferenceDetails] = Field(default=None)


class ExtractedObligationsResponse(BaseModel):
    """
    Response wrapper for the LLM extraction output.
    """

    obligations: list[Obligation] = Field(
        description="List of validated obligation objects",
    )
    control_objectives: Optional[list[ControlObjective]] = Field(default=None)
    control_activities: Optional[list[ControlActivity]] = Field(default=None)

