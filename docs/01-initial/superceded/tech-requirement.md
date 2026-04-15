# Technical Requirements Document (TRD)
## Risk and Control Knowledge Graph (RCKG) Platform

**Document Version:** 1.0  
**Status:** Draft  
**Classification:** Internal — Confidential  
**Last Updated:** April 12, 2026  
**Linked PRD:** product-requirement.md v1.0  
**Linked BRD:** business-requirement.md v1.0

---

## 1. System Architecture Overview

The RCKG platform is a modular, AI-native system organized into six functional layers. Each layer communicates via defined interfaces, enabling independent scaling, replacement, and testing of components.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client Layer                                 │
│          Web UI / REST API / GRC Platform Webhooks                  │
├─────────────────────────────────────────────────────────────────────┤
│                    Agentic Orchestration Layer                       │
│        agents.md  ◄──►  skills.md  ◄──►  Agent Runtime             │
├──────────────────┬──────────────────┬───────────────────────────────┤
│  Ingestion Layer │  Retrieval Layer  │    Reasoning Layer            │
│  PDF→Markdown   │  Vector DB (ANN)  │    GraphRAG (LLM + Graph)     │
│  De Jure Extract│  Graph Traversal  │    ColBERT Re-ranking          │
├──────────────────┴──────────────────┴───────────────────────────────┤
│                       Storage Layer                                 │
│       Property Graph DB        │       Vector Store                 │
│       (Neo4j / ArangoDB)       │   (Qdrant / Pinecone / Milvus)    │
├─────────────────────────────────────────────────────────────────────┤
│                    Temporal & Governance Layer                       │
│   Bitemporal Model  │  SHACL Validator  │  Data Governance Flags    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack Specification

### 2.1 Core Graph Database

**Primary Recommendation: Neo4j Enterprise**
- Native Property Graph Model (PGM) with ACID compliance
- Cypher query language for multi-hop traversal
- Full-text and vector index support for hybrid retrieval
- GDS (Graph Data Science) library for centrality and community detection
- Temporal property support for bitemporal node modeling

**Alternative: ArangoDB**
- Multi-model (document + graph) for flexible schema evolution
- AQL for combined graph and document queries
- Suitable for organizations with existing ArangoDB infrastructure

**Technical Constraints:**
- Minimum cluster size: 3 nodes (1 leader, 2 followers) for HA
- Storage: NVMe SSD required; minimum 2TB provisioned per node for enterprise-scale graph
- Memory: Minimum 128GB RAM per node for in-memory graph caching

---

### 2.2 Vector Database

**Primary Recommendation: Qdrant**
- Native support for multi-vector collections (required for ColBERT late interaction)
- Sparse + dense hybrid search in a single query
- On-disk payload filtering without full scan
- Self-hostable with Kubernetes operator
- HNSW index with configurable ef_construction for recall/latency trade-off

**Alternatives:**
- **Milvus** — Higher throughput for billion-scale vector sets; good for global enterprises with very large regulatory corpora
- **Pinecone** — Managed option for organizations without dedicated ML infrastructure; limited air-gap suitability

**Technical Constraints:**
- Minimum 3-node cluster with replication factor 2
- Vector dimensions must be consistent per collection; separate collections per embedding model
- Payload schema versioned alongside graph schema

---

### 2.3 Embedding Models

Selection is dictated by deployment constraints and compliance domain:

| Model | Parameters | Context Window | Use Case | Deployment |
|---|---|---|---|---|
| **BGE-M3** (BAAI) | 568M | 8192 tokens | Global multilingual compliance (100+ languages) | Self-hosted (GPU) |
| **Nomic-Embed-Text v1.5** | 137M | 8192 tokens | Highly regulated sectors requiring full training data auditability and provenance | Self-hosted (CPU/GPU) |
| **Cohere Embed v4** | Managed | — | Hosted API deployment with enterprise SLA | Managed API |
| **Jina Embeddings v4** | — | — | Multimodal GRC bases with visual evidence (architecture diagrams) | Self-hosted / API |

**Late Interaction (ColBERT) Model:**
- **Model:** `colbert-ir/colbertv2.0` (base) or domain-fine-tuned variant
- **Storage:** Pre-computed token embeddings cached in Qdrant multi-vector collection
- **Index:** PLAID (Production-ready Late Interaction Approximate Nearest Neighbor Datastructure) for sub-linear retrieval

