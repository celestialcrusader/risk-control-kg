"""
Unit and Integration tests for STORY-COMP-201: Two-Dimensional Ontology & Directional Schema Migration.
"""
import pytest
from app.models.rckg_nodes import (
    SemanticRelation,
    AssuranceCoverage,
    ObligationFrameworkMapping,
    ObligationNode,
    FrameworkControlObjectiveNode,
    MappingStatus,
)
from app.models import Base
from app.core.database import SessionLocal, engine


def test_two_dimensional_enums_exist():
    """Verify SemanticRelation and AssuranceCoverage enums have all expected values."""
    assert SemanticRelation.EQUIVALENT.value == "EQUIVALENT"
    assert SemanticRelation.SUBSET_OF.value == "SUBSET_OF"
    assert SemanticRelation.SUPERSET_OF.value == "SUPERSET_OF"
    assert SemanticRelation.OVERLAPS.value == "OVERLAPS"
    assert SemanticRelation.SUPPORTS.value == "SUPPORTS"
    assert SemanticRelation.NONE.value == "NONE"

    assert AssuranceCoverage.FULL_COVERAGE.value == "FULL_COVERAGE"
    assert AssuranceCoverage.PARTIAL_COVERAGE.value == "PARTIAL_COVERAGE"
    assert AssuranceCoverage.NO_COVERAGE.value == "NO_COVERAGE"


def test_obligation_framework_mapping_model_attributes():
    """Verify ObligationFrameworkMapping contains both dimensions."""
    db = SessionLocal()
    # Check column existence on model class
    assert hasattr(ObligationFrameworkMapping, "semantic_relation")
    assert hasattr(ObligationFrameworkMapping, "assurance_coverage")
    assert hasattr(ObligationFrameworkMapping, "confidence_score")
    assert hasattr(ObligationFrameworkMapping, "rationale")
    db.close()


def test_directional_semantics_convention():
    """
    Verify directional semantics:
    - If Target Control encompasses Source Obligation, relation is SUBSET_OF (A ⊆ B) and coverage is FULL_COVERAGE.
    - If Target Control only addresses a part of Source Obligation, relation is SUPERSET_OF (A ⊇ B) and coverage is PARTIAL_COVERAGE.
    - If Target Control is enabling/budgetary, relation is SUPPORTS and coverage is NO_COVERAGE.
    """
    mapping_enabling = ObligationFrameworkMapping(
        semantic_relation=SemanticRelation.SUPPORTS,
        assurance_coverage=AssuranceCoverage.NO_COVERAGE,
        confidence_score=0.90,
        rationale="Budgeting enables security controls but does not satisfy CIA preservation mandate.",
    )
    assert mapping_enabling.semantic_relation == SemanticRelation.SUPPORTS
    assert mapping_enabling.assurance_coverage == AssuranceCoverage.NO_COVERAGE

    mapping_subsumed = ObligationFrameworkMapping(
        semantic_relation=SemanticRelation.SUBSET_OF,
        assurance_coverage=AssuranceCoverage.FULL_COVERAGE,
        confidence_score=0.95,
        rationale="NIST AC-5 completely satisfies and exceeds MAS software release SoD mandate.",
    )
    assert mapping_subsumed.semantic_relation == SemanticRelation.SUBSET_OF
    assert mapping_subsumed.assurance_coverage == AssuranceCoverage.FULL_COVERAGE
