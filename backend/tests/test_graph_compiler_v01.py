"""
TDD Unit Tests for Deterministic v0.1 Facet-Aware Graph Compiler (RCKG-103).

Validates 20 test scenarios across exact matches, partial matches, set-theory relations,
and gap creation logic.
"""

import pytest
from app.services.graph_compiler import (
    RuleBasedGraphCompiler,
    ClosedSetPrimitive,
    GraphMutationDiff,
)


@pytest.fixture
def compiler():
    return RuleBasedGraphCompiler()


# =============================================================================
# 1. Exact Match & EQUIVALENT_TO Scenarios (Scenarios 1 - 5)
# =============================================================================

def test_scenario_01_exact_facet_match_high_similarity(compiler):
    """AC-1: Exact verb, noun, domain match with cosine >= 0.85 -> EQUIVALENT_TO ADD_EDGE."""
    s = {"node_id": "N1", "action_verb": "manages", "subject_noun": "user accounts", "domain_facet": "IAM"}
    t = {"node_id": "N2", "action_verb": "manages", "subject_noun": "user accounts", "domain_facet": "IAM"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.92)

    assert len(diffs) == 1
    d = diffs[0]
    assert d.primitive == ClosedSetPrimitive.ADD_EDGE
    assert d.set_theory_relation == "EQUIVALENT_TO"
    assert d.confidence_score == 0.92


def test_scenario_02_exact_facet_match_case_insensitive(compiler):
    s = {"node_id": "N1", "action_verb": "ENFORCES", "subject_noun": "Access Control", "domain_facet": "SECURITY"}
    t = {"node_id": "N2", "action_verb": "enforces", "subject_noun": "access control", "domain_facet": "security"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.88)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "EQUIVALENT_TO"


def test_scenario_03_exact_facet_match_boundary_085(compiler):
    s = {"node_id": "N1", "action_verb": "audit", "subject_noun": "log", "domain_facet": "logging"}
    t = {"node_id": "N2", "action_verb": "audit", "subject_noun": "log", "domain_facet": "logging"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.85)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "EQUIVALENT_TO"


def test_scenario_04_exact_facet_match_below_085_fallback(compiler):
    """Exact facets but similarity < 0.85 falls back to partial / contingent relation."""
    s = {"node_id": "N1", "action_verb": "manages", "subject_noun": "user accounts", "domain_facet": "IAM"}
    t = {"node_id": "N2", "action_verb": "manages", "subject_noun": "user accounts", "domain_facet": "IAM"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.75)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "CONTINGENT_SATISFIES"


def test_scenario_05_exact_match_payload_fields(compiler):
    s = {"node_id": "N1", "action_verb": "encrypt", "subject_noun": "data at rest", "domain_facet": "crypto"}
    t = {"node_id": "N2", "action_verb": "encrypt", "subject_noun": "data at rest", "domain_facet": "crypto"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.95)
    d = diffs[0]
    assert isinstance(d, GraphMutationDiff)
    assert d.source_node_id == "N1"
    assert d.target_node_id == "N2"


# =============================================================================
# 2. Partial Match & SUBSET_OF / SUPERSET_OF Scenarios (Scenarios 6 - 12)
# =============================================================================

def test_scenario_06_high_sim_partial_noun(compiler):
    """AC-1: High cosine (>= 0.85) with partial verb/noun match -> SUBSET_OF."""
    s = {"node_id": "N1", "action_verb": "manages", "subject_noun": "privileged user accounts", "domain_facet": "IAM"}
    t = {"node_id": "N2", "action_verb": "manages", "subject_noun": "user accounts", "domain_facet": "IAM"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.89)

    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "SUBSET_OF"


def test_scenario_07_high_sim_partial_verb(compiler):
    s = {"node_id": "N1", "action_verb": "reviews and manages", "subject_noun": "system accounts", "domain_facet": "IAM"}
    t = {"node_id": "N2", "action_verb": "manages", "subject_noun": "system accounts", "domain_facet": "IAM"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.87)

    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "SUPERSET_OF"


def test_scenario_08_high_sim_verb_synonym_subset(compiler):
    s = {"node_id": "N1", "action_verb": "provisions", "subject_noun": "accounts", "domain_facet": "IAM"}
    t = {"node_id": "N2", "action_verb": "manages", "subject_noun": "accounts", "domain_facet": "IAM"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.86)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation in ["SUBSET_OF", "CONTINGENT_SATISFIES"]


def test_scenario_09_moderate_similarity_partial_match(compiler):
    s = {"node_id": "N1", "action_verb": "retains", "subject_noun": "audit logs", "domain_facet": "logging"}
    t = {"node_id": "N2", "action_verb": "stores", "subject_noun": "system logs", "domain_facet": "logging"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.72)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "INTERSECTS_WITH"


def test_scenario_10_modality_facet_override(compiler):
    s = {"node_id": "N1", "action_verb": "must perform", "subject_noun": "backup", "modality_facet": "MANDATORY"}
    t = {"node_id": "N2", "action_verb": "should perform", "subject_noun": "backup", "modality_facet": "RECOMMENDED"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.86)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "SUPERSET_OF"