**Technical Constraints:**
- ColBERT token embeddings stored as multi-vector per document chunk (128-dimensional per token)
- All embeddings for air-gapped environments must use self-hosted models only (BGE-M3 or Nomic)
- Embedding model version pinned in pipeline configuration; re-embedding triggered on version upgrade

---

### 2.4 PDF-to-Markdown Extraction Engine

A tiered extraction pipeline is employed based on document characteristics:

| Tier | Tool | Trigger Condition | Output |
|---|---|---|---|
| **T1 — Standard** | Marker (Datalab) | Digitally native PDFs; financial reports; legal contracts | Markdown + JSON |
| **T2 — Complex Layout** | MinerU (OpenDataLab) | Regulatory frameworks with borderless tables; multi-language; academic style | Markdown with HTML-embedded complex structures |
| **T3 — Scanned / Legacy** | LLMWhisperer | Scanned archive documents; multi-column regulatory reports; spatial context critical | Layout-preserving Markdown with confidence scores |
| **T4 — Multi-format** | Docling / BlazeDocs | CI/CD automated pipeline ingestion; API-driven; speed priority | Agent-ready Markdown |

**Document Classifier:**
A lightweight pre-processing classifier (heuristic + LLM-assisted) determines which tier to apply based on:
- PDF metadata (Creator field; embedded font presence)
- Page count and layout complexity score
- Language detection (applying T2 for non-Latin scripts)

**Fallback Chain:** T1 → T2 → T3. If T1 accuracy score falls below threshold, automatically retry with T2.

---

### 2.5 LLM Layer

**Primary Models (in order of preference):**

| Use Case | Model | Rationale |
|---|---|---|
| Rule extraction (De Jure pipeline) | `claude-opus-4` or `gpt-4o` | High accuracy requirement; complex legal text decomposition |
| Crosswalk classification | Fine-tuned LLM on compliance taxonomy | Domain-specific accuracy; MECE logic enforcement |
| GraphRAG synthesis | `claude-sonnet-4` | Fast synthesis with high coherence; cost-effective at scale |
| OSCAL artifact generation | `claude-opus-4` | Structured output with schema adherence |
| Agent orchestration | Model-agnostic (skills.md portable) | Avoid vendor lock-in; declarative specification layer |

**LLM Configuration Requirements:**
- All LLM calls must use structured output mode (JSON schema enforcement) for rule extraction and classification tasks
- Temperature set to 0.0 for all classification and mapping tasks; 0.2 permitted for narrative generation
- Maximum context window usage: 80% of model maximum to prevent truncation artifacts
- All LLM calls logged with prompt hash, model version, and output for auditability

---

### 2.6 Enterprise GRC Platform Integration

**Supported Integration Targets (Phase 2+):**

| Platform | Integration Method | Data Exchanged |
|---|---|---|
| MetricStream | REST API v4 | Control library export; gap findings push |
| ServiceNow GRC | REST API / IntegrationHub | Risk register sync; incident correlation |
| AuditBoard | REST API | Audit evidence pull; gap findings push |
| Riskonnect | REST API | ERM/BCM risk correlation |

**Integration Pattern:**
- Outbound: Webhook-triggered push of gap findings as structured JSON to GRC platform API
- Inbound: Scheduled pull (configurable cadence, default 6h) of control status updates via GRC platform REST API
- Authentication: OAuth 2.0 client credentials flow; secrets stored in Vault (HashiCorp or cloud-native equivalent)

---

## 3. Ingestion Pipeline: Technical Specification

### 3.1 De Jure Regulatory Rule Extraction Pipeline

```
Input: Raw PDF
         │
         ▼
┌─────────────────┐
│  Stage 1:       │  Tool: Marker / MinerU / LLMWhisperer (tiered)
│  Normalization  │  Output: Structured Markdown (.md) with YAML frontmatter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 2:       │  LLM prompt: Decompose section into atomic rule units
│  Semantic       │  Output: JSON array of {rule_text, clause_ref, definitions[],
│  Decomposition  │          jurisdiction, obligation_type}
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Stage 3:       │  LLM-as-a-judge: Score across 19 evaluation dimensions
│  Multi-Criteria │  Dimensions: metadata accuracy, legal definition alignment,
│  Evaluation     │              rule semantics, scope clarity, etc.
└────────┬────────┘
         │
    Score < threshold?
    ┌────┴────┐
   YES       NO
    │         │
    ▼         ▼
┌────────┐  ┌──────────────────────┐
│ Stage 4│  │ Graph Ingestion:     │
│ Itera- │  │ Create Obligation    │
│ tive   │  │ nodes; generate      │
│ Repair │  │ embeddings; link to  │
└────┬───┘  │ Regulation node      │
     │      └──────────────────────┘
     └──────► Re-evaluate (max 3 iterations)
              If still failing → quarantine queue
```

