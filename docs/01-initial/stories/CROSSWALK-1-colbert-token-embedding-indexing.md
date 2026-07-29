# CROSSWALK-1: ColBERT Token Embedding Indexing

**Type**: Story
**Sprint**: Sprint 5
**Story Points**: 13
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, ml, colbert, vector

---

## User Story

> As a **ML engineer**, I want ColBERTv2.0 token-level embeddings to be precomputed for all controls and stored in Qdrant with SQ8 quantization, so that high-precision MaxSim retrieval can be performed efficiently.

---

## Context and Background

Per TRD Section 8.1 and Section 4.3, ColBERT must:
- Create contextualized embeddings for every token in control text
- Store in Qdrant with SQ8 quantization (4x storage reduction)
- Support MaxSim scoring for token-level semantic matching
- Enable retrieval of top-20 candidates for any obligation query

---

## Acceptance Criteria

1. Given a control text is received, when `compute_colbert_embeddings(control_text)` is called, then token-level embeddings are generated
2. Given embeddings are computed, when they are stored in Qdrant, then they are indexed with SQ8 quantization
3. Given an obligation query is performed, when ColBERT MaxSim retrieval is executed, then the top-20 candidate controls are returned
4. Retrieval time: < 1 second for top-20 candidates
5. Each Qdrant point includes payload: `control_id`, `control_name`, `framework_id`
6. ColBERT model: `colbert-ir/colbertv2.0-adept/ir` via HuggingFace

---

## Technical Notes

- **CRITICAL FIX**: The CTO review identified that `Retriever.query()` performs retrieval against an index and does not return raw token embeddings. Use RAGatouille for correct API access:
  ```python
  from RAGatouille import RAGPretrainedModel
  
  colbert = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0-adept/ir")
  colbert.index(
      collection=control_texts,
      index_name="controls_colbert",
      max_length=500,
      doc_len=300,
      nbits=8,
      kmeans_niters=4
  )
  ```
  
  OR use direct HuggingFace transformers:
  ```python
  from transformers import AutoModel, AutoTokenizer
  
  tokenizer = AutoTokenizer.from_pretrained("colbert-ir/colbertv2.0-adept/ir")
  model = AutoModel.from_pretrained("colbert-ir/colbertv2.0-adept/ir")
  
  inputs = tokenizer(control_text, return_tensors="pt", truncation=True, max_length=500)
  outputs = model(**inputs)
  token_embeddings = outputs.last_hidden_state
  ```
- SQ8 quantization reduces storage by 4x
- Use background task for indexing to avoid API blocking

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for ColBERT embedding computation
- [ ] Integration tests for Qdrant storage and retrieval
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/colbert-indexing.md`

---

## Dependencies

- **Blocked by**: INFRA-4, DUALJUDGE-4
- **Blocks**: CROSSWALK-2
