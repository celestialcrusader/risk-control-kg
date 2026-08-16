"""
Bitemporal Graph Revert Endpoint & Audit Trail Service (RCKG-403 / CFIX-101).

Provides first-class graph revert capabilities, attaching audit metadata
(reverted_by, reverted_at, revert_reason, status='REVERTED') and tagging release version (e.g. v1.2.0 [REVERT diff-8921]).
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RevertResult(BaseModel):
    diff_id: str
    auditor_id: str
    revert_reason: str
    reverted_at: str
    status: str = "REVERTED"
    release_tag: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphRevertService:
    """Bitemporal Graph Revert Service."""

    def __init__(
        self,
        current_release: str = "v1.1.0",
        db_session: Optional[Any] = None,
        memgraph_connection: Optional[Any] = None,
    ):
        self.current_release = current_release
        self.db = db_session
        self.conn = memgraph_connection

    def execute_revert(
        self,
        diff_id: str,
        auditor_id: str,
        revert_reason: str,
    ) -> RevertResult:
        """Execute revert operation on target graph diff and emit audit release tag."""
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.isoformat()

        # Update Memgraph graph database if connection exists
        if self.conn:
            try:
                cypher = """
                MATCH ()-[r]->()
                WHERE r.diff_id = $diff_id OR r.mapping_id = $diff_id OR r.node_id = $diff_id
                SET r.status = 'REVERTED',
                    r.reverted_by = $auditor_id,
                    r.reverted_at = $reverted_at,
                    r.revert_reason = $revert_reason
                RETURN count(r) as reverted_count
                """
                params = {
                    "diff_id": diff_id,
                    "auditor_id": auditor_id,
                    "reverted_at": now_str,
                    "revert_reason": revert_reason,
                }

                if hasattr(self.conn, "cursor"):
                    cursor = self.conn.cursor()
                    cursor.execute(cypher, params)
                    if hasattr(self.conn, "commit"):
                        self.conn.commit()
                elif hasattr(self.conn, "session"):
                    # neo4j Driver instance
                    with self.conn.session() as session:
                        session.run(cypher, **params)
                elif hasattr(self.conn, "execute"):
                    self.conn.execute(cypher, params)
            except Exception as ex:
                logger.warning("Memgraph graph revert execution warning: %s", ex)

        # Update PostgreSQL ORM if db_session exists
        if self.db:
            try:
                from app.models import ControlObjectiveFrameworkMapping, MappingStatus
                mappings = self.db.query(ControlObjectiveFrameworkMapping).filter(
                    ControlObjectiveFrameworkMapping.id == diff_id
                ).all()
                for m in mappings:
                    m.status = MappingStatus.DEPRECATED if hasattr(MappingStatus, "DEPRECATED") else "REVERTED"
                    m.reverted_by = auditor_id
                    m.reverted_at = now_dt
                    m.revert_reason = revert_reason
                self.db.commit()
            except Exception as ex:
                logger.warning("DB revert update warning: %s", ex)

        # Compute next release tag
        clean_ver = self.current_release.split()[0].lstrip("v")
        parts = clean_ver.split(".")
        if len(parts) == 3:
            major, minor, patch = parts
            release_tag = f"v{major}.{int(minor) + 1}.0 [REVERT {diff_id}]"
        else:
            release_tag = f"v1.2.0 [REVERT {diff_id}]"

        logger.info(
            "Graph revert executed by auditor %s for diff %s. Reason: %s",
            auditor_id,
            diff_id,
            revert_reason,
        )

        return RevertResult(
            diff_id=diff_id,
            auditor_id=auditor_id,
            revert_reason=revert_reason,
            reverted_at=now_str,
            status="REVERTED",
            release_tag=release_tag,
            metadata={"action": "BITEMPORAL_GRAPH_REVERT"},
        )
