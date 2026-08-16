"""
Pure RCKG Cypher Query Builder Module

Provides parameterized Cypher query generators for node creation,
5-linkage relationship mapping with set-theory metadata, Gap node creation,
and multi-hop graph traversal queries as defined in 06-delta.md.
"""

from typing import Dict, Any, Optional


class RCKGCypherBuilder:
    """Cypher query builder for Pure RCKG Graph operations."""

    @staticmethod
    def build_create_obligation_cypher() -> str:
        return """
        MERGE (o:Obligation {obligation_id: $obligation_id})
        SET o.framework_name = $framework_name,
            o.framework_version = $framework_version,
            o.statement_text = $statement_text,
            o.action_verb = $action_verb,
            o.subject_noun = $subject_noun,
            o.section_reference = $section_reference,
            o.updated_at = timestamp()
        RETURN o
        """

    @staticmethod
    def build_create_control_objective_cypher() -> str:
        return """
        MERGE (co:ControlObjective {objective_id: $objective_id})
        SET co.policy_name = $policy_name,
            co.policy_version = $policy_version,
            co.objective_name = $objective_name,
            co.objective_text = $objective_text,
            co.owner = $owner,
            co.updated_at = timestamp()
        RETURN co
        """

    @staticmethod
    def build_create_control_activity_cypher() -> str:
        return """
        MERGE (ca:ControlActivity {activity_id: $activity_id})
        SET ca.sop_name = $sop_name,
            ca.sop_version = $sop_version,
            ca.activity_name = $activity_name,
            ca.activity_text = $activity_text,
            ca.implementation_method = $implementation_method,
            ca.updated_at = timestamp()
        RETURN ca
        """

    @staticmethod
    def build_create_framework_objective_cypher() -> str:
        return """
        MERGE (fco:FrameworkControlObj {framework_obj_id: $framework_obj_id})
        SET fco.framework_name = $framework_name,
            fco.framework_version = $framework_version,
            fco.objective_name = $objective_name,
            fco.objective_text = $objective_text,
            fco.updated_at = timestamp()
        RETURN fco
        """

    @staticmethod
    def build_create_framework_activity_cypher() -> str:
        return """
        MERGE (fca:FrameworkControlAct {framework_act_id: $framework_act_id})
        SET fca.framework_name = $framework_name,
            fca.framework_version = $framework_version,
            fca.activity_name = $activity_name,
            fca.activity_text = $activity_text,
            fca.updated_at = timestamp()
        RETURN fca
        """

    @staticmethod
    def build_create_risk_cypher() -> str:
        return """
        MERGE (r:Risk {risk_id: $risk_id})
        SET r.risk_name = $risk_name,
            r.description = $description,
            r.category = $category,
            r.severity_level = $severity_level,
            r.updated_at = timestamp()
        RETURN r
        """

    # ── 5 Linkage Relationship Cypher Builders ──────────────────────────────

    @staticmethod
    def build_mitigates_linkage_cypher() -> str:
        """Linkage 1: Control Objective -> Risk (MITIGATES)"""
        return """
        MATCH (co:ControlObjective {objective_id: $objective_id})
        MATCH (r:Risk {risk_id: $risk_id})
        MERGE (co)-[rel:MITIGATES]->(r)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.logic_judge_score = $logic_judge_score,
            rel.technical_judge_score = $technical_judge_score,
            rel.rationale = $rationale,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_defines_linkage_cypher() -> str:
        """Linkage 0: StatutoryRequirement -> Obligation (DEFINES)"""
        return """
        MATCH (d:StatutoryRequirement {node_id: $doc_id})
        MATCH (o:Obligation {node_id: $node_id})
        MERGE (d)-[rel:DEFINES]->(o)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.status = 'PROBABILISTIC_AI'
        RETURN rel
        """

    @staticmethod
    def build_satisfies_linkage_cypher() -> str:
        """Linkage 2: Control Objective -> Obligation (SATISFIES)"""
        return """
        MATCH (co:ControlObjective {objective_id: $objective_id})
        MATCH (o:Obligation {obligation_id: $obligation_id})
        MERGE (co)-[rel:SATISFIES]->(o)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.logic_judge_score = $logic_judge_score,
            rel.technical_judge_score = $technical_judge_score,
            rel.rationale = $rationale,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_operationalized_by_linkage_cypher() -> str:
        """Linkage 3: Control Activity -> Control Objective (OPERATIONALIZED_BY)"""
        return """
        MATCH (ca:ControlActivity {activity_id: $activity_id})
        MATCH (co:ControlObjective {objective_id: $objective_id})
        MERGE (ca)-[rel:OPERATIONALIZED_BY]->(co)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.logic_judge_score = $logic_judge_score,
            rel.technical_judge_score = $technical_judge_score,
            rel.rationale = $rationale,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_crosswalks_to_obj_linkage_cypher() -> str:
        """Linkage 4: Control Objective -> Framework Control Obj (CROSSWALKS_TO_OBJ)"""
        return """
        MATCH (co:ControlObjective {objective_id: $objective_id})
        MATCH (fco:FrameworkControlObj {framework_obj_id: $framework_obj_id})
        MERGE (co)-[rel:CROSSWALKS_TO_OBJ]->(fco)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.logic_judge_score = $logic_judge_score,
            rel.technical_judge_score = $technical_judge_score,
            rel.rationale = $rationale,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_crosswalks_to_act_linkage_cypher() -> str:
        """Linkage 5: Control Activity -> Framework Control Act (CROSSWALKS_TO_ACT)"""
        return """
        MATCH (ca:ControlActivity {activity_id: $activity_id})
        MATCH (fca:FrameworkControlAct {framework_act_id: $framework_act_id})
        MERGE (ca)-[rel:CROSSWALKS_TO_ACT]->(fca)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.logic_judge_score = $logic_judge_score,
            rel.technical_judge_score = $technical_judge_score,
            rel.rationale = $rationale,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    # ── Direct Public Baseline Cypher Builders (STORY-FOUNDATION-104) ───────

    @staticmethod
    def build_obligation_framework_crosswalk_cypher() -> str:
        """Direct Public: Obligation -> Framework Control Objective (CROSSWALKS_TO)"""
        return """
        MATCH (o:Obligation {obligation_id: $obligation_id})
        MATCH (fco:FrameworkControlObj {framework_obj_id: $framework_obj_id})
        MERGE (o)-[rel:CROSSWALKS_TO]->(fco)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.status = $status,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_risk_framework_mitigates_cypher() -> str:
        """Direct Public: Risk -> Framework Control Objective (MITIGATED_BY)"""
        return """
        MATCH (r:Risk {risk_id: $risk_id})
        MATCH (fco:FrameworkControlObj {framework_obj_id: $framework_obj_id})
        MERGE (r)-[rel:MITIGATED_BY]->(fco)
        SET rel.confidence_score = $confidence_score,
            rel.status = $status,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_framework_crosswalk_cypher() -> str:
        """Direct Inter-Framework: Framework Control Obj <---> Framework Control Obj"""
        return """
        MATCH (s:FrameworkControlObj {framework_obj_id: $source_framework_obj_id})
        MATCH (t:FrameworkControlObj {framework_obj_id: $target_framework_obj_id})
        MERGE (s)-[rel:CROSSWALKS_TO]->(t)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.status = $status,
            rel.mapping_date = timestamp()
        RETURN rel
        """

    @staticmethod
    def build_client_aligns_with_framework_cypher() -> str:
        """Client Overlay: Control Objective -> Framework Control Obj (ALIGNS_WITH)"""
        return """
        MATCH (co:ControlObjective {objective_id: $objective_id})
        MATCH (fco:FrameworkControlObj {framework_obj_id: $framework_obj_id})
        MERGE (co)-[rel:ALIGNS_WITH]->(fco)
        SET rel.set_theory_relation = $set_theory_relation,
            rel.confidence_score = $confidence_score,
            rel.mapping_date = timestamp()
        RETURN rel
        """


    @staticmethod
    def build_create_gap_node_cypher() -> str:
        """Create Gap node for partial / disjoint set theory outcomes."""
        return """
        CREATE (g:Gap {
            gap_id: $gap_id,
            target_entity_type: $target_entity_type,
            target_entity_id: $target_entity_id,
            set_theory_relation: $set_theory_relation,
            severity: $severity,
            state: $state,
            due_date: $due_date,
            reviewer_id: $reviewer_id,
            created_at: timestamp()
        })
        RETURN g
        """

    @staticmethod
    def build_supersede_node_cypher() -> str:
        """SUPERSEDE_NODE: Deprecates old node setting valid_to = timestamp(), creates new node, and links them via [:SUPERSEDES]."""
        return """
        MATCH (old {id: $old_node_id})
        SET old.valid_to = timestamp(), old.status = 'SUPERSEDED'
        MERGE (new {id: $new_node_id})
        MERGE (new)-[r:SUPERSEDES]->(old)
        SET r.created_at = timestamp()
        RETURN old, new, r
        """

    @staticmethod
    def build_create_gap_mutation_cypher() -> str:
        """CREATE_GAP: Creates Gap node and connects source and target nodes with DIRECT_GAP_TO edge."""
        return """
        MATCH (s {id: $source_node_id})
        MATCH (t {id: $target_node_id})
        CREATE (g:Gap {
            gap_id: $gap_id,
            source_id: $source_node_id,
            target_id: $target_node_id,
            set_theory_relation: $set_theory_relation,
            severity: $severity,
            created_at: timestamp()
        })
        CREATE (s)-[:HAS_GAP]->(g)
        CREATE (g)-[:DIRECT_GAP_TO]->(t)
        RETURN g
        """

    @staticmethod
    def build_reclassify_edge_cypher() -> str:
        """RECLASSIFY_EDGE: Updates relationship properties or set_theory_relation."""
        return """
        MATCH (s {id: $source_node_id})-[r]->(t {id: $target_node_id})
        SET r.set_theory_relation = $new_relation,
            r.updated_at = timestamp()
        RETURN r
        """

    @staticmethod
    def build_deprecate_edge_cypher() -> str:
        """DEPRECATE_EDGE: Marks relationship status as DEPRECATED."""
        return """
        MATCH (s {id: $source_node_id})-[r]->(t {id: $target_node_id})
        SET r.status = 'DEPRECATED',
            r.deprecated_at = timestamp()
        RETURN r
        """
