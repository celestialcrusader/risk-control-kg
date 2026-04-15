# AI Architecture & Processing Pipeline

## Overview
RCKG utilizes a hierarchical "Brain" and "Muscle" architecture. The "Muscles" are specialized agents that process data, while the "Brain" is the domain-trained model stack that powers them.

## 1. Agentic Processing Pipeline (The "Muscles")

### 1.1 Ingestion Agent (Raw to Flattened)
*   **Purpose**: Converts non-OSCAL data (PDF, Excel, Policy docs) into the Flattened Record layer.
*   **Trigger**: File Upload.
*   **Actions**:
    *   **Extract**: Identifies semantic units (Groups, Objectives, Statements).
    *   **Map**: Uses `auto-mapper` logic to align with standard Facets.
    *   **Write**: Populates PostgreSQL Layer 2 (Flattened) and Memgraph Logic Fabric.
*   **Prompt ID**: `ingest-extraction`, `auto-mapper-analysis`

### 1.2 OSCAL Reconciliation Agent (The Gap-Filler)
*   **Purpose**: Ensures government-audit readiness by backfilling technical metadata.
*   **Trigger**: New entry in Flattened Layer.
*   **Actions**:
    *   **Compare**: Checks flattened record against NIST Full OSCAL catalog (Layer 1).
    *   **Backfill**: Infers or retrieves missing formal parameters (e.g., `set-parameters`, `prop-name`).
    *   **Sync**: Updates PostgreSQL Layer 1 to ensure valid OSCAL export.

### 1.3 RCKG Grooming Agent (The "Gardener")
*   **Purpose**: Maintains the health, density, and efficiency of the Knowledge Graph.
*   **Trigger**: Scheduled Routine or Post-Ingestion.
*   **Actions**:
    *   **Cross-walk**: Matches new Obligations to existing Objectives using Vector Similarity.
    *   **Prune**: Identifies redundant or conflicting control statements.
    *   **Facet Discovery**: Scans new literature to suggest new Facets (e.g., "AI Transparency").
    *   **Optimize**: Creates "Shortcut" edges to minimize reasoning hops between Risks and Controls.

### 1.4 Consumption Agents
*   **RAG Agent**: Answers user queries using the Logic Fabric (GraphRAG).
*   **Audit Agent**: Generates risk-based audit programs (`AuditProgram`) based on graph context.

---

## 2. Domain Training Strategy (The "Specialization")

We treat the LLM not just as a parser, but as a domain expert trained on the "DNA" of GRC.

### 2.1 Library Layer (Continued Pre-training)
*   **Goal**: Teach the model the semantic nuance of risk and control intent.
*   **Hardware**: NVIDIA DGX Spark (128GB Unified Memory).
*   **Software**: Unsloth (Continuous Pre-Training).
*   **Data**: Raw technology risk literature, NIST SP 800 series, ISO standards, Cloud Security Alliance papers.
*   **Scale**: 1M+ context windows.

### 2.2 Action Layer (Instruction Fine-Tuning)
*   **Goal**: Enforce deterministic output and specific reasoning patterns.
*   **Method**: LoRA/QLoRA on DGX Spark.
*   **Capabilities**:
    *   **Parameter Extraction**: Turning technical SOPs ("run daily") into OSCAL values ("frequency: 86400").
    *   **Cross-walk Reasoning**: Generating the `rationale` field for `[:RELATED_TO]` edges.
    *   **Determinism**: Outputting strictly formatted JSON/Cypher.

---

## 3. Infrastructure & Orchestration
*   **Model Hosting**: Ollama (Local) - `Llama 3` / `Mistral`.
*   **Orchestrator**: Langfuse (Prompt Management + Tracing).
*   **Tracing**: All agent actions are traced to `langfuse_prompt` versions.
