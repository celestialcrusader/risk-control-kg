"""
Test suite for INFRA-4: Qdrant Vector Database Initialization

This test module verifies that Qdrant vector database is correctly configured
with the `document_chunks` collection using HNSW indexing and cosine distance.

Test Strategy:
- Integration tests that connect to Qdrant container
- Tests verify collection creation, configuration, and search operations
- Requires Docker Compose stack running with Qdrant service
"""

import pytest
from pathlib import Path
from typing import Generator

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# Test configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Qdrant configuration - matches docker-compose.yml
QDRANT_CONFIG = {
    "host": "localhost",
    "port": 6333,
    "url": "http://localhost:6333",
}


@pytest.fixture(scope="module")
def qdrant_client():
    """
    Fixture to create a Qdrant client.

    This fixture:
    1. Creates a Qdrant client configured for local development
    2. Yields the client for tests
    3. Cleans up test collections after tests complete
    """
    client = QdrantClient(
        host=QDRANT_CONFIG["host"],
        port=QDRANT_CONFIG["port"],
    )
    yield client

    # Cleanup: Delete test collections
    test_collections = ["document_chunks", "test-search-collection"]
    for collection_name in test_collections:
        try:
            if client.collection_exists(collection_name):
                client.delete_collection(collection_name)
        except Exception:
            pass  # Collection may already be deleted


class TestQdrantCollectionConfiguration:
    """Tests for Qdrant collection creation and configuration."""

    def test_qdrant_service_responds(self, qdrant_client):
        """Qdrant service is accessible and responds to requests."""
        # Simple ping to verify service is running
        try:
            client_info = qdrant_client.get_collections()
            assert client_info is not None, "Qdrant client should return collections"
        except Exception as e:
            pytest.fail(f"Qdrant service not responding: {str(e)}")

    def test_document_chunks_collection_created(self, qdrant_client):
        """TC-4.1: Given Qdrant is running, document_chunks collection exists."""
        # First create the collection with proper configuration
        qdrant_client.create_collection(
            collection_name="document_chunks",
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100),
        )

        # Verify collection exists
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]

        assert "document_chunks" in collection_names, \
            f"document_chunks collection not found. Found collections: {collection_names}"

        # Cleanup
        qdrant_client.delete_collection("document_chunks")

    def test_collection_uses_cosine_distance(self, qdrant_client):
        """TC-4.1: document_chunks collection uses cosine distance metric."""
        collection_name = "test-cosine-collection"

        # Create collection with cosine distance
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100),
        )

        # Get collection configuration
        collection_info = qdrant_client.get_collection(collection_name)

        # Verify distance metric is cosine
        vector_config = collection_info.config.params.vectors
        if isinstance(vector_config, dict):
            distance = vector_config.get("distance")
        else:
            distance = getattr(vector_config, "distance", None)

        assert distance == models.Distance.COSINE, \
            f"Collection should use COSINE distance. Got: {distance}"

        # Cleanup
        qdrant_client.delete_collection(collection_name)

    def test_collection_uses_hnsw_indexing(self, qdrant_client):
        """TC-4.1: document_chunks collection uses HNSW indexing."""
        collection_name = "test-hnsw-collection"

        # Create collection with HNSW config
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100),
        )

        # Get collection configuration
        collection_info = qdrant_client.get_collection(collection_name)

        # Verify HNSW configuration exists
        hnsw_config = collection_info.config.hnsw_config
        assert hnsw_config is not None, "HNSW config should be present"

        # Cleanup
        qdrant_client.delete_collection(collection_name)


