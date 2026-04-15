# Technical Requirements Document (TRD)
## Risk and Control Knowledge Graph (RCKG) Platform

**Document Version:** 4.0 — Agentic GraphRAG Architecture  
**Classification:** Internal — Confidential  
**Last Updated:** 2026-04-12  
**Author:** Architecture Team (Claude Code Synthesis)

---

## Executive Summary

The **Risk and Control Knowledge Graph (RCKG)** platform is an AI-native, high-fidelity compliance intelligence system that transforms regulatory obligations into a continuously maintained, temporally-aware knowledge graph. Unlike traditional GRC tools that rely on manual mapping and static databases, RCKG leverages **agentic orchestration**, **GraphRAG**, and **token-level semantic matching (ColBERT)** to achieve:

- **High Fidelity:** Zero-loss document parsing with semantic decomposition into atomic rule units
- **High Precision:** >90% mapping accuracy via set-theory classification and late-interaction retrieval
- **Completeness:** Multi-framework convergence that eliminates duplicate evidence collection
- **Traceability:** Bitemporal graph modeling with full audit trails and explainable AI decisions

This document provides a complete, build-ready technical specification aligned with open-source, self-hosted deployment constraints.

---

## 1. System Architecture Overview

### 1.1 Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Graph as System of Truth** | Property graph stores semantic topology; relational DBs serve as audit logs |
| **LLM as Assistive, Not Authoritative** | LLMs execute bounded tasks; multi-hop conclusions derive from explicit graph paths |
| **Strictly Self-Hosted** | 100% open-source stack for air-gapped environments; no external API dependencies |
| **Bitemporal Persistence** | No hard deletes; `SUPERSEDES` edges preserve full compliance history |
| **Agent Governance** | Hard declarative boundaries via `agents.md`; skills via portable `skills.md` files |
| **Deterministic Outputs** | Every compliance decision traceable to explicit graph path + source document |

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RCKG Platform                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Module 1: Document Ingestion Pipeline               │   │
│  │  PDF → MinerU/Marker → Markdown → De Jure Extraction → JSON      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Module 2: Knowledge Graph Engine                    │   │
│  │  Memgraph (Graph) + Qdrant (Vector) + Postgres (Metadata)       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▲                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Module 3: Agentic Orchestration Layer               │   │
│  │  agents.md (Governance) + skills.md (Declarative Workflows)     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Module 4: Compliance Crosswalk Engine               │   │
│  │  ColBERT (Late Interaction) + Set-Theory Classification         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Module 5: GraphRAG Query Interface                  │   │
│  │  Dense Vector Search + Graph Traversal + LLM Synthesis          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Module 6: OSCAL Export & GRC Integration            │   │
│  │  NIST OSCAL (JSON/XML/YAML) + ServiceNow/MetricStream APIs       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack (Finalized)

### 2.1 Core Infrastructure

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Containerization** | Docker + Docker Compose | MVP deployment; Kubernetes for scale |
| **API Framework** | FastAPI (Python 3.11) | Async support, auto OpenAPI docs |
| **Workflow Engine** | Apache Airflow | DAG-based orchestration, retry logic |
| **Message Queue** | Apache Kafka | Event-driven pipelines, backpressure handling |

### 2.2 Data Storage Layer

| Purpose | Technology | Schema Details |
|---------|------------|----------------|
| **Graph Database** | Memgraph (in-memory) | Property graph with Cypher queries |
| **Vector Database** | Qdrant | Multi-vector ColBERT support, payload filtering |
| **Relational DB** | PostgreSQL 16 | Raw documents, audit logs, OSCAL exports |
| **Object Storage** | MinIO (S3-compatible) | PDFs, Markdown, evidence artifacts |

### 2.3 AI/ML Stack

| Function | Technology | Configuration |
|----------|------------|---------------|
| **PDF → Markdown** | MinerU (primary) + Marker (fallback) | Complex layouts → structured MD |
| **Embeddings (Dense)** | BAAI BGE-M3 | 1024-dim, 84-language support |
| **Embeddings (Token-level)** | ColBERTv2.0 | Late-interaction for precision matching |
| **LLM (Local)** | Mistral 7B / Llama-3.1-8B | vLLM/Ollama serving, JSON mode |
| **Reranker** | BAAI BGE-Reranker-V2-M3 | Top-K refinement post-retrieval |

### 2.4 Supporting Libraries

- **Pydantic** — Data validation for extraction outputs
- **SQLAlchemy** — PostgreSQL ORM
- **NetworkX** — Local graph validation/testing
- **LangChain (light)** — Pipeline orchestration only (no agent framework reliance)
- **SHACL** — Graph constraint validation (pySHACL)

---

## 3. Data Architecture: Three-Layer PostgreSQL Vault

Before data reaches the Memgraph knowledge graph, it flows through a rigorous **Bronze → Silver → Gold** pipeline in PostgreSQL to ensure data quality and lineage.

### 3.1 Bronze Layer (Raw Storage)

**Table:** `staging_controls`

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | UUID | Unique document identifier |
| `canonical_id` | VARCHAR | Framework-specific ID (e.g., "NIST-AC-2") |
| `raw_file_content` | JSONB | Complete raw text from PDF/CSV |
| `hash` | VARCHAR(64) | SHA-256 for deduplication |
| `ingested_at` | TIMESTAMPTZ | When document was received |

**Purpose:** Immutable record of raw ingestion. No transformations. Hash-based deduplication prevents re-processing identical files.

### 3.2 Silver Layer (Semantic Refinery)

**Table:** `semantic_controls`

