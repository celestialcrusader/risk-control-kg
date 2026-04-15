# Risk & Control Knowledge Graph (RCKG) - UAT Guide

## Overview
This document guides you through the User Acceptance Testing (UAT) for the RCKG platform. It covers the end-to-end workflow from data ingestion to intelligent audit program generation.

## Prerequisites
1. **Start Services**:
   ```bash
   docker compose up -d
   ```
2. **Access Swagger UI**: Open `http://localhost:8000/docs`.
3. **Access Neo4j Browser**: Open `http://localhost:7474` (User: `neo4j`, Password: `password`).

---

## UAT Scenario 1: Data Ingestion (Story 5.3)
**Goal**: Verify that users can upload documents and they are strictly parsed into the graph.

1. **Prepare a Test File**: Create a simple CSV `test_control.csv` with headers `nist_ctrl_id, ctrl_grp, ctrl_txt` (e.g., `AC-100, Access, Test Description`).
2. **Upload**:
   - Go to `POST /api/ingest/`.
   - Upload the file.
3. **Verify**:
   - Response should be `200 OK`.
   - In Neo4j Query: `MATCH (n:Control {id: 'AC-100'}) RETURN n`.
   - **Expected Result**: Node exists with correct properties.

---

## UAT Scenario 2: Unstructured Ingestion & Confirmation (Story 4.1 & 6.1)
**Goal**: Verify LLM extraction and the "Draft -> Approve" workflow.

1. **Ingest PDF**:
   - Upload a PDF (e.g., NIST standard) to `POST /api/ingest/`.
   - The system will extract entities (Risks/Definitions) and tag them as `status='DRAFT'`.
2. **Review Drafts**:
   - Go to `GET /api/approvals/`.
   - **Expected Result**: See a list of extracted entities.
3. **Approve**:
   - Copy an `id` from the list.
   - Call `POST /api/approvals/{id}/approve`.
4. **Verify**:
   - Check `GET /api/approvals/` -> Item should be gone.
   - In Neo4j: `MATCH (n) WHERE elementId(n) = '{id}' RETURN n.status`.
   - **Expected Result**: Status is `APPROVED`.

---

## UAT Scenario 3: Context-Aware Chat (Story 5.2)
**Goal**: Verify the GraphRAG capability.

1. **Ask a Question**:
   - Go to `POST /api/chat/`.
   - Body: `{"message": "What risks are associated with Access Control?"}`
2. **Verify**:
   - **Expected Result**: A JSON response containing a natural language answer and a list of `sources` (node names) used from the graph.

---

## UAT Scenario 4: Audit Program Generator (Story 6.3)
**Goal**: Verify the system can synthesize an audit plan.

1. **Generate**:
   - Go to `POST /api/audit/generate`.
   - Body: `{"topic": "Access Control"}`.
2. **Verify**:
   - **Expected Result**: A structured JSON response with:
     - `topic`: "Access Control"
     - `audit_steps`: List of steps including `test_objective`, `test_steps`, and `expected_evidence`.
     - Data should be relevant to the controls in the graph (e.g., referencing "AC-1").

---

## Automated Verification
To run the full suite of automated regression tests:
```bash
./venv/bin/pytest backend/tests/
```