**Scoring Threshold:** Rules scoring below 0.75 (normalized 0–1) after Stage 3 are routed to iterative repair. Rules scoring below threshold after 3 repair iterations are quarantined for human expert review.

---

### 3.2 Chunking Strategy

For RAG retrieval, ingested Markdown is chunked using a hybrid pipeline:

**Primary Strategy: Markdown-Header-Based Chunking**
- Split on `#`, `##`, `###` heading tokens
- Preserve complete semantic sections as defined by the regulatory author
- Each chunk tagged with `section_path` breadcrumb (e.g., `Article 11 > Section 3 > Clause (b)`)

**Secondary Strategy (for dense sub-sections > 2,000 tokens): Semantic Chunking**
- Generate sentence-level embeddings within the section
- Split where cosine distance between consecutive sentence embeddings exceeds threshold (default: 0.75)
- Recall improvement target: +9% over fixed-size chunking on regulatory retrieval benchmarks

**Tertiary Strategy (for complex legal statutes): Agentic Chunking**
- LLM generates a global summary of the parent section
- Summary is appended to each child chunk as context prefix
- Prevents orphaned sub-clause interpretation errors
- Applied to: statutes > 10,000 tokens; documents with extensive cross-referencing

**Anti-Pattern (explicitly prohibited):** Fixed-size character/token splitting on regulatory documents. This approach is forbidden as it destroys semantic boundaries in legal text.

---

## 4. Knowledge Graph Schema

### 4.1 Node Schema

```cypher
// Regulation Node
CREATE (r:Regulation {
  id: STRING,                  // UUID
  framework_id: STRING,        // e.g., "DORA", "EU_AI_ACT"
  name: STRING,
  version: STRING,
  jurisdiction: STRING,
  effective_date: DATE,
  ingestion_time: DATETIME,    // bitemporal: system time
  event_time: DATETIME,        // bitemporal: real-world effective time
  status: ENUM['active', 'superseded', 'draft'],
  language: STRING             // ISO 639-1
})

// Obligation Node
CREATE (o:Obligation {
  id: STRING,
  obligation_text: STRING,
  clause_ref: STRING,          // e.g., "Article 11, §3(b)"
  obligation_type: ENUM['mandatory', 'conditional', 'recommended'],
  effective_date: DATE,
  invalidated_at: DATETIME,    // null if still active
  ingestion_time: DATETIME,
  event_time: DATETIME,
  embedding_id: STRING         // reference to vector store record
})

// Control Node
CREATE (c:Control {
  id: STRING,
  name: STRING,
  description: STRING,
  control_type: ENUM['technical', 'operational', 'managerial'],
  owner: STRING,
  status: ENUM['active', 'deprecated', 'under_review'],
  last_tested: DATE,
  ingestion_time: DATETIME,
  event_time: DATETIME,
  embedding_id: STRING
})

// Risk Node
CREATE (risk:Risk {
  id: STRING,
  name: STRING,
  category: STRING,
  likelihood: INTEGER,         // 1–5 scale
  impact: INTEGER,             // 1–5 scale
  residual_risk_score: FLOAT,
  ingestion_time: DATETIME
})

// Evidence Node
CREATE (e:Evidence {
  id: STRING,
  evidence_type: ENUM['policy_doc', 'test_result', 'screenshot', 'log_export'],
  collection_date: DATE,
  artifact_path: STRING,
  collected_by: STRING,
  ingestion_time: DATETIME
})
```

### 4.2 Edge Schema

```cypher
// Set-theory mapping relationship
CREATE (c:Control)-[:SATISFIES {
  mapping_type: ENUM['equivalent_to','superset_of','subset_of','intersects_with','no_relationship'],
  confidence_score: FLOAT,     // 0.0–1.0
  mapped_by: ENUM['ai_auto', 'human_validated'],
  mapped_at: DATETIME,
  gap_narrative: STRING,       // populated when mapping_type is 'subset_of'
  review_required: BOOLEAN
}]->(o:Obligation)

// Temporal supersession
CREATE (r2:Regulation)-[:SUPERSEDES {
  supersession_date: DATE,
  reason: STRING
}]->(r1:Regulation)

// Evidence chain
CREATE (c:Control)-[:EVIDENCED_BY {
  evidence_date: DATE,
  review_cycle: STRING
}]->(e:Evidence)
```

