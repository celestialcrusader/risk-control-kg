# INFRA-4: Qdrant Vector Database Initialization

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: infrastructure, vector-database, qdrant, ml

---

## User Story

> As a **ML engineer**, I want Qdrant to have the `document_chunks` collection pre-configured with proper schema and payload indexes, so that embedding storage and retrieval can begin immediately.

---

## Context and Background

Per TRD Section 4.3 and Section 3.4, Qdrant stores:
- BGE-M3 dense embeddings
- ColBERTv2.0 token-level embeddings (SQ8 quantized)

The collection schema must support:
- `document_id` payload (for filtering)
- `section` payload (for hierarchy)
- `text` payload (for display)
- `metadata` payload (JSONB)

---

## Acceptance Criteria

1. Given Qdrant is running, when the `document_chunks` collection is created, then it uses HNSW indexing with cosine distance metric
2. Given the collection exists, when a sample embedding is uploaded, then it is stored with all payload fields
3. Given the collection exists, when a vector search query is executed with top-K=10, then the results are returned in < 500ms
4. Given the collection exists, when a payload filter is applied (e.g., `document_id = "doc-123"`), then only matching chunks are returned
5. Qdrant storage path configured: `/qdrant/storage` with named volume
6. Documentation in `docs/01-initial/vector-store.md` includes collection creation script

---

## Definition of Done

- [x] Code written and peer-reviewed
- [x] Unit tests for Qdrant operations
- [x] Integration tests for vector search
- [x] All acceptance criteria verified
- [x] Documentation updated

---

## Dependencies

- **Blocked by**: INFRA-1
- **Blocks**: EMBED-1, CROSSWALK-1

---

## Technical Notes

- Collection configuration:
  ```python
  qdrant_client.create_collection(
      collection_name="document_chunks",
      vectors_config=VectorParams(size=1024, distance="Cosine"),
      hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
  )
  ```
- Enable SQ8 quantization for ColBERT embeddings to reduce storage by 4x
- Create payload index on `document_id` for fast filtering
- Use Qdrant Python client SDK for all operations
