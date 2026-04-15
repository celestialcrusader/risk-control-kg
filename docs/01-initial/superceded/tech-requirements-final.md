# 📕 TECHNICAL REQUIREMENTS DOCUMENT (TRD)
## Risk and Control Knowledge Graph (RCKG) Platform

**Document Version:** 4.0 (Master Design Blueprint)
**Classification:** Internal — Confidential

---

## 1. SYSTEM OVERVIEW & EXECUTIVE VISION

The **Risk and Control Knowledge Graph (RCKG)** is an AI-native, high-fidelity platform designed to continuously and deterministically map regulatory obligations to internal controls. By representing regulations, policies, operational risks, and mitigating controls as an interconnected knowledge graph, RCKG shifts GRC (Governance, Risk, and Compliance) from a reactive, annual audit exercise to a real-time, traceable, operational state.

### 1.1 Key Objectives
*   **High Fidelity Ingestion**: Parse dense, unstructured regulatory documents into discrete atomic rule units without semantic loss.
*   **Completeness in Mapping**: Multi-framework and multi-dimensional crosswalking using exact token-level comparison and logical set theory.
*   **High Precision & Traceability**: Bitemporal modeling ensures compliance states can be reconstructed for any point in history. Every conclusion is linked to a deterministic graph traverse pipeline.
*   **Agentic Orchestration**: Autonomous but strictly governed AI agents continuously maintain, map, groom, and audit the knowledge graph.
*   **Trust via "LLM-as-a-Judge"**: AI-driven decisions are independently audited by "Higher Reasoning" models before committing to the production graph.

---

## 2. CORE TECHNOLOGY STACK (THE UNIFIED STACK)

### 2.1 Principle of Operations
1.  **Graph as the System of Truth**: The property graph manages semantic topology. Relational databases only act as raw storage logs.
2.  **Strictly Self-Hosted**: 100% open-source capable infrastructure to satisfy air-gapped data residency needs. No external LLM API dependencies are required.

### 2.2 Storage Layer
*   **Graph Database (The Logic Fabric):** `Memgraph` (Optimized for in-memory graph traversals and path optimizations).
*   **Vector Database (High-Precision Matcher):** `Qdrant` (Maintains Multi-Vector ColBERT representations for late interaction and dense payloads).
*   **Relational Database (The Vault):** `PostgreSQL 16` (Stores immutable raw ingestion data, OSCAL records, and audit logs).
*   **Object/Blob Storage:** `MinIO` (For unstructured raw PDFs, docs, and evidence artifacts).

### 2.3 AI & Compute
*   **Backend & APIs:** `FastAPI` (Python 3.11).
*   **Orchestration / Message Queues:** `Apache Airflow` + `Kafka` (event-driven async pipelines).
*   **Vector Embeddings:** `BAAI BGE-M3` (Dense) + `ColBERTv2.0` (Token-level Multi-vector).
*   **LLM Inference (Local):** `Ollama` or `vLLM` running domain-trained / heavily prompted models (e.g., Llama 3 / Mistral variants).
*   **Parsing:** `MinerU` (Complex borders/layouts) and `Marker` (standard formats).
*   **Observability & Tracing:** `Langfuse` (Prompt Management + Audit Tracing).

---

## 3. DATA ARCHITECTURE & SCHEMA TOPOLOGY

Data moves through a rigorous pipeline from raw text into an intelligent, queryable Fabric.

### 3.1 The PostgreSQL "Vault" Layer (Data Lineage)
To optimize processing and maintain absolute fidelity, relational data is staged through three quality tiers:
1.  **Bronze Layer (Raw):** `staging_controls`
    *   Stores completely raw unstructured text from PDFs/CSVs.
    *   Fields: `uuid`, `canonical_id`, `raw_file_content` (JSONB blob).
2.  **Silver Layer (Semantic):** `semantic_controls`
    *   The "Refinery". AI has extracted structure.
    *   Fields: `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun` (Facets).
3.  **Gold Layer (Validated):** `golden_controls`
    *   Human-verified or highly-confident AI-validated data. Only Gold records are projected to the Memgraph knowledge graph.

### 3.2 The Memgraph "Logic Fabric" (Graph Schema)
The semantic structures form the intelligent reasoning fabric. Node properties act as the "DNA" for crosswalking.

#### Core Nodes:
*   **`Regulation` (Framework / Authority)**
    *   *Properties:* `framework_id`, `version`, `name`, `jurisdiction`, `status` (active/superseded), `effective_date`.
*   **`ControlGroup`**
    *   *Purpose:* High-level domain grouping (e.g. "Access Control").
*   **`ControlObjective` / `Obligation` (The "Why")**
    *   *Properties:* `id`, `text` (high-level intent), `impact_category`, `obligation_type`.
*   **`ControlStatement` / `ObligationStatement` (The "What")**
    *   *Properties:* `id`, `statement_text`, `action_verb`, `subject_noun`, `gov_domain`, `legal_base`.
    *   *Facets:* `control_function` (Preventive, Detective), `implementation_method` (Automated, Manual), `control_goals` (CIA triad), `asset_scope`.
*   **`RiskStatement` (Threat Vector)**
    *   *Properties:* `id`, `name`, `category`, `likelihood` (1-5), `impact` (1-5), `residual_risk_score`.
*   **`Control` (Internal Mitigation)**
    *   *Properties:* `id`, `name`, `description`, `owner`, `status`.
*   **`Evidence` (Artifacts)**
    *   *Properties:* `id`, `evidence_type`, `artifact_path`.

#### Core Edges:
*   `Framework -> HAS_GROUP -> ControlGroup`
*   `ControlGroup -> CONTAINS -> ControlObjective`
*   `ObligationStatement -> ACHIEVES -> ControlObjective`
*   `Control -> SATISFIES -> ObligationStatement`
*   `Control -> MITIGATES -> RiskStatement`

