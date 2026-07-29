"""
Deterministic v0.1 Facet-Aware Graph Compiler for Pure RCKG Engine (RCKG-103).

Evaluates candidate entity pairs using extracted facet dictionaries (action_verb, subject_noun,
domain_facet, modality_facet, target_role_facet, control_nature) and bi-encoder cosine similarity
to produce strictly typed GraphMutationDiff payloads.
"""

import enum
import logging
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ClosedSetPrimitive(str, enum.Enum):
    ADD_NODE = "ADD_NODE"
    SUPERSEDE_NODE = "SUPERSEDE_NODE"
    ADD_EDGE = "ADD_EDGE"
    RECLASSIFY_EDGE = "RECLASSIFY_EDGE"
    DEPRECATE_EDGE = "DEPRECATE_EDGE"
    MERGE_NODE = "MERGE_NODE"
    SPLIT_NODE = "SPLIT_NODE"
    CREATE_GAP = "CREATE_GAP"


class GraphMutationDiff(BaseModel):
    primitive: ClosedSetPrimitive
    source_node_id: str
    target_node_id: Optional[str] = None
    relationship_type: Optional[str] = None
    set_theory_relation: Optional[str] = None
    condition_clause: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    is_golden_assertion: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CompilerExecutionReport(BaseModel):
    total_evaluated: int = 0
    added_edges_count: int = 0
    created_gaps_count: int = 0
    mutations: List[GraphMutationDiff] = Field(default_factory=list)