def test_scenario_11_target_role_facet_filtering(compiler):
    s = {"node_id": "N1", "action_verb": "audit", "subject_noun": "access", "target_role_facet": "AUDITOR"}
    t = {"node_id": "N2", "action_verb": "audit", "subject_noun": "access", "target_role_facet": "SYSTEM_ADMIN"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.80)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "INTERSECTS_WITH"


def test_scenario_12_control_nature_automated_vs_manual(compiler):
    s = {"node_id": "N1", "action_verb": "review", "subject_noun": "permissions", "control_nature": "AUTOMATED"}
    t = {"node_id": "N2", "action_verb": "review", "subject_noun": "permissions", "control_nature": "MANUAL"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.81)
    assert len(diffs) == 1
    assert diffs[0].set_theory_relation == "INTERSECTS_WITH"


# =============================================================================
# 3. Disjoint Entities & CREATE_GAP Scenarios (Scenarios 13 - 17)
# =============================================================================

def test_scenario_13_disjoint_entities_low_similarity(compiler):
    """AC-1: Disjoint entities (cosine < 0.30) generate CREATE_GAP diff."""
    s = {"node_id": "N1", "action_verb": "encrypts", "subject_noun": "payloads", "domain_facet": "crypto"}
    t = {"node_id": "N2", "action_verb": "mows", "subject_noun": "lawn", "domain_facet": "facilities"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.12)

    assert len(diffs) == 1
    d = diffs[0]
    assert d.primitive == ClosedSetPrimitive.CREATE_GAP
    assert d.metadata.get("gap_type") == "MISSING_INTERMEDIATE_POLICY_OBJECTIVE"


def test_scenario_14_disjoint_zero_similarity(compiler):
    s = {"node_id": "N1", "action_verb": "log", "subject_noun": "events"}
    t = {"node_id": "N2", "action_verb": "hire", "subject_noun": "employees"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.0)
    assert len(diffs) == 1
    assert diffs[0].primitive == ClosedSetPrimitive.CREATE_GAP


def test_scenario_15_disjoint_domain_mismatch(compiler):
    s = {"node_id": "N1", "action_verb": "verify", "subject_noun": "signature", "domain_facet": "cryptography"}
    t = {"node_id": "N2", "action_verb": "verify", "subject_noun": "signature", "domain_facet": "legal_contracts"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.25)
    assert len(diffs) == 1
    assert diffs[0].primitive == ClosedSetPrimitive.CREATE_GAP


def test_scenario_16_gap_diff_metadata_fields(compiler):
    s = {"node_id": "N1", "action_verb": "scan", "subject_noun": "vulnerabilities"}
    t = {"node_id": "N2", "action_verb": "water", "subject_noun": "plants"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.15)
    d = diffs[0]
    assert d.source_node_id == "N1"
    assert d.target_node_id == "N2"
    assert d.metadata.get("gap_severity") == "HIGH"


def test_scenario_17_no_relation_borderline(compiler):
    s = {"node_id": "N1", "action_verb": "update", "subject_noun": "firmware"}
    t = {"node_id": "N2", "action_verb": "clean", "subject_noun": "desk"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.29)
    assert len(diffs) == 1
    assert diffs[0].primitive == ClosedSetPrimitive.CREATE_GAP


# =============================================================================
# 4. Batch Compilation & Edge Cases (Scenarios 18 - 20)
# =============================================================================

def test_scenario_18_batch_compilation_execution(compiler):
    pairs = [
        ({"node_id": "A1", "action_verb": "manage", "subject_noun": "accounts"}, {"node_id": "B1", "action_verb": "manage", "subject_noun": "accounts"}, 0.90),
        ({"node_id": "A2", "action_verb": "encrypt", "subject_noun": "data"}, {"node_id": "B2", "action_verb": "protect", "subject_noun": "data"}, 0.86),
        ({"node_id": "A3", "action_verb": "log", "subject_noun": "events"}, {"node_id": "B3", "action_verb": "cook", "subject_noun": "food"}, 0.10),
    ]
    report = compiler.compile_batch(pairs)
    assert report.total_evaluated == 3
    assert len(report.mutations) == 3
    assert report.added_edges_count == 2
    assert report.created_gaps_count == 1


def test_scenario_19_missing_facets_defaults(compiler):
    s = {"node_id": "N1"}
    t = {"node_id": "N2"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.50)
    assert len(diffs) == 0


def test_scenario_20_pydantic_schema_serialization(compiler):
    """AC-2: Emits strictly typed GraphMutationDiff payloads."""
    s = {"node_id": "N1", "action_verb": "manage", "subject_noun": "access"}
    t = {"node_id": "N2", "action_verb": "manage", "subject_noun": "access"}
    diffs = compiler.compile_mutation(s, t, cosine_sim=0.90)
    payload = diffs[0].model_dump()

    assert "primitive" in payload
    assert "source_node_id" in payload
    assert "confidence_score" in payload
    assert payload["primitive"] == "ADD_EDGE"
