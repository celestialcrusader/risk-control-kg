"""
Unit Tests for RCKGCypherBuilder Cypher Query Generators

Validates that parameterized Cypher statements are correctly generated
for 6 node types, 5 linkages, and Gap nodes per 06-delta.md.
"""

from app.graph.rckg_queries import RCKGCypherBuilder


def test_node_cypher_builders():
    """Verify node creation Cypher statements contain required MERGE labels and fields."""
    ob_cypher = RCKGCypherBuilder.build_create_obligation_cypher()
    assert "MERGE (o:Obligation {obligation_id: $obligation_id})" in ob_cypher
    assert "statement_text" in ob_cypher

    co_cypher = RCKGCypherBuilder.build_create_control_objective_cypher()
    assert "MERGE (co:ControlObjective {objective_id: $objective_id})" in co_cypher
    assert "policy_name" in co_cypher

    ca_cypher = RCKGCypherBuilder.build_create_control_activity_cypher()
    assert "MERGE (ca:ControlActivity {activity_id: $activity_id})" in ca_cypher
    assert "sop_name" in ca_cypher

    fco_cypher = RCKGCypherBuilder.build_create_framework_objective_cypher()
    assert "MERGE (fco:FrameworkControlObj {framework_obj_id: $framework_obj_id})" in fco_cypher

    fca_cypher = RCKGCypherBuilder.build_create_framework_activity_cypher()
    assert "MERGE (fca:FrameworkControlAct {framework_act_id: $framework_act_id})" in fca_cypher

    r_cypher = RCKGCypherBuilder.build_create_risk_cypher()
    assert "MERGE (r:Risk {risk_id: $risk_id})" in r_cypher


def test_all_5_linkage_cypher_builders():
    """Verify all 5 linkage relationship Cypher statements contain correct relationship types and set-theory properties."""
    l1 = RCKGCypherBuilder.build_mitigates_linkage_cypher()
    assert "MERGE (co)-[rel:MITIGATES]->(r)" in l1
    assert "rel.set_theory_relation" in l1

    l2 = RCKGCypherBuilder.build_satisfies_linkage_cypher()
    assert "MERGE (co)-[rel:SATISFIES]->(o)" in l2
    assert "rel.set_theory_relation" in l2

    l3 = RCKGCypherBuilder.build_operationalized_by_linkage_cypher()
    assert "MERGE (ca)-[rel:OPERATIONALIZED_BY]->(co)" in l3
    assert "rel.set_theory_relation" in l3

    l4 = RCKGCypherBuilder.build_crosswalks_to_obj_linkage_cypher()
    assert "MERGE (co)-[rel:CROSSWALKS_TO_OBJ]->(fco)" in l4
    assert "rel.set_theory_relation" in l4

    l5 = RCKGCypherBuilder.build_crosswalks_to_act_linkage_cypher()
    assert "MERGE (ca)-[rel:CROSSWALKS_TO_ACT]->(fca)" in l5
    assert "rel.set_theory_relation" in l5


def test_gap_node_cypher_builder():
    """Verify Gap node Cypher statement format."""
    gap_cypher = RCKGCypherBuilder.build_create_gap_node_cypher()
    assert "CREATE (g:Gap {" in gap_cypher
    assert "target_entity_type" in gap_cypher
    assert "set_theory_relation" in gap_cypher
