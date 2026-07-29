# CROSSWALK-2: BGE-M3 Dense Embedding Reranking

**Type**: Story
**Sprint**: Sprint 5
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, ml, bge-m3, reranking

---

## User Story

> As a **ML engineer**, I want BGE-Reranker-V2-M3 to re-rank the top-20 ColBERT candidates to top-5, so that cross-encoder semantics can further refine the candidate pool before LLM classification.

---

## Context and Background

Per TRD Section 8.2, the reranking pipeline must:
- Accept top-20 ColBERT candidates
- Apply BGE-Reranker-V2-M3 cross-encoder
- Return top-5 re-ranked candidates with confidence scores
- Re-rank time: < 2 seconds

---

## Acceptance Criteria

1. Given top-20 ColBERT candidates, when `rerank_with_bge(obligation_text, candidates)` is called, then re-ranked top-5 are returned
2. Given re-ranking is complete, when the results are sorted, then they are ordered by BGE reranker score (descending)
3. Given an obligation-control pair, when reranked, then the score reflects semantic similarity (higher = more similar)
4. BGE reranker model: `BAAI/bge-reranker-v2-m3` via HuggingFace
5. Output includes: `control_id`, `rerank_score`, `rank` (1-5)
6. Reranking output stored temporarily in Redis with TTL 300 seconds

---

## Technical Notes

- BGE reranking:
  ```python
  from FlagEmbedding import FlagReranker
  
  reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
  
  pairs = [[obligation_text, candidate["text"]] for candidate in colbert_candidates]
  scores = reranker.compute_score(pairs)
  
  ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:5]
  ```
- Redis caching:
  ```python
  cache_key = f"rckg:rerank:{obligation_id}"
  redis_client.setex(cache_key, 300, json.dumps(ranked))
  ```
- Use GPU if available for faster reranking

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for BGE reranking with sample data
- [ ] Integration tests for reranker model
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: CROSSWALK-1
- **Blocks**: CROSSWALK-3