| Field | Type | Description |
|-------|------|-------------|
| `framework_name` | VARCHAR | e.g., "NIST CSF", "DORA" |
| `group_id` | VARCHAR | Control group (e.g., "AC", "PR") |
| `objective_text` | TEXT | High-level intent (Blue Header) |
| `statement_text` | TEXT | Atomic rule statement |
| `action_verb` | VARCHAR | e.g., "shall", "must", "should" |
| `subject_noun` | VARCHAR | e.g., "organization", "system" |
| `control_function` | VARCHAR | Preventive, Detective, Corrective |
| `implementation_method` | VARCHAR | Automated, Manual, Hybrid |
| `control_goals` | TEXT[] | CIA triad tags (Confidentiality, Integrity, Availability) |
| `asset_scope` | TEXT[] | Systems/people/data covered |
| `gov_domain` | VARCHAR | Data domain (e.g., "data-protection", "access-control") |
| `legal_base` | VARCHAR | Jurisdictional legal authority |

**Purpose:** AI-extracted structure with semantic facets. Enables powerful graph queries like "find all preventive controls in access-control domain."

### 3.3 Gold Layer (Validated)

**Table:** `golden_controls`

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Validated control ID |
| `silver_record_id` | UUID | FK to semantic_controls |
| `validation_score` | FLOAT | LLM-as-Judge confidence (0-1) |
| `validated_at` | TIMESTAMPTZ | When human/automated validation occurred |
| `validated_by` | VARCHAR | Agent ID or human auditor ID |
| `status` | VARCHAR | draft | validated | superseded |

**Purpose:** Only Gold records are projected to the Memgraph knowledge graph. Human-verified or highly-confident AI-validated data.

### 3.4 Canonical YAML Ingestion Schema

All external adapters must output to this YAML format before staging into Bronze:

```yaml
metadata:
  title: "NIST Cybersecurity Framework"
  version: "1.1"
  publication_date: "2024-02-01"
  jurisdiction: "US"
  legal_base: "Executive Order 14110"

control-groups:
  - id: "ID"
    title: "Identify"
    objectives:
      - id: "ID.AM"
        title: "Physical Assets"
        prose: "The organization understands the management of its physical assets..."
        statements:
          - id: "ID.AM-1"
            prose: "Physical assets (e.g., hardware, devices, media) within a defined scope are inventoried..."
            metadata:
              action_verb: "is inventoried"
              subject_noun: "Physical assets"
              control_function: "preventive"
              implementation_method: "automated"
              control_goals: ["integrity", "availability"]
              asset_scope: ["hardware", "devices", "media"]
              gov_domain: "asset-management"
```

---

## 4. Agentic Orchestration Architecture

### 4.1 Agent Governance Model (`agents.md`)

All autonomous agents operate under **strict declarative governance** defined in a root `agents.md` file:

#### 3.1.1 Read-Only Zones (Protected)
Agents must NEVER modify:
- `/source-regulations/` — Raw regulatory documents
- `/production-graph/` — Direct node/edge writes without validation
- `/audit-findings/` — Historical findings (append-only)

#### 3.1.2 Permitted Write Zones
Agents may write to:
- `/ingestion-queue/` — Pending documents awaiting processing
- `/audit-logs/` — Agent action logs (append-only)
- `/oscal-exports/` — Generated compliance artifacts
- `/gap-reports/` — Detected compliance gaps (draft status)

#### 3.1.3 Escalation Protocol
Agents must **HALT** and notify human reviewers when:
- Mapping confidence score < **0.85** (dynamic threshold)
- Obligation has `NO_RELATIONSHIP` to any control (unmitigated risk)
- Conflict detection score > **0.92** (semantic near-duplicate)
- SHACL constraint validation fails

#### 3.1.4 System Guarantees
- **No Hard Deletes:** All superseded facts retain `SUPERSEDES` edges
- **Immutable Audit Trail:** Every agent action logged with timestamp, actor, and reasoning trace
- **Isolated Write Access:** Each agent scoped to designated output directories

### 3.2 Declarative Agent Skills (`skills.md`)

Complex workflows are packaged as portable, human-readable **Skill Files** using the **Progressive Disclosure Pattern**:

#### 3.2.1 Skill File Structure
```
skills/
├── iso27001-access-review.md      # ISO 27001 A.9 access control review
├── dora-gap-analysis.md            # DORA ICT risk gap analysis
├── oscal-export.md                 # NIST OSCAL SSP/POA&M generation
├── framework-crosswalk.md          # Multi-framework mapping
├── regulatory-ingest.md            # De Jure extraction pipeline
└── evidence-collector.md           # Audit evidence packaging
```

#### 3.2.2 Progressive Disclosure Levels

| Level | Content | Trigger |
|-------|---------|---------|
| **Level 1 (Discovery)** | ~100-token metadata header at agent startup | Always loaded |
| **Level 2 (Activation)** | Full instruction body (< 5,000 tokens) | Semantic match to skill ID |
| **Level 3 (Execution)** | On-demand scripts/references from `/scripts/` and `/references/` | Step-specific invocation |

#### 3.2.3 Example Skill Header (`dora-gap-analysis.md`)
```markdown
---
name: dora-gap-analysis
version: 1.0
description: Automated DORA Article 11 ICT risk gap analysis
trigger: dora-ict-gap
required_agents: [crosswalk_agent, reporting_agent]
write_zones: [/gap-reports/, /oscal-exports/]
read_zones: [/source-regulations/dora/, /production-graph/]
confidence_threshold: 0.85
escalation_on: [low_confidence, no_relationship, shacl_failure]
---
```

### 4.2 Agent Types (Swarm Roles)