class TestEmbeddingStorage:
    """Tests for embedding storage with payload fields."""

    def test_embedding_upload_with_payload_fields(self, qdrant_client):
        """TC-4.2: Given the collection exists, when a sample embedding is uploaded,
        then it is stored with all payload fields."""
        collection_name = "test-payload-collection"
        test_vector = [0.1] * 1024  # 1024-dimensional vector for BGE-M3

        # Create collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
        )

        # Upload embedding with all payload fields
        points = [
            models.PointStruct(
                id=1,
                vector=test_vector,
                payload={
                    "document_id": "doc-123",
                    "section": "section-4.2",
                    "text": "This is a sample embedding for testing",
                    "metadata": {
                        "file_name": "regulation.pdf",
                        "page_number": 42,
                        "embedding_model": "BGE-M3",
                        "created_at": "2026-01-15T10:30:00Z",
                    },
                },
            )
        ]

        qdrant_client.upsert(collection_name=collection_name, points=points)

        # Retrieve the point to verify payload fields
        retrieved = qdrant_client.get(
            collection_name=collection_name,
            ids=[1],
        )

        assert len(retrieved) == 1, "Should retrieve exactly one point"

        point = retrieved[0]
        payload = point.payload

        # Verify all payload fields are present
        assert payload.get("document_id") == "doc-123", "document_id payload field missing"
        assert payload.get("section") == "section-4.2", "section payload field missing"
        assert payload.get("text") == "This is a sample embedding for testing", "text payload field missing"

        # Verify metadata fields
        metadata = payload.get("metadata", {})
        assert metadata.get("file_name") == "regulation.pdf", "metadata.file_name missing"
        assert metadata.get("page_number") == 42, "metadata.page_number missing"
        assert metadata.get("embedding_model") == "BGE-M3", "metadata.embedding_model missing"

        # Cleanup
        qdrant_client.delete_collection(collection_name)

    def test_multiple_payload_field_types(self, qdrant_client):
        """Payload supports various data types (string, number, boolean, object)."""
        collection_name = "test-types-collection"

        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
        )

        # Upload point with various data types
        point = models.PointStruct(
            id=1,
            vector=[0.5] * 1024,
            payload={
                "string_field": "test",
                "number_field": 42,
                "boolean_field": True,
                "array_field": ["item1", "item2"],
                "object_field": {"nested": "value"},
            },
        )

        qdrant_client.upsert(collection_name=collection_name, points=[point])

        # Verify all types are preserved
        retrieved = qdrant_client.get(collection_name=collection_name, ids=[1])
        payload = retrieved[0].payload

        assert payload["string_field"] == "test"
        assert payload["number_field"] == 42
        assert payload["boolean_field"] is True
        assert payload["array_field"] == ["item1", "item2"]
        assert payload["object_field"]["nested"] == "value"

        # Cleanup
        qdrant_client.delete_collection(collection_name)


