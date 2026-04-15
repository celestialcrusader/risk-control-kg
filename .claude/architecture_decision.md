# Phase 2: Architecture Impact Assessment & Decision

## 1. Goal
Transition DeepEval UI from a static "Dashboard & Forms" application to an **Agentic AI Governance Suite** with a Tri-Panel UI (Chat, CoT, Generative Canvas).

## 2. Codebase Impact Analysis

### Backend (Python/FastAPI)
*   **Current State:** Clean, resource-based REST API (`/projects`, `/datasets`, `/evaluations`). Direct database manipulation via SQLModel.
*   **Impact:** **MEDIUM**. The core data models (extended for RCKG) remain valid. However, we need to introduce a new **Agent Interaction Layer**. 
    *   *New Requirement:* An endpoint (e.g., `/api/chat`) that handles stateful conversation streams.
    *   *New Requirement:* MCP Tool bridging (exposing existing REST logic like "Run Audit" as callable tools for the LLM).
*   **Verdict:** **Bolt-on / Extend**. The FastAPI backend is solid. We just need to add the Agentic API endpoints and the static RCKG tables. No need to rewrite the evaluation engine.

### Frontend (React/Vite)
*   **Current State:** Highly structured, page-based routing (`/projects/:id`, `/evaluations/new`). Heavy reliance on large, static complex components (`AdvancedEvaluationWizard.tsx` is 43KB, `ResultsTable.tsx` is 39KB).
*   **Impact:** **HIGH**. The entire paradigm changes. Users won't navigate to `/evaluations/new` and fill out a 5-step wizard. They will type "Start a new evaluation for Chatbot Alpha" in a master interface, and the canvas will render the necessary config widgets.
*   **Verdict:** **Refactor (Structural Pivot)**. 
    1.  We need to consolidate the root UI into the `TriPanelWorkspace`.
    2.  We **DO NOT** throw away the existing UI components. Instead, we refactor components like `ResultsTable`, `MetricConfig`, and `RunAuditConfirmation` to act as **"Renderable Widgets"**. They should expect to receive data props via the LLM (from the active context state) rather than fetching it all themselves on page load.

## 3. Recommended Approach: The "Strangler Fig" Refactor

We should not start from scratch. The DeepEval integration, DB logic, and Shadcn UI components represent immense value.

**Step 1: Database Foundation (Bolt-on)**
Implement the new RCKG tables (`AIPrinciple`, `Risk`, `Control`, etc.) into `models/audit.py` alongside the existing ones.

**Step 2: The Agent API (Extend)**
Create `app/api/v1/endpoints/agent.py` to handle the LLM chat logic, providing it tools to query the DB and trigger DeepEval runs.

**Step 3: The Tri-Panel Workspace (Refactor)**
Create a new major route: `/workspace`. 
*   Left Panel: Chat Interface.
*   Right Panel (Canvas): A dynamic component renderer. 
Instead of forcing users immediately off the old UI, we build the `/workspace` alongside the legacy dashboards. Gradually, as the Agent becomes capable of rendering all legacy views (like the `ResultsDashboard`) inside its Canvas, we deprecate the old static router pages.

## 4. Addressing Guardrails
*   The Agent API will use LangChain/LlamaIndex (or direct API calls with strict system prompts) to orchestrate tools.
*   **State Constraint:** The Generative Canvas will *never* render raw JSON strings from the LLM. The LLM will return a command: `{ "action": "RENDER_DASHBOARD", "data_id": "run-1234" }`. The React frontend will then fetch `run-1234` from the real FastAPI backend and pass it to the `<ResultsDashboard />` component. This guarantees the LLM cannot hallucinate fake compliance passing scores on the screen.