| Agent | Responsibility | Tools |
|-------|----------------|-------|
| **Ingestion Agent (Raw to Flattened)** | Extracts semantic units (Objectives/Statements), maps Facets using auto-mapper logic, writes to PostgreSQL Silver layer | MinerU, LLM (Extraction), Pydantic, Canonical YAML serializer |
| **OSCAL Reconciliation Agent** | Compares Silver records against full NIST OSCAL catalog to backfill missing formal parameters (sc, version, implementation-state) | OSCAL schema validator, Graph traversal |
| **Crosswalk Agent** | Generates `[:SATISFIES]` mappings using ColBERT retrieval + LLM set-theory classification | Qdrant, ColBERT, LLM (Classification) |
| **Grooming Agent ("The Gardener")** | Consolidates redundant nodes, finds new Facet connections, adds topological shortcuts, prunes orphaned links | Memgraph traversals, SHACL validator, NetworkX |
| **RAG / Audit Agent** | Answers user questions by traversing multi-hop graph paths, pulls exact evidence base before generating answers | Qdrant, Memgraph, Langfuse tracing |
| **Gap Detection Agent** | Monitors Kafka events for `document.ingested`, triggers crosswalk re-evaluation, alerts on new compliance gaps | Kafka consumer, Airflow DAG trigger |
| **Logic Judge Agent** | Higher-Reasoning model that evaluates semantic faithfulness of mappings (Score < 0.95 → human intervention) | Llama 3 70B / Mistral Large |
| **Technical Judge Agent** | Audits technical/mathematical accuracy (e.g., "Hourly" → 3600 seconds in OSCAL parameters), requires 100% exact match | DeepSeek Reasoner / Fine-tuned specialist model |

---

## 4. Ingestion Pipeline (High-Fidelity Extraction)

### 4.1 Pipeline Stages

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Raw PDF    │ →  │  Markdown    │ →  │  Rule Units  │ →  │  Graph Nodes │
│  (MinIO)     │    │  (MinIO)     │    │  (Postgres)  │    │  (Memgraph)  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### 4.2 Stage 1: Document Parsing

**Tool:** MinerU (primary) + Marker (fallback)

**Output:**
- Structured Markdown (`.md`) with preserved heading hierarchy (H1–H6)
- JSON metadata:
  - `heading_tree` — Nested structure of sections
  - `tables` — GitHub-flavored Markdown tables
  - `footnotes` — Inline annotations with parent references
  - `layout` — Column detection, reading order

**Acceptance Criteria:**
- Zero loss of heading hierarchy for any tested regulatory document
- Tables rendered in valid GFM syntax
- Compliance officer can verify semantic fidelity against original PDF

### 4.3 Stage 2: Hybrid Context Chunking

**Strategy:** Markdown Header-Based + Semantic Splitting

```python
# Chunking Logic
if section_has_clear_header:
    chunk = header_based_chunk(section)
    chunk.metadata["section_path"] = "Article 11 > Sec 3 > (a)"
else:
    # Semantic splitting using embedding distance
    sentences = spacy_split(section.text)
    chunks = semantic_split(sentences, threshold=0.75)  # cosine distance
```

**Constraints:**
- **NO character-based chunking** — Preserves legal clause integrity
- **Section breadcrumbs** — `section_path` property on all chunks
- **Embedding threshold** — `> 0.75` cosine distance triggers split

### 4.4 Stage 3: De Jure Rule Unit Extraction

**Four-Stage Automated Pipeline:**

1. **Normalization** — Validate Markdown structural fidelity
2. **Semantic Decomposition** — LLM extracts atomic rule units as JSON arrays:
   ```json
   {
     "rule_text": "Financial institutions shall...",
     "clause_ref": "DORA Article 11(2)",
     "obligation_type": "technical_requirement",
     "action_verb": "shall",
     "subject_noun": "financial institutions",
     "effective_date": "2025-01-01"
   }
   ```
3. **LLM-as-a-Judge Evaluation** — Score extracted rules on:
   - Metadata accuracy
   - Legal definition alignment
   - Rule semantics completeness
4. **Iterative Repair** — Low-scoring extractions reprocessed with upstream context

**Acceptance Criteria:**
- Extracted rules preferred over baseline outputs in **> 80%** of evaluator assessments
- Each rule includes: text, clause reference, obligation type, action verb, jurisdiction

---

## 5. Knowledge Graph Schema (Memgraph)

### 5.1 Node Types (Expanded Schema)

| Node Label | Description | Key Properties |
|------------|-------------|----------------|
| `Regulation` | Regulatory framework | `framework_id`, `name`, `jurisdiction`, `version`, `effective_date`, `status`, `legal_base` |
| `ControlGroup` | High-level domain grouping | `group_id`, `title`, `domain` (e.g., "ID" for Identify, "PR" for Protect) |
| `ControlObjective` / `Obligation` | The "Why" — high-level intent | `id`, `text`, `impact_category`, `obligation_type`, `prose` |
| `ControlStatement` / `ObligationStatement` | The "What" — atomic rule | `id`, `statement_text`, `action_verb`, `subject_noun`, `gov_domain`, `legal_base` |
| `Control` | Internal corporate mitigation | `control_id`, `name`, `description`, `owner`, `status`, `frequency` |
| `Risk` | Operational risk vector | `risk_id`, `name`, `category`, `likelihood` (1-5), `impact` (1-5), `residual_risk_score`, `mitigation_strategy`, `inherent_risk_score` |
| `Policy` | Internal corporate policy | `policy_id`, `name`, `version`, `owner`, `effective_date` |
| `Evidence` | Audit proof artifact | `evidence_id`, `type`, `date`, `artifact_path`, `hash`, `verification_status` |
| `Document` | Ingested source document | `document_id`, `filename`, `hash`, `ingested_at`, `language`, `ai_input_permission` |
| `Framework` | Compliance framework (ISO, NIST) | `framework_id`, `name`, `version`, `domain`, `publication_date` |

### 5.2 Relationship Types (Edges - Expanded)

