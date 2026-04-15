# Knowledge Pipeline Guide: Raw to Golden

This guide documents the "Silver Layer" transformation pipeline, detailing how raw text from PostgreSQL is transformed into structured "Golden Data" for the Knowledge Graph.

## Pipeline Architecture

The pipeline follows a tiered data architecture:
1.  **Bronze Layer (Raw)**: Unstructured text from PDFs/CSVs. Stored in `staging_controls`.
2.  **Silver Layer (Semantic)**: AI-enriched, structured hierarchy (Framework -> Risk). Stored in `semantic_controls`.
3.  **Gold Layer (Validated)**: Final, verified/versioned data. Stored in `golden_controls`.

---

## 1. Data Models (`backend/app/models/sql.py`)
Defines the database schema for all layers.
*   **`StagingControlRecord` (Bronze)**:
    *   *Fields*: `raw_text`, `canonical_id`, `extracted_metadata`.
*   **`SemanticControlRecord` (Silver)**:
    *   *Structure*:
        1.  **Framework**: `framework_name`, `version`.
        2.  **Group**: `group_id`, `group_name`.
        3.  **Objective**: `objective_id`, `objective_text` (Blue Header).
        4.  **Statement**: `statement_id`, `statement_text`, `action_verb`, `subject_noun`, `gov_domain`.
        5.  **Risk**: `risk_name`.
*   **`GoldenControlRecord` (Gold)**: Validated Silver record.

## 2. Silver Transformation (`backend/scripts/transform_silver.py`)
**Purpose**: The AI "Refinery". Extracts the 5-layer hierarchy from Bronze data.
*   **Process**:
    *   Input: `staging_controls` (Pending).
    *   AI Action: Extracts Objective, Statement, and attributes like `action_verb` and `subject_noun` for STRM analysis.
    *   Output: `semantic_controls`.

## 3. Graph Synchronization (`backend/app/services/graph/sync.py`)
**Purpose**: Projects Gold records into the Memgraph schema.
*   **Topology**:
    *   `Framework -> HAS_GROUP -> Group`
    *   `Group -> CONTAINS -> Objective`
    *   `Statement -> ACHIEVES -> Objective`
    *   `Statement -> MITIGATES -> Risk`
*   **Crosswalk**: `Statement -> SUBSET_OF -> Statement`.

## 5. Verification (`backend/scripts/check_silver.py`)
**Purpose**: A utility script to inspect the results of the transformation.
*   **Usage**: Run this to preview the generated Semantic Records (Objective, Statement, Rationale) and verify database persistence.

---

## Usage Workflow

1.  **Ingest Raw Data**: (Already done via `ingest_manual.py` -> `staging_controls`).
2.  **Run Transformation**:
    ```bash
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/ollama/cuda_v12
    python backend/scripts/transform_silver.py
    ```
3.  **Verify Results**:
    ```bash
    python backend/scripts/check_silver.py
    ```
4.  **Promote to Gold & Sync**: (Upcoming step in Sprint 4).
