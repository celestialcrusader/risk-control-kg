# Actionable Next Steps & Implementation Roadmap
## Clear Trace (CT) & Risk Control Knowledge Graph (RCKG) Suite

**Document Version:** 1.0 — Active Action Plan  
**Status:** Approved for Execution  
**Classification:** Internal — Confidential  
**Last Updated:** July 27, 2026  
**Linked Documents:**
- BRD: [01-business-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/01-business-requirement-doc.md) v3.0
- PRD: [02-product-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/02-product-requirement-doc.md) v3.0
- TRD: [03-technical-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/03-technical-requirement-doc.md) v7.0
- Code Audit: [04-current-state-of-code.md](file:///home/zackchow/coding/rckg/docs/02-pickup/04-current-state-of-code.md)

---

## 1. Execution Overview & Roadmap Phasing

To transition the existing RCKG backend into the fully operational **Clear Trace Executive Control Tower**, work is structured into four sequential, high-velocity phases:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 0 (Sprint 0): DGX Spark Bare-Metal & vLLM Inference Engine Setup     │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1 (Sprint 1): Backend Static RCKG Schema & Agent API Implementation  │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2 (Sprint 2): Tri-Panel React Workspace & Generative Canvas Build    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3 (Sprint 3): DeepEval Grounded Metrics & End-to-End UAT Validation   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Phase 0 (Sprint 0) — DGX Spark Infrastructure Rollout

### Story 0.1 — Bare-Metal OS & Host Provisioning
- **Task:** Flash the NVIDIA DGX Spark box with **Ubuntu 24.04 LTS (ARM64)**, install **NVIDIA CUDA Toolkit 13.0**, NVIDIA Container Toolkit, and Docker Engine.
- **Acceptance Criteria:**
  - `nvidia-smi` displays GPU devices and CUDA 13.0 runtime cleanly on ARM64 host.
  - Docker container runtime successfully executes GPU-accelerated container test (`docker run --gpus all ubuntu nvidia-smi`).

### Story 0.2 — Native ARM64 vLLM Compilation & Model Deployment
- **Task:** Compile **vLLM natively on ARM64** with CUDA 13.0, download `Llama-3.1-Nemotron-70B-Instruct` quantized model files, and launch vLLM local API server.
- **Acceptance Criteria:**
  - Local vLLM server active on `http://localhost:8000/v1` serving OpenAI-compatible completion endpoints.
  - Inference latency for streaming tokens is `< 1.0s` to first token with zero external network access (100% air-gapped).

### Story 0.3 — Automated CI/CD SSH Rolling Deployment Pipeline
- **Task:** Configure CI/CD runner script (GitLab/Jenkins) with SSH access to the DGX Spark box.
- **Acceptance Criteria:**
  - A git push to `main` automatically triggers SSH execution, pulls updated code, and runs `docker-compose -f docker-compose.yml -f docker-compose.dgx.yml up -d --build`.
  - Deployment completes with zero downtime for backend API health checks.

---

## 3. Phase 1 (Sprint 1) — Backend Static RCKG Database & Agent API

### Story 1.1 — SQLModel Static RCKG Schema Implementation
- **Task:** Create `backend/app/models/audit.py` implementing SQLModel classes for `AIPrinciple`, `Risk`, `Control`, `SystemRiskProfile`, and `ControlAssessment` per TRD v7.0. Generate and run Alembic database migration.
- **Acceptance Criteria:**
  - Tables created in PostgreSQL 16 database with proper primary keys, foreign key constraints, and indexes.
  - Pytest suite verifies CRUD operations for all 5 new models.

### Story 1.2 — FastAPI Agent Chat Endpoint (`/api/v1/agent/chat`)
- **Task:** Create `backend/app/api/agent.py` implementing a streaming chat endpoint compatible with Vercel AI SDK protocols. Connect LLM agent logic to local vLLM endpoint.
- **Acceptance Criteria:**
  - Endpoint handles POST requests containing user message arrays, returning HTTP Server-Sent Events (SSE) stream.
  - Supports structured tool call emissions.

### Story 1.3 — Model Context Protocol (MCP) Tool Bridge Functions
- **Task:** Implement backend service functions exposed as MCP tools to the LLM agent:
  - `get_inherent_risk_profile(ai_solution_id)`
  - `calculate_risk_tier(ai_solution_id, facing, jurisdiction, agency, impact, data, is_black_box)`
  - `assess_control(ai_solution_id, control_id, status, evidence_link)`
  - `get_principle_dashboard_score(ai_solution_id)`
- **Acceptance Criteria:**
  - Agent can successfully invoke tools to query PostgreSQL DB and execute Zack/Wukongtai 5-dimension risk scoring logic.

---

## 4. Phase 2 (Sprint 2) — Tri-Panel React Workspace & Generative Canvas

### Story 2.1 — React Vite Frontend Setup with Vercel AI SDK v4
- **Task:** Initialize React Vite application in `backend/frontend/` with Tailwind CSS, Shadcn UI, and `@ai-sdk/react` v4.
- **Acceptance Criteria:**
  - Frontend uses `DefaultChatTransport` explicitly pointing to `/api/v1/agent/chat`.
  - Text input state managed via local React `useState` and dispatched using `sendMessage`.

### Story 2.2 — Tri-Panel Workspace Layout (`/workspace`)
- **Task:** Build `TriPanelWorkspace` component featuring:
  - Left Panel: Chat Interface (Input & Message Stream).
  - Center Panel: Real-Time Chain-of-Thought (CoT) & MCP Tool Trace viewer.
  - Right Panel: Generative Canvas.
- **Acceptance Criteria:**
  - Layout is fluid, responsive, and updates canvas views based on LLM command events.

### Story 2.3 — Renderable Canvas Widgets Migration
- **Task:** Refactor existing UI components into renderable canvas widgets:
  - `NistRadarChartWidget`: Renders NIST AI RMF scores.
  - `RiskQuestionnaireWidget`: 5-dimension interactive slider questionnaire.
  - `ControlResultsTableWidget`: Interactive Pass/Fail control breakdown.
- **Acceptance Criteria:**
  - Canvas components receive verified props fetched directly from FastAPI backend, guaranteeing zero hallucinated data from LLM text.

---

## 5. Phase 3 (Sprint 3) — Grounded Testing & End-to-End Validation

### Story 3.1 — DeepEval Metric Integration & Auto-Assessment
- **Task:** Connect DeepEval evaluation runner output (e.g. BiasMetric score) to auto-update `ControlAssessment` status in PostgreSQL.
- **Acceptance Criteria:**
  - Executing a DeepEval test suite with `bias_score = 0.02` (< 0.05 threshold) automatically updates linked `ControlAssessment` status from `PENDING` to `PASS`.

### Story 3.2 — End-to-End Executive Audit & OSCAL Export Validation
- **Task:** Perform full UAT workflow: Profile new AI application -> View dynamic Tier 2 assignment -> Execute DeepEval test -> Verify AI Principle Fairness score rollup -> Export NIST OSCAL 1.1.3 JSON package.
- **Acceptance Criteria:**
  - Complete end-to-end execution verified cleanly with zero errors.
  - Exported OSCAL JSON package passes official NIST OSCAL schema validation.

---

## 6. Immediate Recommended Action Items for Next Developer

1. **Verify Backend Tests:** Run `pytest backend/tests` to confirm baseline 3-layer vault ingestion tests pass.
2. **Implement SQLModel Schemas:** Add `backend/app/models/audit.py` with `AIPrinciple`, `Risk`, `Control`, `SystemRiskProfile`, and `ControlAssessment`.
3. **Initialize Frontend App:** Run `npm create vite@latest backend/frontend -- --template react-ts` and install `@ai-sdk/react` v4.
4. **Deploy Infrastructure:** Execute `docker compose -f docker-compose.yml -f docker-compose.dgx.yml up -d` to launch the database stack.
