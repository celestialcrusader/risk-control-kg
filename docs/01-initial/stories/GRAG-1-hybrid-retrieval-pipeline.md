# GRAG-1: Hybrid Retrieval Pipeline

**Type**: Story
**Sprint**: Sprint 7
**Story Points**: 10
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, rag, retrieval, graph

---

## User Story

> As a **compliance officer**, I want a hybrid retrieval pipeline that combines dense vector search with graph traversal, so that I can get comprehensive answers to compliance questions.

---

## Context and Background

Per TRD Section 10.1, GraphRAG must:
- Stage 1: Dense vector search (BGE-M3) to identify top-K candidate nodes
- Stage 2: One-hop graph traversal from candidate nodes to extract semantic subgraph
- Stage 3: Combined result passed to LLM for grounded synthesis
- Query response time: < 5 seconds p95

---

## Acceptance Criteria

1. Given a natural language query, when `graphrag_query(query)` is called, then dense vector search returns top-10 candidate nodes from Qdrant
2. Given candidates are retrieved, when graph traversal is executed, then one-hop neighbors are fetched from Memgraph
3. Given the subgraph is extracted, when it is combined with vector results, then the LLM receives both raw text and structured graph context
4. Query response time: < 5 seconds p95 for queries against active graph
5. Context includes: retrieved chunks, graph nodes, graph edges, relationship types
6. Results cached in Redis with TTL 300 seconds

---

## Technical Notes

- Dense vector search:
  ```python
  from qdrant_client import QdrantClient

  client = QdrantClient("localhost", port=6333)
  query_embedding = embedding_model.encode(query)
  search_results = client.search(
      collection_name="document_chunks",
      query_vector=query_embedding,
      limit=10,
      query_filter=Filter(must=[
        FieldCondition(key="ai-input", match=MatchValue(value="yes"))
      ])
  )
  ```
- Graph traversal using Memgraph client:
  ```cypher
  MATCH (n)-[r]->(neighbor)
  WHERE n.id IN $candidate_ids
  RETURN n, r, neighbor
  LIMIT 50
  ```
- Context assembly combines vector results, graph nodes, and graph edges

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for retrieval pipeline
- [ ] Integration tests for Qdrant + Memgraph
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/graphrag.md`

---

## Dependencies

- **Blocked by**: INFRA-4, INFRA-1
- **Blocks**: GRAG-2
