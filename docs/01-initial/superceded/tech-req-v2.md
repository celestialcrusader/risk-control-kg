Below is a **fully rewritten, end-to-end Technical Requirements Document (TRD)** with:

* **All technology decisions finalized (no options)**
* **100% open-source, self-hosted stack**
* **Clear data flow, components, and responsibilities**
* **Aligned with your research (GraphRAG, ColBERT, Markdown, temporal KG)**

This is written to be **build-ready**.

---

# 📕 TECHNICAL REQUIREMENTS DOCUMENT (TRD)

## High-Fidelity Risk & Control Knowledge Graph Platform

---

# 1. SYSTEM OVERVIEW

## 1.1 Objective

Design and implement a **self-hosted, open-source AI-native platform** that:

* Ingests regulatory and policy documents
* Extracts structured obligations
* Constructs a **temporal knowledge graph**
* Performs **high-precision control mapping using ColBERT**
* Enables **GraphRAG-based querying**
* Outputs compliance artifacts in **OSCAL format**

---

## 1.2 Architectural Principles

* **Open-source only (no proprietary dependencies)**
* **Deterministic + traceable outputs**
* **Separation of retrieval and reasoning**
* **Graph as system of truth**
* **LLM as assistive, not authoritative**

---

# 2. FINALIZED TECHNOLOGY STACK

## 2.1 Core Infrastructure

| Layer            | Technology                                |
| ---------------- | ----------------------------------------- |
| Containerization | Docker                                    |
| Orchestration    | Docker Compose (MVP) / Kubernetes (scale) |
| Message Queue    | Apache Kafka                              |
| Workflow Engine  | Apache Airflow                            |
| API Framework    | FastAPI                                   |
| Backend Language | Python 3.11                               |

---

## 2.2 Data Storage

| Purpose               | Technology            |
| --------------------- | --------------------- |
| Graph Database        | Memgraph              |
| Vector Database       | Qdrant                |
| Metadata / Relational | PostgreSQL            |
| Object Storage        | MinIO (S3-compatible) |

---

## 2.3 AI / ML Stack

| Function             | Technology                                |
| -------------------- | ----------------------------------------- |
| Embeddings           | BAAI BGE-M3                               |
| Reranking / Matching | ColBERT (late interaction)                |
| LLM (local)          | Mistral 7B / Mixtral (via Ollama or vLLM) |
| Tokenization         | HuggingFace Transformers                  |

---

## 2.4 Document Processing

| Function        | Technology             |
| --------------- | ---------------------- |
| PDF → Markdown  | MinerU                 |
| Backup Parser   | Marker                 |
| Text Processing | Python (regex + spaCy) |

---

## 2.5 Supporting Libraries

* LangChain (light usage only for pipelines, NOT orchestration)
* LlamaIndex (for document indexing abstractions)
* Pydantic (data validation)
* SQLAlchemy (DB ORM)
* NetworkX (local graph validation/testing)

---

# 3. END-TO-END DATA FLOW

---

## 3.1 Ingestion Pipeline

### Input

* Regulatory PDFs
* Policy documents
* Control libraries

### Flow

1. Upload → stored in **MinIO**
2. Metadata registered in **PostgreSQL**
3. Kafka event triggered:

   ```
   topic: document.ingested
   ```

---

## 3.2 Document Parsing

### Tool: MinerU

Output:

* Structured Markdown (`.md`)
* JSON metadata:

  * headings
  * tables
  * layout

Stored in:

* MinIO (raw + parsed)
* PostgreSQL (document index)

---

## 3.3 Chunking Strategy

### Hybrid Approach

1. **Markdown Header-Based Chunking**
2. **Semantic Chunking (embedding distance threshold)**

### Implementation

* Use custom Python pipeline
* Sentence segmentation via spaCy
* Embedding-based split using BGE-M3

---

## 3.4 Embedding Pipeline

### Model: BGE-M3

Process:

* Chunk → embedding vector
* Store in **Qdrant**

### Qdrant Schema

```
collection: document_chunks
payload:
  - document_id
  - section
  - text
  - metadata
```

---

## 3.5 Knowledge Graph Construction

### Graph DB: Memgraph

### Node Types

* Regulation
* Obligation
* Control
* Risk
* Evidence
* Document

### Relationship Types