---

## 5. Late Interaction (ColBERT) Retrieval Architecture

### 5.1 Offline Phase (Indexing)

```
Regulatory Obligation Text
         │
         ▼
   Tokenize (WordPiece)
         │
         ▼
   ColBERT Encoder → Per-token contextualized embeddings
   [T1_emb, T2_emb, ..., Tn_emb]  (dim=128 each)
         │
         ▼
   Store as Multi-Vector in Qdrant
   Collection: "obligations_colbert"
   Point: {id: obligation_id, vectors: [[T1], [T2], ..., [Tn]]}
```

### 5.2 Online Phase (Query Retrieval)

```
User Query / Control Text
         │
         ▼
   ColBERT Encoder → Query token embeddings [Q1, Q2, ..., Qm]
         │
         ▼
   MaxSim Scoring (per query token):
   For each Qi: find max cosine_sim(Qi, Tj) across all document tokens
   Aggregate: sum(max_sims) = relevance_score
         │
         ▼
   PLAID ANN Index → Top-K candidates (K=100)
         │
         ▼
   Exact MaxSim Re-ranking → Top-N results (N=20)
         │
         ▼
   One-Hop Graph Traversal → Semantic subgraph extraction
         │
         ▼
   LLM Synthesis → Final compliance determination with path trace
```

**Performance Target:**  
10,000 control × 5,000 obligation crosswalk: < 10 minutes total  
Single query latency: < 500ms (95th percentile)  
FLOPs reduction vs. cross-encoder: > 100× at equivalent accuracy

---

## 6. Temporal Knowledge Graph Implementation

### 6.1 Bitemporal Query Interface

```python
# Example: Reconstruct compliance posture at a historical date
def query_compliance_posture(
    framework_id: str,
    as_of_date: datetime,
    control_ids: list[str] | None = None
) -> CompliancePosture:
    """
    Returns the compliance posture that was active at as_of_date.
    Uses event_time for regulatory obligation validity.
    Uses ingestion_time to exclude facts not yet recorded at query time.
    """
    cypher = """
    MATCH (c:Control)-[r:SATISFIES]->(o:Obligation)-[:MANDATED_BY]->(reg:Regulation)
    WHERE reg.framework_id = $framework_id
      AND o.event_time <= $as_of_date          // obligation was active
      AND (o.invalidated_at IS NULL OR o.invalidated_at > $as_of_date)  // not yet invalidated
      AND r.mapped_at <= $as_of_date           // mapping existed at that time
    RETURN c, r, o, reg
    """
```

### 6.2 Regulatory Update Processing Workflow

```
New Regulation Version Detected
         │
         ▼
  Ingest new PDF → De Jure pipeline
         │
         ▼
  Create new Regulation node (version N+1)
         │
         ▼
  Create SUPERSEDES edge:
  (Regulation v N+1)-[:SUPERSEDES {supersession_date}]->(Regulation vN)
         │
         ▼
  Mark prior Obligation nodes:
  SET o.invalidated_at = supersession_date, o.status = 'superseded'
         │
         ▼
  Extract new Obligation nodes from updated text
         │
         ▼
  Trigger crosswalk re-evaluation for all new/changed obligations
         │
         ▼
  Generate gap delta report: net_new_gaps, resolved_gaps, unchanged_gaps
         │
         ▼
  Notify compliance owners of net_new_gaps via configured alert channel
```

---

## 7. Agentic Framework Specification

### 7.1 agents.md Root Governance File Structure

```markdown
---
name: rckg-compliance-agents
version: 1.0.0
description: Governance constraints for all RCKG autonomous agents
---

## Project Context
This repository contains the Risk and Control Knowledge Graph platform.
Agents operate in compliance-critical environments.

## Strict Constraints

### Read-Only Zones (NEVER modify)
- `/source-regulations/` — Raw ingested regulatory documents
- `/graph/production/` — Production graph write operations require human approval
- `/controls/library/` — Control definitions owned by GRC team

### Permitted Write Zones
- `/audit-findings/` — Gap reports and audit evidence packages
- `/oscal-exports/` — Generated OSCAL artifacts
- `/ingestion-queue/` — Staging area for new documents pending review

### Escalation Rules
- HALT and notify human reviewer if: mapping_type = 'intersects_with' AND confidence_score < 0.80
- HALT and notify if: any Obligation node invalidated_at would be set on a framework with active audit in progress
- HALT if: OSCAL export fails schema validation after 2 retry attempts

### Prohibited Actions
- Agents MUST NOT delete any node or edge from the production graph
- Agents MUST NOT modify control status without an associated evidence record
- Agents MUST NOT commit OSCAL artifacts to version control without schema validation pass
```