| Edge Label | Source → Target | Properties | Semantics |
|------------|-----------------|------------|-----------|
| `HAS_GROUP` | Regulation → ControlGroup | — | Framework contains group |
| `CONTAINS` | ControlGroup → ControlObjective | — | Group contains objective |
| `ACHIEVES` | ControlStatement → ControlObjective | — | Statement achieves objective |
| `MANDATED_BY` | ObligationStatement → Regulation | `clause_ref` | Links obligation to source |
| `SATISFIES` | Control → ObligationStatement | `mapping_type`, `confidence_score`, `reasoning`, `mapped_at` | Set-theory classification |
| `EQUIVALENT_TO` | Control → ObligationStatement | — | Full 1:1 coverage |
| `SUPERSET_OF` | Control → ObligationStatement | — | Control exceeds requirement |
| `SUBSET_OF` | Control → ObligationStatement | `gap_details`, `gap_narrative` | Partial coverage — gap exists |
| `INTERSECTS_WITH` | Control → ObligationStatement | `divergence_notes`, `human_review_required` | Overlapping but divergent |
| `NO_RELATIONSHIP` | Control → ObligationStatement | `risk_level`, `criticality` | Unmitigated — unmanaged risk |
| `MITIGATES` | Control → RiskStatement | — | Control addresses risk |
| `MITIGATED_BY` | RiskStatement → Control | — | Risk is mitigated by control |
| `EVIDENCED_BY` | Control → Evidence | `date`, `verification_status`, `artifact_path` | Links control to audit proof |
| `GOVERNED_BY` | Control → Policy | — | Authorizing policy |
| `SUPERSEDES` | Regulation → Regulation | `effective_date`, `superseded_at` | Temporal version relationship |
| `BELONGS_TO` | Node → Framework | — | Framework membership |
| `DERIVED_FROM` | Node → Document | `page_ref`, `section_path`, `hash` | Source document lineage |
| `HAS_GAP` | Obligation → Gap | `severity`, `description`, `created_at`, `remediation_status` | Unmet obligation generates gap |

### 5.3 Trust via LLM-as-a-Judge Evaluator Layers

To ensure autonomous trust, all AI-driven decisions undergo **Higher-Reasoning Judge** validation before committing to the production graph:

#### 5.3.1 Logic Judge (Semantic Faithfulness)

**Model:** Llama 3 70B / Mistral Large  
**Purpose:** Evaluates whether the mapping preserves actual intent of the control/regulation.

**Evaluation Criteria:**
- Does the `SUPERSET_OF` classification truly exceed the regulatory requirement?
- Is `SUBSET_OF` justified by concrete missing elements?
- Does the reasoning trace align with legal interpretation standards?

**Threshold:** Score < 0.95 triggers manual intervention queue.

#### 5.3.2 Technical Judge (Mathematical Accuracy)

**Model:** DeepSeek Reasoner / Fine-tuned specialist  
**Purpose:** Audits technical/formal parameters for 100% exact match.

**Evaluation Examples:**
- "Hourly monitoring" in control text must reconcile to `"frequency": "3600"` in OSCAL `interval` parameter
- "Real-time" must map to `latency_threshold <= 1000ms` in implementation-state
- Date ranges must be consistent across `effective_date`, `valid_from`, `valid_to`

**Threshold:** 100% exact match required. Any deviation → quarantine.

#### 5.3.3 Fine-Tuning Loop

Poorly graded generation outputs from Judges are placed into:
```sql
-- PostgreSQL fine-tuning dataset
CREATE TABLE judge_training_data (
    input_text TEXT,
    model_output TEXT,
    judge_score FLOAT,
    judge_reasoning TEXT,
    corrected_output TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Used for DPO (Direct Preference Optimization) / RLHF fine-tuning to continually elevate foundational models.

### 5.4 Bitemporal Data Model

All nodes/edges carry **dual timestamps**:

```cypher
// Node properties
valid_from: DateTime    // Event time: when fact became active in real world
valid_to: DateTime      // Event time: when fact became inactive (NULL = active)
ingested_at: DateTime   // Ingestion time: when RCKG recorded the fact
status: String          // active | superseded | invalidated
```

**Temporal Query Support:**
```cypher
// Query compliance posture as of a specific date
MATCH (c:Control)-[:SATISFIES]->(o:Obligation)
WHERE c.valid_from <= $as_of_date AND (c.valid_to IS NULL OR c.valid_to > $as_of_date)
RETURN c, o
```

**No Hard Deletes:**
- Superseded nodes retain `SUPERSEDES` edges to new versions
- Inactive edges marked with `invalidated_at` but remain queryable for historical audits

---

## 6. Control Mapping Engine (High-Precision Crosswalk)

### 6.1 Problem Statement

Mapping **10,000+ controls** against **5,000+ regulatory obligations** requires:
- **Token-level precision** — Legal language nuance lost in dense embeddings
- **Scalability** — Cross-encoders too slow for production
- **Set-theory classification** — Not just similarity, but logical relationship

### 6.2 Solution: ColBERT (Late Interaction Retrieval)

**Why ColBERT:**
- Creates **token-level embeddings** (no compression loss)
- **MaxSim scoring** for exact semantic token-matching
- **Precomputed control embeddings** — Query-time efficient

**Implementation:**

#### Step 1: Indexing (Offline)
```python
# Precompute token embeddings for all controls
controls = graph.query("MATCH (c:Control) RETURN c.control_id, c.description")
colbert_index = ColBERTIndex()
for control in controls:
    token_embeddings = colbert_model.encode(control.description)
    colbert_index.add(control.control_id, token_embeddings)
colbert_index.save("qdrant://colbert_controls_index")
```

#### Step 2: Querying (Online)
```python
# Obligation → token embeddings
obligation_embeddings = colbert_model.encode(obligation.text)

# MaxSim scoring against indexed controls
scores = colbert_index.search(obligation_embeddings, top_k=50)
candidate_controls = scores[:10]  # Top-10 for LLM classification
```

#### Step 3: Set-Theory Classification (LLM-as-Judge)
```python
classification_prompt = """
Given:
- Obligation: "{obligation_text}"
- Control: "{control_text}"

Classify the set-theory relationship:
- EQUIVALENT_TO: Full 1:1 coverage
- SUPERSET_OF: Control exceeds requirement (no gap)
- SUBSET_OF: Partial coverage (gap exists)
- INTERSECTS_WITH: Overlapping but divergent (human review)
- NO_RELATIONSHIP: No coverage (unmitigated risk)

Output JSON: {{"mapping_type": "...", "confidence": 0.xx, "reasoning": "..."}}
"""