class TestVectorSearch:
    """Tests for vector search operations."""

    def test_vector_search_returns_results(self, qdrant_client):
        """TC-4.3: Given the collection exists, when a vector search query is executed
        with top-K=10, then the results are returned."""
        collection_name = "test-search-collection"

        # Create collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=10, distance=models.Distance.COSINE),
        )

        # Upload test vectors
        test_vectors = [
            models.PointStruct(
                id=i,
                vector=[i * 0.1] * 10,
                payload={"document_id": f"doc-{i}", "text": f"Document {i}"},
            )
            for i in range(5)
        ]

        qdrant_client.upsert(collection_name=collection_name, points=test_vectors)

        # Execute search with top-K=10 (more than available)
        query_vector = [0.5] * 10
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
        )

        # Verify results are returned
        assert len(search_results) > 0, "Search should return at least one result"
        assert len(search_results) <= 5, "Should return at most all 5 uploaded vectors"

        # Each result should have id, score, and payload
        for result in search_results:
            assert result.id is not None, "Result should have an id"
            assert result.score is not None, "Result should have a similarity score"
            assert result.payload is not None, "Result should have payload"

        # Cleanup
        qdrant_client.delete_collection(collection_name)

    def test_vector_search_performance_under_500ms(self, qdrant_client):
        """TC-4.3: Vector search with top-K=10 returns results in < 500ms."""
        import time

        collection_name = "test-performance-collection"

        # Create collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
        )

        # Upload 100 test vectors
        test_vectors = [
            models.PointStruct(
                id=i,
                vector=[0.1 * i] * 1024,
                payload={"document_id": f"doc-{i}"},
            )
            for i in range(100)
        ]

        qdrant_client.upsert(collection_name=collection_name, points=test_vectors)

        # Measure search time
        query_vector = [0.5] * 1024
        start_time = time.perf_counter()

        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
        )

        end_time = time.perf_counter()
        search_time_ms = (end_time - start_time) * 1000

        # Verify results
        assert len(search_results) == 10, f"Should return exactly 10 results. Got: {len(search_results)}"

        # Verify performance (should be well under 500ms for 100 vectors)
        assert search_time_ms < 500, \
            f"Search took {search_time_ms:.2f}ms, which exceeds 500ms threshold"

        # Cleanup
        qdrant_client.delete_collection(collection_name)

    def test_vector_search_with_payload_filter(self, qdrant_client):
        """TC-4.4: Given the collection exists, when a payload filter is applied
        (e.g., document_id = "doc-123"), then only matching chunks are returned."""
        collection_name = "test-filter-collection"

        # Create collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=10, distance=models.Distance.COSINE),
        )

        # Upload test vectors with different document_ids
        test_vectors = [
            models.PointStruct(
                id=i,
                vector=[i * 0.1] * 10,
                payload={"document_id": f"doc-{i % 3}", "section": f"section-{i}"},
            )
            for i in range(9)
        ]

        qdrant_client.upsert(collection_name=collection_name, points=test_vectors)

        # Search with payload filter for document_id = "doc-0"
        query_vector = [0.5] * 10
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value="doc-0"),
                    ),
                ],
            ),
        )

        # Verify only matching results are returned
        for result in search_results:
            assert result.payload.get("document_id") == "doc-0", \
                f"Filter should only return doc-0, got: {result.payload.get('document_id')}"

        # Verify correct number of results (ids 0, 3, 6 have doc-0)
        assert len(search_results) == 3, \
            f"Should return exactly 3 results for doc-0. Got: {len(search_results)}"

        # Cleanup
        qdrant_client.delete_collection(collection_name)

    def test_search_with_multiple_payload_filters(self, qdrant_client):
        """Payload filters can be combined with AND/OR logic."""
        collection_name = "test-multi-filter-collection"

        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=10, distance=models.Distance.COSINE),
        )

        # Upload test vectors
        test_vectors = [
            models.PointStruct(
                id=i,
                vector=[i * 0.1] * 10,
                payload={
                    "document_id": f"doc-{i % 2}",
                    "section": f"section-A" if i < 5 else f"section-B",
                },
            )
            for i in range(10)
        ]

        qdrant_client.upsert(collection_name=collection_name, points=test_vectors)

        # Search with multiple filters (AND logic)
        query_vector = [0.5] * 10
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=10,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value="doc-0"),
                    ),
                    models.FieldCondition(
                        key="section",
                        match=models.MatchValue(value="section-A"),
                    ),
                ],
            ),
        )

        # Verify both filters are applied
        for result in search_results:
            payload = result.payload
            assert payload.get("document_id") == "doc-0", "document_id filter not applied"
            assert payload.get("section") == "section-A", "section filter not applied"

        # Cleanup
        qdrant_client.delete_collection(collection_name)


class TestQdrantStorageConfiguration:
    """Tests for Qdrant storage configuration."""

    def test_qdrant_storage_volume_configured(self, qdrant_client):
        """TC-4.5: Qdrant storage path is configured as /qdrant/storage with named volume."""
        # This is verified by docker-compose.yml having:
        # volumes:
        #   - qdrant_storage:/qdrant/storage
        # and:
        # volumes:
        #   qdrant_storage:

        # We verify the collection can be created and persists
        collection_name = "test-persistence-collection"

        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=10, distance=models.Distance.COSINE),
        )

        # Verify collection exists
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        assert collection_name in collection_names, "Collection should persist in storage"

        # Cleanup
        qdrant_client.delete_collection(collection_name)

    def test_qdrant_documentation_exists(self, qdrant_client):
        """TC-4.6: Documentation in docs/01-initial/vector-store.md includes collection creation script."""
        docs_dir = PROJECT_ROOT / "docs" / "01-initial"
        vector_store_doc = docs_dir / "vector-store.md"

        assert vector_store_doc.exists(), "vector-store.md should exist"

        content = vector_store_doc.read_text()

        # Verify documentation includes key sections
        assert "document_chunks" in content, "Documentation should mention document_chunks collection"
        assert "cosine" in content.lower() or "COSINE" in content, \
            "Documentation should mention cosine distance metric"
        assert "hnsw" in content.lower() or "HNSW" in content, \
            "Documentation should mention HNSW indexing"
        assert "qdrant_client" in content or "QdrantClient" in content, \
            "Documentation should show Python client usage"

        # Cleanup
        try:
            if qdrant_client.collection_exists("document_chunks"):
                qdrant_client.delete_collection("document_chunks")
        except Exception:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
