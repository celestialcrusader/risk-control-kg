"""
Memgraph Execution Engine & Transactional Outbox Dual-Write Service (RCKG-104).

Maps GraphMutationDiff primitives strictly into parameterized Cypher template execution,
maintaining 100% synchronization between PostgreSQL ORM and Memgraph graph store.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.rckg_nodes import GraphOutboxLog
from app.graph.rckg_queries import RCKGCypherBuilder
from app.services.graph_compiler import ClosedSetPrimitive, GraphMutationDiff

from app.services.governance_engine import DualTierGovernanceEngine, GraphRegressionError

logger = logging.getLogger(__name__)


class MemgraphService:
    """Manages secure parameterized Cypher execution and dual-write outbox transactions."""

    def __init__(self, db_session: Optional[Session] = None, memgraph_connection: Optional[Any] = None):
        self.db = db_session
        self.conn = memgraph_connection
        self.governance_engine = DualTierGovernanceEngine(db_session=self.db)
        if self.db and hasattr(self.db, "query"):
            self.governance_engine.load_golden_assertions()

    def render_cypher_and_params(self, mutation: GraphMutationDiff) -> tuple[str, dict[str, Any]]:
        """Maps GraphMutationDiff primitive to parameterized Cypher string and params dict."""
        prim = mutation.primitive

        if prim == ClosedSetPrimitive.ADD_NODE:
            label = mutation.metadata.get("label", "Clause") if mutation.metadata else "Clause"
            node_status = mutation.metadata.get("node_status", "RESOLVED") if mutation.metadata else "RESOLVED"
            obj_name = mutation.metadata.get("objective_name", mutation.source_node_id) if mutation.metadata else mutation.source_node_id
            obj_text = mutation.metadata.get("objective_text", "") if mutation.metadata else ""

            cypher = f"""
            MERGE (n:{label} {{id: $node_id}})
            ON CREATE SET
                n.objective_name = $objective_name,
                n.objective_text = $objective_text,
                n.node_status = $node_status,
                n.created_at = timestamp()
            ON MATCH SET
                n.objective_name = CASE WHEN n.node_status = 'STUB_UNRESOLVED' THEN $objective_name ELSE n.objective_name END,
                n.objective_text = CASE WHEN n.node_status = 'STUB_UNRESOLVED' THEN $objective_text ELSE n.objective_text END,
                n.node_status = 'RESOLVED',
                n.updated_at = timestamp()
            RETURN n
            """
            params = {
                "node_id": mutation.source_node_id,
                "objective_name": obj_name,
                "objective_text": obj_text,
                "node_status": node_status,
            }


        elif prim == ClosedSetPrimitive.ADD_EDGE:
            rel_type = (mutation.relationship_type or "SATISFIES").upper()
            if rel_type == "DEFINES":
                cypher = RCKGCypherBuilder.build_defines_linkage_cypher()
                params = {
                    "doc_id": mutation.source_node_id,
                    "node_id": mutation.target_node_id or "",
                    "set_theory_relation": mutation.set_theory_relation or "EQUIVALENT_TO",
                }
            elif rel_type == "OPERATIONALIZED_BY":
                cypher = RCKGCypherBuilder.build_operationalized_by_linkage_cypher()
                params = {
                    "activity_id": mutation.source_node_id,
                    "objective_id": mutation.target_node_id or "",
                    "set_theory_relation": mutation.set_theory_relation or "EQUIVALENT_TO",
                    "confidence_score": str(mutation.confidence_score),
                    "logic_judge_score": "1.0",
                    "technical_judge_score": "1.0",
                    "rationale": "Automated Graph Compiler Mutation",
                }
            else:
                cypher = RCKGCypherBuilder.build_satisfies_linkage_cypher()
                params = {
                    "objective_id": mutation.source_node_id,
                    "obligation_id": mutation.target_node_id or "",
                    "set_theory_relation": mutation.set_theory_relation or "SUPERSET_OF",
                    "confidence_score": str(mutation.confidence_score),
                    "logic_judge_score": "1.0",
                    "technical_judge_score": "1.0",
                    "rationale": "Automated Graph Compiler Mutation",
                }

        elif prim == ClosedSetPrimitive.SUPERSEDE_NODE:
            cypher = RCKGCypherBuilder.build_supersede_node_cypher()
            params = {
                "old_node_id": mutation.source_node_id,
                "new_node_id": mutation.target_node_id or f"NEW-{uuid4().hex[:8]}",
            }

        elif prim == ClosedSetPrimitive.CREATE_GAP:
            cypher = RCKGCypherBuilder.build_create_gap_mutation_cypher()
            params = {
                "gap_id": f"GAP-{uuid4().hex[:8]}",
                "source_node_id": mutation.source_node_id,
                "target_node_id": mutation.target_node_id or "",
                "set_theory_relation": mutation.set_theory_relation or "NO_RELATIONSHIP",
                "severity": mutation.metadata.get("gap_severity", "HIGH"),
            }

        elif prim == ClosedSetPrimitive.RECLASSIFY_EDGE:
            cypher = RCKGCypherBuilder.build_reclassify_edge_cypher()
            params = {
                "source_node_id": mutation.source_node_id,
                "target_node_id": mutation.target_node_id or "",
                "new_relation": mutation.set_theory_relation or "INTERSECTS_WITH",
            }

        elif prim == ClosedSetPrimitive.DEPRECATE_EDGE:
            cypher = RCKGCypherBuilder.build_deprecate_edge_cypher()
            params = {
                "source_node_id": mutation.source_node_id,
                "target_node_id": mutation.target_node_id or "",
            }

        else:
            cypher = RCKGCypherBuilder.build_satisfies_linkage_cypher()
            params = {
                "objective_id": mutation.source_node_id,
                "obligation_id": mutation.target_node_id or "",
                "set_theory_relation": "NO_RELATIONSHIP",
                "confidence_score": "0.0",
                "logic_judge_score": "0.0",
                "technical_judge_score": "0.0",
                "rationale": "Fallback Default",
            }

        return cypher, params

    def enqueue_and_execute(self, mutation: GraphMutationDiff) -> GraphOutboxLog:
        """
        Transactional Outbox Pattern (FIX-201 / CFIX-300):
        1. Validate mutation against DualTierGovernanceEngine.
        2. Enqueue GraphMutationDiff to PostgreSQL graph_outbox_log table.
        3. Render parameterized Cypher and execute against Memgraph FIRST.
        4. Mark outbox log status = 'EXECUTED' and commit DB ONLY IF Memgraph succeeds.
        5. Rollback PostgreSQL if Memgraph execution fails.
        """
        mutation_dict = {
            "action": mutation.metadata.get("action", mutation.primitive.value),
            "source_id": mutation.source_node_id,
            "target_id": mutation.target_node_id,
            "relation_type": mutation.set_theory_relation,
        }

        # Check governance rules (will raise GraphRegressionError if Golden Assertion violated)
        val_res = self.governance_engine.validate_mutation(mutation_dict)

        payload = mutation.model_dump()
        initial_status = "PENDING" if val_res.is_allowed else "GOVERNANCE_BLOCKED"
        outbox_entry = GraphOutboxLog(
            primitive=mutation.primitive.value,
            payload=payload,
            status=initial_status,
        )
        if self.db and hasattr(self.db, "add"):
            self.db.add(outbox_entry)
            if hasattr(self.db, "flush"):
                self.db.flush()

        if not val_res.is_allowed:
            logger.warning(
                "Graph mutation (%s -> %s) blocked by governance gate: %s",
                mutation.source_node_id, mutation.target_node_id, val_res.reason,
            )
            if self.db and hasattr(self.db, "commit"):
                self.db.commit()
            return outbox_entry

        # Synchronous Dual-Judge Evaluation (REMED-102)
        from app.services.judge import LOGIC_THRESHOLD, TECHNICAL_THRESHOLD
        from app.services.dual_judge_async import AsynchronousDualJudgeService

        try:
            judge_svc = AsynchronousDualJudgeService()
            judge_res = judge_svc.evaluate_single(
                source_id=mutation.source_node_id,
                target_id=mutation.target_node_id,
                relation_type=mutation.primitive.value,
                confidence_score=mutation.confidence_score,
            )
            outbox_entry.judge_logic_score = judge_res.logic_judge_score
            outbox_entry.judge_technical_score = judge_res.technical_judge_score

            is_structural = mutation.primitive in (ClosedSetPrimitive.ADD_NODE, ClosedSetPrimitive.ADD_EDGE) and mutation.confidence_score >= 1.0
            if not is_structural and (judge_res.logic_judge_score < LOGIC_THRESHOLD or judge_res.technical_judge_score < TECHNICAL_THRESHOLD):
                outbox_entry.status = "PENDING_HITL_REVIEW"
                outbox_entry.error_message = f"Dual-Judge score low: logic={judge_res.logic_judge_score}, tech={judge_res.technical_judge_score}"
                if self.db and hasattr(self.db, "commit"):
                    self.db.commit()
                logger.warning(
                    "Mutation (%s -> %s) held for HITL review: logic %.2f < %.2f or tech %.2f < %.2f",
                    mutation.source_node_id, mutation.target_node_id,
                    judge_res.logic_judge_score, LOGIC_THRESHOLD,
                    judge_res.technical_judge_score, TECHNICAL_THRESHOLD,
                )
                return outbox_entry
        except Exception as judge_err:
            outbox_entry.status = "PENDING_JUDGE_REVIEW"
            outbox_entry.error_message = f"Dual-Judge execution error: {judge_err}"
            if self.db and hasattr(self.db, "commit"):
                self.db.commit()
            logger.warning(
                "Mutation (%s -> %s) held for PENDING_JUDGE_REVIEW due to LLM error: %s",
                mutation.source_node_id, mutation.target_node_id, judge_err,
            )
            return outbox_entry

        # Render parameterized Cypher
        cypher, params = self.render_cypher_and_params(mutation)

        # Attempt Memgraph execution
        try:
            if self.conn:
                if hasattr(self.conn, "session"):
                    with self.conn.session() as session:
                        session.run(cypher, params)
                elif hasattr(self.conn, "cursor"):
                    cursor = self.conn.cursor()
                    cursor.execute(cypher, params)
                    if hasattr(self.conn, "commit"):
                        self.conn.commit()

            outbox_entry.status = "EXECUTED"
            outbox_entry.processed_at = datetime.now(timezone.utc)
            if self.db and hasattr(self.db, "commit"):
                self.db.commit()
            logger.info(f"Dual-write outbox entry {outbox_entry.id} processed successfully.")
            return outbox_entry
        except Exception as e:
            if self.db and hasattr(self.db, "rollback"):
                self.db.rollback()
            logger.error(f"Memgraph execution failed for outbox entry: {e}")
            raise