### 7.2 Example SKILL.md Structure (ISO 27001 Access Review)

```markdown
---
name: iso27001-access-review
description: >
  Performs an automated ISO 27001 Annex A.9 Access Control review against
  AWS IAM, Azure AD, or GCP IAM infrastructure. Triggered when user requests
  an access control audit, access review, or ISO 27001 A.9 compliance check.
version: 1.2.0
author: GRC Engineering Team
---

## Instructions

You are executing an ISO 27001 Access Control compliance review.

### Step 1: Retrieve Obligations
Query the knowledge graph for all active Obligation nodes linked to
Regulation {framework_id: "ISO_27001"} with clause_ref matching "Annex A.9.*"

### Step 2: Collect Infrastructure Evidence
Execute `/scripts/aws_iam_export.py` to extract current IAM policy assignments.
Store output to `/audit-findings/access-review-{date}/iam_snapshot.json`

### Step 3: Run Crosswalk
For each retrieved Obligation, evaluate the IAM snapshot against the
obligation text using the crosswalk engine API endpoint.

### Step 4: Generate Findings Report
Write gap findings to `/audit-findings/access-review-{date}/findings.md`
Format: obligation_id | mapping_type | gap_narrative | recommended_action

### Step 5: Escalate
Any Subset-of or No-relationship mappings MUST be flagged for human review
before closing the audit task.

## References
- `/references/iso27001-a9-definitions.md`
- `/references/aws-iam-permission-taxonomy.md`
```

---

## 8. OSCAL Integration

### 8.1 Compliance-as-Code Pipeline

```
Knowledge Graph State
         │
         ▼
  Trestle CLI → Read control responses from /controls/markdown/
         │        (human-editable individual Markdown files per control)
         ▼
  AI Agent validates control Markdown against graph Obligation nodes
         │
         ▼
  Schema validation: NIST OSCAL JSON Schema v1.1.x
         │
         ▼
  Compile → OSCAL SSP JSON artifact
         │
         ▼
  Git commit → Version-controlled compliance artifact
         │
         ▼
  CI/CD pipeline → Validate → Tag release → Deliver to audit portal
```

### 8.2 OSCAL Node Mapping

| OSCAL Construct | Knowledge Graph Equivalent |
|---|---|
| `catalog` | `Regulation` node with all child `Obligation` nodes |
| `profile` | Filtered subgraph of selected `Obligation` nodes |
| `component-definition` | `Control` node with `EVIDENCED_BY` edges |
| `system-security-plan` | Full subgraph: Controls + Obligations + Evidence |
| `plan-of-action-and-milestones` | All `SUBSET_OF` and `NO_RELATIONSHIP` edges with gap narratives |

---

## 9. Data Pipeline Infrastructure

### 9.1 Orchestration

**Recommended:** Apache Airflow (self-hosted) or Prefect Cloud  
**Trigger types:**
- Schedule-based (nightly regulatory source check)
- Event-based (new document dropped to ingestion S3 bucket / object store)
- API-triggered (GRC platform webhook on control update)

**DAG structure:**
```
ingest_document_dag
  ├── classify_document
  ├── extract_markdown (tiered: T1/T2/T3/T4)
  ├── run_de_jure_pipeline
  │     ├── normalize
  │     ├── decompose
  │     ├── evaluate
  │     └── repair (conditional)
  ├── generate_embeddings
  ├── upsert_graph_nodes
  └── trigger_crosswalk_reevaluation
```

### 9.2 Message Queue

**Recommended:** Apache Kafka or AWS SQS  
**Topics:**
- `rckg.ingestion.new-document` — Triggers ingestion DAG
- `rckg.crosswalk.reevaluation-needed` — Triggers crosswalk engine for affected obligation set
- `rckg.gap.detected` — Triggers notification service for compliance owners
- `rckg.agent.task` — Distributes agentic skill tasks to available agent workers

---

## 10. Security Architecture

### 10.1 Authentication and Authorization

| Layer | Mechanism |
|---|---|
| User authentication | SAML 2.0 / OIDC (SSO integration) |
| API authentication | OAuth 2.0 with short-lived JWT tokens |
| Agent authentication | Mutual TLS + service account tokens |
| Secret management | HashiCorp Vault or AWS Secrets Manager |
| RBAC | Framework-level, Control-level, Evidence-level granularity |

