"""
PostgreSQL Outbox Event-Driven Embedding Sync Controller (RCKG-404).

Listens for SUPERSEDE_NODE PostgreSQL outbox events and updates Qdrant vector point payload metadata
with valid_to timestamps to enable bitemporal time-travel queries.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# AI-REQ-06: Strict single embedding model to maintain vector space consistency in Qdrant
EMBEDDING_MODEL_NAME = os.getenv("MODEL_EMBEDDING_NAME", "Qwen/Qwen3-Embedding-8B")
EMBEDDING_DIM = int(os.getenv("MODEL_EMBEDDING_DIM", "4096"))


class OutboxEvent(BaseModel):
    event_id: str
    event_type: str
    payload: Dict[str, Any]


class QdrantVectorStoreMock:
    """Mock/Wrapper for Qdrant Vector DB bitemporal payload synchronization."""

    def __init__(self):
        self.points: Dict[str, Dict[str, Any]] = {}

    def upsert_point(self, point_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        self.points[point_id] = {"vector": vector, "payload": payload}

    def get_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        return self.points.get(point_id)

    def update_payload(self, point_id: str, payload_diff: Dict[str, Any]) -> bool:
        if point_id in self.points:
            self.points[point_id]["payload"].update(payload_diff)
            return True
        return False

    def search_with_bitemporal_filter(self, as_of_date: str) -> List[Dict[str, Any]]:
        """Filter points where valid_from <= as_of_date and (valid_to is null or valid_to > as_of_date)."""
        matching = []
        for pid, pt in self.points.items():
            payload = pt["payload"]
            v_from = payload.get("valid_from", "")
            v_to = payload.get("valid_to")

            if v_from <= as_of_date:
                if v_to is None or v_to > as_of_date:
                    matching.append(pt)

        return matching


class EmbeddingSyncController:
    """PostgreSQL Outbox Event Listener for Vector Payload Sync."""

    def __init__(self, vector_store: Optional[QdrantVectorStoreMock] = None):
        self.vector_store = vector_store or QdrantVectorStoreMock()

    def process_outbox_event(self, event: OutboxEvent) -> Dict[str, Any]:
        """Process outbox event and update Qdrant payload."""
        if event.event_type == "SUPERSEDE_NODE":
            node_id = event.payload.get("node_id")
            valid_to = event.payload.get("valid_to")
            superseded_by = event.payload.get("superseded_by")

            if node_id and valid_to:
                success = self.vector_store.update_payload(
                    point_id=node_id,
                    payload_diff={"valid_to": valid_to, "superseded_by": superseded_by},
                )
                logger.info(
                    "Updated Qdrant point %s payload with valid_to=%s (Status: %s)",
                    node_id,
                    valid_to,
                    success,
                )
                return {"status": "SUCCESS", "node_id": node_id, "synced": success}

        return {"status": "SKIPPED", "reason": f"Unhandled event_type {event.event_type}"}