llm_response = llm.classify(classification_prompt)
```

#### Step 4: Graph Update
```cypher
// Create relationship with classification metadata
MATCH (o:Obligation {obligation_id: $obligation_id})
MATCH (c:Control {control_id: $control_id})
MERGE (c)-[rel:SATISFIES {
  mapping_type: $mapping_type,
  confidence_score: $confidence,
  reasoning: $reasoning,
  mapped_at: datetime()
}]->(o)

// If SUBSET_OF, auto-generate gap record
FOREACH (x IN CASE WHEN $mapping_type = 'SUBSET_OF' THEN [1] ELSE [] END |
  CREATE (g:Gap {
    gap_id: randomUUID(),
    severity: 'medium',
    description: $gap_narrative,
    created_at: datetime()
  })
  CREATE (o)-[:HAS_GAP]->(g)
)
```

### 6.3 Mapping Classifications (Set Theory)

| Classification | Semantics | System Action |
|----------------|-----------|---------------|
| `EQUIVALENT_TO` | Full 1:1 coverage | Auto-satisfies obligation |
| `SUPERSET_OF` | Control exceeds requirement | Auto-satisfies; no gap |
| `SUBSET_OF` | Partial coverage | Auto-flag gap; generate narrative |
| `INTERSECTS_WITH` | Overlapping but divergent | **HALT** — human-in-the-loop review |
| `NO_RELATIONSHIP` | No coverage | **CRITICAL** — unmitigated risk alert |

### 6.4 Multi-Framework Convergence

When a control satisfies an obligation in **Framework A**, the system automatically:
1. Identifies overlapping obligations in **Framework B, C, D**
2. Mirrors the `SATISFIES` relationship (with re-classification)
3. Eliminates duplicate evidence collection

**Result:** Single control satisfies multiple frameworks → **audit fatigue reduction**

---

## 7. GraphRAG Query Architecture

### 7.1 Query Flow

```
┌─────────────────┐
│  User Query     │
│  "GDPR Art 32"  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Embedding      │
│  (BGE-M3)       │
└────────┬────────┘
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Qdrant         │─────►│  Memgraph       │
│  Top-K Chunks   │      │  Subgraph       │
└────────┬────────┘      │  Traversal      │
         ▼               └────────┬────────┘
         ▼                        │
┌────────────────────────────────┴────────┐
│  LLM Synthesis (Grounded)               │
│  — NO hallucinated answers              │
│  — All responses traceable to graph     │
└─────────────────────────────────────────┘
```

### 7.2 Hybrid Retrieval Algorithm

```python
def graphrag_query(user_query: str, as_of_date: DateTime | None = None):
    # Stage 1: Dense vector search
    query_embedding = bge_m3.encode(user_query)
    top_chunks = qdrant.search(query_embedding, top_k=20)
    
    # Stage 2: Extract candidate nodes
    candidate_obligations = [chunk.payload['obligation_id'] for chunk in top_chunks]
    
    # Stage 3: Graph traversal (one-hop expansion)
    subgraph = memgraph.query("""
        MATCH (o:Obligation {obligation_id: $id})-[:SATISFIES*1..2]-(c:Control)
        WHERE $as_of_date IS NULL OR (c.valid_from <= $as_of_date AND (c.valid_to IS NULL OR c.valid_to > $as_of_date))
        RETURN o, c
    """, {"id": candidate_obligations, "as_of_date": as_of_date})
    
    # Stage 4: LLM synthesis with context
    context = serialize_subgraph(subgraph)
    answer = llm.generate(
        prompt=f"""
        Answer based ONLY on this graph context:
        {context}
        
        User query: {user_query}
        
        If context insufficient, state "Insufficient graph context" — do not hallucinate.
        """
    )
    
    return {
        "answer": answer,
        "source_paths": extract_tracing_paths(subgraph),
        "confidence": compute_confidence(subgraph)
    }
```

### 7.3 Traceability Requirements

Every query response must include:
- **Source nodes** — Exact Obligation/Control IDs
- **Edge paths** — Graph traversal used
- **Evidence references** — Linked Evidence nodes
- **Document lineage** — Page/section references from source PDFs

---

## 8. SHACL Constraint Validation

### 8.1 Purpose

Prevent **graph topology corruption** by validating relationships before materialization:

```turtle
# SHACL Shape: Control must satisfy Obligation with valid mapping_type
_:ControlSatisfiesObligationShape
    a sh:NodeShape ;
    sh:targetClass :Control ;
    sh:property [
        sh:path :SATISFIES ;
        sh:minCount 0 ;
        sh:node [
            sh:property [
                sh:path :mapping_type ;
                sh:in ("EQUIVALENT_TO" "SUPERSET_OF" "SUBSET_OF" "INTERSECTS_WITH" "NO_RELATIONSHIP") ;
            ] ;
            sh:property [
                sh:path :confidence_score ;
                sh:minInclusive 0.0 ;
                sh:maxInclusive 1.0 ;
            ] ;
        ] ;
    ] ;
```

### 8.2 Validation Pipeline

```python
# Before committing new relationship
new_rel = create_satisfies_edge(control_id, obligation_id, mapping_type, confidence)

# Validate against SHACL shapes
validator = pySHACL.validate(graph, shacl_graph=shapes_graph)

if not validator.is_valid:
    # Quarantine for human review
    quarantine_for_review(new_rel, validator.results)
else:
    # Commit to production graph
    memgraph.commit(new_rel)
```

### 8.3 Logic Consistency & Bi-Directional Sync

For UI edits that modify graph nodes, bi-directional sync ensures:

1. **UI Edit** → User modifies `control.description` in web UI
2. **PostgreSQL Audit Log** → Action logged with `reasoning_trace`
3. **Memgraph Update** → Node updated atomically
4. **Langfuse Trace** → Full prompt/output captured for compliance
5. **Feedback Loop** → If SHACL fails, UI shows error with specific shape violation

**Constraints enforced at sync boundary:**
- No modifying `/source-regulations/` (Read-Only Zone)
- No direct `/production-graph/` writes without validation
- All agent writes scoped to designated output zones

### 8.4 Prohibited Patterns

```python
# Before committing new relationship
new_rel = create_satisfies_edge(control_id, obligation_id, mapping_type, confidence)

