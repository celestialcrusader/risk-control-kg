"""
Dual-Tier Governance Engine & Golden Assertions Snapshot Testing Compiler Gate (RCKG-402).

Prevents auto-commissions of ontology/schema mutations (ADD_NODE_TYPE, REDEFINE_FACET)
by flagging them for Human Committee sign-off, and raises GraphRegressionError on mutations
that contradict pinned Golden Assertions.
"""

import logging
from typing import Dict, Any, List, Set, Tuple, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GraphRegressionError(Exception):
    """Raised when a proposed graph mutation violates a pinned Golden Assertion."""
    pass


class GovernanceValidationResult(BaseModel):
    is_allowed: bool
    status: str  # AUTO_COMMIT_APPROVED / NEEDS_HUMAN_GOVERNANCE_SIGN_OFF / BLOCKED_GOLDEN_ASSERTION
    reason: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DualTierGovernanceEngine:
    """Dual-Tier Governance Engine & Compiler Gate."""

    ONTOLOGY_ACTIONS: Set[str] = {
        "ADD_NODE_TYPE",
        "DELETE_NODE_TYPE",
        "REDEFINE_FACET",
        "ALTER_ONTOLOGY_SCHEMA",
    }

    def __init__(self, db_session: Optional[Any] = None):
        self.db = db_session
        self._golden_assertions: Set[Tuple[str, str, str]] = set()

    def register_golden_assertion(self, source_id: str, target_id: str, relation_type: str) -> None:
        """Pin a Golden Assertion pair (source_id, target_id, relation_type) and persist to DB."""
        self._golden_assertions.add((source_id, target_id, relation_type))
        if self.db:
            try:
                from app.models import ControlObjectiveFrameworkMapping, SetTheoryRelation
                rel_enum = SetTheoryRelation[relation_type] if relation_type in SetTheoryRelation.__members__ else SetTheoryRelation.EQUIVALENT_TO
                mapping = ControlObjectiveFrameworkMapping(
                    set_theory_relation=rel_enum,
                    is_golden_assertion="TRUE",
                    status="HUMAN_ATTESTED",
                )
                if hasattr(self.db, "merge"):
                    self.db.merge(mapping)
                if hasattr(self.db, "commit"):
                    self.db.commit()
            except Exception as e:
                logger.error(
                    "Failed to persist golden assertion (%s -> %s [%s]) to database: %s",
                    source_id, target_id, relation_type, e,
                )
                if hasattr(self.db, "rollback"):
                    try:
                        self.db.rollback()
                    except Exception:
                        pass


    def load_golden_assertions(self) -> int:
        """Load all pinned Golden Assertions from PostgreSQL database into memory."""
        if not self.db:
            return 0

        try:
            from app.models import ControlObjectiveFrameworkMapping
            records = self.db.query(ControlObjectiveFrameworkMapping).filter(
                ControlObjectiveFrameworkMapping.is_golden_assertion == "TRUE"
            ).all()

            for rec in records:
                s_id = getattr(rec, "control_objective_id", "") or ""
                t_id = getattr(rec, "framework_objective_id", "") or ""
                rel = rec.set_theory_relation.name if hasattr(rec.set_theory_relation, "name") else str(rec.set_theory_relation)
                self._golden_assertions.add((str(s_id), str(t_id), rel))
            return len(records)
        except Exception as ex:
            logger.warning("Failed to load golden assertions from DB: %s", ex)
            return 0

    def validate_mutation(self, mutation: Dict[str, Any]) -> GovernanceValidationResult:
        """Validate proposed mutation against ontology rules & Golden Assertions."""
        action = mutation.get("action", "")

        # Check Tier 1: Ontology / Schema mutations
        if action in self.ONTOLOGY_ACTIONS:
            return GovernanceValidationResult(
                is_allowed=False,
                status="NEEDS_HUMAN_GOVERNANCE_SIGN_OFF",
                reason=f"Ontology mutation action '{action}' requires Human Governance Committee sign-off.",
            )

        # Check Tier 2: Golden Assertion regression check
        source_id = mutation.get("source_id")
        target_id = mutation.get("target_id")
        relation_type = mutation.get("relation_type")

        if action in ["DEPRECATE_EDGE", "RECLASSIFY_EDGE", "SUPERSEDE_NODE"]:
            key = (source_id, target_id, relation_type)
            if key in self._golden_assertions:
                raise GraphRegressionError(
                    f"Golden Assertion regression detected: Pinned edge ({source_id} -> {target_id} [{relation_type}]) cannot be broken or deprecated by LLM mutation."
                )

        return GovernanceValidationResult(
            is_allowed=True,
            status="AUTO_COMMIT_APPROVED",
            reason="Instance mutation approved by compiler gate.",
        )