### 10.2 Data Governance Implementation

All source Markdown documents include a metadata governance header:

```yaml
---
framework_id: DORA
version: "2025-01"
jurisdiction: EU
effective_date: 2025-01-17
ai-train: "no"
ai-input: "yes"
search: "yes"
classification: internal-restricted
---
```

- `ai-input: no` — Document is excluded from all agentic retrieval operations
- `ai-train: no` — Document is excluded from any fine-tuning pipelines
- Access to `classification: internal-restricted` documents requires explicit RBAC role assignment

### 10.3 Audit Logging

All of the following events are written to an immutable, append-only audit log:

- Document ingestion events (document_id, hash, timestamp, extracted_rules_count)
- Graph node creation, update, and invalidation events
- All crosswalk mapping classifications (control_id, obligation_id, mapping_type, confidence, timestamp)
- All LLM calls (prompt hash, model, token count, latency — not full prompt text for data minimization)
- All user compliance queries (user_id, query_text, response_path)
- All agent task executions (skill_id, agent_id, actions_taken, outputs_written)

---

## 11. Deployment Architecture

### 11.1 Cloud-Native (Primary)

```
┌─────────────────────────────────────────────┐
│           Kubernetes Cluster                 │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Ingestion│  │ Crosswalk│  │  Graph   │  │
│  │  Pods    │  │  Engine  │  │  Query   │  │
│  │  (N=3)   │  │  Pods    │  │  API     │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │        Data Layer (StatefulSets)     │   │
│  │  Neo4j Cluster │ Qdrant Cluster      │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │                    │
    External API          Internal Mesh
         │                    │
    GRC Platforms        Kafka / SQS
```

### 11.2 Air-Gapped (Self-Hosted)

For organizations requiring full data sovereignty:
- All embedding models deployed as local inference servers (Ollama or vLLM)
- LLM inference via self-hosted model (Llama 3.x or equivalent open-weight model)
- No external API calls permitted; all dependencies vendored
- Graph and vector databases deployed on-premises on bare metal or private VMware
- CI/CD pipeline runs entirely within private GitLab or Gitea instance

---

## 12. Testing and Validation Requirements

### 12.1 Unit Testing

| Component | Coverage Target | Testing Approach |
|---|---|---|
| PDF extraction accuracy | > 95% structural preservation | ParseBench enterprise corpus subset |
| De Jure rule extraction | > 80% evaluator preference | Held-out regulatory document set with manual annotations |
| Crosswalk classification | > 90% accuracy | Labeled control-obligation pair benchmark |
| Temporal query correctness | 100% | Synthetic time-series compliance dataset |
| OSCAL schema validity | 100% | NIST OSCAL validator |

### 12.2 Integration Testing

- End-to-end ingestion: Raw PDF → Graph node creation (< 5 minutes per document)
- GRC platform sync: Control update in GRC → Reflected in graph (< 6 hours, configurable)
- Agent governance: Agent attempting prohibited write → Hard failure, no partial write
- Gap notification: New obligation ingested creating gap → Compliance owner notified (< 24 hours)

### 12.3 Performance Testing

- Crosswalk load test: 10,000 controls × 5,000 obligations on target hardware → < 10 minutes
- Query latency test: 100 concurrent natural language compliance queries → p95 < 5 seconds
- Graph scale test: 1,000,000 nodes + 5,000,000 edges; single-hop query → < 500ms

---

## 13. Dependencies and Third-Party Licenses

| Component | License | Notes |
|---|---|---|
| Neo4j Community | GPL v3 / Enterprise (commercial) | Enterprise required for clustering |
| Qdrant | Apache 2.0 | Fully open-source |
| ColBERT / PLAID | MIT | Research model; production deployment validated |
| BGE-M3 | MIT | Open weights; self-hostable |
| Nomic-Embed-Text v1.5 | Apache 2.0 | Open weights and training data |
| Marker (Datalab) | GPL v3 | LLM-boosted mode requires Gemini API key |
| MinerU (OpenDataLab) | Apache 2.0 | Self-hostable |
| Trestle (IBM) | Apache 2.0 | OSCAL CI/CD integration |
| Apache Airflow | Apache 2.0 | Pipeline orchestration |
| Apache Kafka | Apache 2.0 | Message queue |

---

*End of Technical Requirements Document*