# Pure RCKG Strategic Alignment, Delta Analysis & Production Blueprint

**Document Version:** 3.2 — Master Production Engineering & Governance Blueprint  
**Status:** Approved / Active Production Specification  
**Classification:** Internal — Confidential  
**Last Updated:** July 28, 2026  
**Linked Pickup Documentation:**
- README: [README.md](file:///home/zackchow/coding/rckg/docs/02-pickup/README.md)
- BRD: [01-business-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/01-business-requirement-doc.md)
- PRD: [02-product-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/02-product-requirement-doc.md)
- TRD: [03-technical-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/03-technical-requirement-doc.md)
- Current Code Audit: [04-current-state-of-code.md](file:///home/zackchow/coding/rckg/docs/04-current-state-of-code.md)

---

## 1. Executive Summary & Strategic Realignment

This document establishes the master production engineering specification, governance rules, and grounded execution plan for the **Risk and Control Knowledge Graph (RCKG)** engine.

### Strategic Shift & Scope Lock
The RCKG platform is 100% focused on pure Risk and Control Knowledge Graphing. All secondary UI copilot integrations (Wukongtai risk tiering, Clear Trace generative canvas, DeepEval testkits) are set aside to prioritize building the core graph processing engine.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PURE RCKG GRAPH PROCESSING ENGINE                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. TWO-PHASE LIFECYCLE PARADIGM                                                       │
│    • Phase 1 (Cold-Start Bootstrap): Bulk 4-Stage Funnel builds initial Graph (v1.0.0) │
│    • Phase 2 (Steady-State Maintenance): Incremental Mutation Pipeline (Graphiti)      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. DUAL-TIER GOVERNANCE MODEL                                                          │
│    • Instance Mutations: Auto-validated via Python Compiler Gates                      │
│    • Ontology Mutations: MANDATORY Human/Committee Governance Gate (No LLM Auto-Commit)│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. CLOSED-SET MUTATION PRIMITIVES & PARAMETERIZED CYPHER                               │
│    • Structured JSON Primitives (ADD_EDGE, SUPERSEDE_NODE, RECLASSIFY_EDGE, etc.)      │
│    • Database writes executed strictly via parameterized Cypher templates              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. LITERAL SNAPSHOT REGRESSION TESTING (GOLDEN ASSERTIONS SUITE)                        │
│    • Pinned suite of human-attested Golden Assertions                                  │
│    • Mutations breaking Golden Assertions trigger mandatory Human Review               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. FIRST-CLASS GRAPH REVERT & BITEMPORAL TIME-TRAVEL                                   │
│    • Revert-with-reason (reverted_by, reverted_at, revert_reason) tags release vX.Y.Z │
│    • Embedding Sync Controller preserves AS OF DATE queries in Qdrant & ColBERT        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ingestion Taxonomy & Multi-Format Parsing Architecture

### 2.1 Multi-Source Document Ingestion Mapping Matrix

| Document Category | Target Graph Node Type | Node Label | Description / Semantic Scope | Example Source Documents |
|---|---|---|---|---|
| **Regulatory Mandates** | **Obligation** | `:Obligation` | Atomic, legally binding statutory or regulatory clause requirements. | EU AI Act, DORA, NIS 2, GDPR, MAS TRM, US State AI Laws |
| **Internal Corporate Policies** | **Control Objective** | `:ControlObjective` | High-level governance statements defining mandatory security/risk targets. | Information Security Policy, AI Ethics Policy, Data Retention Policy |
| **Process & Operational Docs** | **Control Activity** | `:ControlActivity` | Concrete procedural steps, SOPs, workflows, and technical configurations executing a policy. | User Access Provisioning SOP, Backup Standard, Incident Response Guide |
| **Industry Good Practice** | **Framework Control Objective** | `:FrameworkControlObj` | Standardized benchmark objectives published by international standards bodies. | NIST AI RMF (GOVERN-1.1), ISO/IEC 27001 (A.5.1), ISO 42001 (B.6) |
| **Industry Good Practice** | **Framework Control Activity** | `:FrameworkControlAct` | Standardized implementation guidance and benchmark control activities. | NIST SP 800-53 (AC-2(1)), IM8 Security Controls (Clause 3.2.1) |
| **Risk Inventories** | **Risk** | `:Risk` | Inherent or operational threats capable of compromising assets or compliance posture. | Threat Catalog, Operational Risk Register, IT Vulnerability Catalog |

### 2.2 Upstream Format Classifier & Parser Routing Pipeline

Upstream of parsing, a **Format Classifier Router** inspects document structure and routes to the appropriate parser stack:

```
                               Raw Enterprise File
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ Upstream Format Classifier│
                         └─────────────┬─────────────┘
                                       │
      ┌────────────────────────┬───────┴───────────────┬────────────────────────┐
      ▼                        ▼                       ▼                        ▼
┌───────────┐            ┌───────────┐           ┌───────────┐            ┌───────────┐
│ Native PDF│            │Scanned PDF│           │ DOCX / HTML│           │Complex PDF│
│ (Vector)  │            │  (Image)  │           │ Text Flow │           │ Matrix    │
└─────┬─────┘            └─────┬─────┘           └─────┬─────┘            └─────┬─────┘
      │                        │                       │                        │
      ▼                        ▼                       ▼                        ▼
┌───────────┐            ┌───────────┐           ┌───────────┐            ┌───────────┐
│ Marker /  │            │ OCR Engine│           │ python-docx│            │TableTrans-│
│ PyMuPDF   │            │ (Surya/   │           │ / BeautifulSoup        │ former /  │
│ Layout    │            │ Tesseract)│           │           │            │pdfplumber │
└─────┬─────┘            └─────┬─────┘           └─────┬─────┘            └─────┬─────┘
      │                        │                       │                        │
      └────────────────────────┴───────┬───────────────┴────────────────────────┘
                                       ▼
                         De Jure Rule Unit Extraction
                    (Clause-Boundary Chunking, NOT Tokens)
```

---

## 3. Graph Topology Engine: Canonical Linkages & Escape Hatch Shortcuts

### 3.1 Canonical 5-Linkage Topology

Under ideal conditions, enterprise data flows through five canonical relationship types:

```
              ┌───────────────────────────┐
              │           Risk            │
              └─────────────┬─────────────┘
                            │ (MITIGATES)
                            ▼
 ┌──────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────────┐
 │    Obligation    │◄───┤     Control Objective     ├───►│ Framework Control Objective   │
 └──────────────────┘    └─────────────┬─────────────┘    └───────────────────────────────┘
      (SATISFIES)                      │                         (CROSSWALKS_TO_OBJ)
                                       │ (OPERATIONALIZED_BY)
                                       ▼
                         ┌───────────────────────────┐    ┌───────────────────────────────┐
                         │     Control Activity      ├───►│  Framework Control Activity   │
                         └───────────────────────────┘    └───────────────────────────────┘
                                                                 (CROSSWALKS_TO_ACT)
```

### 3.2 The "Escape Hatch" Topology (Handling Real-World Incomplete Documents)

To prevent mis-modeling incomplete enterprise documents, RCKG supports **Escape Hatch Direct Edges** (e.g. `[Risk] ──(DIRECT_GAP_TO)──► [FrameworkControlObj]`). Creating an Escape Hatch edge automatically generates an explicit `[:Gap]` node with `gap_type: "MISSING_INTERMEDIATE_POLICY_OBJECTIVE"`.

---

## 4. Probabilistic NLI Set-Theory Engine & Conditional Entailment

### 4.1 Conditional Entailment & `condition_confidence` Calibration

Legal text is conditional. A control activity satisfies an obligation *under specific operational parameters*. In addition to extracting the string `condition_clause`, the engine assigns a **`condition_confidence`** score quantifying model certainty over the extracted condition.

### 4.2 Mandatory Edge Metadata Schema

```cypher
(:ControlObjective)-[r:SATISFIES {
  set_theory_relation: "CONTINGENT_SATISFIES",   // NLI category
  condition_clause: "Applies ONLY IF data_type == 'PII' AND hosting == 'Cloud'", // Semantic condition
  condition_confidence: 0.88,                   // Generative extraction certainty (0.00 - 1.00)
  confidence_score: 0.92,                       // Calibrated overall probability (0.00 - 1.00)
  status: "PROBABILISTIC_AI",                   // 'PROBABILISTIC_AI' or 'HUMAN_ATTESTED'
  is_golden_assertion: false,                   // True if pinned in Golden Regression Suite
  nli_entailment_logits: [0.02, 0.05, 0.93],    // [Equivalent, Superset, Subset/Contingent]
  model_version: "rckg-nli-cross-encoder-v1.2", // Exact classification model version
  prompt_version: "set-theory-cot-v3.1",        // Prompt/CoT template version
  embedding_model: "Qwen3-Embedding-8B",        // Dense embedding model
  logic_judge_score: 0.95,                      // Teacher Logic Judge score (if sampled)
  technical_judge_score: 0.90,                  // Teacher Technical Judge score (if sampled)
  attested_by: null,                            // Auditor User ID upon human sign-off
  attested_at: null,                            // Timestamp of human sign-off
  reverted_by: null,                            // Auditor ID if mutation reverted
  reverted_at: null,                            // Timestamp of revert
  revert_reason: null,                          // Audit rationale for revert
  mapping_date: datetime()                      // System ingestion time
}]->(:Obligation)
```

---

## 5. Evaluation Harness, Benchmark Selection & Retraining Cadence

### 5.1 Gold Crosswalk Evaluation Benchmark Harness (Build FIRST)

- **Initial Calibration Corpus:** 1,000 human-annotated crosswalk candidate pairs (NIST SP 800-53 $\leftrightarrow$ ISO 27001, NIST AI RMF $\leftrightarrow$ EU AI Act, MAS TRM $\leftrightarrow$ Corporate Policies).
- **Expansion Target:** Expands to 2,500 - 5,000 pairs following initial calibration to address class distribution skew (e.g. balancing `NO_RELATIONSHIP` vs `EQUIVALENT_TO`).
- **Cold-Start Domain Calibration:** Non-regulatory document classes (SOPs, Risk Registers) use dedicated domain-specific calibration subsets (250 pairs each for SOP $\leftrightarrow$ Activity and Risk $\leftrightarrow$ Framework).

### 5.2 Benchmark-Driven Embedding Selection

Stage 1 dense embedding selection is driven empirically by benchmark evaluation against the Gold Harness (evaluating Qwen3-Embedding-8B, Voyage-law-2, BGE-M3, Stella-en-400M for **Recall@500**).

### 5.3 KTO / DPO Retraining Cadence & Feedback Accumulator

The Dual-Judge feedback collection service accumulates teacher scores asynchronously. When **500 new high-confidence preference pairs** (Dual-Judge Score $\ge 0.90$ for `CHOSEN`, $< 0.60$ for `REJECTED`) are accumulated, an automated worker triggers KTO/DPO student LLM fine-tuning.

### 5.4 Open Source Crosswalk Seed Ingestion & Golden Assertions Suite Bootstrap

To solve the cold-start graph bootstrapping problem deterministically, RCKG ingests official, open-source compliance crosswalk databases before running any AI pipeline:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               OPEN SOURCE COMPLIANCE CROSSWALK SEED HARVESTING PIPELINE                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. NIST OLIR XML Database Parser (https://csrc.nist.gov/projects/olir)                │
│    • Official Government Crosswalks: NIST SP 800-53 Rev 5 ↔ ISO/IEC 27001:2022        │
│    • NIST SP 800-53 Rev 5 ↔ NIST CSF 2.0 │ NIST SP 800-53 Rev 5 ↔ ISO 27002:2022       │
│    • NIST SP 800-66 Rev 2 (HIPAA ↔ NIST 800-53)                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Cloud Security Alliance (CSA) Cloud Controls Matrix (CCM v4) Excel Parser           │
│    • CCM v4 Meta-Framework Crosswalks: CCM ↔ NIST 800-53, ISO 27001/27002, PCI DSS 4.0 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Eramba GRC & ComplianceAsCode Embedded DB Mining                                    │
│    • Extracted Control Mappings: CIS Critical Controls v8 ↔ NIST 800-53, SOC 2 ↔ ISO   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ SEED GRAPH OUTPUT (v1.0.0 Baseline):                                                   │
│ • ~1,700 Framework Nodes + ~3,100 Pre-Validated Crosswalk Edges                       │
│ • All Seed Edges set to status: "HUMAN_ATTESTED" and is_golden_assertion: true        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Seed Data Execution Strategy & Priority
1. **NIST OLIR XML Loader (Sprint 1 Priority):** Download official NIST OLIR XML database directly from CSRC. Parse XML `<InformativeReference>` tags to auto-create `FrameworkControlObj` and `FrameworkControlAct` nodes linked by `CROSSWALKS_TO_OBJ` / `CROSSWALKS_TO_ACT` edges.
2. **Golden Assertions Suite Initialization:** All 3,100+ government-published edges are tagged with `status: "HUMAN_ATTESTED"` and `is_golden_assertion: true`, providing an immediate regression test suite against which future LLM graph mutations are checked.


---

## 6. Grounded DGX Spark Compute Architecture & Latency Budget

### 6.1 BM25 Architecture & Network Hop Buffer

Stage 1 BM25 sparse keyword retrieval executes on a dedicated **Elasticsearch Cluster** with a 15-second network hop buffer incorporated into Stage 1 timing.

### 6.2 Pre-Computed ColBERT Token Embedding Caching

In Stage 2, ColBERTv2 token embeddings for static source entity nodes are **pre-computed and cached in VRAM/RAM**. Stage 2 reranking computes *only* pairwise MaxSim late-interaction matrix multiplications over pre-cached token representations.

### 6.3 Grounded Hardware & Latency Summary

| Stage | Technology / Model | Candidate Count | Latency | VRAM / Hardware Footprint |
|---|---|---|---|---|
| **Stage 1 (BM25 Sweep)** | Elasticsearch Sparse Index + Network Buffer | 50,000,000 pairs | ~90 + 15 sec | Elasticsearch Cluster (16GB RAM) |
| **Stage 1.5 (Bi-Encoder)**| Benchmark-selected Dense Vector | 500,000 pairs | ~45 sec | Qdrant Vector DB (16GB RAM) |
| **Stage 2 (ColBERTv2)** | Pre-Cached Token MaxSim Reranking | 50,000 pairs | ~60 sec | ColBERT GPU batch (8GB VRAM) |
| **Stage 2.5 (NLI Rerank)**| DeBERTa-v3-Large Cross-Encoder | 10,000 pairs | ~30 sec | Fast Cross-Encoder (4GB VRAM) |
| **Stage 3 (Distilled LLM)**| Llama-3.1-8B-Instruct (vLLM) | ~2,500 pairs | ~210 sec | vLLM 8B batch (16GB VRAM) |
| **Stage 4 (Dual Judge)** | 70B Teacher (Asynchronous) | ~100 pairs | ~120 sec (Async) | vLLM 70B FP16 (79GB VRAM) |
| **Total Synchronous Run**| **Hardened 4-Stage Funnel** | **50,000,000 initial** | **~7.5 min sync** | **Fits in 128GB Unified Memory** |

---

## 7. Graph-Centric AI Knowledge Engineering & Governance Architecture

### 7.1 Two-Phase Lifecycle Integration (Cold-Start vs. Steady-State)

The system operates across two distinct lifecycle phases:
- **Phase 1: Cold-Start Bootstrap Mode (Sprint 1–3):** When the graph is empty, the 4-Stage Multistage Retrieval & Classification Funnel (Sections 5–6) executes in bulk to construct the initial baseline Knowledge Graph (`v1.0.0`).
- **Phase 2: Steady-State Maintenance Mode (Graphiti Pattern, Sprint 4+):** Once populated, the platform switches to incremental **Graph Mutation Diffs**. The 4-stage funnel and facet matching machinery move *inside* the `SemanticChangeDetector` as a specialized subroutine.

```
                           PARADIGM LIFECYCLE RECONCILIATION
                           
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ PHASE 1: COLD-START BOOTSTRAP MODE                                              │
 │ Bulk 4-Stage Funnel ──► Ingests Corpus ──► Populates Base Graph (v1.0.0)         │
 └────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ PHASE 2: STEADY-STATE MAINTENANCE MODE (Graphiti Pattern)                       │
 │ New Document ──► Semantic Change Detector ──► Mutation Diff ──► Graph Release v1.1.0│
 │ (4-Stage Funnel operates INSIDE Semantic Change Detector as a subroutine)       │
 └─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Dual-Tier Governance Model (Instance vs. Ontology Mutations)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DUAL-TIER GOVERNANCE MODEL                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. INSTANCE-LEVEL MUTATIONS (ADD_EDGE, SUPERSEDE_NODE, MUTATE_PROPERTIES, CREATE_GAP) │
│    • Executed via automated Python Graph Compiler gates.                               │
│    • High-confidence mutations auto-committed to Graph (vX.Y.Z).                      │
│    • Low-confidence / high-risk items routed to Human Attestation Gate.               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. ONTOLOGY-LEVEL MUTATIONS (ADD_NODE_TYPE, MUTATE_RELATION_SEMANTICS, REDEFINE_FACET)│
│    • MANDATORY Human / Committee Governance Gate.                                      │
│    • ZERO LLM Auto-Commits permitted for schema evolution.                            │
│    • Requires formal schema migration script & committee sign-off.                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Closed-Set Typed Mutation Primitives & Parameterized Cypher

The Candidate Mutation Generator emits **only** a strictly typed JSON payload containing predefined mutation primitives:
- Primitives: `ADD_NODE`, `SUPERSEDE_NODE`, `ADD_EDGE`, `RECLASSIFY_EDGE`, `DEPRECATE_EDGE`, `MERGE_NODE`, `SPLIT_NODE`, `CREATE_GAP`.
- **Database Writes:** Executed strictly via **parameterized Cypher query templates** (no raw LLM-generated Cypher strings).

### 7.4 Literal Snapshot Regression Testing (Golden Assertions Suite)

- **Mechanism:** Maintain a pinned database suite of **Golden Graph Assertions** (critical human-attested edges, mandatory obligation-to-control links, key compliance Q&A paths).
- **Compiler Rule:** Any proposed mutation diff that flips, invalidates, or contradicts a Golden Assertion triggers an immediate **Graph Regression Alert** and forces mandatory human review, regardless of model confidence score.

### 7.5 First-Class Graph Revert (`revert_mutation_diff`)

In compliance, reverting a bad commit with a clear audit trail (`reverted_by`, `reverted_at`, `revert_reason`) is a first-class operation. Executing a revert tags a new release version (e.g. `v2.4.1 [REVERT diff-8921]`) and updates vector payload metadata via the Embedding Sync Controller.

### 7.6 Event-Driven Embedding Sync Controller

When a node is superseded (`SUPERSEDE_NODE`), the **Embedding Sync Controller** (PostgreSQL Outbox / Event-Driven Listener pattern) updates Qdrant vector payloads and ColBERT token caches, tagging historical vectors with `valid_to` timestamps to preserve point-in-time time-travel queries (`AS OF DATE 2025-06-01`).

### 7.7 Downstream GraphRAG Translation Layer Interface

Memgraph Cypher subgraphs connect to downstream GraphRAG query engines via a dedicated **GraphRAG Translation Service** mapping 6 node types, Gaps, and bitemporal dates to GraphRAG Entity/Relationship schemas and community summaries for executive risk Q&A.

---

## 8. Current State vs. Final Intent (The Delta Analysis)

### 8.1 Architectural Delta Matrix

| Dimension | Current Codebase / Docs | Target Pure RCKG Engine | Delta & Required Modifications |
|---|---|---|---|
| **Product Focus** | Skewed toward Clear Trace UI & Wukongtai AI Risk Tiering | 100% Pure Risk Control Knowledge Graph (RCKG) processing engine | **Drop/Defer** Wukongtai tiering & UI Copilot features; **Focus** on core graph. |
| **Lifecycle Model** | Single static ingestion pipeline | Two-Phase Lifecycle (Phase 1 Bulk Bootstrap ──► Phase 2 Graphiti Maintenance) | **Build** Bulk 4-stage funnel for bootstrap; switch to Graphiti diff engine post-v1.0.0. |
| **Governance Tiering** | Uniform AI confidence threshold | Dual-Tier Governance (Instance Auto-Gate vs Mandatory Human Ontology Committee Gate) | **Enforce** zero LLM auto-commit rule for ontology/schema evolution. |
| **Mutation Payload** | Unstructured text output | Closed-Set Typed Primitives (`ADD_EDGE`, `SUPERSEDE_NODE`) + Parameterized Cypher | **Restrict** LLM writes to structured JSON primitives executed via Cypher templates. |
| **Regression Testing** | Abstract validation narrative | Literal Snapshot Regression Testing against pinned **Golden Assertions Suite** | **Build** Golden Assertions test suite; block mutations that flip golden edges. |
| **Audit Revert** | Accretive history only | First-Class Graph Revert (`revert_mutation_diff`) with audit metadata | **Implement** `revert_mutation_diff` endpoint tagging release tags (`vX.Y.Z [REVERT]`). |
| **Ingestion Pipeline** | Basic PDF text extraction | Upstream Format Classifier + Multi-Format Layout/Table Parser | **Build** Upstream Format Classifier routing to Marker/PyMuPDF/Surya/TableTransformer. |
| **Graph Entities** | Legacy schema (`Control`, `Obligation`, `Gap`) | 6 Node Types (`Obligation`, `ControlObjective`, `ControlActivity`, `FrameworkControlObj`, `FrameworkControlAct`, `Risk`) | **Update** SQLModel ORM & Memgraph Cypher schemas for all 6 entity nodes. |
| **Graph Linkages** | 1 primary linkage (`Control` $\rightarrow$ `Obligation`) | 5 Canonical Linkages + Direct Escape Hatch Shortcuts | **Implement** Cypher queries & service logic for canonical + escape hatch edges. |
| **Set-Theory Engine** | Documented in story `CROSSWALK-3` but incomplete | Probabilistic NLI + Conditional Entailment (`condition_clause` & `condition_confidence`) | **Build** NLI cross-encoder + distilled 8B classifier with `condition_confidence` scoring. |
| **Vector Index Sync** | Unsynchronized vector indices | Event-Driven **Embedding Sync Controller** (Postgres Outbox pattern) | **Build** Embedding Sync Controller for Qdrant payload & ColBERT token cache sync. |
| **Evaluation Harness** | Unmeasured accuracy projections | 1,000-pair Gold Crosswalk Benchmark Harness (NIST $\leftrightarrow$ ISO) | **Assemble** gold evaluation corpus FIRST to drive embedding & threshold decisions. |
| **Audit Governance** | Unverified AI assertions | Human Attestation Gate (`status: "PROBABILISTIC_AI"` vs `"HUMAN_ATTESTED"`) + Provenance | **Add** `attested_by`, `attested_at`, `model_version`, and `prompt_version` to edges. |
| **Compute Scaling** | Unbounded $O(N \cdot M)$ space | Hardened 4-Stage Funnel (BM25 + Hop Buffer ──► Bi-Encoder ──► ColBERT ──► Cross-Encoder) | **Deploy** BM25 + dense bi-encoder + ColBERTv2 (pre-cached tokens) + DeBERTa Cross-Encoder. |
| **Compiler Baseline** | Full AI pipeline required upfront | Rule-Based MVP Graph Compiler Baseline (v0.1 regex/cosine gate) | **Build** deterministic v0.1 rule-based Graph Compiler before connecting LLM. |
| **Downstream Usage** | Graph as standalone output | Knowledge Graph powering downstream GraphRAG Executive Q&A | **Build** GraphRAG Translation Layer mapping Cypher paths to GraphRAG community summaries. |

---

## 9. Phased Implementation Next Steps

### Phase 1 — Schema Realignment, Benchmark Harness & Rule-Based MVP (Sprint 1)
1. **NIST OLIR XML Loader & Seed Graph Ingestion (Build FIRST):**
   - Download official NIST OLIR XML database (`https://csrc.nist.gov/projects/olir`). Write `NistOlirXmlParser` to parse `<InformativeReference>` tags, creating ~1,700 `FrameworkControlObj`/`FrameworkControlAct` nodes and ~3,100 pre-validated crosswalk edges (`status: "HUMAN_ATTESTED"`, `is_golden_assertion: true`).
2. **Gold Evaluation Benchmark Harness:**
   - Assemble 1,000 human-annotated crosswalk candidate pairs (NIST SP 800-53 $\leftrightarrow$ ISO 27001) to evaluate retrieval Recall@500 and cross-encoder precision empirically.
3. **Update SQLModel Schema (`backend/app/models/`):**
   - Implement ORM models for 6 entity nodes, `GapNode`, `ShortCircuitAuditLog`, and linkage mapping tables with `condition_clause`, `condition_confidence`, `status`, `is_golden_assertion`, `attested_by`, `reverted_by`.
4. **Deterministic Rule-Based Graph Compiler MVP (v0.1):**
   - Implement rule-based `GraphMutationDiff` engine using regex, keyword matching, and bi-encoder cosine distance calibrated against the Gold Harness.


### Phase 2 — Upstream Format Classifier & Multi-Format Ingestion (Sprint 2)
1. **Upstream Format Classifier & Ingestion Pipeline (`backend/app/services/`):**
   - Implement Upstream Format Classifier routing Native PDF, Scanned Image (Surya/Tesseract OCR), DOCX, and Control Matrices (TableTransformer/pdfplumber).
2. **Bulk Cold-Start Graph Construction (Phase 1 Pipeline):**
   - Execute 4-Stage Funnel to ingest initial enterprise corpus and populate base Knowledge Graph (`v1.0.0`).

### Phase 3 — Hardened 4-Stage Funnel & NLI Classification Engine (Sprint 3)
1. **Hardened 4-Stage Candidate Filtering Funnel:**
   - Integrate Elasticsearch BM25 (with 15s hop buffer) + dense bi-encoder + ColBERTv2 (pre-cached token embeddings) + DeBERTa-v3 NLI Cross-Encoder.
2. **Distilled 8B Student LLM & KTO/DPO Alignment:**
   - Deploy fine-tuned Llama-3.1-8B-Instruct for CoT set-theory reasoning, `condition_clause`, and `condition_confidence` extraction on ambiguous pairs ($0.30 \le \text{confidence} < 0.85$).
3. **Asynchronous 70B Dual-Judge Audit Pass & Retraining Trigger:**
   - Configure background worker task executing 70B Dual-Judge verification. Trigger KTO/DPO student LLM fine-tuning upon accumulating 500 new preference pairs.

### Phase 4 — Embedding Sync Controller, Graph Compiler, Governance & GraphRAG (Sprint 4)
1. **Embedding Sync Controller & Graph Revert Engine:**
   - Build Postgres outbox event listener synchronizing Qdrant vector payloads and ColBERT token caches upon `SUPERSEDE_NODE` commits. Implement `revert_mutation_diff` endpoint.
2. **Dual-Tier Governance & Golden Assertions Compiler:**
   - Implement mandatory Human Committee Gate for ontology mutations and Golden Assertions regression snapshot testing prior to Memgraph commit.
3. **GraphRAG Translation Layer & End-to-End Audit Validation:**
   - Wire Memgraph Cypher subgraphs to downstream GraphRAG query engine via GraphRAG Translation Layer. Verify end-to-end multi-source corpus ingestion, mutation diff execution, and Human Attestation sign-off.
