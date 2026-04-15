# Technical Requirements Document
## Risk and Control Knowledge Graph (RCKG) Platform
### End-State Architecture Edition — Version 6.0

| Field | Value |
|---|---|
| **Document Version** | 6.0 — End-State Architecture |
| **Classification** | Internal — Confidential |
| **Status** | APPROVED — REVISION 1 |
| **Issued** | 2026-04-12 |
| **Author** | Senior AI Architecture Synthesis |
| **Predecessor Docs** | TRD v5.0 (Master Synthesis) · TRD v4.0-A/B (Agentic GraphRAG + Master Design Blueprint) |
| **Review Cycle** | Quarterly |
| **Next Review Date** | 2026-07-12 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [End-State Architecture Overview](#2-end-state-architecture-overview)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Technology Stack](#4-technology-stack)
5. [Knowledge Graph Schema & Ontology Design](#5-knowledge-graph-schema--ontology-design)
6. [Data Architecture — Three-Layer PostgreSQL Vault](#6-data-architecture--three-layer-postgresql-vault)
7. [Ingestion Pipeline — High Fidelity De Jure Extraction](#7-ingestion-pipeline--high-fidelity-de-jure-extraction)
8. [Compliance Crosswalk Engine — High-Precision Mapping](#8-compliance-crosswalk-engine--high-precision-mapping)
9. [Agentic Orchestration Layer — Temporal + Kafka](#9-agentic-orchestration-layer---temporal--kafka)
10. [GraphRAG Query Architecture](#10-graphrag-query-architecture)
11. [Security, Governance & Data Management](#11-security-governance--data-management)
12. [SHACL Constraint Validation & Graph Integrity](#12-shacl-constraint-validation--graph-integrity)
13. [OSCAL Export Engine](#13-oscal-export-engine)
14. [Performance, Accuracy & Quality Requirements](#14-performance-accuracy--quality-requirements)
15. [Testing & Quality Assurance Framework](#15-testing--quality-assurance-framework)
16. [Observability & Monitoring](#16-observability--monitoring)
17. [Failure Handling & Resilience](#17-failure-handling--resilience)
18. [Deployment Architecture — Demo & Production](#18-deployment-architecture---demo--production)
19. [Workflow Orchestration — Temporal Workflows + Kafka Events](#19-workflow-orchestration---temporal-workflows--kafka-events)
20. [HITL & Training Data Pipeline](#20-hitl--training-data-pipeline)
21. [Implementation Timeline](#21-implementation-timeline)
22. [Document History & Revision Control](#22-document-history--revision-control)

---

## 1. Executive Summary

The **Risk and Control Knowledge Graph (RCKG) Platform** is an AI-native, high-fidelity compliance intelligence system that deterministically transforms regulatory obligations into a continuously maintained, temporally-aware knowledge graph. This document is the authoritative synthesis of two predecessor technical designs (v4.0-A and v4.0-B), augmented with current best practices in knowledge graph ontology design, compliance traceability, and agentic AI governance.

RCKG addresses a fundamental failure mode in traditional GRC tooling: the inability to provide machine-readable, audit-grade traceability from a regulatory clause to the exact control, policy, evidence artefact, and risk vector that satisfies it. It achieves this through **four architectural pillars**:

- **High Fidelity Ingestion** — Zero-loss document parsing with semantic decomposition into atomic rule units via the De Jure pipeline.
- **High Precision Mapping** — >90% classification accuracy using ColBERT late-interaction retrieval combined with formal set-theory classification.
- **Completeness & Coverage** — Multi-framework convergence with quantified coverage metrics, gap lifecycle tracking, and MECE (Mutually Exclusive, Collectively Exhaustive) output reporting.
- **End-to-End Traceability** — Bitemporal graph modelling with full provenance chains from clause reference through to evidence artefact hash, queryable at any historical date.

### 1.1 Design Principles

| Principle | Specification | Non-Negotiable? |
|---|---|---|
| **Graph as System of Truth** | Property graph manages semantic topology; RDBMS serves only as audit vault and staging layer. | YES |
| **LLM as Assistive, Not Authoritative** | LLMs execute bounded extraction and classification tasks. Multi-hop compliance conclusions derive exclusively from explicit graph paths. | YES |
| **Strictly Self-Hosted** | 100% open-source stack; air-gapped capable; zero external API dependencies. | YES |
| **Bitemporal Persistence** | All facts carry `valid_from` / `valid_to` (event time) + `ingested_at` (system time). No hard deletes ever. | YES |
| **Deterministic Outputs** | Every compliance decision traceable to an explicit graph path + source document page reference. | YES |
| **Dual-Judge Validation** | All AI-generated mappings independently audited by a Logic Judge (semantic) and a Technical Judge (precision) before graph commit. | YES |
| **OSCAL-Native Export** | All compliance artefacts exportable as NIST OSCAL 1.1.3 JSON/XML/YAML with embedded provenance metadata. | YES |
| **MECE Coverage Reporting** | Gap reports are Mutually Exclusive, Collectively Exhaustive — no obligation is double-counted or omitted. | YES |

---

## 2. Comparative Analysis of Predecessor Documents

### 2.1 Strengths Carried Forward from Each Document

| Dimension | TRD v4.0-A (Agentic GraphRAG) | TRD v4.0-B (Master Design Blueprint) |
|---|---|---|
| Specification Depth | Build-ready: code samples, Cypher DDL, Kafka topic schemas, Airflow DAG definitions | Conceptually clear; stronger narrative for stakeholder communication |
| Agent Governance | Comprehensive `agents.md` + `skills.md` model with filesystem-level isolation | Brain-and-Muscle metaphor; MECE output requirement |
| Evaluation Model | LLM-as-Judge for extraction scoring | **Dual-Judge (Logic + Technical) with DPO/RLHF fine-tuning loop — SUPERIOR; incorporated** |
| Graph Schema | Complete node/edge schema with temporal properties and SHACL shapes | **ControlGroup / ControlObjective hierarchy more granular — INCORPORATED** |
| Observability | Full Prometheus + Grafana + Langfuse + OpenTelemetry stack | Langfuse audit tracing of prompt versions and agent actions |
| Failure Handling | Dead-letter queue, exponential backoff, quarantine pattern | Not specified |
| Deployment | Docker Compose MVP + Kubernetes production architecture | Not specified |
| OSCAL Integration | OSCAL Export Agent with SSP/POA&M/SAR generation | **OSCAL Reconciliation Agent for NIST catalog backfill — SUPERIOR; incorporated** |

### 2.2 Critical Gaps Identified in Both Documents — Resolved in v5.0

| Gap Category | Description | Resolution in This Document |
|---|---|---|
| **Ontology Design** | Neither document defined a formal ontology namespace, derivation rules, or alignment to standard ontologies. | Section 5 introduces a formal RCKG Ontology with derivation rules and alignment to PROV-O, OSCAL, and schema.org. |
| **Completeness Metrics** | No quantified coverage metric beyond per-mapping classification. No framework-level coverage score. | Section 8.5 introduces a Coverage Score Model with per-framework and aggregate metrics. |
| **Gap Lifecycle** | Gap nodes created but no lifecycle defined. | Section 5.3 defines a full Gap lifecycle state machine: OPEN → IN_REMEDIATION → REMEDIATED → VERIFIED → CLOSED. |
| **Control Effectiveness** | Mapping only — no runtime control effectiveness scoring. | Section 5.2 adds `ControlEffectiveness` node and `TESTED_BY` edge. |
| **Third-Party / Vendor Risk** | No third-party nodes in graph schema. | Section 5.2 adds `ThirdParty` node with `VENDOR_OF` and `ASSESSED_BY` edges. |
| **ESG Risk Dimension** | Neither document addressed ESG as a risk dimension. | Section 5.2 adds `esg_dimension` tag to Risk nodes. |
| **Testing Pyramid** | No test specification beyond accuracy metrics. | Section 15 defines a full testing pyramid: unit, integration, E2E, and adversarial. |
| **Data Retention Policy** | No retention schedule defined. | Section 11.3 specifies retention policy per data tier. |
| **OSCAL Provenance** | OSCAL exports lacked confidence scores, mapping rationale, and responsible-party fields per the NIST OSCAL Mapping Model spec. | Section 13.3 adds full OSCAL provenance metadata. |
| **Regulatory Change Monitoring** | Deferred to Phase 2 in both documents with no specification. | Section 20.2 provides a detailed Phase 2 specification. |

---

## 3. System Architecture Overview

### 3.1 High-Level Architecture — Six-Module Pipeline

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             RCKG Platform v5.0                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  M1  Document Ingestion Pipeline                                              │
│      PDF → MinerU/Marker → Markdown → De Jure Extraction → Bronze/Silver/Gold│
│                              ▼                                                │
│  M2  Knowledge Graph Engine                                                   │
│      Memgraph (Graph) · Qdrant (Vector) · PostgreSQL (Vault) · MinIO (Blobs) │
│                              ▲                                                │
│  M3  Agentic Orchestration Layer                                              │
│      agents.md (Governance) · skills.md (Declarative Workflows) · Kafka      │
│                              ▼                                                │
│  M4  Compliance Crosswalk Engine                                              │
│      ColBERT (Late Interaction) · BGE-M3 (Dense) · Set-Theory Classification  │
│                              ▼                                                │
│  M5  GraphRAG Query Interface                                                 │
│      Hybrid Retrieval · Multi-Hop Graph Traversal · Grounded LLM Synthesis    │
│                              ▼                                                │
│  M6  OSCAL Export & GRC Integration                                           │
│      NIST OSCAL 1.1.3 (JSON/XML/YAML) · ServiceNow · MetricStream APIs        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Module | Name | Primary Function | Key Technologies |
|---|---|---|---|
| M1 | Document Ingestion Pipeline | Transform raw regulatory PDFs into structured, validated obligation nodes | MinerU, Marker, spaCy, Pydantic |
| M2 | Knowledge Graph Engine | Persist, version, and query the semantic compliance fabric | Memgraph, Qdrant, PostgreSQL 16, MinIO |
| M3 | Agentic Orchestration Layer | Govern autonomous agent workflows with declarative boundaries | agents.md, skills.md, Temporal, Kafka |
| M4 | Compliance Crosswalk Engine | Map obligations to controls at token-level with set-theory classification | ColBERTv2.0, BGE-M3, LLM Classifier, pySHACL |
| M5 | GraphRAG Query Interface | Answer compliance queries grounded exclusively in graph context | Qdrant, Memgraph traversal, LLM Synthesis |
| M6 | OSCAL Export & GRC Integration | Emit machine-readable compliance artefacts for GRC platforms and auditors | NIST OSCAL 1.1.3, ServiceNow, MetricStream APIs |

### 3.2 Data Flow & Quality Gate Architecture

Data flows unidirectionally through three mandatory quality checkpoints. No module may write to the production graph without passing all three:

| Checkpoint | Name | Criterion | Failure Action |
|---|---|---|---|
| **CP-1** | Extraction Gate | Rule unit passes LLM-as-Judge evaluation ≥ 0.80 | Iterative repair → dead-letter queue |
| **CP-2** | Mapping Gate | Obligation-to-Control mapping passes Dual-Judge validation AND SHACL constraint check | Quarantine → human review |
| **CP-3** | Graph Commit Gate | Gold-tier record exists in PostgreSQL before any Memgraph write | Reject write → data integrity alert |

> ⚠️ **CRITICAL INVARIANT:** The Memgraph **hot layer** MUST at all times be a strict subset of validated Gold-tier records in PostgreSQL. The **cold layer** (PostgreSQL) holds all historical data with full bitemporal integrity. Any divergence constitutes a data integrity incident requiring immediate investigation.

### 3.3 Hot/Cold Graph Separation

To ensure long-term scalability while maintaining bitemporal audit integrity, the graph is split into two layers:

| Layer | Technology | Data Type | Size Limit | Retention |
|---|---|---|---|---|
| **HOT** | Memgraph (in-memory) | Active obligations (last 90 days), current control mappings, open/in-remediation Gaps | 32GB RAM | Archived monthly to cold layer |
| **COLD** | PostgreSQL (disk-based) | Superseded regulations, historical mapping states, closed/accepted Gaps, full audit trail | 90TB+ | 10 years minimum (regulatory requirement) |

**Archival Process (Monthly):**
1. Identify nodes with `valid_to` set (superseded or closed)
2. Export to PostgreSQL cold store with full bitemporal properties
3. Remove from Memgraph hot layer (soft delete only)
4. Maintain referential integrity via `gold_record_id` FK in PostgreSQL

> 📊 **Query Performance Impact:** Active compliance queries run against Memgraph (<500ms). Historical queries are directed to PostgreSQL cold store (~2-5 seconds). Both layers are transparent to end users via unified query API.

---

## 4. Technology Stack

### 4.1 Core Infrastructure

| Component | Technology | Version | Justification |
|---|---|---|---|
| Containerization (Demo) | Docker + Docker Compose | Latest stable | Rapid single-node deployment for demo/POC |
| Containerization (Production) | Kubernetes | 1.30+ | Horizontal scaling, StatefulSets for datastores |
| API Framework | FastAPI (Python) | 3.11+ | Async, auto OpenAPI spec, high throughput |
| Workflow Engine | Temporal.io | 1.6+ | **Event-driven, stateful workflow orchestration** for agentic workflows, HITL approval gates, and scheduled batch jobs. Durability, checkpointing, pause/resume support. |
| Message Queue | Apache Kafka | 3.7+ | **Event bus for high-throughput pipelines** — document ingestion events, workflow triggers, audit event streaming. |
| Secret Management | HashiCorp Vault | Latest | Credential rotation, policy-based access |

### 4.2 Storage Layer

| Purpose | Technology | Role in Architecture |
|---|---|---|
| Graph Database (Hot Layer) | Memgraph (in-memory) | **Active graph only** — current obligations, active controls, open gaps. 32GB RAM limit. Monthly archival to cold layer. |
| Graph Database (Cold Layer) | PostgreSQL 16 | **Historical graph data** — superseded regulations, historical states, closed gaps. 90TB+ storage. 10-year retention. |
| Vector Database (Precision Matcher) | Qdrant | Multi-vector ColBERT (SQ8 quantized) + dense BGE-M3 embeddings. Payload filtering for faceted retrieval. 200GB+ storage. |
| Relational Database (The Vault) | PostgreSQL 16 | Bronze/Silver/Gold staging layers, immutable audit log, OSCAL export cache. Source of ground truth for graph projection. |
| Object Storage | MinIO (S3-compatible) | Raw PDFs, Markdown conversions, evidence artefacts. SHA-256 addressed. WORM policy on `source-regulations` bucket. |
| Cache Layer | Redis 7 | Query result caching (TTL 300s), rate-limit counters, session state for multi-step agent tasks. |

### 4.3 AI/ML Stack

| Function | Technology | Configuration / Notes |
|---|---|---|
| PDF → Markdown (Primary) | MinerU | Complex layouts, tables, multi-column. Fallback to Marker if layout error >10%. |
| PDF → Markdown (Fallback) | Marker | Standard single-column regulatory docs. |
| Dense Embeddings | BAAI BGE-M3 | 1024-dim, 84-language, multilingual regulatory support. |
| Token-Level Embeddings | ColBERTv2.0 | 128-dim per token. Multi-vector Qdrant collection. Precomputed offline for all control descriptions. |
| Reranker | BAAI BGE-Reranker-V2-M3 | Top-K refinement post-retrieval. Applied after ColBERT MaxSim. |
| LLM Inference — Extraction | Llama 3.1 8B / Mistral 7B | JSON-mode extraction. Served via vLLM (production) or Ollama (dev). |
| LLM — Logic Judge | Llama 3.1 70B (quantized) | Semantic faithfulness evaluation. Score < 0.95 triggers human intervention. |
| LLM — Technical Judge | DeepSeek-R1 / Qwen2.5-72B | Mathematical and technical precision audit. Requires 100% exact match for parametric facts. |
| Graph Constraint Validation | pySHACL | SHACL shapes enforce schema topology before every graph commit. |
| LLM Observability | Langfuse (self-hosted) | Prompt version tracking, span tracing, evaluation scoring, fine-tune dataset curation. |

---

## 5. Knowledge Graph Schema & Ontology Design

> **DESIGN PRINCIPLE:** The RCKG ontology follows a data-centric approach — formal ontology derivation begins from the PostgreSQL relational schema (stable), then is projected upward into the graph. This eliminates the need for complex ontology-merging pipelines when new documents are ingested.

### 5.1 Ontology Namespace & Alignment

RCKG aligns to the following established ontologies to ensure interoperability:

| Standard Ontology | Alignment Purpose | Key Concepts Borrowed |
|---|---|---|
| PROV-O (W3C Provenance Ontology) | Data lineage and derivation tracing | `prov:wasDerivedFrom`, `prov:wasGeneratedBy`, `prov:Entity` |
| NIST OSCAL Mapping Model | Control mapping set-theory classification | `equivalent-to`, `subset-of`, `superset-of`, `intersects-with`, `no-relationship`, `confidence`, `provenance` |
| schema.org | Base entity typing for interoperability | `schema:Thing`, `schema:Action`, `schema:CreativeWork` |
| Dublin Core (DCMI) | Document metadata | `dc:title`, `dc:version`, `dc:date`, `dc:source`, `dc:language` |

### 5.2 Node Types — Complete Schema

All nodes carry mandatory **bitemporal properties**: `valid_from`, `valid_to` (NULL = active), `ingested_at`, `updated_at`, `status`, `version_seq`, and `created_by`.

| Node Label | Description | Key Properties | Ontology Alignment |
|---|---|---|---|
| `Regulation` | Regulatory framework or authority document | `framework_id`, `name`, `jurisdiction`, `version`, `effective_date`, `legal_base`, `language`, `ai_input_permission` | `schema:CreativeWork` |
| `ControlGroup` | High-level domain grouping (e.g. "Access Control") | `group_id`, `title`, `parent_framework_id`, `domain_tag` | `schema:DefinedTerm` |
| `ControlObjective` | High-level intent / "Why" layer of a requirement | `objective_id`, `text`, `impact_category`, `obligation_type`, `clause_ref` | `schema:Goal` |
| `Obligation` | Atomic, discrete rule unit — the "What" layer extracted by De Jure pipeline | `obligation_id`, `text`, `clause_ref`, `action_verb`, `subject_noun`, `effective_date`, `obligation_strength` (SHALL/SHOULD/MAY) | `prov:Entity` |
| `Control` | Internal corporate control that mitigates risk or satisfies obligations | `control_id`, `name`, `description`, `owner`, `status`, `frequency`, `implementation_method`, `control_function`, `control_goals[]`, `asset_scope[]` | `schema:Action` |
| `ControlEffectiveness` | Runtime effectiveness record for a control (test result) | `effectiveness_id`, `test_date`, `result` (pass/fail/partial), `tester_id`, `score` (0–1), `evidence_ref` | `prov:Activity` |
| `Risk` | Operational, cyber, or compliance risk vector | `risk_id`, `name`, `category`, `subcategory`, `likelihood` (1–5), `impact` (1–5), `inherent_score`, `residual_score`, `esg_dimension` (E/S/G/null) | `schema:Thing` |
| `Policy` | Internal corporate policy document | `policy_id`, `name`, `version`, `owner`, `effective_date`, `approved_by` | `schema:CreativeWork` |
| `Evidence` | Audit proof artefact linked to a control | `evidence_id`, `type`, `date`, `artifact_path`, `hash` (SHA-256), `verification_status`, `collected_by` | `prov:Entity` |
| `Document` | Source document ingested into the system | `document_id`, `filename`, `hash`, `ingested_at`, `language`, `framework_id`, `page_count`, `ai_input_permission` | `schema:DigitalDocument` |
| `Gap` | Identified compliance gap — obligation not fully satisfied | `gap_id`, `description`, `severity` (critical/high/medium/low), `lifecycle_state`, `created_at`, `target_remediation_date`, `owner` | `schema:Action` |
| `ThirdParty` | Vendor or supplier subject to third-party risk assessment | `party_id`, `name`, `category`, `country`, `criticality_tier` (1–3), `last_assessed` | `schema:Organization` |
| `Framework` | Compliance framework (ISO, NIST, DORA, GDPR) | `framework_id`, `name`, `version`, `domain`, `publisher`, `effective_date` | `schema:DefinedTermSet` |

### 5.3 Gap Node Lifecycle State Machine

Every `Gap` node transitions through the following states. Transitions are append-only events in the audit log; the `lifecycle_state` field is updated in-place.

```
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │  [SUBSET_OF / NO_RELATIONSHIP mapping detected]             │
  │                      ▼                                       │
  │                   OPEN ──────────────────────► ACCEPTED      │
  │                      │                         (risk accepted│
  │                      │ owner assigned            by auth.)   │
  │                      ▼                              │        │
  │              IN_REMEDIATION ◄────────────────────── │        │
  │                      │  (re-test fails)         on review    │
  │                      │ owner attests fix        date         │
  │                      ▼                                       │
  │                REMEDIATED                                    │
  │                      │  (Technical Judge                     │
  │                      │   re-mapping passes)                  │
  │                      ▼                                       │
  │                 VERIFIED                                     │
  │                      │  (auditor sign-off)                   │
  │                      ▼                                       │
  │                  CLOSED ◄─ Terminal state                    │
  └──────────────────────────────────────────────────────────────┘
```

| State | Trigger | Required Fields | Next Allowed States |
|---|---|---|---|
| `OPEN` | SUBSET_OF or NO_RELATIONSHIP mapping detected | `gap_id`, `obligation_id`, `severity`, `description`, `created_at` | IN_REMEDIATION, ACCEPTED |
| `IN_REMEDIATION` | Owner assigned and remediation plan approved | + `owner`, `target_remediation_date`, `remediation_plan` | REMEDIATED, OPEN (plan rejected) |
| `REMEDIATED` | Owner attests control has been updated/deployed | + `remediated_at`, `remediation_evidence_ref` | VERIFIED, IN_REMEDIATION (re-test fails) |
| `VERIFIED` | Technical Judge confirms re-mapping yields SUPERSET_OF or EQUIVALENT_TO | + `verified_at`, `verified_by`, `re_mapping_confidence` | CLOSED |
| `CLOSED` | Audit sign-off received | + `closed_at`, `auditor_id` | Terminal — no further transitions |
| `ACCEPTED` | Risk formally accepted by authorised owner | + `accepted_at`, `accepted_by`, `acceptance_rationale`, `review_date` | OPEN (on review date) |

### 5.4 Relationship Types — Edge Schema

| Edge Label | Source → Target | Key Edge Properties | Semantics |
|---|---|---|---|
| `MANDATED_BY` | Obligation → Regulation | `clause_ref`, `page_ref`, `section_path` | Links obligation to source regulatory document |
| `BELONGS_TO_GROUP` | ControlObjective → ControlGroup | — | Hierarchical grouping within framework |
| `DECOMPOSES_TO` | ControlObjective → Obligation | `decomposition_method` | One objective produces N atomic obligations |
| `SATISFIES` | Control → Obligation | `mapping_type`, `confidence_score`, `reasoning`, `logic_judge_score`, `tech_judge_score`, `mapped_at`, `mapped_by` | **Core crosswalk edge** — carries full set-theory classification |
| `HAS_GAP` | Obligation → Gap | `gap_id`, `created_at` | Links unmitigated obligation to its Gap node |
| `MITIGATED_BY` | Risk → Control | `mitigation_type` (full/partial) | Control addresses risk vector |
| `EVIDENCED_BY` | Control → Evidence | `date`, `verification_status`, `collection_method` | Links control to audit proof artefact |
| `GOVERNED_BY` | Control → Policy | `version` | Authorising policy for the control |
| `TESTED_BY` | Control → ControlEffectiveness | `test_cycle` | Links control to its effectiveness test record |
| `SUPERSEDES` | Regulation → Regulation | `effective_date`, `reason` | Temporal version relationship — old node retained |
| `DERIVED_FROM` | Obligation → Document | `page_ref`, `section_path`, `chunk_id` | PROV-O provenance to source PDF |
| `SATISFIES_VIA` | Control → Framework | `coverage_score` | Aggregated framework-level satisfaction record |
| `VENDOR_OF` | ThirdParty → Control | `contract_ref` | Vendor provides or manages this control |
| `ASSESSED_BY` | ThirdParty → Evidence | `assessment_date`, `assessor_id` | Third-party assessment evidence link |
| `BELONGS_TO` | Node → Framework | — | Generic framework membership |

### 5.5 Bitemporal Data Model

Every node and edge implements **dual timestamps** (Allen's Interval Algebra), enabling point-in-time compliance reconstruction for any historical date:

| Property | Dimension | Description | Nullable? |
|---|---|---|---|
| `valid_from` | Event Time | When the fact became active in the real world | NO |
| `valid_to` | Event Time | When the fact became inactive. NULL = currently active. | YES (NULL = active) |
| `ingested_at` | System Time | When RCKG first recorded this fact. Immutable after creation. | NO |
| `updated_at` | System Time | Last time any property on this node was modified. | NO |
| `status` | Lifecycle | `active` \| `superseded` \| `invalidated` \| `draft` | NO |
| `version_seq` | Versioning | Monotonically increasing integer; incremented on any property update. | NO |

```cypher
-- Example: Reconstruct compliance posture as of a specific historical date
MATCH (c:Control)-[rel:SATISFIES]->(o:Obligation)-[:MANDATED_BY]->(r:Regulation)
WHERE r.framework_id = $framework_id
  AND c.valid_from <= $as_of_date
  AND (c.valid_to IS NULL OR c.valid_to > $as_of_date)
  AND rel.valid_from <= $as_of_date
  AND (rel.valid_to IS NULL OR rel.valid_to > $as_of_date)
RETURN c, rel, o, r
```

> 🚫 **NO HARD DELETES:** Bitemporal integrity is enforced at the application layer. Both the PostgreSQL vault and Memgraph graph operate in append-only mode for all compliance-relevant data. Agents that attempt hard deletes outside approved write zones are logged and blocked.

---

## 6. Data Architecture — Three-Layer PostgreSQL Vault

All data flows through a **Bronze → Silver → Gold** quality pipeline before being projected to the Memgraph knowledge graph.

### 6.1 Bronze Layer — Raw Immutable Storage

**Table:** `staging_controls` | **Purpose:** Immutable record of raw ingestion. No transformations. Hash-based deduplication.

| Field | Type | Description | Constraints |
|---|---|---|---|
| `uuid` | UUID | Unique document identifier | PRIMARY KEY |
| `canonical_id` | VARCHAR(255) | Framework-specific ID (e.g. 'DORA-Art11-2') | NOT NULL |
| `raw_file_content` | JSONB | Complete raw text from PDF/CSV extraction | NOT NULL |
| `hash` | VARCHAR(64) | SHA-256 of raw content for deduplication | UNIQUE |
| `source_url` | TEXT | Origin URL or filesystem path | NULLABLE |
| `ingested_at` | TIMESTAMPTZ | Ingestion timestamp | DEFAULT NOW() |
| `ingestion_agent_id` | VARCHAR(128) | Agent that performed ingestion | NOT NULL |

### 6.2 Silver Layer — Semantic Refinery

**Table:** `semantic_controls` | **Purpose:** AI-extracted structure with semantic facets. Enables powerful graph queries.

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Silver record identifier |
| `bronze_id` | UUID | FK to staging_controls |
| `framework_name` | VARCHAR(128) | e.g. 'NIST CSF', 'DORA', 'ISO 27001' |
| `group_id` | VARCHAR(64) | Control group (e.g. 'AC', 'PR', 'DE') |
| `objective_text` | TEXT | High-level intent (Blue Header / ControlObjective) |
| `statement_text` | TEXT | Atomic rule statement text |
| `action_verb` | VARCHAR(64) | Extracted deontic verb: SHALL / SHOULD / MUST / MAY |
| `obligation_strength` | VARCHAR(16) | Mandatory / Recommended / Permissive |
| `subject_noun` | VARCHAR(255) | Who must comply: 'organization', 'financial institution' |
| `control_function` | VARCHAR(32) | Preventive \| Detective \| Corrective \| Compensating |
| `implementation_method` | VARCHAR(32) | Automated \| Manual \| Hybrid |
| `control_goals` | TEXT[] | CIA triad: Confidentiality, Integrity, Availability |
| `asset_scope` | TEXT[] | Systems, people, data in scope |
| `gov_domain` | VARCHAR(128) | e.g. 'access-control', 'data-protection', 'incident-response' |
| `legal_base` | VARCHAR(255) | Jurisdictional legal authority |
| `clause_ref` | VARCHAR(128) | e.g. 'DORA Article 11(2)(a)' |
| `extraction_score` | FLOAT | LLM-as-Judge extraction quality score (0–1) |
| `extracted_at` | TIMESTAMPTZ | When AI extraction ran |
| `extraction_model` | VARCHAR(128) | Model ID used for extraction |

### 6.3 Gold Layer — Validated Records

**Table:** `golden_controls` | **Purpose:** Dual-Judge validated data. Only Gold records are projected to Memgraph.

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Gold record identifier — becomes Obligation node ID in Memgraph |
| `silver_record_id` | UUID | FK to semantic_controls |
| `logic_judge_score` | FLOAT | Semantic faithfulness score from Logic Judge (0–1). Must be ≥ 0.95. |
| `tech_judge_score` | FLOAT | Technical precision score from Technical Judge (0–1). Must be 1.0 for parametric facts. |
| `aggregate_confidence` | FLOAT | Weighted aggregate: `(logic_score × 0.6) + (tech_score × 0.4)` |
| `validated_at` | TIMESTAMPTZ | When validation completed |
| `validated_by` | VARCHAR(255) | Agent ID or human auditor LDAP ID |
| `validation_method` | VARCHAR(32) | `auto-dual-judge` \| `human-review` \| `human-override` |
| `status` | VARCHAR(32) | `draft` \| `validated` \| `superseded` |
| `oscal_reconciled` | BOOLEAN | Whether OSCAL Reconciliation Agent has backfilled NIST parameters |
| `oscal_param_id` | VARCHAR(128) | Corresponding NIST OSCAL catalog parameter ID if applicable |

### 6.4 Canonical YAML Ingestion Schema

All external adapters MUST output to this schema before staging into the Bronze layer. Structural validation via Pydantic v2 is enforced at the adapter boundary.

```yaml
metadata:
  title: "NIST Cybersecurity Framework"
  version: "2.0"
  publication_date: "2024-02-01"
  jurisdiction: "US"
  legal_base: "Executive Order 14028"
  language: "en"

control-groups:
  - id: "GV"
    title: "Govern"
    objectives:
      - id: "GV.OC"
        title: "Organizational Context"
        prose: "The circumstances surrounding the organization's cybersecurity risk management..."
        statements:
          - id: "GV.OC-01"
            prose: "The organizational mission is understood and informs cybersecurity risk management."
            metadata:
              action_verb: "is understood"
              subject_noun: "organizational mission"
              obligation_strength: "SHALL"
              control_function: "preventive"
              implementation_method: "hybrid"
              control_goals: ["integrity", "availability"]
              asset_scope: ["organization"]
              gov_domain: "governance"
```

---

## 7. Ingestion Pipeline — High Fidelity De Jure Extraction

### 7.1 Pipeline Overview

```
Raw PDF (MinIO)
      │
      ▼  Stage 1: Validation & Deduplication
SHA-256 hash check → skip if duplicate → Bronze write
      │
      ▼  Stage 2: PDF → Markdown Conversion
MinerU (primary) → Marker (fallback) → Structured MD
      │
      ▼  Stage 3: Hybrid Context Chunking
Header-first → Semantic cosine fallback (threshold > 0.75)
      │
      ▼  Stage 4: De Jure Rule Unit Extraction
LLM extraction → LLM-as-Judge evaluation → Iterative repair → Silver write
      │
      ▼  Stage 5: Dual-Judge Validation & Gold Promotion
Logic Judge (≥ 0.95) + Technical Judge (100% parametric) → Gold write → Memgraph projection
```

### 7.2 Stage 2: Chunking Rules (Non-Negotiable)

- **NO character-based chunking** under any circumstance. Legal clauses may not be split at character boundaries.
- **Header-first:** Where clear Markdown headers exist (H1–H6), the chunk boundary is the header. The chunk inherits the full breadcrumb as `section_path`.
- **Semantic fallback:** Where headers are absent, BGE-M3 cosine distance is computed between adjacent sentences. Distance >0.75 triggers a chunk boundary.
- **Maximum chunk size:** 512 tokens for ColBERT indexing. Larger chunks are sub-split at sentence boundaries.
- **Overlap:** 50-token overlap between adjacent chunks to prevent context loss at boundaries.

```python
# Chunking Logic
if section_has_clear_header:
    chunk = header_based_chunk(section)
    chunk.metadata["section_path"] = "Article 11 > Section 3 > (a)"
else:
    sentences = spacy_split(section.text)
    chunks = semantic_split(sentences, threshold=0.75)  # BGE-M3 cosine distance

# Enforce max size
for chunk in chunks:
    if chunk.token_count > 512:
        chunk = sub_split_at_sentence_boundary(chunk, max_tokens=512, overlap=50)
```

### 7.3 Stage 4: De Jure Extraction

The following sub-phases (4.1–4.4) are internal steps within Stage 4:

| Phase | Operation | Model | Failure Mode |
|---|---|---|---|
| 4.1 | Normalization — validate Markdown structural fidelity and heading contiguity | Deterministic (rule-based) | Quarantine document; notify Ingestion Agent |
| 4.2 | Semantic Decomposition — LLM extracts atomic rule units as JSON arrays | Llama 3.1 8B (JSON mode) | Retry with upstream context (max 3 attempts); escalate to human if all fail |
| 4.3 | LLM-as-Judge Evaluation — score each extraction on metadata accuracy, legal definition alignment, and rule semantics completeness | Llama 3.1 70B | Score <0.80 → trigger Phase 4.4 |
| 4.4 | Iterative Repair — low-scoring extractions reprocessed with full clause context + adjacent section | Llama 3.1 8B with expanded context | After 2 repair attempts → dead-letter queue; human review |

Minimum required fields per extracted rule unit:
```json
{
  "rule_text": "Financial institutions shall maintain...",
  "clause_ref": "DORA Article 11(2)(a)",
  "obligation_type": "technical_requirement",
  "action_verb": "shall",
  "obligation_strength": "SHALL",
  "subject_noun": "financial institutions",
  "effective_date": "2025-01-17",
  "jurisdiction": "EU"
}
```

### 7.4 Stage 5: Dual-Judge Validation

| Judge | Model | Evaluates | Threshold | Failure Action |
|---|---|---|---|---|
| **Logic Judge** | Llama 3.1 70B (quantized) | Semantic faithfulness: intent captured? action verb correct? obligation strength accurate? | Score ≥ 0.95 | Reject; trigger repair; if 2nd attempt fails → human queue |
| **Technical Judge** | DeepSeek-R1 or Qwen2.5-72B | Mathematical precision: parametric facts exact? (e.g. '4 hours', 'annual' = 365 days) | 100% exact match on parametric fields | Reject with correction note; targeted repair of parametric fields |

> ✅ **FINE-TUNING LOOP:** Records rejected by either judge are automatically curated into a DPO/RLHF fine-tuning dataset in Langfuse. The extraction model is retrained monthly on this signal to continuously elevate baseline quality.

---

## 8. Compliance Crosswalk Engine — High-Precision Mapping

### 8.1 ColBERT Late-Interaction Retrieval

ColBERT solves the precision-vs-speed trade-off by maintaining token-level embeddings while enabling efficient MaxSim scoring. Every control description is decomposed into a vector per token (128 dimensions), stored as a multi-vector payload in Qdrant.

```
Offline (Indexing):
  Control descriptions → ColBERT tokenizer → [token_emb_1 ... token_emb_N]
  → Stored as multi-vector payload in Qdrant collection: colbert_controls

Online (Query):
  Obligation text → ColBERT tokenizer → [token_emb_1 ... token_emb_M]
  → MaxSim scoring: max(sim(q_i, d_j)) for each query token i across all doc tokens j
  → Top-50 candidates → BGE-M3 reranker → Top-10 for LLM classification
```

```python
# Step 1: Indexing (offline)
for control in graph.query("MATCH (c:Control) RETURN c.control_id, c.description"):
    token_embeddings = colbert_model.encode(control.description)
    qdrant.upsert(
        collection_name="colbert_controls",
        points=[{"id": control.control_id, "vectors": token_embeddings}]
    )

# Step 2: Query (online)
obligation_tokens = colbert_model.encode(obligation.text)
candidates = qdrant.search(
    collection_name="colbert_controls",
    query_vector=obligation_tokens,
    limit=50,
    search_params={"hnsw_ef": 128}
)

# Step 3: BGE-M3 reranking → Top-10
top_10 = bge_reranker.rerank(obligation.text, candidates[:50])[:10]
```

### 8.2 Set-Theory Classification Model

Following the **NIST OSCAL control mapping model specification**, classifications are expressed as formal set-theory relationships:

| Classification | Formal Semantics | OSCAL Alignment | System Action | Agent Escalation? |
|---|---|---|---|---|
| `EQUIVALENT_TO` | Control A = Obligation B: full 1:1 semantic coverage | `equivalent-to` | Auto-satisfy obligation; no Gap node created | NO |
| `SUPERSET_OF` | Control A ⊃ Obligation B: control exceeds requirement | `superset-of` | Auto-satisfy; log excess coverage for optimisation | NO |
| `SUBSET_OF` | Control A ⊂ Obligation B: partial coverage only | `subset-of` | **CRITICAL:** Auto-create Gap node; severity derived from obligation_strength; flag in POA&M | NO (automated) |
| `INTERSECTS_WITH` | Control A ∩ Obligation B ≠ ∅ but A ≠ B: overlapping but divergent | `intersects-with` | **HALT:** route to human review queue with `divergence_notes` | YES — mandatory |
| `NO_RELATIONSHIP` | Control A ∩ Obligation B = ∅: no semantic overlap | `no-relationship` | **CRITICAL ALERT:** unmitigated risk; Gap node severity=CRITICAL; notify risk owner | YES — immediate |

```python
# LLM Classification Prompt
classification_prompt = """
Given:
  Obligation: "{obligation_text}"
  Control:    "{control_text}"

Classify the set-theory relationship between the Control and the Obligation.
Use exactly one of these values:
  - EQUIVALENT_TO   : Full 1-to-1 semantic coverage
  - SUPERSET_OF     : Control exceeds the regulatory requirement
  - SUBSET_OF       : Control partially addresses the requirement (gap exists)
  - INTERSECTS_WITH : Overlapping but with divergent goals (human review needed)
  - NO_RELATIONSHIP : Control has no coverage of the obligation

Output JSON only:
{{
  "mapping_type": "...",
  "confidence": 0.XX,
  "reasoning": "..."
}}
"""
```

### 8.3 Graph Update — SATISFIES Edge Creation

```cypher
-- Commit SATISFIES edge with full provenance metadata
MATCH (o:Obligation {obligation_id: $obligation_id})
MATCH (c:Control {control_id: $control_id})
MERGE (c)-[rel:SATISFIES {
  mapping_type:       $mapping_type,
  confidence_score:   $confidence,
  reasoning:          $reasoning,
  logic_judge_score:  $logic_score,
  tech_judge_score:   $tech_score,
  mapped_at:          datetime(),
  mapped_by:          $agent_id,
  valid_from:         datetime(),
  valid_to:           null,
  status:             'active'
}]->(o)

-- Auto-create Gap node for SUBSET_OF mappings
FOREACH (x IN CASE WHEN $mapping_type = 'SUBSET_OF' THEN [1] ELSE [] END |
  CREATE (g:Gap {
    gap_id:           randomUUID(),
    severity:         $derived_severity,
    lifecycle_state:  'OPEN',
    description:      $gap_narrative,
    created_at:       datetime(),
    obligation_id:    $obligation_id
  })
  CREATE (o)-[:HAS_GAP]->(g)
)
```

### 8.4 Multi-Framework Convergence

When a Control satisfies an Obligation in Framework A, the system automatically identifies semantically equivalent Obligations in Frameworks B, C, D and creates provisional `SATISFIES` edges for confirmation. This eliminates duplicate evidence collection across frameworks.

```cypher
-- Find crosswalk candidates after a confirmed SATISFIES edge
MATCH (o1:Obligation {obligation_id: $confirmed_obligation_id})
MATCH (o2:Obligation)
WHERE o2.obligation_id <> o1.obligation_id
  AND NOT (c)-[:SATISFIES]->(o2)
  AND qdrant_similarity(o1.obligation_id, o2.obligation_id) > 0.88
CREATE (c)-[:SATISFIES {
  mapping_type:    'PROVISIONAL',
  source_crosswalk: $confirmed_obligation_id,
  status:          'draft'
}]->(o2)
```

### 8.5 Coverage Score Model — Completeness Metrics

For every Framework in the graph, the following metrics are maintained in real-time and exposed via the compliance dashboard:

| Metric | Formula | Target | Alert Threshold |
|---|---|---|---|
| **Framework Coverage Score** | (# Obligations with SUPERSET_OF or EQUIVALENT_TO) / (# Total Obligations) | ≥ 85% | < 70% → Critical alert |
| **Partial Coverage Rate** | (# Obligations with SUBSET_OF) / (# Total Obligations) | < 10% | > 20% → High alert |
| **Unmitigated Rate** | (# Obligations with NO_RELATIONSHIP) / (# Total Obligations) | **0%** | > 0% → Critical alert; immediate escalation |
| **Pending Review Rate** | (# INTERSECTS_WITH pending human review) / (# Total mappings) | < 5% | > 15% → Operational alert |
| **Mapping Confidence Mean** | Mean(confidence_score) across all SATISFIES edges | ≥ 0.87 | < 0.82 → Quality alert |
| **Gap Remediation Rate** | (# Gaps in VERIFIED or CLOSED) / (# Total Gaps) | ≥ 60% within 90 days | < 40% at 60 days → Escalate to CISO |

---

## 9. Agentic Orchestration Layer

### 9.1 Governance Model — `agents.md`

All autonomous agents operate under strict declarative governance defined in the root `agents.md` file. This file is version-controlled, reviewed quarterly, and its contents override any in-context instructions an agent may receive.

#### Write Zones & Access Policy

| Zone Type | Path / Resource | Agent Access |
|---|---|---|
| READ-ONLY (Protected) | `/source-regulations/` | Read only. WORM bucket policy in MinIO. |
| READ-ONLY (Protected) | `/production-graph/` (Memgraph) | Query only. No direct Cypher writes without Gold record FK validation. |
| READ-ONLY (Protected) | `/audit-findings/` | Append-only. No modifications. |
| WRITE (Permitted) | `/ingestion-queue/` | Write pending documents. |
| WRITE (Permitted) | `/audit-logs/` | Append-only. Agent action logs. |
| WRITE (Permitted) | `/oscal-exports/` | Generated OSCAL artefacts. |
| WRITE (Permitted) | `/gap-reports/` | Draft status only. Require human promotion to final. |

#### Mandatory Escalation Triggers

Agents **MUST HALT** and notify human reviewers when:
- Mapping confidence score < **0.85** after dual-judge evaluation
- Obligation has `NO_RELATIONSHIP` to any Control (unmitigated risk)
- `INTERSECTS_WITH` classification detected (divergent intent)
- SHACL constraint validation fails on proposed graph write
- Logic Judge score < **0.95** after two repair attempts
- Agent action count exceeds **500** in a single skill execution (runaway detection)

### 9.2 Agent Swarm Roles

| Agent | Role | Primary Responsibility | Write Zones |
|---|---|---|---|
| **Ingestion Agent** | Muscle | De Jure pipeline; populates Bronze → Silver PostgreSQL layers | `/ingestion-queue/`, Postgres Bronze/Silver |
| **OSCAL Reconciliation Agent** | Muscle | Backfills NIST OSCAL catalog parameters into Silver records | Postgres Silver (`oscal_param_id` field) |
| **Dual-Judge Validation Agent** | Brain | Logic + Technical Judge evaluation; Gold promotion; fine-tune curation | Postgres Gold |
| **Crosswalk (Mapping) Agent** | Muscle | ColBERT retrieval; LLM classification; SATISFIES edge commit; Gap node creation | Memgraph (via Gold FK), `/gap-reports/` |
| **Grooming Agent (The Gardener)** | Muscle | Orphan detection; redundant node consolidation; SHACL re-validation | Memgraph (merge ops only) |
| **Gap Detection & Monitoring Agent** | Muscle | Coverage score recomputation; threshold breach alerts | `/gap-reports/` |
| **RAG / Audit Agent** | Muscle | GraphRAG query answering grounded exclusively in graph context | `/audit-logs/` |
| **OSCAL Export Agent** | Muscle | Compile validated subgraphs into NIST OSCAL SSP/POA&M/SAR | `/oscal-exports/` |

### 9.3 Declarative Skill Files — Progressive Disclosure Pattern

| Disclosure Level | Content | Size | Trigger |
|---|---|---|---|
| **Level 1 (Discovery)** | Metadata header: name, version, description, trigger, required_agents, write_zones, confidence_threshold | ~100 tokens | Always loaded at agent startup |
| **Level 2 (Activation)** | Full instruction body with stepwise procedure, decision trees, and error handling | < 5,000 tokens | Semantic match to skill trigger keyword |
| **Level 3 (Execution)** | On-demand scripts and reference documents from `/scripts/` and `/references/` | Variable | Step-specific invocation during execution |

```yaml
# Example Skill Header: dora-gap-analysis.md
---
name: dora-gap-analysis
version: 1.1
description: Automated DORA Article 11 ICT risk gap analysis with MECE output
trigger: dora-ict-gap
required_agents: [crosswalk_agent, dual_judge_agent, reporting_agent]
write_zones: [/gap-reports/, /oscal-exports/]
read_zones: [/source-regulations/dora/, /production-graph/]
confidence_threshold: 0.85
escalation_on: [low_confidence, no_relationship, shacl_failure, intersects_with]
mece_required: true
---
```

---

## 10. GraphRAG Query Architecture

### 10.1 Zero-Hallucination Guarantee

The RAG/Audit Agent operates under an absolute constraint: every statement in a query response must be traceable to an explicit graph path in the Memgraph production graph.

> 🚫 **ANTI-HALLUCINATION ENFORCEMENT:** If the graph context is insufficient, the agent MUST respond with `"Insufficient graph context — cannot answer without hallucination"`. All answers pass an inline hallucination detector before returning to the user. Failed answers are quarantined and logged.

### 10.2 Hybrid Retrieval — Four Stages

| Stage | Operation | Technology | Output |
|---|---|---|---|
| 1 | Dense vector search — encode query; retrieve Top-20 semantically similar chunks | Qdrant + BGE-M3 | Top-20 candidate chunk IDs |
| 2 | ColBERT re-ranking — MaxSim re-rank Top-20 for token-level precision | Qdrant ColBERT multi-vector | Top-10 refined candidates |
| 3 | Graph traversal expansion — 1–3 hop traversal for each candidate; pull related Controls, Evidence, Policies, Risks, Gaps | Memgraph Cypher with bitemporal filter | Bounded subgraph (max 50 nodes) |
| 4 | Grounded LLM synthesis — serialise subgraph; generate answer exclusively from context | LLM (Llama 3.1 8B / Mistral 7B) | Answer + source paths + evidence refs + confidence |

```python
def graphrag_query(user_query: str, as_of_date: datetime | None = None) -> dict:
    # Stage 1: Dense retrieval
    query_embedding = bge_m3.encode(user_query)
    top_chunks = qdrant.search("document_chunks", query_embedding, top_k=20)

    # Stage 2: ColBERT re-rank
    top_10 = colbert_reranker.rerank(user_query, top_chunks)[:10]

    # Stage 3: Graph traversal
    candidate_ids = [c.payload["obligation_id"] for c in top_10]
    subgraph = memgraph.query("""
        MATCH (o:Obligation)-[rel:SATISFIES*1..3]-(c:Control)
        WHERE o.obligation_id IN $ids
          AND ($as_of_date IS NULL
               OR (c.valid_from <= $as_of_date
                   AND (c.valid_to IS NULL OR c.valid_to > $as_of_date)))
        OPTIONAL MATCH (c)-[:EVIDENCED_BY]->(e:Evidence)
        OPTIONAL MATCH (o)-[:DERIVED_FROM]->(d:Document)
        RETURN o, rel, c, e, d
    """, {"ids": candidate_ids, "as_of_date": as_of_date})

    # Stage 4: Grounded synthesis
    context = serialize_subgraph(subgraph)
    answer = llm.generate(
        prompt=f"""Answer ONLY using the graph context below. 
        If context is insufficient, state "Insufficient graph context — cannot answer without hallucination."
        Do not use any external knowledge.

        Graph Context:
        {context}

        User Query: {user_query}"""
    )

    return {
        "answer": answer,
        "source_nodes": extract_node_ids(subgraph),
        "edge_paths": extract_cypher_paths(subgraph),
        "evidence_refs": extract_evidence_ids(subgraph),
        "document_lineage": extract_lineage(subgraph),
        "as_of_date": as_of_date,
        "confidence_score": compute_confidence(subgraph),
        "hallucination_flag": hallucination_detector.check(answer, context)
    }
```

### 10.3 Traceability Contract — Mandatory Query Response Fields

| Response Field | Type | Required? |
|---|---|---|
| `answer` | String | YES |
| `source_nodes` | UUID[] | YES — exact Obligation and Control IDs |
| `edge_paths` | String[] | YES — traversal paths as Cypher patterns |
| `evidence_refs` | UUID[] | YES — Evidence node IDs |
| `document_lineage` | Object[] | YES — `{document_id, page_ref, section_path}` per source node |
| `as_of_date` | ISO8601 | YES |
| `confidence_score` | Float (0–1) | YES |
| `hallucination_flag` | Boolean | YES |
| `query_latency_ms` | Integer | YES |

---

## 11. Security, Governance & Data Management

### 11.1 Access Control Architecture

| Control Type | Implementation | Scope |
|---|---|---|
| Document-Level Access | `ai_input_permission` flag on Document nodes; enforced in Qdrant payload filter and Memgraph WHERE clauses | Per-document privacy control |
| Role-Based Access (RBAC) | PostgreSQL row-level security (RLS) per role: `compliance_admin`, `compliance_auditor`, `risk_owner`, `read_only` | All relational data |
| Graph RBAC | Memgraph role bindings: `graph_admin`, `graph_writer`, `graph_reader`. `graph_writer` requires Gold FK validation. | Memgraph production graph |
| Agent Write Isolation | Filesystem permissions + Kafka ACLs; each agent scoped to declared `write_zones` in `agents.md` | All agent operations |
| Secret Management | All credentials in HashiCorp Vault; rotated every 90 days | All service-to-service auth |
| Network Segmentation | Agents communicate via internal Kafka bus only; external egress blocked in air-gapped mode | All agent network traffic |

### 11.2 Encryption

| Data State | Algorithm | Key Management |
|---|---|---|
| At Rest — PostgreSQL | AES-256 (TDE) | HashiCorp Vault KMS |
| At Rest — MinIO | AES-256 SSE-S3 | MinIO KMS + Vault integration |
| At Rest — Memgraph | AES-256 encrypted persistence volume | Kubernetes Sealed Secrets |
| In Transit — All services | TLS 1.3 minimum | Cert-Manager (K8s) / Internal CA (air-gapped) |
| Kafka | TLS 1.3 + SASL/SCRAM-SHA-512 | Vault PKI secrets engine |

### 11.3 Data Retention Policy

| Data Tier | Retention Period | Deletion Method | Legal Hold Override |
|---|---|---|---|
| Bronze Layer (Raw) | 7 years | Logical delete flag (immutable for legal hold) | YES |
| Silver Layer (Semantic) | 7 years | Logical delete flag | YES |
| Gold Layer (Validated) | 10 years (regulatory minimum) | No deletion permitted; `superseded` status only | YES |
| Memgraph (Production Graph) | Indefinite (bitemporal) | No hard deletes. `status=invalidated` only. | N/A |
| Audit Logs | 10 years | Append-only; no deletion mechanism exposed | YES |
| OSCAL Exports | 7 years | Archived to cold MinIO tier after 1 year | YES |
| Evidence Artefacts | 7 years after control retirement | Archived to cold MinIO tier after 3 years | YES |
| Langfuse Traces | 2 years | Auto-purge after retention period | YES |

### 11.4 Immutable Audit Log Schema

```sql
-- Append-only; protected by RLS (INSERT only; no UPDATE or DELETE)
CREATE TABLE audit_log (
    log_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_type       VARCHAR(20) NOT NULL,    -- 'agent' | 'human' | 'system'
    actor_id         VARCHAR(255) NOT NULL,
    action           VARCHAR(100) NOT NULL,   -- 'graph_write' | 'graph_query' | 'export' | 'map' | 'validate' | 'escalate'
    resource_type    VARCHAR(50),             -- 'Obligation' | 'Control' | 'Gap' | 'Edge' | 'Evidence'
    resource_id      UUID,
    timestamp        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reasoning_trace  TEXT,                    -- Full LLM justification (JSON) for agent actions
    ip_address       INET,
    session_id       UUID,
    skill_id         VARCHAR(128),            -- Skill file that triggered this action (agents only)
    confidence_score FLOAT                    -- Confidence at time of action (agents only)
);

-- Row-level security: enforce append-only
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_insert_only ON audit_log FOR INSERT WITH CHECK (true);
CREATE POLICY audit_no_update ON audit_log FOR UPDATE USING (false);
CREATE POLICY audit_no_delete ON audit_log FOR DELETE USING (false);
```

---

## 12. SHACL Constraint Validation & Graph Integrity

### 12.1 Core SHACL Shapes

| Shape Name | Target | Constraint | Failure Consequence |
|---|---|---|---|
| `ControlSatisfiesObligationShape` | SATISFIES edges | `mapping_type` must be one of five enumerated values; `confidence_score` must be 0.0–1.0; both judge scores must be present | Quarantine; human review |
| `ObligationCompletenessShape` | Obligation nodes | Every Obligation must have at least one SATISFIES edge OR one HAS_GAP edge. Orphan Obligations (neither) are forbidden. | Alert; trigger re-mapping DAG |
| `ControlOrphanShape` | Control nodes | Every Control must have at least one MITIGATED_BY inbound from a Risk node, OR a documented exception. | Flag as orphan; Grooming Agent review |
| `EvidenceIntegrityShape` | Evidence nodes | Every Evidence node must have exactly one EVIDENCED_BY inbound from a Control node. | Quarantine evidence; alert |
| `GapLifecycleShape` | Gap nodes | `lifecycle_state` must be one of: OPEN, IN_REMEDIATION, REMEDIATED, VERIFIED, CLOSED, ACCEPTED. | Reject graph write |
| `BitemporalIntegrityShape` | All nodes | `valid_from` must not be NULL. `valid_to`, if present, must be > `valid_from`. `status` must be valid enum. | Reject graph write |
| `GoldFKShape` | All graph writes | The `gold_record_id` property on every Obligation node must reference an existing UUID in `golden_controls`. | Reject graph write; data integrity breach |

```turtle
# SHACL Shape Example: Obligation completeness
:ObligationCompletenessShape
    a sh:NodeShape ;
    sh:targetClass :Obligation ;
    sh:or (
        [ sh:property [ sh:path :SATISFIES ; sh:minCount 1 ] ]
        [ sh:property [ sh:path :HAS_GAP   ; sh:minCount 1 ] ]
    ) ;
    sh:message "Every Obligation must have at least one SATISFIES or HAS_GAP relationship." .

# SHACL Shape Example: SATISFIES edge validation
:SatisfiesEdgeShape
    a sh:NodeShape ;
    sh:targetClass :SatisfiesRelationship ;
    sh:property [
        sh:path :mapping_type ;
        sh:in ("EQUIVALENT_TO" "SUPERSET_OF" "SUBSET_OF" "INTERSECTS_WITH" "NO_RELATIONSHIP") ;
    ] ;
    sh:property [
        sh:path :confidence_score ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
    ] .
```

> 🚫 **PROHIBITED GRAPH PATTERNS:** (1) Control without MITIGATED_BY link to any Risk (unless exception documented). (2) Obligation with no SATISFIES and no HAS_GAP relationship. (3) Evidence without EVIDENCED_BY from a Control. (4) Any node with `status=active` and `valid_to` set to a past date.

---

## 13. OSCAL Export Engine

### 13.1 Supported OSCAL Artefact Types (NIST OSCAL 1.1.3)

| OSCAL Artefact | Description | Graph Source | Format Support |
|---|---|---|---|
| System Security Plan (SSP) | Full compliance posture of a system | Active Controls + EQUIVALENT_TO/SUPERSET_OF SATISFIES edges + Evidence nodes | JSON, XML, YAML |
| Plan of Action & Milestones (POA&M) | Identified gaps and remediation plans | SUBSET_OF/NO_RELATIONSHIP mappings + Gap nodes in OPEN/IN_REMEDIATION state | JSON, XML, YAML |
| Security Assessment Report (SAR) | Control validation test results | ControlEffectiveness nodes + Evidence + TESTED_BY edges | JSON, XML, YAML |
| Component Definition | Individual control component specification | Single Control node + MITIGATED_BY Risk + GOVERNED_BY Policy | JSON, XML, YAML |
| Control Mapping | Framework crosswalk with set-theory provenance | All SATISFIES edges with mapping_type, confidence_score, clause_ref | JSON, XML, YAML |

### 13.2 OSCAL Provenance Metadata

Per the **NIST OSCAL control mapping model specification**, every exported mapping item includes the following provenance fields:

| OSCAL Provenance Field | Source in RCKG Graph | Description |
|---|---|---|
| `matching-rationale` | `SATISFIES.reasoning` | LLM-generated natural language explanation of the mapping decision |
| `confidence-score` | `SATISFIES.confidence_score` | Numeric confidence (0.0–1.0) in the mapping classification |
| `mapping-status` | `SATISFIES.mapping_type` | One of: equivalent-to, superset-of, subset-of, intersects-with, no-relationship |
| `responsible-party` | `SATISFIES.mapped_by` | Agent ID or human auditor who created/confirmed the mapping |
| `mapping-date` | `SATISFIES.mapped_at` | ISO 8601 timestamp of mapping creation |
| `incompatibility-description` | `Gap.description` | Gap narrative explaining what is missing from the control |

```python
def generate_oscal_ssp(framework_id: str, as_of_date: datetime = None) -> dict:
    # Query active controls and their satisfied obligations
    controls = memgraph.query("""
        MATCH (c:Control)-[rel:SATISFIES]->(o:Obligation)-[:MANDATED_BY]->(r:Regulation)
        WHERE r.framework_id = $framework_id
          AND rel.mapping_type IN ['EQUIVALENT_TO', 'SUPERSET_OF']
          AND c.status = 'active'
        OPTIONAL MATCH (c)-[:EVIDENCED_BY]->(e:Evidence)
        RETURN c, rel, o, r, collect(e) as evidence
    """, {"framework_id": framework_id})

    # Build OSCAL SSP with embedded provenance
    ssp = {
        "system-security-plan": {
            "metadata": build_oscal_metadata(framework_id),
            "control-implementation": {
                "implemented-requirements": [
                    {
                        "control-id": row.o.clause_ref,
                        "implementation-status": {"state": "implemented"},
                        "mapping": {
                            "matching-rationale": row.rel.reasoning,
                            "confidence-score":   row.rel.confidence_score,
                            "mapping-status":     row.rel.mapping_type.lower().replace("_", "-"),
                            "responsible-party":  row.rel.mapped_by,
                            "mapping-date":       row.rel.mapped_at.isoformat()
                        }
                    }
                    for row in controls
                ]
            }
        }
    }

    # Validate against NIST OSCAL 1.1.3 schema
    oscal_validator.validate(ssp, schema_version="1.1.3")
    return ssp
```

---

## 14. Performance, Accuracy & Quality Requirements

### 14.1 Latency Targets

| Operation | p50 Target | p95 Target | Measurement Point |
|---|---|---|---|
| Natural language compliance query (GraphRAG) | < 2 seconds | < 5 seconds | API gateway response time |
| Crosswalk completion (10K controls × 5K obligations) | < 8 minutes | < 12 minutes | Temporal `mapping_workflow` task duration |
| OSCAL SSP generation (10K controls) | < 30 minutes | < 60 minutes | OSCAL Export Agent task duration |
| PDF → Markdown conversion (< 100 pages) | < 15 seconds | < 30 seconds | Ingestion pipeline Stage 2 |
| Single obligation mapping (ColBERT + LLM) | < 3 seconds | < 8 seconds | Crosswalk Agent per-pair latency |
| Graph node query — single hop | < 100ms | < 500ms | Memgraph query executor |
| ColBERT retrieval — Top-50 | < 80ms | < 200ms | Qdrant query endpoint |
| Graph build (1M nodes, 5M edges) | < 4 hours | < 6 hours | Full graph build DAG |

### 14.2 Accuracy Requirements

| Metric | Target | Measurement Method | Alert Threshold |
|---|---|---|---|
| Control-to-Obligation Classification Accuracy | > 90% | Held-out benchmark of 1,000 manually annotated pairs; evaluated monthly | < 85% → halt auto-commit; mandatory model review |
| Rule Extraction Preference Rate | > 80% | Evaluator model preference over zero-shot baseline | < 75% → trigger DPO fine-tuning cycle immediately |
| Zero Hallucinated Compliance Determinations | 100% | All query responses pass hallucination detector; monthly sample audit | Any hallucination detected → incident; system audit |
| Dual-Judge Agreement Rate | > 95% | % of records where both judges pass on first attempt | < 90% → model quality review |
| SHACL Validation Pass Rate | > 99.9% | % of proposed graph writes passing all SHACL shapes on first submission | < 99% → immediate schema review |
| False Positive Gap Rate | < 5% | % of Gap nodes subsequently reclassified as EQUIVALENT_TO/SUPERSET_OF | > 10% → mapping model review |

### 14.3 Confidence Threshold Matrix

| Confidence Score Range | System Behaviour | Human Review Required? | Graph Action |
|---|---|---|---|
| ≥ 0.92 | High confidence — auto-commit | NO | Direct SATISFIES edge commit to Memgraph |
| 0.85 – 0.91 | Acceptable — auto-commit with enhanced logging | NO (async audit sample) | Commit with `elevated_monitoring` flag |
| 0.70 – 0.84 | Low confidence — queue for review | YES — within 72 hours | Provisional edge (status=draft); not counted in coverage score |
| < 0.70 | Reject — discard; log failure | YES — immediate | No edge created; dead-letter queue; re-extraction triggered |

### 14.4 Scalability Targets

| Metric | MVP Target | Production Target |
|---|---|---|
| Knowledge Graph Nodes | 100K nodes, 500K edges | 5M nodes, 25M edges |
| Concurrent Document Ingestion | 10 documents parallel | 100 documents parallel |
| API Throughput | 100 RPS | 1,000 RPS (FastAPI + Uvicorn workers) |
| Frameworks Supported | 5 (NIST CSF, ISO 27001, DORA, GDPR, SOC 2) | Unlimited (adapter pattern) |
| Qdrant Collection Size | 1M vectors | 50M+ vectors (horizontal sharding) |
| Concurrent Users (Query) | 10 concurrent | 500 concurrent |

---

## 15. Testing & Quality Assurance Framework

| Test Level | Scope | Tools | Frequency | Pass Threshold |
|---|---|---|---|---|
| **Unit Tests** | Individual functions: chunking logic, ColBERT scoring, SHACL shape evaluation, bitemporal query filters | pytest, hypothesis (property-based) | Every commit (CI) | > 95% coverage; 0 critical failures |
| **Integration Tests** | Pipeline stage-to-stage: Bronze→Silver→Gold promotion; SHACL pipeline; Kafka routing; Temporal workflow execution | pytest + testcontainers | Every PR merge | 100% workflow tasks complete; 0 data loss |
| **Accuracy Tests (LLM)** | Mapping accuracy on held-out benchmark of 1,000 annotated pairs across 5 frameworks | Custom evaluator harness + LLM-as-Judge | Weekly | > 90% classification accuracy |
| **End-to-End Tests** | Full pipeline: PDF ingestion → rule extraction → crosswalk → graph commit → GraphRAG query → OSCAL export | Playwright (API) + custom E2E harness | Pre-release | All 50 curated scenarios pass |
| **Adversarial / Red Team Tests** | Hallucination injection; SHACL bypass attempts; prompt injection via document content; orphan node creation | Custom adversarial harness; OWASP LLM Top 10 suite | Monthly | Zero successful bypasses |
| **Performance Tests** | Load test at 2× expected peak: 1,000 concurrent queries; full crosswalk under load; OSCAL export under load | k6 + Grafana | Monthly + pre-release | All p95 targets met at 2× load |
| **Regression Tests** | Re-run full benchmark after any model update, schema change, or SHACL shape modification | Full test suite replay | After any model/schema change | No accuracy regression > 2% |

---

## 16. Observability & Monitoring

### 16.1 Monitoring Stack

| Tool | Purpose | Data Collected |
|---|---|---|
| **Prometheus** | Metrics collection from all services | Request rates, error rates, latency percentiles, queue depths, model inference times |
| **Grafana** | Dashboards, alerting, and SLO tracking | Compliance coverage scores, mapping confidence distributions, gap lifecycle metrics, agent activity |
| **Langfuse** (self-hosted) | LLM observability | All LLM inputs/outputs, judge scores, prompt versions, latency per model call, fine-tune dataset curation |
| **OpenTelemetry** | Distributed tracing across all microservices | Trace IDs propagated from API ingress through all agent actions to graph commit |
| **AlertManager** | Alert routing and escalation | PagerDuty / Slack / email routing based on severity |

### 16.2 Key Metrics & Alert Thresholds

| Metric | Dashboard | Warning Threshold | Critical Threshold |
|---|---|---|---|
| Framework Coverage Score | Compliance Dashboard | < 75% | < 65% → Immediate CISO escalation |
| Unmitigated Obligations (NO_RELATIONSHIP) | Risk Dashboard | > 0 new this week | > 5 → P1 incident |
| Mapping Confidence Mean | Compliance Dashboard | < 0.85 | < 0.80 → Halt auto-commit |
| Extraction Accuracy | Agent Dashboard | < 82% | < 78% → Halt ingestion pipeline |
| Query Latency p95 | API Dashboard | > 4 seconds | > 6 seconds → Scale up RAG agents |
| Kafka Consumer Lag | Operations Dashboard | > 500 messages | > 2,000 messages → Horizontal scale |
| SHACL Validation Failures | Data Quality Dashboard | > 5 per day | > 20 per day → Schema incident |
| Dead Letter Queue Depth | Operations Dashboard | > 10 items | > 50 items → Human review backlog alert |
| New Gaps Detected (rate) | Risk Dashboard | > 30% new gaps per ingestion cycle | > 60% → Review framework coverage |
| Dual-Judge Disagreement Rate | Quality Dashboard | > 10% | > 20% → Model alignment review |

---

## 17. Failure Handling & Resilience

| Failure Mode | Detection | Primary Handling | Fallback / Escalation |
|---|---|---|---|
| PDF parsing error (MinerU) | Layout error > 10% of pages | Retry with Marker fallback parser | Quarantine to dead-letter queue; human review |
| Low-confidence extraction (< 0.80) | LLM-as-Judge score | Iterative repair with upstream context (max 2 attempts) | Dead-letter queue; 24-hour human review SLA |
| Dual-Judge disagreement | Logic score < 0.95 OR Tech mismatch | Targeted repair of specific failing field; re-evaluate | After 2 repairs → human queue; Langfuse fine-tune dataset |
| SHACL validation failure | pySHACL evaluation | Quarantine proposed write; log violation details | Human review; schema audit if systematic |
| LLM inference timeout / error | Timeout > 30s | Retry with exponential backoff (3 attempts) | Route to fallback model; log incident |
| Kafka consumer lag > 2,000 | Prometheus alert | Horizontal scale via partition rebalancing | Priority processing for critical gap events |
| Memgraph write conflict | Optimistic locking failure | Retry with jitter backoff (max 5 attempts) | Log; alert if persistent |
| Missing Gold FK on graph write | SHACL GoldFKShape | Reject write; log data integrity alert | Immediate incident; manual investigation |
| Agent runaway (> 500 actions) | Action counter per session | HALT agent; snapshot state; notify human | Restart with human confirmation |
| Vector index corruption (Qdrant) | Health check failure | Failover to replica; trigger index rebuild | Downgrade to dense-only retrieval while ColBERT rebuilds |

### 17.1 Dead-Letter Queue Schema

```sql
CREATE TABLE dead_letter_queue (
    task_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id          VARCHAR(128),
    agent_id          VARCHAR(128) NOT NULL,
    error_type        VARCHAR(64) NOT NULL,
    error_detail      TEXT,
    context_snapshot  JSONB,             -- Full agent state at time of failure
    failed_at         TIMESTAMPTZ DEFAULT NOW(),
    retry_at          TIMESTAMPTZ,
    retry_count       INTEGER DEFAULT 0,
    human_assigned_to VARCHAR(255),
    resolution_status VARCHAR(32) DEFAULT 'pending',  -- pending | in_review | resolved | escalated
    resolved_at       TIMESTAMPTZ
);
-- SLO: All items must be assigned within 24 hours of creation
```

---

## 18. Deployment Architecture — Demo & Production

### 18.1 Demo Environment — Single DGX Spark Node

**Hardware Specifications:**
| Component | Specification |
|-----------|---------------|
| **GPU** | NVIDIA Grace Blackwell (128GB unified RAM) |
| **Storage** | 4TB NVMe SSD |
| **Use Case** | Proof-of-concept, demo, internal validation, technical review |

**GPU Memory Allocation:**
| Workload | VRAM Allocation | Purpose |
|----------|-----------------|---------|
| vLLM (Llama 3.1 70B quantized) | 40% | Logic Judge + Technical Judge inference |
| ColBERT + BGE-M3 | 20% | Token-level + dense embedding retrieval |
| MinerU/Marker | 15% | On-demand PDF parsing (throttled) |
| Reserved/Burst | 25% | Query latency headroom, GPU yielding |

**Software Stack (Docker Compose):**
```yaml
# docker-compose.demo.yml — DGX Spark single-node deployment
services:
  # --- Data Layer ---
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: rckg_vault
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init/postgres:/docker-entrypoint-initdb.d
    mem_limit: 64g
  
  memgraph:
    image: memgraph/memgraph-mage:latest
    mem_limit: 32g  # Hot graph limited to 32GB
    volumes:
      - memgraph_data:/var/lib/memgraph
  
  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_storage:/qdrant/storage
    command: ["--port", "6333", "--storage", "/qdrant/storage", "--force-use-sq8"]
  
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: rckg_admin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
      MINIO_WORM: "on"
    volumes:
      - minio_data:/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 8gb --maxmemory-policy allkeys-lru
  
  # --- Application Layer ---
  api:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [postgres, memgraph, qdrant, redis, temporal]
    deploy:
      resources:
        limits:
          memory: 16G
  
  # --- Orchestration Layer ---
  temporal:
    image: temporalio/auto-setup:latest
    depends_on: [postgres]
    environment:
      TEMPORAL_DATABASE: postgres
      TEMPORAL_DB_PORT: 5432
      TEMPORAL_DATABASE_USER: rckg_admin
      TEMPORAL_DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
  
  # --- AI/LLM Layer ---
  vllm:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    volumes:
      - ./models:/models
      - ./cache:/cache
    environment:
      VLLM_MODEL: /models/llama-3.1-70b-q4_0
      VLLM_GPU_MEMORY_UTILIZATION: 0.4
      VLLMtensor_parallel_size: 1
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  # --- Observability ---
  langfuse:
    image: langfuse/langfuse:latest
    depends_on: [postgres]
  
  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    volumes:
      - grafana_data:/var/lib/grafana
  
  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - prometheus_data:/prometheus
```

### 18.2 Production Environment — Cloud Kubernetes

**Target Infrastructure (Example: AWS):**
| Component | Kubernetes Resource | Scaling Strategy | Storage |
|---|---|---|---|
| **PostgreSQL** | AWS RDS/Aurora (PostgreSQL 16) | Primary + 2 read replicas; Auto-scaling storage | 100GB–10TB+ SSD; 10-year retention |
| **Memgraph (Hot)** | EC2 r6i.8xlarge (32GB RAM) | Single instance with weekly failover | 32GB RAM limit; monthly archival |
| **Qdrant** | EC2 c6i.4xstateful + NVMe | 3-replica shard cluster; ConsistencyLevel=Majority | 200GB+ NVMe SSD per replica |
| **MinIO** | Distributed EC2 (4+ nodes) | Erasure coding; Cross-region replication | 10TB+ object storage (S3-compatible) |
| **FastAPI** | EKS Autoscaler (HPA) | CPU 70% threshold; min 5 / max 50 replicas | Stateless; ephemeral storage |
| **Temporal** | EKS deployment | Multi-AZ; PostgreSQL backend | 100GB+ PVC |
| **Kafka** | MSK (Managed Kafka) | 5-broker KRaft cluster; 7-day retention | 50GB+ SSD per broker |
| **vLLM (GPU)** | EC2 g5.2xlarge (A100 40GB) | GPU cluster with load balancing; model caching | GPU node pool; quantized models |

**GPU Cluster Specifications (Production):**
| Instance Type | GPU | VRAM | Purpose |
|---------------|-----|------|---------|
| **g5.2xlarge** | NVIDIA A100 | 40GB | Logic Judge (70B model, quantized) |
| **g5.4xlarge** | NVIDIA A100 | 80GB | Technical Judge (72B model, quantized) |
| **g5.8xlarge** | NVIDIA A100 | 160GB | Batch inference (ColBERT, BGE-M3) |

**Cloud Architecture Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    RCKG Production (AWS)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  EKS Cluster (Kubernetes)                                 │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  API Layer (FastAPI + Uvicorn)                      │ │ │
│  │  │  - HPA: 5-50 replicas                               │ │ │
│  │  │  - Auto-scaling on CPU/memory                       │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Temporal Cluster                                   │ │ │
│  │  │  - Workflow execution                               │ │ │
│  │  │  - Event sourcing + replay                          │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  GPU Worker Pool                                    │ │ │
│  │  │  - vLLM inference (A100)                            │ │ │
│  │  │  - Tiered GPU queue (High/Low priority)             │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  RDS Aurora (PostgreSQL)                                  │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Cold Store (90TB+)                                 │ │ │
│  │  │  - Superseded nodes                                 │ │ │
│  │  │  - Historical states                                │ │ │
│  │  │  - Full audit trail                                 │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  MSK (Kafka)                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Event Bus                                          │ │ │
│  │  │  - document.ingested                                │ │ │
│  │  │  - extraction.completed                             │ │ │
│  │  │  - validation.completed                             │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  S3 + Qdrant + MinIO                                      │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Vector Store (Qdrant)                              │ │ │
│  │  │  - ColBERT (SQ8 quantized)                          │ │ │
│  │  │  - BGE-M3 dense                                     │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 18.3 Air-Gapped Deployment Checklist

- [ ] All AI models pre-downloaded to MinIO: BGE-M3, ColBERTv2.0, BGE-Reranker-V2-M3, Llama 3.1 8B, Llama 3.1 70B, DeepSeek-R1
- [ ] All container images mirrored to internal registry (Harbor recommended)
- [ ] NIST OSCAL catalog downloaded and stored locally
- [ ] NIST OSCAL Reconciliation Agent configured to query local catalog copy
- [ ] All Temporal Cron workflows configured to use local Kafka brokers with no external HTTP dependencies
- [ ] Certificate authority (CA) configured for internal TLS
- [ ] HashiCorp Vault deployed internally with PKI secrets engine

---

## 19. Workflow Orchestration — Temporal Workflows + Kafka Events

### 19.1 Architecture Overview

RCKG uses a **hybrid orchestration model**:
- **Temporal.io**: Primary workflow engine for stateful, long-running, human-in-the-loop (HITL) workflows
- **Kafka**: Event bus for decoupled, high-throughput pipeline triggers

**Key Design Decisions:**
| Concern | Solution | Rationale |
|---|---|---|
| **Stateful Workflows** | Temporal | Pause/resume, replay, durability guarantees |
| **Async Eventing** | Kafka | Decoupled producers/consumers, high throughput |
| **Scheduled Batch Jobs** | Temporal (Cron Triggers) | Daily grooming, coverage scoring, gap lifecycle |
| **HITL Workflows** | Temporal Workflow + SDK | Human approval gates, timeout handling, callbacks |

### 19.2 Kafka Topic Registry

| Topic | Producer | Consumer(s) | Retention | Key Fields |
|---|---|---|---|---|
| `document.ingested` | Ingestion Agent | Temporal: `document_ingestion_workflow`, Gap Detection Agent | 7 days | `document_id`, `hash`, `framework_id`, `source_path` |
| `extraction.completed` | Ingestion Agent | Temporal: `extraction_validation_workflow`, Embedding Agent | 7 days | `obligation_ids[]`, `document_id`, `extraction_scores[]` |
| `validation.completed` | Dual-Judge Agent | Temporal: `graph_build_workflow`, Embedding Agent | 7 days | `gold_record_ids[]`, `rejected_ids[]`, `mean_confidence` |
| `embedding.completed` | Embedding Agent | Temporal: `graph_build_workflow`, Crosswalk Agent | 7 days | `obligation_ids[]`, `qdrant_collection_id` |
| `mapping.completed` | Crosswalk Agent | Temporal: `mapping_workflow`, Gap Detection Agent, Coverage Score Agent | 7 days | `mapped_pairs[]`, `gaps_detected[]`, `coverage_delta` |
| `gap.detected` | Crosswalk Agent | Alerting Agent, OSCAL Export Agent | 30 days | `gap_id`, `obligation_id`, `severity`, `framework_id` |
| `coverage.alert` | Coverage Score Agent | Alerting Agent, Dashboard Agent | 30 days | `framework_id`, `metric_name`, `current_value`, `threshold` |
| `oscal.export_requested` | UI/API | Temporal: `oscal_export_workflow` | 7 days | `framework_id`, `output_format`, `requested_by` |
| `graph.grooming_required` | Grooming Agent | Temporal: `grooming_workflow` (cron trigger) | 3 days | `orphan_node_ids[]`, `redundant_edge_ids[]` |
| `approval.callback` | HITL UI | Temporal: `human_approval_workflow` | 24 hours | `approval_id`, `decision`, `reviewer_id`, `timestamp` |

### 19.3 Temporal Workflow Registry

| Workflow ID | Input | Key Activities | Human Gates | Output |
|---|---|---|---|---|
| `document_ingestion_workflow` | `{document_id, source_path}` | 1. MinIO download<br>2. SHA-256 dedup check<br>3. MinerU parsing → Markdown<br>4. Marker fallback if confidence < 0.85<br>5. Write to Bronze | None | `bronze_record_id`, `parse_confidence` |
| `extraction_validation_workflow` | `{bronze_record_id}` | 1. Hybrid chunking (Markdown headers + semantic split)<br>2. De Jure LLM extraction (Mistral 8B)<br>3. LLM-as-Judge extraction quality check<br>4. Iterative repair loop (max 3 retries) | `review_required` if confidence < 0.70 | `silver_record_id[]`, `review_queue_ids[]` |
| `dual_judge_validation_workflow` | `{silver_record_ids[]}` | 1. Logic Judge (Llama 3.1 70B): semantic faithfulness score<br>2. Technical Judge (DeepSeek-R1 72B): technical/mathematical accuracy<br>3. Aggregate scoring with weighted mean<br>4. Gold promotion OR dead-letter queue | `hitl_review` if Logic Score < 0.95 OR Technical Score < 1.0 | `gold_record_ids[]`, `dlq_record_ids[]` |
| `oscal_reconciliation_workflow` | `{gold_record_ids[]}` | 1. Query local NIST OSCAL catalog (PostgreSQL)<br>2. Backfill missing `oscal_param_id` fields<br>3. Update Silver records<br>4. Re-promote to Gold if improved | None | `updated_gold_ids[]`, `missing_param_alerts[]` |
| `embedding_workflow` | `{gold_record_ids[]}` | 1. BGE-M3 dense embeddings<br>2. ColBERTv2.0 token-level embeddings<br>3. Qdrant index update (upsert)<br>4. Index health validation | None | `qdrant_collection_id`, `embedding_count` |
| `graph_build_workflow` | `{embedding_completed_id}` | 1. Cypher node/edge generation from Gold<br>2. SHACL validation against shape library<br>3. Gold FK check against PostgreSQL<br>4. Memgraph commit with bitemporal tags | None | `memgraph_node_count`, `validation_errors[]` |
| `mapping_workflow` | `{obligation_id, candidate_control_ids[]}` | 1. ColBERT MaxSim retrieval (top-20 candidates)<br>2. BGE-Reranker-V2-M3 re-ranking (top-5)<br>3. LLM classification: EQUIVALENT/SUPERSET/SUBSET/INTERSECTS/NO_RELATIONSHIP<br>4. Dual-Judge verification<br>5. Create SATISFIES edge + Gap node if SUBSET/NO_RELATIONSHIP | `low_confidence` if LLM score < 0.85 | `satisfies_edge_id`, `gap_node_id?` |
| `oscal_export_workflow` | `{framework_id, output_format}` | 1. Graph traversal: Control → Obligations → Evidence<br>2. Map to OSCAL 1.1.3 schema<br>3. Generate JSON/Markdown report<br>4. Store in MinIO + link to Graph node | None | `oscal_file_url`, `validation_status` |
| `human_approval_workflow` | `{approval_id, request_type}` | 1. Wait for HITL callback (poll Temporal signal)<br>2. Evaluate decision (approve/reject/modify)<br>3. Apply changes to Graph/PostgreSQL<br>4. Trigger downstream workflows | **Signal: `submission_received`**<br>**Signal: `approval_callback`** | `approval_record_id`, `workflow_resume_id` |

### 19.4 Temporal Workflow Implementation Example (Python SDK)

```python
from temporalio import workflow
from temporalio.worker import Worker
from typing import List, Dict

@workflow.defn
class DocumentIngestionWorkflow:
    @workflow.run
    async def run(self, document_id: str, source_path: str) -> Dict:
        # Activity: Download from MinIO
        file_bytes = await workflow.execute_activity(
            "minio_download_activity",
            args=[source_path],
            start_to_close_timeout=workflow.timedelta(minutes=5)
        )
        
        # Activity: SHA-256 dedup check
        existing_hash = await workflow.execute_activity(
            "sha256_dedup_check_activity",
            args=[file_bytes],
            start_to_close_timeout=workflow.timedelta(minutes=1)
        )
        
        if existing_hash:
            return {"status": "duplicate", "bronze_record_id": existing_hash}
        
        # Activity: MinerU parsing
        markdown_content = await workflow.execute_activity(
            "mineru_parse_activity",
            args=[file_bytes],
            start_to_close_timeout=workflow.timedelta(minutes=10)
        )
        
        # Activity: Write to Bronze
        bronze_id = await workflow.execute_activity(
            "write_bronze_activity",
            args=[document_id, markdown_content],
            start_to_close_timeout=workflow.timedelta(minutes=2)
        )
        
        # Signal downstream: extraction workflow
        await workflow.execute_activity(
            "publish_kafka_activity",
            args=["extraction.completed", {"bronze_record_id": bronze_id}],
            start_to_close_timeout=workflow.timedelta(minutes=1)
        )
        
        return {"status": "completed", "bronze_record_id": bronze_id}


# Worker registration
if __name__ == "__main__":
    worker = Worker(
        client,
        task_queue="ingestion-task-queue",
        activities=[
            minio_download_activity,
            sha256_dedup_check_activity,
            mineru_parse_activity,
            write_bronze_activity,
            publish_kafka_activity,
        ],
        workflows=[DocumentIngestionWorkflow],
    )
    worker.run()
```

### 19.5 Temporal Scheduled Workflows (Batch Jobs)

| Workflow ID | Trigger | Key Activities | Schedule |
|---|---|---|---|
| `grooming_workflow` | Cron: `0 2 * * *` | 1. Orphan detection (Nodes with no incoming edges)<br>2. Redundant edge consolidation (MaxSim < 0.85)<br>3. SATISFIES edge validation<br>4. SHACL re-validation | Daily 02:00 UTC |
| `coverage_score_workflow` | Cron: `0 6 * * *` | 1. Per-framework coverage score calculation<br>2. Threshold breach detection<br>3. Publish `coverage.alert` to Kafka | Daily 06:00 UTC |
| `gap_lifecycle_workflow` | Cron: `0 6 30 * * *` | 1. Gap state machine evaluation (OPEN → IN_REMEDIATION → REMEDIATED → VERIFIED → CLOSED)<br>2. Remediation due date alerts<br>3. ACCEPTED gap review date check<br>4. POA&M update | Daily 06:30 UTC |
| `archival_workflow` | Cron: `0 1 1 * *` | 1. Monthly hot-to-cold graph archival (nodes > 90 days old)<br>2. PostgreSQL cold store upsert<br>3. Memgraph node status update to `superseded` | Monthly 01:00 UTC |
| `dpo_finetuning_workflow` | Cron: `0 0 1 * *` | 1. Langfuse reject pair extraction (confidence < 0.70)<br>2. DPO dataset preparation<br>3. Fine-tuning job submission (vLLM)<br>4. A/B test benchmark evaluation | Monthly 00:00 UTC |

### 19.6 HITL (Human-in-the-Loop) Integration

**Approval Workflow Pattern:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User       │     │  Temporal    │     │   System     │
│   UI/HITL    │     │  Workflow    │     │   Backend    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ 1. Submit request  │                    │
       │───────────────────>│                    │
       │                    │ 2. Signal: received│
       │                    │───────────────────>│
       │                    │                    │
       │                    │ 3. Wait for signal │
       │                    │ (pause workflow)   │
       │                    │                    │
       │ 4. Review decision │                    │
       │───────────────────>│                    │
       │                    │ 5. Signal: callback│
       │                    │<───────────────────│
       │                    │                    │
       │                    │ 6. Resume workflow │
       │                    │<───────────────────│
       │                    │                    │
       │                    │ 7. Apply changes   │
       │                    │───────────────────>│
       │                    │                    │
```

**Approval Types:**
| Type | Trigger | Workflow | Timeout | Callback Field |
|---|---|---|---|---|
| `extraction_review` | LLM confidence < 0.70 | `extraction_validation_workflow` | 48 hours | `review_notes`, `corrected_text` |
| `mapping_verification` | Low-confidence crosswalk | `mapping_workflow` | 72 hours | `override_type`, `confidence_override` |
| `gap_resolution` | Gap state = ASSIGNED | `gap_lifecycle_workflow` | 30 days | `resolution_evidence`, `acceptance_criteria` |
| `model_finetuning` | Dual-Judge fail rate > 5% | `dpo_finetuning_workflow` | N/A | `dataset_approval`, `model_version` |

---

## 20. HITL & Training Data Pipeline

### 20.1 HITL (Human-in-the-Loop) Architecture

**Integration Points:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HITL Training Loop                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │   Langfuse   │      │  Temporal    │      │   HITL UI    │              │
│  │   Observability  │      │  Workflow    │      │  (React/Next.js) │        │
│  │   Dashboard  │      │  Engine      │      │              │              │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘              │
│         │                     │                     │                       │
│         │ 1. Extract rejects  │                     │                       │
│         │────────────────────>│                     │                       │
│         │   (confidence < 0.70)                      │                       │
│         │                     │                     │                       │
│         │                     │ 2. Signal: workflow │                       │
│         │                     │   pause (approval)  │                       │
│         │                     │────────────────────>│                       │
│         │                     │                     │                       │
│         │                     │                     │ 3. SME review         │
│         │                     │                     │──────────────────────>│
│         │                     │                     │   (accept/modify)     │
│         │                     │                     │                       │
│         │                     │ 4. Signal: callback │                       │
│         │                     │<────────────────────│                       │
│         │                     │                     │                       │
│         │                     │ 5. Resume workflow  │                       │
│         │                     │<────────────────────│                       │
│         │                     │                     │                       │
│         │                     │ 6. Store corrections│                       │
│         │<────────────────────│                     │                       │
│         │   DPO dataset       │                     │                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 20.2 Rejection Classification

| Category | Trigger | Handler |
|---|---|---|
| **Extraction Low Confidence** | LLM confidence < 0.70 | Route to `extraction_review` queue; SME rewrites text |
| **Logic Judge Fail** | Semantic faithfulness score < 0.95 | Route to `mapping_verification` queue; SME validates mapping |
| **Technical Judge Fail** | Technical accuracy ≠ 100% | Route to `technical_review` queue; SME corrects parameters |
| **Crosswalk Ambiguity** | INTERSECTS_WITH relationship detected | Route to `crosswalk_review` queue; SME resolves overlap |
| **Gap Resolution Dispute** | ACCEPTED gap flag raised | Route to `gap_resolution` queue; SME provides evidence |

### 20.3 DPO (Direct Preference Optimization) Dataset Format

```yaml
# Langfuse export: reject_pairs.yaml
- trace_id: "uuid-extraction-001"
  workflow_id: "extraction_validation_workflow"
  input_prompt: |
    Extract control obligations from:
    "The organization must limit information system access to authorized users..."
  
  rejected_output: |
    {
      "id": "AC-1.a.1",
      "prose": "The organization shall control system access...",
      "confidence": 0.62
    }
  
  preferred_output: |
    {
      "id": "AC-1.a",
      "prose": "The organization must limit information system access to authorized users...",
      "action_verb": "limit",
      "subject_noun": "information system access",
      "confidence": 0.97
    }
  
  reason: "Semantic loss: 'control' ≠ 'limit'; missing facets"
  
  reviewer_id: "sme-john-doe"
  reviewed_at: "2026-04-10T14:30:00Z"
```

### 20.4 Fine-Tuning Pipeline (Temporal)

| Step | Task | Tool | Output |
|---|---|---|---|
| 1 | Extract reject pairs from Langfuse | Python + Langfuse API | `reject_pairs.parquet` |
| 2 | Format as DPO training data | Custom script | `dpo_dataset.jsonl` |
| 3 | Split: 80% train, 10% val, 10% test | sklearn | `train/val/test splits` |
| 4 | Submit fine-tuning job | vLLM + Axolotl | `fine-tuned-model-checkpoint` |
| 5 | A/B test on benchmark | Custom evaluator | `precision_recall_f1 scores` |
| 6 | Promote if improvement > 2% | Git + Model Registry | `model:v1.1.0` |
| 7 | Deploy to GPU worker pool | Kubernetes + vLLM | `production model endpoint` |

### 20.5 Evaluation Metrics

| Metric | Baseline (v1.0) | Target (v2.0) | Method |
|---|---|---|---|
| **Extraction Precision** | 0.82 | 0.92 | Human review (n=1000) |
| **Logic Judge Agreement** | 0.88 | 0.95 | Dual-Judge consensus |
| **Technical Judge Pass Rate** | 0.75 | 1.00 | Parameter validation |
| **Crosswalk Precision** | 0.78 | 0.90 | ColBERT + LLM classification |
| **End-to-End Mapping F1** | 0.71 | 0.85 | OSCAL export validation |

---

## 21. Implementation Roadmap & Future Enhancements

### Phase 1 — MVP (Months 1–4)

**Objective:** Deploy a functional RCKG with full De Jure pipeline, ColBERT crosswalk, bitemporal graph, and OSCAL SSP/POA&M export for three frameworks (NIST CSF, ISO 27001, DORA).

| Month | Deliverables |
|---|---|
| **Month 1** | Infrastructure provisioning (Docker Compose); PostgreSQL schema (Bronze/Silver/Gold); MinIO WORM buckets; Langfuse self-hosted; pySHACL shape library v1.0. |
| **Month 2** | Ingestion pipeline (MinerU + Marker + chunking); LLM-as-Judge extraction; Dual-Judge validation; Bronze→Silver→Gold promotion. |
| **Month 3** | ColBERT indexing; SATISFIES edge creation; Gap lifecycle state machine; SHACL enforcement; Coverage Score Model; Grooming Agent. |
| **Month 4** | GraphRAG query interface; OSCAL SSP/POA&M/SAR export; Prometheus + Grafana dashboards; E2E test suite; performance benchmark. |

### Phase 2 — Production Hardening (Months 5–8)

| Capability | Description |
|---|---|
| **Kubernetes Production Deployment** | Migration from Docker Compose to full Kubernetes with HA PostgreSQL, Qdrant cluster, and Memgraph sharding. |
| **Regulatory Change Monitoring** | Web scraper agents monitoring official regulatory publication feeds (EUR-Lex, NIST, ISO) and auto-queuing new document versions. |
| **DPO/RLHF Fine-Tuning Pipeline** | Automated monthly fine-tuning cycle using Langfuse-curated reject pairs; A/B testing of fine-tuned vs base models on benchmark. |
| **Third-Party Risk Module** | `ThirdParty` node integration; `VENDOR_OF` edges; third-party assessment evidence collection; supplier risk scoring. |
| **ESG Risk Dimension** | ESG tagging on Risk nodes; ESG-specific crosswalk against ESRS, GRI, TCFD; ESG compliance posture dashboard. |
| **Executive Dashboard** | Real-time board-level compliance posture visualisation; framework coverage heat maps; gap trend analysis. |
| **Multi-Language UI** | Support for 84 languages leveraging BGE-M3 multilingual embeddings; localised OSCAL export. |

### Phase 3 — Advanced Capabilities (Months 9–12)

| Capability | Description |
|---|---|
| **External Auditor Portal** | Read-only API portal with OSCAL export self-service; auditor-scoped RBAC; evidence package download. |
| **Automated Remediation Workflows** | Auto-create Jira/ServiceNow tickets for new Gap nodes; workflow integration for remediation sign-off. |
| **OSCAL 2.0 + Agentic AI Extensions** | Integration with NIST CSWP 53 OSCAL 2.0 agentic AI extensions for autonomous risk reasoning and continuous assurance. |
| **Digital Twin Integration** | Connect RCKG control graph to infrastructure digital twin for real-time control effectiveness monitoring. |
| **Predictive Risk Analytics** | ML model trained on historical gap patterns to predict emerging compliance gaps before regulatory cycle. |

---

## 22. Document History & Revision Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2025-12-21 | Architecture Team | Initial draft — foundation architecture |
| 2.0 | 2026-01-15 | Tech Review | ColBERT + Memgraph finalized |
| 3.0 | 2026-02-28 | Architecture Synthesis | Agentic orchestration layer added |
| 4.0-A | 2026-04-12 | Claude Code Synthesis | Full Agentic GraphRAG TRD |
| 4.0-B | 2026-04-12 | Master Blueprint Team | Master Design Blueprint with Dual-Judge model |
| **5.0** | **2026-04-12** | **Senior AI Architecture Synthesis** | **MASTER SYNTHESIS:** Comparative analysis of 4.0-A and 4.0-B; all gaps resolved; OSCAL provenance metadata; Gap lifecycle state machine; ThirdParty node + ESG dimension; full testing pyramid; data retention policy; Coverage Score Model; SHACL GoldFK shape; Dual-Judge validation; DPO fine-tuning loop; MECE coverage reporting. |
| **6.0** | **2026-04-12** | **End-State Architecture Synthesis** | **END-STATE ARCHITECTURE:** Temporal.io workflow orchestration (replacing Airflow primary); Kafka kept for event bus + Airflow for scheduled batch jobs; Hot/Cold graph separation (Memgraph hot 32GB + PostgreSQL cold 90TB+); Complete DGX Spark demo specs (Grace Blackwell 128GB unified RAM); Production Kubernetes cluster architecture (EKS + GPU worker pool); HITL & Training Data Pipeline (DPO fine-tuning loop); Workflow implementation examples (Temporal SDK); Complete deployment configurations (docker-compose.demo.yml + production cloud specs); Bitemporal data model enforcement; ColBERT + Dual-Judge validation; Air-gap deployment checklist. |

---

> ✅ **DOCUMENT STATUS:** This document (v6.0) is the single authoritative technical specification for the RCKG Platform. Predecessor documents (v1.0 through v5.0) are superseded and should not be used for implementation guidance. All build decisions must reference this document.

---

*Risk and Control Knowledge Graph (RCKG) Platform · TRD v6.0 · 2026-04-12 · CONFIDENTIAL — INTERNAL USE ONLY*