* REQUIRES
* MITIGATED_BY
* EVIDENCED_BY
* DERIVED_FROM
* SUPERSEDES
* BELONGS_TO

---

### Extraction Process

1. Markdown → LLM extraction (Mistral)
2. Structured output (JSON schema)
3. Transform into Cypher queries
4. Insert into Memgraph

---

## 3.6 Temporal Modeling

Each node contains:

```
valid_from
valid_to
ingested_at
status (active/superseded)
```

No deletion:

* Use `SUPERSEDES` relationships

---

# 4. CONTROL MAPPING ENGINE (CRITICAL)

---

## 4.1 Problem

Mapping:

* Thousands of obligations
* Thousands of controls

---

## 4.2 Solution: ColBERT (Late Interaction)

### Why

* Token-level matching
* Avoids embedding compression loss
* Scalable vs cross-encoders

---

## 4.3 Implementation

### Step 1: Indexing

* Controls token embeddings precomputed
* Stored in ColBERT index

---

### Step 2: Querying

* Obligation → token embeddings
* Run MaxSim scoring against controls

---

### Step 3: Classification

LLM-assisted classification:

* Equivalent
* Superset
* Subset
* Intersects
* None

---

### Step 4: Graph Update

Create relationships:

```
(Obligation)-[:MITIGATED_BY {type: "subset"}]->(Control)
```

---

# 5. RETRIEVAL ARCHITECTURE (GraphRAG)

---

## 5.1 Query Flow

1. User query → embedding (BGE-M3)
2. Retrieve top-K chunks (Qdrant)
3. Extract related nodes
4. Expand via Memgraph traversal
5. Return subgraph
6. LLM generates answer (grounded)

---

## 5.2 Key Constraint

> LLM MUST NOT answer without graph context

---

# 6. API LAYER

---

## 6.1 Framework: FastAPI

### Endpoints

| Endpoint        | Purpose             |
| --------------- | ------------------- |
| `/ingest`       | Upload documents    |
| `/parse`        | Trigger parsing     |
| `/extract`      | Extract obligations |
| `/map`          | Run control mapping |
| `/query`        | GraphRAG query      |
| `/export/oscal` | Export compliance   |

---

# 7. OSCAL OUTPUT ENGINE

---

## 7.1 Format

* JSON (NIST OSCAL)

---

## 7.2 Process

1. Graph traversal:

   * Control → obligations
2. Map to OSCAL schema
3. Output JSON

---

# 8. WORKFLOW ORCHESTRATION

---

## 8.1 Tool: Apache Airflow

### DAGs

* document_ingestion_dag
* parsing_dag
* extraction_dag
* embedding_dag
* graph_build_dag
* mapping_dag

---

## 8.2 Event Triggering

* Kafka triggers Airflow DAGs

---

# 9. DEPLOYMENT

---

## 9.1 MVP

* Docker Compose
* Single-node deployment

---

## 9.2 Production

* Kubernetes cluster
* Horizontal scaling:

  * Qdrant
  * Kafka
  * API layer

---

## 9.3 Air-Gapped Support

* All models local
* No internet required

---

# 10. SECURITY

---

* No external API calls
* Role-based API access
* Data encrypted at rest (Postgres, MinIO)

---

# 11. OBSERVABILITY

---

Track:

* Extraction accuracy
* Mapping confidence scores
* Query latency
* Graph growth

Tools:

* Prometheus
* Grafana

---

# 12. FAILURE HANDLING

---

| Failure                | Handling                   |
| ---------------------- | -------------------------- |
| Parsing error          | Retry + fallback (Marker)  |
| Low-confidence mapping | Flag for review            |
| LLM failure            | Retry with fallback prompt |
| Missing graph links    | Log + reprocess            |

---

# 13. SYSTEM GUARANTEES

---

The system guarantees:

* Traceable outputs (graph-backed)
* No black-box decisions
* Reproducible pipelines
* Full auditability

---

# 🔥 FINAL NOTE

This TRD is now:

* **Fully opinionated (no ambiguity)**
* **Aligned with open-source constraint**
* **Directly implementable**
* **Consistent with your research thesis**

---

If you want next level:

I can generate:

* **Memgraph schema (Cypher DDL + examples)**
* **ColBERT pipeline code structure**
* **Airflow DAG templates**
* **End-to-end system diagram (very powerful for this)**
