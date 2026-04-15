# Product Requirements Document (PRD)
**Project Name:** Risk Control Knowledge Graph (RCKG)
**Version:** 4.0 (Dual-Access)
**Target Audience:** Product Managers, Compliance Officers, **Knowledge Engineers**
**Date:** 2025-12-21

## 1. Product Vision
To transform compliance from manual drudgery into an **Autonomous Intelligence Operation**. RCKG is a "Living Logic Fabric" that ingests, de-conflicts, and actively grooms risk data, empowering users via both a **Native Portal** and **Enterprise Integrations**.

## 2. Key Features: The Knowledge Pipeline

### 2.1 Stage 1: The Harvest (Ingestion Engine)
*   **Multi-Format Support**: Ingest PDF, Excel, and OSCAL automatically.
*   **Integrity Gate**: Hash-based duplicate prevention.
*   **Flattening Engine**: Converts complex nested documents into standardized "Flattened Records."

### 2.2 Stage 2: The Refinery (Entity Resolution)
*   **Semantic De-confliction**: Automatically flag incoming requirements that are >92% similar.
*   **Conflict Logic**: Identify contradictory parameters.

### 2.3 Stage 3: The Logic Fabric (Synthesis)
*   **Canonical Mapping**: Merge tools to combine duplicates into a single master node.
*   **Facet Navigation**: Filter the graph by "Asset Type," "Function," or "Impact" tags.
*   **Orphan Detection**: Visual alerts for Risks with no Controls.

### 2.4 Stage 4: The Grooming (Maintenance)
*   **Path Optimization**: Shortens reasoning hops (<3 hops).
*   **Lineage Engine**: Click any node to see its original source PDF.

## 3. Interfaces & Integration (Dual-Access)

### 3.1 The "Stateless Portal" (Native UI)
*   **Target User**: SMEs, Auditors, Subsidiaries without GRC access.
*   **Nature**: **Stateless**. No local storage; visualizes Backend State only.
*   **Modules**:
    *   **Ingestion Wizard**: Drag-and-drop file upload with progress bar.
    *   **Graph Explorer**: Interactive node visualization (React Flow).
    *   **Resolution Interface**: "Tinder-style" conflict merge/branch UI.

### 3.2 The "Integrator Bridge" (Enterprise API)
*   **Target User**: ServiceNow / Archer Systems.
*   **Nature**: **API-First**.
*   **Capabilities**:
    *   **Pull**: Fetch Canonical Controls by ID.
    *   **Push**: Receive "Compliance Status" updates via Webhooks.
    *   **Query**: "Ask the Graph" endpoint for logic reasoning.

## 4. Roadmap Alignment

### Phase 1: Foundation (Sprint 1 - DONE)
*   [x] Infra Setup (Postgres+Mg).
*   [x] Basic Ingestion & Conflict Logic.

### Phase 2: The Refinery (Sprint 2 - CURRENT)
*   [ ] **Observability**: Langfuse Integration.
*   [ ] **Refinery**: Verified Extraction (LLM-as-a-Judge).
*   [ ] **Versioning**: Revision Node Logic.
*   [ ] Local AI (Llama 3.2 3B).

### Phase 3: Portal (Sprint 3)
*   [ ] React UI (Stateless Portal).
*   [ ] Graph Explorer (Canonical + Revision).
*   [ ] HITL Conflict Queue.

### Phase 4: Intelligence (Sprint 4)
*   [ ] Orphan Hunting (Agents).
*   [ ] DGX Spark Migration (70B Scale).