# Validate against SHACL shapes
validator = pySHACL.validate(graph, shacl_graph=shapes_graph)

if not validator.is_valid:
    # Quarantine for human review
    quarantine_for_review(new_rel, validator.results)
else:
    # Commit to production graph
    memgraph.commit(new_rel)
```

### 8.3 Prohibited Patterns

SHACL prevents:
- `Control` without `MITIGATED_BY` link to any `Risk` (orphan detection)
- `Obligation` with no `SATISFIES` relationship (unmitigated)
- `Evidence` without `EVIDENCED_BY` from a `Control`
- Any node with `status: active` but `valid_to` in the future

---

## 9. Workflow Orchestration (Airflow + Kafka)

### 9.1 Event-Driven Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Kafka     │────►│   Airflow   │────►│   Agents    │
│  Events     │     │   DAGs      │     │  Workers    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 9.2 Kafka Topics

| Topic | Producer | Consumer | Event Schema |
|-------|----------|----------|--------------|
| `document.ingested` | Ingestion Agent | Mapping Agent | `{"document_id": "uuid", "hash": "sha256", "framework_id": "..."}` |
| `extraction.completed` | Extraction Agent | Embedding Agent | `{"obligation_ids": ["uuid", ...], "document_id": "..."}` |
| `mapping.completed` | Mapping Agent | Gap Detection Agent | `{"mapped_pairs": [...], "gaps_detected": [...]}` |
| `gap.detected` | Mapping Agent | Alerting Agent | `{"gap_id": "uuid", "obligation_id": "uuid", "severity": "critical"}` |
| `oscal.export_requested` | UI/API | OSCAL Export Agent | `{"framework_id": "...", "output_format": "json"}` |

### 9.3 Airflow DAGs

| DAG | Trigger | Tasks |
|-----|---------|-------|
| `document_ingestion_dag` | Kafka `document.ingested` | MinIO download → MinerU parsing → Markdown validation |
| `extraction_dag` | Kafka `extraction.completed` | LLM rule extraction → LLM-as-Judge evaluation → Iterative repair |
| `embedding_dag` | Kafka `extraction.completed` | BGE-M3 dense embeddings → ColBERT token embeddings → Qdrant index |
| `graph_build_dag` | Kafka `embedding.completed` | Memgraph Cypher generation → SHACL validation → Graph commit |
| `mapping_dag` | Kafka `document.ingested` | ColBERT retrieval → LLM classification → Graph update |
| `grooming_dag` | Scheduled (daily) | Orphan detection → Path optimization → Redundancy flagging |

---

## 10. OSCAL Export Engine

### 10.1 Output Formats

| Format | Use Case | Schema |
|--------|----------|--------|
| **JSON** | CI/CD integration, API responses | NIST OSCAL 1.1.3 |
| **XML** | Legacy GRC platform imports | NIST OSCAL 1.1.3 |
| **YAML** | Human-readable documentation | NIST OSCAL 1.1.3 |

### 10.2 Supported OSCAL Components

| Component | Description | Graph Source |
|-----------|-------------|--------------|
| **SSP (System Security Plan)** | Full compliance posture | All active Controls + SATISFIES edges |
| **POA&M (Plan of Action & Milestones)** | Identified gaps | SUBSET_OF/NO_RELATIONSHIP mappings + Gap nodes |
| **SAR (Security Assessment Report)** | Control validation results | Evidence nodes + verification_status |
| **Component Definition** | Individual control spec | Single Control node + MITIGATED_BY links |

### 10.3 Export Pipeline

```python
def generate_oscal_export(framework_id: str, format: str = "json"):
    # Query graph for relevant subgraph
    controls = memgraph.query("""
        MATCH (c:Control)-[:SATISFIES]->(o:Obligation)-[:MANDATED_BY]->(r:Regulation)
        WHERE r.framework_id = $framework_id AND c.status = 'active'
        RETURN c, o, r
    """, {"framework_id": framework_id})
    
    gaps = memgraph.query("""
        MATCH (c:Control)-[rel:SATISFIES]->(o:Obligation)
        WHERE rel.mapping_type IN ('SUBSET_OF', 'NO_RELATIONSHIP')
        AND c.status = 'active'
        RETURN c, o, rel
    """)
    
    # Map to OSCAL schema
    ssp = oscal_mapper.to_ssp(controls)
    poam = oscal_mapper.to_poam(gaps)
    
    # Validate against NIST schema
    oscal_validator.validate(ssp)
    oscal_validator.validate(poam)
    
    # Export
    return export_to_format(ssp + poam, format)
