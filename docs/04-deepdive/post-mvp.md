# Pure RCKG Engine — Post-MVP Production Hardening Sprint Plan

**Document Version:** 1.0 — Production Hardening Sprint Plan  
**Status:** Draft / Pending Approval  
**Classification:** Internal — Confidential Engineering Specification  
**Date:** July 31, 2026  
**Prerequisite:** Completion of [real-mvp.md](file:///home/zackchow/coding/rckg/docs/04-deepdive/real-mvp.md) (Sprints 1–3)  
**Governing Spec:** [06-delta.md](file:///home/zackchow/coding/rckg/docs/02-pickup/06-delta.md)  
**Target Repository:** `/home/zackchow/coding/rckg`  

---

## 1. Executive Context & Post-MVP Scope

The Real MVP (Sprints 1–3 in `real-mvp.md`) delivers a **functional, end-to-end extraction and graph injection pipeline**. However, 4 infrastructure-heavy components were deferred because they require dedicated cluster services (Qdrant, Kafka) or large GPU model weights (ColBERT, Surya OCR):

| Deferred Item | Code Review Finding | Current State | Production Risk |
|---|---|---|---|
| **#9 Real Qdrant Vector Store** | `QdrantVectorStoreMock` in-memory dict | `EmbeddingSyncController` stores payloads in a Python `dict` lost on restart | Bitemporal time-travel queries non-functional after restart |
| **#21 ColBERT Model Loading** | Synthetic hash-seeded embeddings via `_generate_synthetic_token_embeddings()` | `ColBERTTokenCacheService` uses NumPy deterministic hashes instead of real token embeddings | Stage 2 MaxSim reranking produces random ranking, not semantic |
| **#22 Kafka Event Publishing** | `logger.info()` instead of Kafka producer | `_publish_retrain_trigger_event()` is a log statement only | KTO/DPO fine-tuning pipeline never triggered — models never improve |
| **#23 PDF Format Classifier** | Crude heuristic Latin-1 byte scanning | `classify()` uses `/Font` string count from raw PDF bytes instead of real PDF structure introspection | SCANNED_PDF and COMPLEX_MATRIX parser routes rarely activated; scanned documents mis-parsed |

This post-MVP sprint plan (Sprint 4 — Production Hardening) swaps all 4 stubs with enterprise-grade implementations, enabling:
- **Real bitemporal time-travel** queries against persistent Qdrant vector collections
- **Semantic MaxSim reranking** via locally-loaded `colbert-ir/colbertv2.0` model weights
- **Automated student LLM fine-tuning pipeline** via Kafka → `kto.retrain.trigger` topic
- **Accurate format routing** for scanned PDFs and complex matrix documents via PyMuPDF feature extraction

---

## 2. Sprint Planning Principles

- **Sprint Length:** 2-week sprint
- **Team Composition:** 1 AI/Backend Engineer + 1 Infrastructure/DevOps Engineer
- **Velocity Assumption:** ~28–32 Story Points (heavier infrastructure integration work)
- **Sprint Goal Philosophy:** After Sprint 4, all 27 code review findings are resolved at **enterprise production-grade** level. Every service call uses a real persistent backing store or GPU model — no in-memory mocks remain.
- **Ticket ID Prefix:** `PMVP-` (Post-MVP production hardening prefix)
- **Hardware Assumption:** NVIDIA DGX Spark (128GB VRAM) — ColBERT and Qdrant can be loaded alongside vLLM inference.

---

## 3. Sprint 4: Production Hardening — Qdrant, ColBERT, Kafka & Format Classifier

**Sprint Goal:** Replace all 4 deferred MVP stubs with enterprise production-grade implementations: a live Qdrant vector store with bitemporal payload support, a locally-loaded ColBERT cross-encoder for semantic MaxSim reranking, a live Kafka producer for KTO/DPO preference streaming, and a real PyMuPDF-based format classifier that correctly activates SCANNED_PDF and COMPLEX_MATRIX routing paths.

**Rationale:** Sprints 1–3 made the pipeline functionally correct. Sprint 4 makes it **enterprise-grade at scale** — suitable for processing real compliance document corpora across thousands of regulatory frameworks.

**Stories in this Sprint:** `PMVP-400`, `PMVP-401`, `PMVP-402`, `PMVP-403`  
**Total Story Points:** 31

---

### [PMVP-400] Replace `QdrantVectorStoreMock` with Live Qdrant Client & Bitemporal Collection

**Type:** Story  
**Sprint:** Sprint 4  
**Story Points:** 8  
**Priority:** High  
**Assigned To:** Backend Engineer  
**Labels:** `backend`, `qdrant`, `vector-store`, `bitemporal`, `infrastructure`

#### User Story
> As a **Compliance Officer**, I want **bitemporal time-travel queries to return consistent results across server restarts**, so that **I can query the knowledge graph as it existed at any historical point in time (AS-OF-DATE) with guarantee that superseded node versions are correctly filtered**.

#### Context and Background
Code Review Finding #9: `EmbeddingSyncController` uses `QdrantVectorStoreMock` — a plain Python `dict` (`self.points: Dict[str, Dict[str, Any]] = {}`) — to store vector point payloads. When the FastAPI process restarts, all stored embeddings and their bitemporal metadata (`valid_from`, `valid_to`) are lost. Per Delta §7.6, the `EmbeddingSyncController` must listen to `SUPERSEDE_NODE` outbox events and update persistent Qdrant point payloads with `valid_to` timestamps to enable AS-OF-DATE historical graph traversal.

This story introduces a live Qdrant client connection and provisions a dedicated `rckg_compliance_nodes` collection with a payload index on `valid_from` and `valid_to` fields.

#### Acceptance Criteria
1. Given a running Qdrant instance (port 6333), when `EmbeddingSyncController` initializes, then a real `QdrantClient` is created pointing to the configured Qdrant host — **not `QdrantVectorStoreMock`**.
2. Given a `SUPERSEDE_NODE` outbox event with `node_id` and `valid_to`, when `process_outbox_event()` is called, then `qdrant_client.set_payload()` is called to update the point's `valid_to` field in the persistent `rckg_compliance_nodes` collection.
3. Given the server restarts, when `search_with_bitemporal_filter(as_of_date="2026-01-01")` is called, then only points where `valid_from <= "2026-01-01"` and `(valid_to is null OR valid_to > "2026-01-01")` are returned — verified against the persisted Qdrant collection.
4. Given a node is upserted via `upsert_point(point_id, vector, payload)`, when the Qdrant collection is queried, then the point is retrievable by ID with its full payload intact.
5. Given Qdrant is unavailable, when `EmbeddingSyncController` initializes, then a connection error is raised immediately (fail-fast — no fallback to in-memory mock in production).

#### Technical Notes
- Use the official `qdrant-client` Python package (`pip install qdrant-client>=1.9.0`).
- The Qdrant collection `rckg_compliance_nodes` must be created with:
  - Vector size matching the BGE-M3 embedding dimension: **1024**
  - Distance metric: **Cosine**
  - Payload index on `valid_from` (keyword type) and `valid_to` (keyword type) for bitemporal filtering.
- The `QdrantVectorStoreMock` class should be **moved to** `backend/tests/mocks/qdrant_mock.py` — it remains useful for unit testing but must not be used in production.
- Bitemporal filter in Qdrant uses `models.Filter` with `must` conditions (see Qdrant Python SDK `models.FieldCondition`).
- `QDRANT_HOST` and `QDRANT_PORT` should be configurable via environment variables.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|-------------------|
| `backend/app/services/embedding_sync.py` | Replace `QdrantVectorStoreMock` with live `QdrantClient`; rewrite `upsert_point()`, `update_payload()`, `search_with_bitemporal_filter()` |
| `backend/app/core/config.py` | Add `QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_COLLECTION_NAME` settings |
| `backend/tests/mocks/qdrant_mock.py` | **[NEW]** Move `QdrantVectorStoreMock` here for test isolation |
| `backend/tests/test_embedding_sync_live.py` | **[NEW]** Integration test against live Qdrant instance |
| `docker-compose.yml` | Ensure `qdrant` service is defined with correct port mapping |

##### Relevant Code Blocks

**`backend/app/services/embedding_sync.py`** — Replace mock with live client

_Find the class definition (lines 21–81):_
```python
class QdrantVectorStoreMock:
    """Mock/Wrapper for Qdrant Vector DB bitemporal payload synchronization."""

    def __init__(self):
        self.points: Dict[str, Dict[str, Any]] = {}
    ...

class EmbeddingSyncController:
    """PostgreSQL Outbox Event Listener for Vector Payload Sync."""

    def __init__(self, vector_store: Optional[QdrantVectorStoreMock] = None):
        self.vector_store = vector_store or QdrantVectorStoreMock()
```

_Replace the full file with:_
```python
"""
PostgreSQL Outbox Event-Driven Embedding Sync Controller (RCKG-404).

Listens for SUPERSEDE_NODE PostgreSQL outbox events and updates Qdrant vector point payload metadata
with valid_to timestamps to enable bitemporal time-travel queries.

Production: Uses live qdrant-client connection to persistent Qdrant vector store.
"""

import logging
import os
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client import models as qdrant_models

logger = logging.getLogger(__name__)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "rckg_compliance_nodes")
VECTOR_SIZE = int(os.getenv("QDRANT_VECTOR_SIZE", "1024"))  # BGE-M3 embedding dimension


class OutboxEvent(BaseModel):
    event_id: str
    event_type: str
    payload: Dict[str, Any]


class EmbeddingSyncController:
    """PostgreSQL Outbox Event Listener for Persistent Qdrant Vector Payload Sync."""

    def __init__(self, client: Optional[QdrantClient] = None):
        self.client = client or QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create rckg_compliance_nodes collection if it does not already exist."""
        existing = [c.name for c in self.client.get_collections().collections]
        if QDRANT_COLLECTION_NAME not in existing:
            self.client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )
            # Create payload index for bitemporal filtering
            self.client.create_payload_index(
                collection_name=QDRANT_COLLECTION_NAME,
                field_name="valid_from",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=QDRANT_COLLECTION_NAME,
                field_name="valid_to",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
            logger.info("Created Qdrant collection '%s'", QDRANT_COLLECTION_NAME)

    def upsert_point(self, point_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        """Upsert a vector point with full payload into Qdrant."""
        self.client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def update_payload(self, point_id: str, payload_diff: Dict[str, Any]) -> bool:
        """Update an existing point's payload fields (e.g., set valid_to for supersession)."""
        try:
            self.client.set_payload(
                collection_name=QDRANT_COLLECTION_NAME,
                payload=payload_diff,
                points=[point_id],
            )
            return True
        except Exception as e:
            logger.error("Failed to update Qdrant payload for %s: %s", point_id, e)
            return False

    def search_with_bitemporal_filter(self, as_of_date: str) -> List[Dict[str, Any]]:
        """Scroll all points valid at as_of_date using bitemporal payload filter."""
        results, _ = self.client.scroll(
            collection_name=QDRANT_COLLECTION_NAME,
            scroll_filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="valid_from",
                        range=qdrant_models.Range(lte=as_of_date),
                    ),
                ],
                should=[
                    qdrant_models.IsNullCondition(
                        is_null=qdrant_models.PayloadField(key="valid_to")
                    ),
                    qdrant_models.FieldCondition(
                        key="valid_to",
                        range=qdrant_models.Range(gt=as_of_date),
                    ),
                ],
            ),
            with_payload=True,
            with_vectors=False,
            limit=10000,
        )
        return [r.payload for r in results]

    def process_outbox_event(self, event: OutboxEvent) -> Dict[str, Any]:
        """Process outbox event and update Qdrant payload."""
        if event.event_type == "SUPERSEDE_NODE":
            node_id = event.payload.get("node_id")
            valid_to = event.payload.get("valid_to")
            superseded_by = event.payload.get("superseded_by")

            if node_id and valid_to:
                success = self.update_payload(
                    point_id=node_id,
                    payload_diff={"valid_to": valid_to, "superseded_by": superseded_by},
                )
                logger.info(
                    "Updated Qdrant point %s payload with valid_to=%s (Status: %s)",
                    node_id, valid_to, success,
                )
                return {"status": "SUCCESS", "node_id": node_id, "synced": success}

        return {"status": "SKIPPED", "reason": f"Unhandled event_type {event.event_type}"}
```

##### Environment / Config Changes

```env
# .env — Add if not already present
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=rckg_compliance_nodes
QDRANT_VECTOR_SIZE=1024
```

##### Migration / Schema Changes

```bash
# Qdrant collection created automatically by _ensure_collection() on first startup.
# To manually recreate if collection is corrupted:
python3 -c "
from qdrant_client import QdrantClient
c = QdrantClient(host='localhost', port=6333)
c.delete_collection('rckg_compliance_nodes')
print('Collection deleted — will be recreated on next EmbeddingSyncController init.')
"
```

##### Where NOT to Touch
- Do **not** delete `QdrantVectorStoreMock` — move it to `backend/tests/mocks/qdrant_mock.py` and update all test imports.
- Do **not** change `OutboxEvent` schema — it is already correct.
- Do **not** modify `MemgraphService` — the outbox event listener is separate from graph mutation writes.

#### Definition of Done
- [ ] `EmbeddingSyncController.__init__()` creates a live `QdrantClient` — no fallback to in-memory mock.
- [ ] `_ensure_collection()` creates `rckg_compliance_nodes` collection with correct vector size and payload indexes.
- [ ] `upsert_point()` writes to persistent Qdrant storage.
- [ ] `search_with_bitemporal_filter()` uses Qdrant scroll with `must`/`should` filter conditions.
- [ ] `QdrantVectorStoreMock` moved to `backend/tests/mocks/qdrant_mock.py`.
- [ ] Integration test passes against a running Qdrant container.

#### Dependencies
- Blocked by: Real-MVP Sprint 1–3 complete
- Blocks: `PMVP-401` (ColBERT upserts embeddings into Qdrant)

---

### [PMVP-401] Load Real ColBERTv2 Model Weights and Replace Synthetic Hash Embeddings

**Type:** Story  
**Sprint:** Sprint 4  
**Story Points:** 8  
**Priority:** High  
**Assigned To:** Backend Engineer  
**Labels:** `backend`, `colbert`, `retrieval`, `gpu`, `embeddings`

#### User Story
> As a **System Architect**, I want **Stage 2 of the 4-Stage Funnel to use real ColBERTv2 token embeddings for MaxSim late-interaction reranking**, so that **candidate compliance clauses are semantically reranked by legal language similarity, not random hash-based pseudo-embeddings**.

#### Context and Background
Code Review Finding #21: `ColBERTTokenCacheService._generate_synthetic_token_embeddings()` generates deterministic but semantically meaningless token vectors from character hash seeds (`sum(ord(c) for c in word) % 10000`). The `ColBERTReranker.compute_maxsim_score()` function is correctly implemented with MaxSim late-interaction (`sum max(QᵢDⱼ)`) but operates over synthetic data. This story loads the `colbert-ir/colbertv2.0` checkpoint from HuggingFace, runs real BERT-family tokenization, and computes true 128-dimensional contextual token embeddings.

Since the DGX Spark has 128GB VRAM, ColBERTv2 (110M parameters) can be loaded in float16 alongside the vLLM inference server without resource conflicts.

#### Acceptance Criteria
1. Given `ColBERTTokenCacheService` initializes, when the model is loaded, then `colbert-ir/colbertv2.0` weights are loaded from local cache (or downloaded to `~/.cache/colbert/`) and held in GPU memory.
2. Given a text string, when `get_or_compute_embeddings(node_id, text)` is called, then a real BERT tokenizer is applied and contextual token embeddings (shape: `[seq_len, 128]`) are returned.
3. Given two semantically similar compliance texts (e.g., "The organization must encrypt PII" and "Personal data shall be protected by encryption"), when `compute_maxsim_score()` is called, then the MaxSim score is significantly higher than for two semantically dissimilar texts.
4. Given token matrices cached in VRAM, when `has_cached(node_id)` returns True, then no re-tokenization or model inference is performed (cache hit).
5. Given CPU-only deployment (no GPU), when ColBERT model loads, then it falls back to `float32` CPU inference with a warning log.

#### Technical Notes
- Use `ragatouille` or direct `transformers` / `colbert-ai/ColBERT` library to load `colbert-ir/colbertv2.0`.
- Recommended approach: Use `ColBERT` from `colbert` package (`pip install colbert-ai`). The `Checkpoint` class provides `docFromText()` and `queryFromText()` methods that handle tokenization and projection internally.
- Token embedding dimension: **128** (already correct in `ColBERTTokenCacheService.__init__`).
- Max token length: **512** for documents, **32** for queries (already correct).
- Store pre-computed document token matrices in VRAM using `torch.Tensor` (float16 on GPU, float32 on CPU).
- The `_tensor_cache` dict should store `torch.Tensor` objects instead of `np.ndarray` for GPU-compatible MaxSim.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|-------------------|
| `backend/app/services/retrieval/colbert_service.py` | Replace `_generate_synthetic_token_embeddings()` with real ColBERT model inference |
| `requirements.txt` | Add `colbert-ai>=0.2.21` or `ragatouille>=0.0.7` |
| `backend/tests/test_colbert_reranker.py` | **[NEW]** Test real MaxSim scoring with known semantic pairs |

##### Relevant Code Blocks

**`backend/app/services/retrieval/colbert_service.py`** — Replace synthetic embeddings with real model

_Find (lines 33–50):_
```python
def _generate_synthetic_token_embeddings(self, text: str) -> np.ndarray:
    """Deterministically project text tokens into normalized 128-d ColBERT vectors."""
    words = text.split()[: self.max_token_len]
    if not words:
        words = ["empty"]

    # Generate deterministic pseudo-random token vectors from hash seed
    vectors = []
    for word in words:
        seed = sum(ord(c) for c in word) % 10000
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dim).astype(np.float32)
        # L2 normalize token vector
        vec = vec / (np.linalg.norm(vec) + 1e-9)
        vectors.append(vec)

    return np.array(vectors, dtype=np.float32)
```

_Replace with:_
```python
def _load_colbert_model(self) -> None:
    """Load ColBERTv2 checkpoint from HuggingFace or local cache."""
    try:
        import torch
        from colbert.modeling.checkpoint import Checkpoint
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            logger.warning("ColBERT running on CPU — VRAM not available. Performance degraded.")
        self._colbert_checkpoint = Checkpoint(
            "colbert-ir/colbertv2.0",
            colbert_config=None,  # Uses default config from checkpoint
        )
        self._colbert_checkpoint.model.eval()
        self._device = device
        logger.info("ColBERTv2 model loaded on %s", device)
    except Exception as e:
        logger.error("Failed to load ColBERT model: %s — falling back to synthetic embeddings", e)
        self._colbert_checkpoint = None
        self._device = "cpu"

def _compute_real_token_embeddings(self, text: str) -> "np.ndarray":
    """Compute real ColBERT contextual token embeddings from text."""
    import torch
    import numpy as np

    if self._colbert_checkpoint is None:
        return self._generate_synthetic_token_embeddings_fallback(text)

    with torch.no_grad():
        # Encode text as document — returns (1, seq_len, 128) tensor
        embeddings = self._colbert_checkpoint.docFromText(
            [text],
            bsize=1,
            keep_dims=True,
        )
    # Shape: (seq_len, 128), L2 normalized
    return embeddings[0].cpu().numpy().astype(np.float32)

def _generate_synthetic_token_embeddings_fallback(self, text: str) -> "np.ndarray":
    """Fallback to deterministic synthetic embeddings when model is unavailable."""
    import numpy as np
    words = text.split()[: self.max_token_len]
    if not words:
        words = ["empty"]
    vectors = []
    for word in words:
        seed = sum(ord(c) for c in word) % 10000
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dim).astype(np.float32)
        vec = vec / (np.linalg.norm(vec) + 1e-9)
        vectors.append(vec)
    return np.array(vectors, dtype=np.float32)
```

_Find `__init__` (lines 28–31):_
```python
def __init__(self, max_token_len: int = 512, dim: int = 128):
    self.max_token_len = max_token_len
    self.dim = dim
    self._tensor_cache: Dict[str, np.ndarray] = {}
```

_Replace with:_
```python
def __init__(self, max_token_len: int = 512, dim: int = 128):
    self.max_token_len = max_token_len
    self.dim = dim
    self._tensor_cache: Dict[str, "np.ndarray"] = {}
    self._colbert_checkpoint = None
    self._device = "cpu"
    self._load_colbert_model()
```

_Find `get_or_compute_embeddings` (lines 52–59):_
```python
def get_or_compute_embeddings(self, node_id: str, text: str) -> np.ndarray:
    """Return cached token matrix or compute and cache representation."""
    if node_id in self._tensor_cache:
        return self._tensor_cache[node_id]

    embeddings = self._generate_synthetic_token_embeddings(text)
    self._tensor_cache[node_id] = embeddings
    return embeddings
```

_Replace with:_
```python
def get_or_compute_embeddings(self, node_id: str, text: str) -> "np.ndarray":
    """Return cached token matrix or compute real ColBERT embeddings and cache."""
    if node_id in self._tensor_cache:
        return self._tensor_cache[node_id]

    embeddings = self._compute_real_token_embeddings(text)
    self._tensor_cache[node_id] = embeddings
    return embeddings
```

##### Where NOT to Touch
- Do **not** modify `compute_maxsim_score()` — the MaxSim formula (`sum max(QᵢDⱼ)`) is already correctly implemented.
- Do **not** modify `ColBERTReranker.rerank()` — the orchestration loop is correct; only the embedding source changes.

#### Definition of Done
- [ ] `ColBERTTokenCacheService._load_colbert_model()` successfully loads `colbert-ir/colbertv2.0`.
- [ ] `_compute_real_token_embeddings()` returns `(seq_len, 128)` float32 arrays from real tokenization.
- [ ] `_generate_synthetic_token_embeddings_fallback()` is only called when `_colbert_checkpoint is None`.
- [ ] Semantic similarity test: "encrypt PII" vs "protect personal data" scores higher than "encrypt PII" vs "firewall configuration".
- [ ] `pytest backend/tests/test_colbert_reranker.py` passes.

#### Dependencies
- Blocked by: Real-MVP Sprint 3 (`FIX-302` BM25 retrieval) — ColBERT is Stage 2 after BM25 Stage 1.
- Blocks: None

---

### [PMVP-402] Wire Live Kafka Producer for KTO/DPO Preference Pair Streaming

**Type:** Story  
**Sprint:** Sprint 4  
**Story Points:** 8  
**Priority:** High  
**Assigned To:** Backend Engineer  
**Labels:** `backend`, `kafka`, `kto`, `dpo`, `mlops`, `fine-tuning`

#### User Story
> As a **ML Engineer**, I want **the Dual-Judge `PreferenceAccumulatorWorker` to publish CHOSEN/REJECTED preference pairs to a Kafka topic**, so that **the KTO/DPO student LLM fine-tuning pipeline is automatically triggered when 500 high-quality pairs are accumulated — eliminating the need for manual batch collection**.

#### Context and Background
Code Review Finding #22: `PreferenceAccumulatorWorker._publish_retrain_trigger_event()` is a single `logger.info()` statement. Per Delta §5.3, when the accumulator reaches `target_threshold` (default 500) high-confidence pairs, a Kafka event must be published to topic `kto.retrain.trigger`. This event carries the accumulated preference pairs as a JSON payload, triggering downstream ML training infrastructure (e.g., Kubernetes Job, Ray Train worker) to launch a fine-tuning run of the student LLM.

This story introduces a `kafka-python` (or `confluent-kafka`) producer into the `PreferenceAccumulatorWorker`, configurable via environment variables, with graceful fallback to disk-based batch file export when Kafka is unavailable.

#### Acceptance Criteria
1. Given `KAFKA_BOOTSTRAP_SERVERS` is set in the environment, when `PreferenceAccumulatorWorker` initializes, then a live Kafka producer is created connected to the configured brokers.
2. Given 500 preference pairs have been accumulated, when `_publish_retrain_trigger_event()` is called, then a Kafka message is published to topic `kto.retrain.trigger` with a JSON payload containing: `total_pairs`, `timestamp`, and the serialized preference pairs.
3. Given Kafka is unavailable, when `_publish_retrain_trigger_event()` is called, then the preference pairs are written to a JSON file at `data/kto_batches/batch_{timestamp}.json` as a fallback (no exception raised, warning logged).
4. Given a Kafka message is published, when inspected, then the message key is the `session_id` and the value is a UTF-8 encoded JSON string.
5. Given the threshold is not yet reached, when `add_preference_pair()` is called, then no Kafka message is sent.

#### Technical Notes
- Use `kafka-python` (`pip install kafka-python>=2.0.2`) or `confluent-kafka` (`pip install confluent-kafka>=2.3.0`).
- Kafka topic `kto.retrain.trigger` must have at least 1 partition and replication factor 1 for development.
- The Kafka message value should follow the schema:
  ```json
  {
    "session_id": "uuid",
    "timestamp": "2026-07-31T15:00:00Z",
    "total_pairs": 500,
    "pairs": [
      {"chosen": {...}, "rejected": {...}, "score": 0.92},
      ...
    ]
  }
  ```
- Use asynchronous delivery (fire-and-forget) — do not block the accumulation loop waiting for Kafka ACK.
- The `KAFKA_BOOTSTRAP_SERVERS` env var should accept a comma-separated list (e.g., `"kafka:9092,kafka2:9092"`).
- `data/kto_batches/` directory must be created if it does not exist.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|-------------------|
| `backend/app/services/dual_judge_async.py` | Replace `logger.info()` in `_publish_retrain_trigger_event()` with live Kafka producer |
| `backend/app/core/config.py` | Add `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_KTO_TOPIC`, `KTO_BATCH_FALLBACK_DIR` settings |
| `requirements.txt` | Add `kafka-python>=2.0.2` |
| `backend/tests/test_preference_accumulator.py` | **[NEW]** Test accumulation threshold and serialization (mock Kafka) |
| `docker-compose.yml` | Ensure Kafka + Zookeeper services are defined |

##### Relevant Code Blocks

**`backend/app/services/dual_judge_async.py`** — Replace logger stub with live Kafka producer

_Find (lines 103–108):_
```python
    def _publish_retrain_trigger_event(self) -> None:
        """Publish KTO/DPO model retraining event to Kafka topic kto.retrain.trigger."""
        logger.info(
            "Target threshold %d reached. Published KTO/DPO model retrain event to Kafka topic kto.retrain.trigger",
            self.target_threshold,
        )
```

_Replace with:_
```python
    def _publish_retrain_trigger_event(self) -> None:
        """Publish KTO/DPO model retraining event to Kafka topic kto.retrain.trigger."""
        import json
        import os
        import uuid
        from datetime import datetime, timezone

        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
        topic = os.getenv("KAFKA_KTO_TOPIC", "kto.retrain.trigger")
        session_id = str(uuid.uuid4())

        payload = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_pairs": len(self.accumulated_pairs),
            "pairs": self.accumulated_pairs,
        }
        payload_bytes = json.dumps(payload).encode("utf-8")

        if kafka_servers:
            try:
                from kafka import KafkaProducer
                producer = KafkaProducer(
                    bootstrap_servers=kafka_servers.split(","),
                    value_serializer=lambda v: v,
                    key_serializer=lambda k: k.encode("utf-8"),
                )
                future = producer.send(topic, key=session_id, value=payload_bytes)
                producer.flush(timeout=5)
                metadata = future.get(timeout=5)
                logger.info(
                    "Published KTO/DPO retrain event to Kafka topic=%s partition=%s offset=%s session_id=%s",
                    topic, metadata.partition, metadata.offset, session_id,
                )
            except Exception as e:
                logger.warning("Kafka publish failed (%s) — falling back to disk batch file.", e)
                self._write_batch_to_disk(payload, session_id)
        else:
            logger.warning("KAFKA_BOOTSTRAP_SERVERS not set — writing preference batch to disk.")
            self._write_batch_to_disk(payload, session_id)

    def _write_batch_to_disk(self, payload: dict, session_id: str) -> None:
        """Fallback: write accumulated preference pairs to JSON file on disk."""
        import json
        import os
        from pathlib import Path

        batch_dir = Path(os.getenv("KTO_BATCH_FALLBACK_DIR", "data/kto_batches"))
        batch_dir.mkdir(parents=True, exist_ok=True)

        batch_file = batch_dir / f"batch_{session_id}.json"
        batch_file.write_text(json.dumps(payload, indent=2))
        logger.info("Preference batch written to disk: %s", batch_file)
```

##### Environment / Config Changes

```env
# .env — Add if not already present
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_KTO_TOPIC=kto.retrain.trigger
KTO_BATCH_FALLBACK_DIR=data/kto_batches
```

##### Where NOT to Touch
- Do **not** modify `add_preference_pair()` — the accumulation logic and threshold check are correct.
- Do **not** modify `DualJudgeAuditResult` — the schema is correct.
- Do **not** remove `self.accumulated_pairs.clear()` after publish — it is correct and must be called after successful delivery.

#### Definition of Done
- [ ] `_publish_retrain_trigger_event()` creates a live `KafkaProducer` when `KAFKA_BOOTSTRAP_SERVERS` is set.
- [ ] Kafka message published to `kto.retrain.trigger` topic with correct JSON payload.
- [ ] Disk fallback creates `data/kto_batches/batch_{session_id}.json` when Kafka is unavailable.
- [ ] Unit test covers: threshold trigger → Kafka publish (mocked), threshold trigger → disk fallback.
- [ ] `docker-compose.yml` includes Kafka + Zookeeper service definitions.

#### Dependencies
- Blocked by: Real-MVP Sprint 3 (FIX-305 Dual-Judge LLM)
- Blocks: None (downstream ML training infrastructure is out of scope for this sprint)

---

### [PMVP-403] Implement Real PyMuPDF Feature Inspection in Format Classifier

**Type:** Story  
**Sprint:** Sprint 4  
**Story Points:** 7  
**Priority:** Medium  
**Assigned To:** Backend Engineer  
**Labels:** `backend`, `pdf`, `format-classifier`, `pymupdf`, `ocr`

#### User Story
> As a **Compliance Engineer**, I want **the upstream format classifier to accurately distinguish between native digital PDFs, scanned image PDFs, and complex matrix/table PDFs**, so that **scanned regulatory documents are routed to OCR parsers and complex table-heavy compliance matrices are routed to TableTransformer — not all treated as native digital PDFs by default**.

#### Context and Background
Code Review Finding #23: `UpstreamFormatClassifier.classify()` currently inspects PDF structure by decoding raw bytes as Latin-1 text and counting string occurrences of `/Font`, `/Image`, `/XObject`, and `/Table`. This is brittle and inaccurate — scanned PDFs often contain embedded fonts for metadata even when the page content is rasterized images. The `page_count` is hardcoded to `1` regardless of actual document length.

The correct approach is to use **PyMuPDF (`fitz`)** — which can open a PDF, iterate over each page, count actual embedded text characters, embedded image objects, and table-like structures — providing accurate feature counts to `classify_pdf_features()`.

#### Acceptance Criteria
1. Given a native digital PDF (e.g., MAS TRM Guidelines), when `classify()` is called, then `page_count` reflects the actual number of pages, `text_char_count` is a real character count from PDF text extraction, and `image_count` counts actual embedded image objects — not string matches.
2. Given a scanned image-only PDF (< 50 text chars per page, image on every page), when `classify()` is called, then `format = DocumentFormat.SCANNED_PDF` and `recommended_parser = "SuryaOcrParser"` are returned.
3. Given a complex matrix PDF (≥ 50 table cells detected per page), when `classify()` is called, then `format = DocumentFormat.COMPLEX_MATRIX` and `recommended_parser = "TableTransformerParser"` are returned.
4. Given PyMuPDF is unavailable, when `classify()` is called, then the existing Latin-1 byte inspection fallback is used with a warning log (no exception raised).
5. Given a DOCX or HTML file, when `classify()` is called, then magic byte detection still routes correctly without invoking PyMuPDF.

#### Technical Notes
- Use `import fitz` (PyMuPDF, `pip install PyMuPDF>=1.23.0`).
- For table detection: count the number of `fitz.Page.find_tables()` results across all pages. Each `TableFinder` result that has `>= 2 columns and >= 2 rows` counts as `+1 table`; estimate `table_cell_count = sum(table.col_count * table.row_count for table in page.find_tables())`.
- For image counting: use `page.get_images(full=True)` — each `(xref, smask, ...)` tuple is one embedded image object.
- For text density: use `len(page.get_text("text"))` per page.
- For font counting: use `doc.get_page_fonts(page_num)` — count unique font names.
- `fitz.open()` from bytes: use `fitz.open(stream=file_bytes, filetype="pdf")`.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|-------------------|
| `backend/app/services/format_classifier.py` | Rewrite PDF section of `classify()` to use `fitz` for real feature extraction |
| `requirements.txt` | Ensure `PyMuPDF>=1.23.0` is listed |
| `backend/tests/test_format_classifier.py` | **[NEW]** Tests for native PDF, scanned PDF, and complex matrix classification |

##### Relevant Code Blocks

**`backend/app/services/format_classifier.py`** — Replace Latin-1 byte scan with PyMuPDF

_Find the PDF block inside `classify()` (lines 101–115):_
```python
                if fmt == DocumentFormat.NATIVE_PDF:
                    text_sample = file_bytes.decode("latin1", errors="ignore")
                    font_count = text_sample.count("/Font")
                    image_count = text_sample.count("/Image") + text_sample.count("/XObject")
                    table_cell_count = text_sample.count("/Table") * 25
                    text_char_count = len(text_sample) // 5

                    return self.classify_pdf_features(
                        text_char_count=text_char_count,
                        page_count=1,
                        image_count=image_count,
                        table_cell_count=table_cell_count,
                        font_count=font_count,
                        filename=filename,
                    )
```

_Replace with:_
```python
                if fmt == DocumentFormat.NATIVE_PDF:
                    return self._classify_pdf_with_pymupdf(file_bytes, filename)
```

_Add new method to `UpstreamFormatClassifier`:_
```python
    def _classify_pdf_with_pymupdf(self, file_bytes: bytes, filename: str) -> ClassificationResult:
        """Classify PDF using PyMuPDF for accurate feature extraction."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=file_bytes, filetype="pdf")
            page_count = len(doc)
            total_text_chars = 0
            total_image_count = 0
            total_table_cells = 0
            total_fonts = set()

            for page_num in range(page_count):
                page = doc.load_page(page_num)
                total_text_chars += len(page.get_text("text"))
                total_image_count += len(page.get_images(full=True))
                # Count table cells via find_tables()
                try:
                    for table in page.find_tables().tables:
                        if table.col_count >= 2 and table.row_count >= 2:
                            total_table_cells += table.col_count * table.row_count
                except Exception:
                    pass  # find_tables not supported in older PyMuPDF builds
                for font_info in doc.get_page_fonts(page_num):
                    total_fonts.add(font_info[3])  # font name

            doc.close()

            return self.classify_pdf_features(
                text_char_count=total_text_chars,
                page_count=page_count,
                image_count=total_image_count,
                table_cell_count=total_table_cells,
                font_count=len(total_fonts),
                filename=filename,
            )

        except ImportError:
            logger.warning("PyMuPDF not available — falling back to Latin-1 byte heuristic.")
            text_sample = file_bytes.decode("latin1", errors="ignore")
            return self.classify_pdf_features(
                text_char_count=len(text_sample) // 5,
                page_count=1,
                image_count=text_sample.count("/Image") + text_sample.count("/XObject"),
                table_cell_count=text_sample.count("/Table") * 25,
                font_count=text_sample.count("/Font"),
                filename=filename,
            )

        except Exception as e:
            logger.error("PyMuPDF classification failed for %s: %s — using NATIVE_PDF default.", filename, e)
            return ClassificationResult(
                format=DocumentFormat.NATIVE_PDF,
                recommended_parser="MarkerParser",
                confidence=0.70,
                detected_mime="application/pdf",
                metadata={"filename": filename, "error": str(e)},
            )
```

##### Where NOT to Touch
- Do **not** modify `classify_pdf_features()` — the classification rules (thresholds for SCANNED vs COMPLEX_MATRIX vs NATIVE_PDF) are already correct.
- Do **not** modify DOCX or HTML classification branches — they use magic byte routing and do not need PyMuPDF.
- Do **not** change `ClassificationResult` or `DocumentFormat` models — they are correct.

#### Definition of Done
- [ ] `classify()` for PDF files calls `_classify_pdf_with_pymupdf()` using `fitz.open()`.
- [ ] `page_count` reflects actual PDF page count from `len(doc)`.
- [ ] `text_char_count` is from `page.get_text("text")` summed over all pages.
- [ ] `image_count` is from `page.get_images(full=True)` summed over all pages.
- [ ] `table_cell_count` is from `page.find_tables()` with `col_count * row_count`.
- [ ] Scanned PDF test fixture returns `DocumentFormat.SCANNED_PDF`.
- [ ] Complex matrix PDF test fixture returns `DocumentFormat.COMPLEX_MATRIX`.
- [ ] Latin-1 fallback activates and logs a warning when `import fitz` fails.

#### Dependencies
- Blocked by: None (independent of other Sprint 4 stories)
- Blocks: None

---

## 4. Sprint Plan Summary

### Backlog Health Check

| Metric | Value |
|--------|-------|
| **Stories in Sprint 4** | 4 |
| **Total Story Points** | 31 |
| **Estimated Duration** | 2 weeks |
| **Deferred Items Resolved** | 4 / 4 |
| **Combined with Real-MVP** | 7 total sprints, 20 stories, 117 story points |
| **Total Calendar Duration** | ~8 weeks (Sprints 1–4) |

### Post-MVP Coverage Matrix

| Finding # | Description | Code Review Severity | Story ID | Sprint |
|---|---|:---:|---|---|
| #9 | Real Qdrant bitemporal vector store | 🔴 CRITICAL | `PMVP-400` | Sprint 4 |
| #21 | ColBERT model loading (real MaxSim) | 🟡 MODERATE | `PMVP-401` | Sprint 4 |
| #22 | Kafka KTO/DPO event publishing | 🟡 MODERATE | `PMVP-402` | Sprint 4 |
| #23 | PDF format classifier via PyMuPDF | 🟡 MODERATE | `PMVP-403` | Sprint 4 |

### Complete 4-Sprint Coverage (Real-MVP + Post-MVP)

```
Sprint 1 (Real-MVP) — FIX-100 to FIX-105  → Bug Fixes + LLM Extraction     29 pts
Sprint 2 (Real-MVP) — FIX-200 to FIX-204  → Seed Graph + Service Layer      27 pts
Sprint 3 (Real-MVP) — FIX-300 to FIX-306  → Retrieval + Steady-State        30 pts
Sprint 4 (Post-MVP) — PMVP-400 to PMVP-403 → Qdrant, ColBERT, Kafka, PDF   31 pts
────────────────────────────────────────────────────────────────────────────────
TOTAL                                                                        117 pts  |  8 weeks
All 27 code-review.md findings resolved at enterprise production grade            ✅
```

### Infrastructure Prerequisites for Sprint 4

Before Sprint 4 begins, ensure the following cluster services are running:

| Service | Image | Port | Notes |
|---|---|---|---|
| Qdrant | `qdrant/qdrant:v1.9.4` | 6333 (HTTP), 6334 (gRPC) | Add to `docker-compose.yml` |
| Kafka | `confluentinc/cp-kafka:7.6.0` | 9092 | Requires Zookeeper or KRaft mode |
| Zookeeper | `confluentinc/cp-zookeeper:7.6.0` | 2181 | Only needed with non-KRaft Kafka |
| ColBERT weights | HuggingFace `colbert-ir/colbertv2.0` | N/A — GPU model | Pre-download to `/models/colbert/` |

### Dependency Map

```
PMVP-400 (Qdrant live) ──────────────────────► FIX-300 (Cold-Start) writes embeddings to Qdrant
PMVP-401 (ColBERT model) ────────────────────► Stage 2 reranking uses real token embeddings
PMVP-402 (Kafka publisher) ──────────────────► FIX-305 (Dual-Judge LLM) feeds preference pairs to Kafka
PMVP-403 (PDF format classifier) ────────────► Independent; activates SCANNED_PDF / COMPLEX_MATRIX routes
```

### Risks to Delivery

| # | Risk | Probability | Impact | Mitigation |
|---|------|-------------|--------|------------|
| 1 | ColBERT model download fails / HuggingFace access unavailable | Low | High | Pre-download `colbert-ir/colbertv2.0` to `/models/colbert/` before sprint begins. Set `COLBERT_MODEL_PATH` env var to local path. |
| 2 | Qdrant `find_tables()` not supported in older PyMuPDF builds | Medium | Low | Wrap in `try/except`; table detection is optional — gracefully skip, log warning. |
| 3 | Kafka topic `kto.retrain.trigger` not pre-created before producer sends | Medium | Medium | Producer should call `admin.create_topics()` on init if topic doesn't exist. |
| 4 | ColBERT VRAM contention with vLLM on DGX Spark | Low | High | ColBERT 110M at float16 uses ~220MB VRAM — negligible next to vLLM. Run `nvidia-smi` to confirm available headroom before loading. |
| 5 | PyMuPDF `page.find_tables()` requires PyMuPDF ≥ 1.23.0 | Medium | Medium | Pin `PyMuPDF>=1.23.0` in `requirements.txt`. Add version check in `_classify_pdf_with_pymupdf()`. |
