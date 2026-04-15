# Technical Requirements Document (TRD)
**Project Name:** Risk Control Knowledge Graph (RCKG)
**Version:** 4.0 (Dual-Access)
**Date:** 2025-12-21

## 1. Executive Summary
RCKG is a local-first intelligence engine built on a **Unified Knowledge Stack** (Postgres + Memgraph). It supports **Dual-Access** consumption via a **Stateless SPA Frontend** and **Enterprise Webhooks**.

## 2. System Architecture

### 2.1 The "Unified Knowledge Stack"
*   **PostgreSQL 16 (The Vault)**: Immutable Source-of-Truth, Vector Storage (768d), Audit Logs.
*   **Memgraph (The Brain)**: In-Memory Graph Reasoning, Path Optimization.
*   **Backend**: FastAPI (Python 3.11).
    *   **Ingestion Service**: Excel -> Vector.
    *   **Logic Service**: Postgres -> Memgraph.
    *   **Integrator Service**: Webhook Dispatcher & External API.

### 2.2 Frontend Architecture (Stateless Portal)
*   **Framework**: **React + Vite**.
*   **Styling**: **TailwindCSS** (Standard Utility).
*   **State Management**: **None/Minimal** (React Query cache only). Zero local persistence.
*   **Visualization**: **React Flow** (Graph Explorer).
*   **Deployment**: Dockerized (`nginx:alpine` serving static build).

### 2.3 Integration Architecture (Enterprise Bridge)
*   **Protocol**: REST (OpenAPI 3.1) + Webhooks.
*   **Security**: mTLS or API Key (via OpenBao) for Machine-to-Machine.
*   **Patterns**:
    *   **Outbound**: `POST /webhook` on key events (e.g., "New Risk Detected").
    *   **Inbound**: `GET /query?q=...` for graph reasoning.

## 3. The Knowledge Pipeline (Flow)
1.  **Harvest**: Ingest -> Vector.
2.  **Refinery**: De-conflict -> Flag.
3.  **Synthesis**: Project to Memgraph.
4.  **Grooming**: Agent Optimization.

## 4. Data Strategy: Dual-Schema (Refinery)

We employ a **Dual-Schema Strategy** to verify inputs against a raw source of truth.

### Table 1: OSCALCatalog (The Raw Source)
*   **Purpose**: Stores the "Entirety" of the uploaded file as a JSONB blob (Context Preserved).
*   **Schema**:
    *   `uuid` (PK)
    *   `catalog_name`
    *   `raw_file_content` (JSONB)
    *   `created_at`

### Table 2: FlattenedControlRecord (The Actionable Data)
*   **Purpose**: The "Refined" unit of compliance for Vector Search.
*   **Schema**:
    *   `id` (PK)
    *   `parent_catalog_uuid` (FK -> OSCALCatalog)
    *   `prose` (LLM Target)
    *   `embedding` (Vector 768d)
    *   `facets_json`

### The "Internal Refinery" Workflow
1.  **Ingest**: Save Raw -> `OSCALCatalog`.
2.  **Flatten**: Parse -> `FlattenedControlRecord`.
3.  **Conflict Check**: Compare Embeddings of New vs Existing.
    *   If Similarity > 0.92: Flag as `CONFLICT`.
    *   Else: Commit as `CLEAN`.
4.  **Sync**: `CLEAN` records -> Memgraph.

## 5. Integrity Guardrails
*   **Auditability**: Middleware intercepts every writable API call.
*   **Explainability**: `reasoning_trace` property on AI edges.
*   **Consistency**: Dual-Write (Postgres 1st, then Graph).
*   **Storage Separation**:
    *   **PostgreSQL**: Immutable record storage and vector embeddings.
    *   **Memgraph**: In-memory relational reasoning.

## 5. Hardware & Scalability
*   **Target**: NVIDIA DGX Spark.
*   **Vector Performance**: HNSW Index.
*   **Graph Performance**: In-Memory (128GB RAM).

## 6. Security
*   **Authentication**: Keycloak (OIDC).
*   **Secrets**: OpenBao.
*   **Data**: LUKS + `pgcrypto`.
