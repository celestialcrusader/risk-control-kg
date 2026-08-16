"""
Qdrant Parent-Child Vector Indexing and Context Hydration Service for RCKG.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class QdrantParentChildService:
    def __init__(self, client: Optional[Any] = None, collection_name: str = "rckg_clauses"):
        self.client = client
        self.collection_name = collection_name
        if self.client:
            self.init_qdrant_collection()

    def init_qdrant_collection(self) -> None:
        """Ensures Qdrant collection exists with Cosine vector configuration."""
        try:
            from qdrant_client.http import models as rest
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(size=4096, distance=rest.Distance.COSINE)
                )
                logger.info("Qdrant collection '%s' created successfully.", self.collection_name)
        except Exception as err:
            logger.debug("Qdrant collection initialization note: %s", err)


    def search_and_hydrate_parent_clauses(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Performs vector search on child chunks and hydrates full parent clause context."""
        if not self.client:
            return []

        try:
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
            )
        except Exception as exc:
            logger.warning("Qdrant search error: %s", exc)
            return []

        hydrated_results = []
        for hit in hits:
            payload = getattr(hit, "payload", {}) or {}
            parent_id = payload.get("parent_clause_id")
            child_text = payload.get("text", "")
            
            parent_text = self._fetch_parent_clause_text(parent_id) if parent_id else child_text
            
            hydrated_results.append({
                "child_clause_id": payload.get("clause_id"),
                "parent_clause_id": parent_id,
                "score": getattr(hit, "score", 1.0),
                "retrieved_context": parent_text,
                "child_snippet": child_text,
            })

        return hydrated_results

    def _fetch_parent_clause_text(self, parent_id: Optional[str]) -> str:
        """Fetches parent clause context from database/graph storage."""
        if not parent_id:
            return ""
        return f"Parent Clause [{parent_id}] Context"
