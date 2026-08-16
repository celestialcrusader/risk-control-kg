# AI Model Integration Requirements Document (AI-REQ-06)

**Document Version:** 2.0 (Strict Primary AI Model Matrix — Zero Fallbacks)  
**Status:** Approved / Active Requirement Specification  
**Scope:** `docs/06-add-ai` — AI Layer Modernization & Model Architecture Upgrade  
**Target Hardware:** On-Premises NVIDIA DGX Cluster / Dedicated Inference Endpoints  

---

## 1. Executive Summary & Objective

The objective of this specification is to define the dedicated AI model matrix and infrastructure requirements for the Risk Control Knowledge Graph (RCKG) platform. To streamline operations and eliminate secondary service hosting overhead, the platform employs a strict 1-to-1 mapping between functional jobs and primary AI models. No secondary model fallback services are hosted or invoked.

---

## 2. AI Model Matrix & Target Architecture

| Functional Job | Dedicated Primary Model | Endpoint / Runtime Protocol | Primary Purpose & SLA |
| :--- | :--- | :--- | :--- |
| **1. PDF/Document Parsing** | **PaddleOCR-VL-1.6** | vLLM Vision (Port 8002) | Direct image-to-Markdown extraction with layout & table preservation |
| **2. General Extraction** | **Qwen3-30B-A3B** | vLLM OpenAI API (Port 8000) | Atomic rule unit & Pydantic JSON extraction from Markdown |
| **3. Interactive Copilot** | **Qwen3-30B-A3B** | vLLM SSE Stream (Port 8000) | Real-time chat, tool calling (MCP), Generative Canvas events |
| **4. Dense Embeddings** | **Qwen3-Embedding-8B** | TEI / Sentence-Transformers | Dense vector generation (4096-dim) for Qdrant storage & search |
| **5. Candidate Reranking** | **Qwen3-Reranker-8B** | FlashRank / HuggingFace TEI | Cross-encoder rescoring of text pairs `(query, document)` |
| **6. NLI Evaluation** | **ModernBERT-large-NLI** | ONNX / PyTorch Local Pipeline | High-throughput premise-hypothesis set-theory classification |
| **7. Ambiguous Graph Adjudication** | **Qwen3-Next-80B-A3B** | vLLM OpenAI API (Port 8004) | Asynchronous Dual-Judge reasoning for low-confidence commits |
| **8. GraphRAG Translation** | **Qwen3-Next-80B-A3B** | vLLM OpenAI API (Port 8004) | Hierarchical graph community summary & global query synthesis |

---

## 3. Detailed Functional Requirements (Zero Fallbacks)

### FR-01: Multimodal PDF-to-Markdown Ingestion Pipeline
- **Requirement:** `pdf_to_markdown.py` must use `PaddleOCR-VL-1.6` via dedicated vLLM Vision endpoint (`http://localhost:8002/v1`) to convert raw document pages directly to Markdown.
- **Failure Handling:** If `PaddleOCR-VL-1.6` is unreachable or returns an error, the operation raises an explicit `RuntimeError("PaddleOCR-VL-1.6 endpoint unreachable")`. No secondary parser fallback is hosted.

### FR-02: Atomic Rule Unit Extraction & Copilot API
- **Requirement:** `extraction.py` and the interactive Copilot endpoint must invoke `Qwen3-30B-A3B` via vLLM OpenAI-compatible JSON API (`http://localhost:8000/v1`).
- **Schema Adherence:** Extraction must enforce strict Pydantic model validation (`Obligation`, `ControlObjective`, `ControlActivity`).
- **Failure Handling:** If `Qwen3-30B-A3B` is unavailable, requests fail with HTTP 503 Service Unavailable.

### FR-03: Vector Embedding & Dense Retrieval (Qdrant)
- **Requirement:** `embedding_sync.py` must generate dense 4096-dimensional embeddings using `Qwen3-Embedding-8B` for all extracted clauses, storing vector payloads in Qdrant.
- **Vector Space Consistency:** All Qdrant vector indexing and queries use `Qwen3-Embedding-8B` exclusively.

### FR-04: Multi-Stage Candidate Reranking
- **Requirement:** Hybrid search (BM25 + Qdrant dense vector) candidates in `colbert_service.py` / retrieval pipeline must be rescored using `Qwen3-Reranker-8B` cross-encoder scoring on `(query, document)` text pairs.
- **Failure Handling:** If `Qwen3-Reranker-8B` is unreachable, hybrid candidates are returned sorted by normalized RRF (Reciprocal Rank Fusion) score without reranking.

### FR-05: Fast Set-Theory NLI Engine
- **Requirement:** `nli_engine.py` must utilize `ModernBERT-large-NLI` to evaluate premise-hypothesis relationship (`ENTAILED_SATISFIES`, `EXPRESSLY_FORBIDS`, `EQUIVALENT_SATISFIES`, `CONTINGENT_SATISFIES`, `PARTIAL_SATISFIES`, `NEUTRAL_UNMAPPED`).
- **Zero-Fallback Requirement:** System must NOT produce fake high-confidence scores from keyword heuristics or secondary models. If inference fails, status must be recorded as `PENDING_CLASSIFICATION` with confidence `0.0`.

### FR-06: Asynchronous Dual-Judge Graph Adjudication
- **Requirement:** `judge.py` and `dual_judge_async.py` must use `Qwen3-Next-80B-A3B` for high-complexity, ambiguous graph commit adjudication (Logic Judge & Technical Judge).
- **Gating Rule:** Mutations with logic score < 0.70 or technical score < 0.70 must be intercepted and routed to `PENDING_HITL_REVIEW` state in `GraphOutboxLog`.

### FR-07: GraphRAG Community Summarization & Global Querying
- **Requirement:** `graphrag_translator.py` must employ `Qwen3-Next-80B-A3B` to execute hierarchical community summarization over Memgraph graph clusters and synthesize answers for global compliance queries.

---

## 4. Environment & Port Allocation Matrix

```env
# AI Model Endpoints Configuration (.env)
MODEL_PARSER_ENDPOINT=http://localhost:8002/v1
MODEL_PARSER_NAME=baidu/PaddleOCR-VL-1.6

MODEL_EXTRACTION_ENDPOINT=http://localhost:8000/v1
MODEL_EXTRACTION_NAME=Qwen/Qwen3-30B-A3B

MODEL_EMBEDDING_NAME=Qwen/Qwen3-Embedding-8B
MODEL_EMBEDDING_DIM=4096

MODEL_RERANKER_NAME=Qwen/Qwen3-Reranker-8B

MODEL_NLI_NAME=answerdotai/ModernBERT-large-NLI

MODEL_JUDGE_ENDPOINT=http://localhost:8004/v1
MODEL_JUDGE_NAME=Qwen/Qwen3-Next-80B-A3B

MODEL_GRAPHRAG_ENDPOINT=http://localhost:8004/v1
MODEL_GRAPHRAG_NAME=Qwen/Qwen3-Next-80B-A3B
```

---

## 5. Architectural Quality Standards

1. **Strict Locality Enforcement:** All local model endpoints must be bound to loopback (`127.0.0.1`) or private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
2. **Zero Fallbacks & No Fakes:** No secondary fallback services are hosted. Inference failures yield explicit `PENDING` or error states with `0.0` confidence rather than fake static scores.
3. **Single Model Invariance:** Each AI functional job maps strictly to its designated primary model.