```

---

## 11. Security & Data Governance

### 11.1 Access Controls

| Control Type | Implementation |
|--------------|----------------|
| **Document-Level Access** | Metadata flag `ai_input_permission: yes/no` on Document nodes |
| **Role-Based Access (RBAC)** | Framework/Control/Evidence level permissions (via PostgreSQL row-level security) |
| **Agent Write Isolation** | Filesystem-level permissions; agents scoped to designated directories |

### 11.2 Encryption

| Data State | Algorithm |
|------------|-----------|
| **At Rest** | AES-256 (PostgreSQL TDE, MinIO encryption) |
| **In Transit** | TLS 1.3 (API, Kafka, MinIO) |

### 11.3 Audit Logging

**Immutable, Append-Only Logs:**
```sql
-- PostgreSQL audit table
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY,
    actor_type VARCHAR(20),  -- 'agent' | 'user' | 'system'
    actor_id VARCHAR(255),
    action VARCHAR(100),     -- 'graph_write' | 'export' | 'query'
    resource_type VARCHAR(50),
    resource_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    reasoning_trace TEXT,    -- LLM justification for agent actions
    ip_address INET
);
```

---

## 12. Performance Requirements

### 12.1 Latency Targets

| Operation | p95 Latency | Notes |
|-----------|-------------|-------|
| Crosswalk completion (10K controls × 5K obligations) | < 10 minutes | End-to-end (ColBERT + LLM classification) |
| Compliance query (natural language) | < 5 seconds | p95; includes GraphRAG + LLM synthesis |
| OSCAL artifact generation | < 60 minutes | Full SSP for 10K controls |
| PDF → Markdown conversion | < 30 seconds | Document < 100 pages |
| Graph node query (single hop) | < 500ms | Memgraph in-memory |
| ColBERT retrieval (Top-K) | < 200ms | Qdrant |

### 12.2 Scalability Targets

| Metric | Minimum Capacity |
|--------|------------------|
| **Knowledge Graph** | 1M nodes, 5M edges |
| **Concurrent Ingestion** | 100 documents parallel processing |
| **Embedding Scaling** | Horizontal scaling via Qdrant replicas |
| **API Throughput** | 1000 RPS (FastAPI + Uvicorn workers) |

---

## 13. Accuracy Requirements

### 13.1 Mapping Classification Accuracy

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Control-to-Obligation Classification** | > 90% | Held-out benchmark set (manually annotated) |
| **Rule Extraction Preference** | > 80% | Evaluator model preference over baseline |
| **Zero Hallucinated Compliance Determinations** | 100% | All answers traceable to explicit graph path |

### 13.2 Confidence Thresholds

| Action | Confidence Threshold | System Behavior |
|--------|----------------------|-----------------|
| **Auto-commit mapping** | ≥ 0.85 | Direct graph update |
| **Human-in-the-loop review** | 0.70 – 0.85 | Queue for auditor approval |
| **Reject & flag** | < 0.70 | Discard; log failure |

---

## 14. Failure Handling & Resilience

| Failure Mode | Handling Strategy |
|--------------|-------------------|
| **PDF Parsing Error** | Retry with Marker fallback; quarantine if both fail |
| **Low-Confidence Mapping** | Flag for review; do not auto-commit |
| **LLM Failure (timeout/error)** | Retry with exponential backoff; fallback prompt |
| **SHACL Validation Failure** | Quarantine for human review |
| **Missing Graph Links** | Log; trigger re-extraction DAG |
| **Kafka Consumer Lag** | Horizontal scaling via partition rebalancing |
| **Agent Conflict (same node write)** | Optimistic locking; retry with backoff |

### 14.1 Dead-Letter Queue Pattern

Failed tasks routed to dead-letter queue for human review:
```python
try:
    agent.execute(skill)
except LowConfidenceError as e:
    dead_letter_queue.send({
        "task_id": task_id,
        "error": str(e),
        "context": e.context,
        "retry_at": datetime.now() + timedelta(hours=24)
    })
```

---

## 15. Trust, Traceability & Observability

### 15.1 Temporal "Time Machine" Memory

No graph data is manually pruned; history is sacrosanct.

- **Dual Timestamps:** Every node features `event_time` (real-world effective date) and `ingestion_time`
- **Supersession Flow:** When a regulation updates, nodes are flagged `status: superseded` and linked via `SUPERSEDES` edges
- **Auditor Time-Travel:** Auditors can request "Compliance Posture as of 2024-01-01" and the graph traverse automatically excludes invalidated edges

```cypher
// Query compliance posture as of a specific date
MATCH (c:Control)-[rel:SATISFIES]->(o:Obligation)-[:MANDATED_BY]->(r:Regulation)
WHERE c.valid_from <= $as_of_date 
  AND (c.valid_to IS NULL OR c.valid_to > $as_of_date)
  AND rel.invalidated_at IS NULL
RETURN c, rel, o, r
```

### 15.2 Langfuse Auditing & Tracing

All agent actions, LLM inputs, prompt versions, and outputs are actively logged:

| Trace Type | Example | Purpose |
|------------|---------|---------|
| `ingest-extraction` | LLM extracting rules from PDF | Prompt version tracking for compliance |
| `auto-mapper-analysis` | ColBERT + LLM classification | Reasoning trace for auditor review |
| `graph-validation` | SHACL constraint checks | Audit trail for graph integrity |
| `gap-generation` | Gap narrative creation | Evidence chain for POA&M |

**Refinement Pipeline:**
```sql
-- Poorly graded outputs feed fine-tuning
CREATE TABLE langfuse_training_feedback (
    trace_id UUID PRIMARY KEY,
    prompt_template VARCHAR(255),
    model_output TEXT,
    judge_score FLOAT,
    human_correction TEXT,
    used_for_dpo BOOLEAN DEFAULT TRUE
);
```

### 15.3 API Integrity & Audit Trail

The Integrator Service ensures an **immutable Audit Trail** is written to PostgreSQL for every write-command executed in the graph:

```sql
CREATE TABLE api_audit_log (
    log_id UUID PRIMARY KEY,
    request_id UUID,
    actor_type VARCHAR(20),  -- 'agent' | 'user' | 'system'
    actor_id VARCHAR(255),
    action VARCHAR(100),     -- 'graph_write' | 'edge_create' | 'node_update'
    resource_type VARCHAR(50),
    resource_id UUID,
    request_payload JSONB,
    response_payload JSONB,
    reasoning_trace TEXT,    -- LLM justification for agent actions
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    immutable_hash VARCHAR(64)  -- SHA-256 of entire row for tamper detection
);
```

---

## 17. Observability & Monitoring

### 17.1 Key Metrics

| Metric | Dashboard | Alert Threshold |
|--------|-----------|-----------------|
| **Extraction Accuracy** | Agent dashboard | < 80% → alert |
| **Mapping Confidence Distribution** | Compliance dashboard | Mean < 0.85 → alert |
| **Query Latency (p95)** | API dashboard | > 5s → alert |
| **Graph Growth Rate** | Operations dashboard | — |
| **Gap Detection Rate** | Risk dashboard | > 50% new gaps/month → alert |
| **Kafka Consumer Lag** | Operations dashboard | > 1000 messages → alert |

### 17.2 Tools

| Tool | Purpose |
|------|---------|
| **Prometheus** | Metrics collection |
| **Grafana** | Dashboards & alerting |
| **Langfuse** | LLM tracing & evaluation |
| **OpenTelemetry** | Distributed tracing (API, agents) |

---

## 18. Deployment Architecture

### 18.1 MVP (Single-Node)

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data

  memgraph:
    image: memgraph/memgraph-mage:latest

  qdrant:
    image: qdrant/qdrant

  minio:
    image: minio/minio
    command: server /data

  api:
    build: ./backend
    ports:
      - "8000:8000"

  airflow:
    image: apache/airflow

  kafka:
    image: confluentinc/cp-kafka
```