---

## 4. INGESTION PIPELINE (HIGH ACCURACY EXTRACTION)

Data extraction transforms unstructured prose into the RCKG `Canonical YAML` schema via the "De Jure" pipeline.

### 4.1 Tiered Document parsing
1.  **Read & Norm**: Convert raw PDFs to Markdown using `MinerU`.
2.  **Semantic Split**: Markdown Header chunking preserves parent/child clause groupings. If headers fail, semantic cosine distance thresholds (`>0.75`) force chunks.
3.  **Decompose & Extract**: Extract atomic rules into the `Canonical Ingestion Schema`.

### 4.2 Canonical Ingestion Schema
All external adapters must output to this YAML format before staging into `Bronze`:
```yaml
metadata:
  title: "Framework Name"
  version: "Revision 5"
control-groups:
  - id: "AC"
    title: "Access Control"
    objectives:
      - id: "AC-1"
        title: "Policy and Procedures"
        prose: "The high level intent of the policy..."
        statements:
          - id: "AC-1.a"
            prose: "The organization must limit information system access..."
```

---

## 5. COMPLETENESS IN MAPPING: CROSSWALK ENGINE

Standard cross-encoders are too slow, and standard dense embeddings lose the critical token sequence nuance important in legal texts.

### 5.1 Late Interaction Retrieval (ColBERT)
*   Instead of compressing an entire control into one vector, ColBERT creates contextualized embeddings for **every single token**. 
*   **Multi-Vector Storage in Qdrant:** Allows for exact `MaxSim` semantic token-matching between incoming control language and millions of obligations concurrently without hallucination.

### 5.2 Set-Theory Classification (High Precision)
Once candidate pairs are pulled via ColBERT, an AI model strictly outputs a mathematical Set Theory relationship, forming the `[:SATISFIES]` edge:
*   `EQUIVALENT_TO` ($A = B$): 1-to-1 match. 
*   `SUPERSET_OF` ($A \supset B$): Control exceeds the regulatory requirement. (Requirement Met).
*   `SUBSET_OF` ($A \subset B$): Control partially addresses the requirement. (Gap Flagged!).
*   `INTERSECTS_WITH` ($A \cap B$): Partial overlap with distinct goals. (Kicks to Human Review).
*   `NO_RELATIONSHIP`: Control completely misses the mark. (Critical Gap Flagged!).

---

## 6. THE AGENTIC ORCHESTRATION LAYER

RCKG utilizes a hierarchical **Brain and Muscle** architecture. The "Muscles" are specialized agents. The "Brain" is the underlying foundational graph fabric.

### 6.1 Agent Swarm Roles
1.  **Ingestion Agent (Raw to Flattened):** Extracts semantic units (Objectives/Statements), maps Facets utilizing auto-mapper logic, and writes to Postgres Layer 2 (Silver).
2.  **OSCAL Reconciliation Agent:** Compares silver records against the NIST full OSCAL catalog to backfill missing formal parameters.
3.  **Cross-walk Agent:** Generates the `[:SATISFIES]` mapping using ColBERT search.
4.  **Grooming Agent ("The Gardener"):** Consolidates redundant nodes, finds new Facet connections, adds topological shortcuts, and prunes orphaned links.
5.  **RAG / Audit Agent:** Answers user questions by traversing Graph multi-hop paths to pull the exact evidence base before generating answers.

### 6.2 Strict Governance (`agents.md`) & Skills (`skills.md`)
Agents operate strictly within defined constraints:
*   **Read-Only:** Production `/graph/production/` and `source-regulations/`.
*   **Progressive Disclosure via `skills.md`:** Agent workflows (like `iso27001-access-review.md`) define exact stepwise procedures:
    *   *Step 1:* Query Obligation Graph.
    *   *Step 2:* Collect Infrastructure Evidence (`/scripts/`).
    *   *Step 3:* Execute Crosswalk logic.
    *   *Step 4:* Generate MECE (Mutually Exclusive, Collectively Exhaustive) output reports.

---

## 7. TRUST, TRACEABILITY & OBSERVEABILITY

### 7.1 Temporal "Time Machine" Memory
No graph data is manually pruned; history is sacrosanct. 
*   Every node features dual tags: `event_time` (real-world effective date) and `ingestion_time`.
*   When a regulation updates, nodes are flagged `status: superseded` and linked via `SUPERSEDES` edges. 
*   Auditors can request the "Compliance Posture as of 2024-01-01" and the graph traverse will automatically exclude invalidated edges.

### 7.2 The Evaluator Layers ("LLM-as-a-Judge")
To ensure autonomous trust, actions are scored by Higher-Reasoning Judges:
1.  **Logic Judge (e.g., Llama 3 70B):** Evaluates semantic faithfulness (Did the mapper lose the actual intent of the control?). Score `< 0.95` triggers manual intervention.
2.  **Technical Judge (e.g., DeepSeek Reasoner):** Audits technical/mathematical accuracy (Does "Hourly" properly reconcile to "3600 seconds" in OSCAL parameters?). Requires 100% exact match.

### 7.3 Langfuse Auditing
*   **Tracing:** All agent actions, LLM inputs, prompt versions (`ingest-extraction`, `auto-mapper-analysis`), and outputs are actively logged inside Langfuse.
*   **Refinement:** Poorly graded generation outputs from the Judges are placed into a Fine-Tuning loop (DPO/RLHF) to continually elevate the foundational models.
*   **API Integrity:** The Integrator Service ensures an immutable Audit Trail is written to Postgres for every write-command executed in the graph.