class RuleBasedGraphCompiler:
    """v0.1 Facet-Aware Rule-Based Graph Compiler Engine."""

    def compile_mutation(
        self,
        source_entity: Dict[str, Any],
        target_entity: Dict[str, Any],
        cosine_sim: float,
    ) -> List[GraphMutationDiff]:
        mutations = []

        s_id = source_entity.get("node_id", "UNKNOWN_SOURCE")
        t_id = target_entity.get("node_id", "UNKNOWN_TARGET")

        s_verb = str(source_entity.get("action_verb", "")).strip().lower()
        s_noun = str(source_entity.get("subject_noun", "")).strip().lower()
        s_domain = str(source_entity.get("domain_facet", "")).strip().lower()
        s_modality = str(source_entity.get("modality_facet", "")).strip().upper()
        s_role = str(source_entity.get("target_role_facet", "")).strip().upper()
        s_nature = str(source_entity.get("control_nature", "")).strip().upper()

        t_verb = str(target_entity.get("action_verb", "")).strip().lower()
        t_noun = str(target_entity.get("subject_noun", "")).strip().lower()
        t_domain = str(target_entity.get("domain_facet", "")).strip().lower()
        t_modality = str(target_entity.get("modality_facet", "")).strip().upper()
        t_role = str(target_entity.get("target_role_facet", "")).strip().upper()
        t_nature = str(target_entity.get("control_nature", "")).strip().upper()

        # Rule 1: Disjoint Entities (cosine < 0.30) -> CREATE_GAP
        if cosine_sim < 0.30 or (s_domain and t_domain and s_domain != t_domain and cosine_sim < 0.50):
            gap_type = "MISSING_INTERMEDIATE_POLICY_OBJECTIVE"
            gap_severity = "HIGH" if cosine_sim < 0.20 else "MEDIUM"
            mutations.append(
                GraphMutationDiff(
                    primitive=ClosedSetPrimitive.CREATE_GAP,
                    source_node_id=s_id,
                    target_node_id=t_id,
                    confidence_score=cosine_sim,
                    metadata={"gap_type": gap_type, "gap_severity": gap_severity},
                )
            )
            return mutations

        # Rule 2: Exact Action Verb + Subject Noun + Domain Match (cosine >= 0.85) -> EQUIVALENT_TO
        if s_verb and s_noun and s_verb == t_verb and s_noun == t_noun and (not s_domain or not t_domain or s_domain == t_domain) and cosine_sim >= 0.85:
            mutations.append(
                GraphMutationDiff(
                    primitive=ClosedSetPrimitive.ADD_EDGE,
                    source_node_id=s_id,
                    target_node_id=t_id,
                    relationship_type="SATISFIES",
                    set_theory_relation="EQUIVALENT_TO",
                    confidence_score=cosine_sim,
                )
            )
            return mutations

        # Rule 3: Modality Override (MANDATORY vs RECOMMENDED) -> SUPERSET_OF
        if s_modality == "MANDATORY" and t_modality == "RECOMMENDED" and cosine_sim >= 0.85:
            mutations.append(
                GraphMutationDiff(
                    primitive=ClosedSetPrimitive.ADD_EDGE,
                    source_node_id=s_id,
                    target_node_id=t_id,
                    relationship_type="SUPERSEDES",
                    set_theory_relation="SUPERSET_OF",
                    confidence_score=cosine_sim,
                )
            )
            return mutations

        # Rule 4: Partial Verb / Noun Match (cosine >= 0.85) -> SUBSET_OF or SUPERSET_OF
        if cosine_sim >= 0.85:
            if "reviews and" in s_verb or ("and" in s_verb and len(s_verb) > len(t_verb)):
                rel = "SUPERSET_OF"
            elif "privileged" in s_noun or s_verb in ["provisions", "creates", "disables", "removes"]:
                rel = "SUBSET_OF"
            elif len(s_noun) > len(t_noun):
                rel = "SUBSET_OF"
            else:
                rel = "SUBSET_OF"

            mutations.append(
                GraphMutationDiff(
                    primitive=ClosedSetPrimitive.ADD_EDGE,
                    source_node_id=s_id,
                    target_node_id=t_id,
                    relationship_type="SATISFIES",
                    set_theory_relation=rel,
                    confidence_score=cosine_sim,
                )
            )
            return mutations

        # Rule 5: Facet/Role/Nature Mismatch or Moderate Similarity -> INTERSECTS_WITH or CONTINGENT_SATISFIES
        if (s_role and t_role and s_role != t_role) or (s_nature and t_nature and s_nature != t_nature) or (0.70 <= cosine_sim < 0.85 and s_verb != t_verb):
            mutations.append(
                GraphMutationDiff(
                    primitive=ClosedSetPrimitive.ADD_EDGE,
                    source_node_id=s_id,
                    target_node_id=t_id,
                    relationship_type="PARTIALLY_SATISFIES",
                    set_theory_relation="INTERSECTS_WITH",
                    confidence_score=cosine_sim,
                )
            )
            return mutations

        if cosine_sim >= 0.70:
            mutations.append(
                GraphMutationDiff(
                    primitive=ClosedSetPrimitive.ADD_EDGE,
                    source_node_id=s_id,
                    target_node_id=t_id,
                    relationship_type="SATISFIES",
                    set_theory_relation="CONTINGENT_SATISFIES",
                    confidence_score=cosine_sim,
                )
            )
            return mutations

        # Fallback: NO_RELATIONSHIP
        mutations.append(
            GraphMutationDiff(
                primitive=ClosedSetPrimitive.ADD_EDGE,
                source_node_id=s_id,
                target_node_id=t_id,
                relationship_type="NO_RELATIONSHIP",
                set_theory_relation="NO_RELATIONSHIP",
                confidence_score=cosine_sim,
            )
        )
        return mutations

    def compile_batch(
        self, pairs: List[Tuple[Dict[str, Any], Dict[str, Any], float]]
    ) -> CompilerExecutionReport:
        report = CompilerExecutionReport(total_evaluated=len(pairs))
        for source_e, target_e, cos_sim in pairs:
            diffs = self.compile_mutation(source_e, target_e, cos_sim)
            for d in diffs:
                report.mutations.append(d)
                if d.primitive == ClosedSetPrimitive.ADD_EDGE:
                    report.added_edges_count += 1
                elif d.primitive == ClosedSetPrimitive.CREATE_GAP:
                    report.created_gaps_count += 1
        return report
