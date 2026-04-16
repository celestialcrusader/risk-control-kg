"""
Qdrant Vector Database Client for RCKG.

This module provides a unified interface for storing and retrieving
embedding vectors in Qdrant vector database.

Configuration via environment variables:
    - QDRANT_HOST: Qdrant server host (default: localhost)
    - QDRANT_PORT: Qdrant server port (default: 6333)
"""

import os
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.models import Distance, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


@dataclass
class EmbeddingChunk:
    """Represents a chunk of text with its embedding vector."""

    id: Union[str, int]
    vector: List[float]
    document_id: str
    section: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


class QdrantVectorStore:
    """
    Qdrant vector database client for embedding storage and retrieval.

    Configuration via environment variables:
        - QDRANT_HOST: Qdrant server host (default: localhost)
        - QDRANT_PORT: Qdrant server port (default: 6333)
        - COLLECTION_NAME: Collection name (default: document_chunks)
        - VECTOR_SIZE: Vector dimension size (default: 1024 for BGE-M3)
    """

    DEFAULT_COLLECTION_NAME = "document_chunks"
    DEFAULT_VECTOR_SIZE = 1024  # BGE-M3 embedding size

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        vector_size: Optional[int] = None,
    ):
        """
        Initialize Qdrant vector store client.

        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection to use
            vector_size: Dimension size of vectors (1024 for BGE-M3)
        """
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = collection_name or os.getenv(
            "QDRANT_COLLECTION_NAME",
            self.DEFAULT_COLLECTION_NAME
        )
        self.vector_size = vector_size or int(
            os.getenv("QDRANT_VECTOR_SIZE", str(self.DEFAULT_VECTOR_SIZE))
        )

        # Initialize Qdrant client
        self.client = QdrantClient(
            host=self.host,
            port=self.port,
        )

        # Ensure collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists, creating it if necessary."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                ),
                hnsw_config= models.HnswConfigDiff(
                    m=16,
                    ef_construct=100
                ),
            )

    def upload_embedding(
        self,
        chunk: EmbeddingChunk,
    ) -> bool:
        """
        Upload a single embedding chunk.

        Args:
            chunk: EmbeddingChunk object with vector and payload

        Returns:
            True if upload succeeded
        """
        payload: Dict[str, Any] = {
            "document_id": chunk.document_id,
            "section": chunk.section,
            "text": chunk.text,
        }

        if chunk.metadata:
            payload["metadata"] = chunk.metadata

        point = models.PointStruct(
            id=str(chunk.id),
            vector=chunk.vector,
            payload=payload,
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )

        return True

    def upload_embeddings(
        self,
        chunks: List[EmbeddingChunk],
    ) -> int:
        """
        Upload multiple embedding chunks.

        Args:
            chunks: List of EmbeddingChunk objects

        Returns:
            Number of chunks uploaded
        """
        points = []
        for chunk in chunks:
            payload: Dict[str, Any] = {
                "document_id": chunk.document_id,
                "section": chunk.section,
                "text": chunk.text,
            }

            if chunk.metadata:
                payload["metadata"] = chunk.metadata

            points.append(
                models.PointStruct(
                    id=str(chunk.id),
                    vector=chunk.vector,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        return len(chunks)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_by: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_by: Optional payload filter (e.g., {"document_id": "doc-123"})

        Returns:
            List of results with id, score, and payload
        """
        query_filter = None

        if filter_by:
            conditions = []
            for key, value in filter_by.items():
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value),
                    )
                )

            if conditions:
                query_filter = models.Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]

    def get(
        self,
        ids: Union[List[Union[str, int]], Union[str, int]],
    ) -> List[Dict[str, Any]]:
        """
        Get chunks by ID.

        Args:
            ids: Single ID or list of IDs to retrieve

        Returns:
            List of chunks with id and payload
        """
        if isinstance(ids, (str, int)):
            ids = [ids]

        results = self.client.get(
            collection_name=self.collection_name,
            ids=ids,
        )

        return [
            {
                "id": result.id,
                "payload": result.payload,
            }
            for result in results
        ]

    def delete_collection(self) -> bool:
        """
        Delete the collection.

        Returns:
            True if deletion succeeded
        """
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
            return True
        return False

    def collection_exists(self) -> bool:
        """Check if the collection exists."""
        return self.client.collection_exists(self.collection_name)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection configuration information."""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": info.config.params.vectors,
            "vector_size": info.config.params.vector_size,
            "distance": info.config.params.distance,
            "point_count": info.points_count,
        }


# Singleton instance for convenience
_qdrant_store_instance: Optional[QdrantVectorStore] = None


def get_qdrant_vector_store() -> QdrantVectorStore:
    """
    Get the singleton Qdrant vector store instance.

    Returns:
        QdrantVectorStore instance configured from environment variables
    """
    global _qdrant_store_instance
    if _qdrant_store_instance is None:
        _qdrant_store_instance = QdrantVectorStore()
    return _qdrant_store_instance


__all__ = [
    "QdrantVectorStore",
    "EmbeddingChunk",
    "get_qdrant_vector_store",
]