### 18.2 Production (Kubernetes)

| Component | Scaling Strategy |
|-----------|------------------|
| **Qdrant** | StatefulSet with 3 replicas + persistent storage |
| **Kafka** | 3-broker cluster + ZooKeeper/KRaft |
| **API Layer** | Horizontal Pod Autoscaler (CPU 70% threshold) |
| **MinIO** | Distributed mode (4+ nodes) |
| **Memgraph** | In-memory cluster (sharding) |
| **Airflow** | KubernetesExecutor + Celery |

### 18.3 Air-Gapped Support

- **All models downloaded offline** (BGE-M3, ColBERT, Mistral)
- **No external API calls** — all services self-hosted
- **Airflow DAGs run fully offline**

---

## 19. Future Enhancements (Out of Scope for MVP)

| Feature | Description | Phase |
|---------|-------------|-------|
| **Automated Regulatory Change Monitoring** | Web scraping of regulatory sources | Phase 2 |
| **Real-Time Board Dashboard** | Executive compliance posture visualization | Phase 2 |
| **External Auditor Portal Integration** | Direct API integration with auditor systems | Phase 3 |
| **Automated Remediation Workflows** | Auto-create Jira tickets for gaps | Phase 3 |
| **Multi-Language UI** | Support 84 languages for interface | Phase 2 |

---

## 20. Appendix

### 20.1 Cypher DDL Examples

```cypher
// Create indexes for query optimization
CREATE INDEX obligation_id IF NOT EXISTS FOR (o:Obligation) ON (o.obligation_id);
CREATE INDEX control_id IF NOT EXISTS FOR (c:Control) ON (c.control_id);
CREATE INDEX framework_id IF NOT EXISTS FOR (r:Regulation) ON (r.framework_id);

// Create vector index for Qdrant (via API, not Cypher)
// curl -X PUT 'qdrant:6333/collections/document_chunks' -d '{...}'

// Example temporal query
MATCH (o:Obligation)-[:SATISFIES {mapping_type: 'EQUIVALENT_TO'}]->(c:Control)
WHERE o.effective_date <= '2026-04-12'
  AND (c.valid_to IS NULL OR c.valid_to > '2026-04-12')
RETURN o, c
```

### 20.2 ColBERT Configuration

```python
# ColBERT model configuration
colbert_config = {
    "doc_len": 512,
    "query_len": 64,
    "dim": 128,
    "nbits": 8,  # Quantization for index size reduction
    "maxmar": 16,  # MaxSim aggregation window
}

# Qdrant collection configuration
qdrant_config = {
    "collection_name": "colbert_controls",
    "vector_size": 128,
    "distance": "Cosine",
    "hnsw_config": {
        "m": 16,
        "ef_construct": 100,
    },
}
```

### 20.3 Sample Skill File (regulatory-ingest.md)

```markdown
---
name: regulatory-ingest
version: 1.0
description: De Jure pipeline for regulatory PDF ingestion
trigger: document.ingested
required_agents: [ingestion_agent, extraction_agent, embedding_agent]
write_zones: [/ingestion-queue/, /audit-logs/]
read_zones: [/source-regulations/]
confidence_threshold: 0.85
escalation_on: [parsing_failure, extraction_failure, low_confidence]
---

# Regulatory Document Ingestion Skill

## Objective
Transform raw regulatory PDFs into graph-ready obligation nodes via the De Jure pipeline.

## Steps

### Step 1: Document Validation
1. Download document from MinIO using `document_id`
2. Compute SHA-256 hash — compare against existing documents (deduplication)
3. Extract metadata: `framework_id`, `version`, `effective_date`, `language`

### Step 2: PDF → Markdown Conversion
1. Attempt MinerU conversion
2. If MinerU fails (layout error > 10%), fallback to Marker
3. Validate heading hierarchy (H1 → H6) — must be contiguous

### Step 3: Semantic Decomposition
1. Extract atomic rule units via LLM:
   ```python
   prompt = """
   Extract atomic obligations from this regulatory text.
   Output JSON array of {{rule_text, clause_ref, obligation_type}}.
   """
   ```
2. Score each extraction on metadata accuracy (LLM-as-Judge)
3. Retry failed extractions with upstream context

### Step 4: Graph Ingestion
1. Create Obligation nodes in Memgraph
2. Create DERIVED_FROM edges to Document nodes
3. Queue for embedding generation (BGE-M3 + ColBERT)

## Acceptance Criteria
- Zero loss of heading hierarchy
- Extraction preference > 80% in evaluator assessments
- All obligations have `clause_ref` and `obligation_type` populated
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-21 | Initial Draft | Foundation architecture |
| 2.0 | 2026-01-15 | Tech Review | ColBERT + Memgraph finalized |
| 3.0 | 2026-02-28 | Architecture Synthesis | Agentic orchestration added |
| 4.0 | 2026-04-12 | Claude Code | Full synthesis with agent governance |
| 4.1 | 2026-04-12 | Claude Code | Added Three-Layer Vault, LLM-as-Judge, Canonical YAML, Facet schema, OSCAL Reconciliation Agent, Langfuse integration details, expanded node/edge schemas with Residual Risk Score, Logic/Technical Judge layers |

---

**END OF DOCUMENT**
