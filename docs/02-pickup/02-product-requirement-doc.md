# Product Requirement Document (PRD)
## Clear Trace (CT) & Risk Control Knowledge Graph (RCKG) Suite

**Document Version:** 3.0 — Clear Trace Executive Control Tower Pivot  
**Status:** Approved / Active Baseline  
**Classification:** Internal — Confidential  
**Last Updated:** July 27, 2026  
**Supersedes:** `docs/01-initial/product-requirement.md` v2.0  
**Linked Requirements:**
- BRD: [01-business-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/01-business-requirement-doc.md) v3.0
- TRD: [03-technical-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/03-technical-requirement-doc.md) v7.0

---

## 1. Product Vision & Scope

The **Clear Trace (CT)** AI Governance Suite is an interactive Executive Control Tower that bridges organizational AI Principles directly to grounded, executable technical metrics and process evidence. Built on top of the **Risk and Control Knowledge Graph (RCKG)** engine, Clear Trace transitions enterprise compliance from static paper checklists to continuous, data-driven "Provable Governance."

### Core Product Scope
Clear Trace integrates six functional core modules into a single web application:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLEAR TRACE (CT) EXECUTIVE CONTROL TOWER                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  MODULE 1: Tri-Panel Copilot Workspace (Chat, Reasoning CoT, Canvas)       │
├─────────────────────────────────────────────────────────────────────────────┤
│  MODULE 2: Inherent Risk Profiling Engine (Zack/Wukongtai 5-Dim Model)      │
├─────────────────────────────────────────────────────────────────────────────┤
│  MODULE 3: Principles-to-Grounded-Testing Pipeline (DeepEval + Evidence)   │
├─────────────────────────────────────────────────────────────────────────────┤
│  MODULE 4: Executive Principle Scoring & Board Reporting                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  MODULE 5: RCKG Graph Engine, Crosswalks & OSCAL Export                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  MODULE 6: DGX Spark Infrastructure & Native vLLM Deployment                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. User Personas & Scenarios

### 2.1 CISO / CIO — "Executive Cam"
- **Goal:** Maintain immediate, board-level awareness of total AI deployment risk across all business units without wading through technical code repositories.
- **Workflow:** Opens the `/workspace` Tri-Panel UI, types *"Generate our NIST AI RMF executive status report,"* reviews the real-time reasoning trace, and inspects the interactive radar chart rendered on the Generative Canvas.

### 2.2 Compliance Officer / Auditor — "Alex"
- **Goal:** Conduct thorough, verifiable audits for new AI solutions and generate audit-grade evidence packages for regulators (EU AI Act / NIST).
- **Workflow:** Queries the Copilot for *"Chatbot Alpha Fairness controls,"* views the split between DeepEval technical metric scores (e.g. Bias score 0.02 = PASS) and process evidence uploads, then clicks *"Export NIST OSCAL Package"*.

### 2.3 AI Solution Owner / Product Manager — "Jordan"
- **Goal:** Profile a newly proposed LLM application in under 3 minutes to determine required controls before launching to production.
- **Workflow:** Completes the 5-dimension Inherent Risk Profiling questionnaire via the Copilot canvas, receives an automatic Tier 2 (High Risk) classification, and views the generated control checklist.

---

## 3. Detailed Feature Requirements

### 3.1 Module 1 — Tri-Panel Copilot Workspace (`/workspace`)

#### FR-1.1 Tri-Panel UX Layout & Component Architecture
The core interface must feature a synchronized 3-panel layout:
- **Left Panel (Chat Interface):** Accepts natural language prompts, displays user/assistant message history, manages active session state using Vercel AI SDK v4 (`@ai-sdk/react`).
- **Center Panel (Reasoning CoT & Tool Trace):** Displays real-time streaming Chain-of-Thought logs, Model Context Protocol (MCP) tool execution parameters, database query outputs, and raw extracted JSON data for total transparency.
- **Right Panel (Generative Canvas):** A dynamic React widget renderer that accepts structured JSON commands from the LLM and renders high-fidelity interactive UI components (Charts, Tables, Questionnaires, Reports) rather than raw Markdown text.

#### FR-1.2 Generative UI Guardrail & State Isolation
- The Generative Canvas **must never** render hallucinated metrics from LLM text output.
- The LLM streams a structured command event (e.g. `{ "action": "RENDER_WIDGET", "widget": "ResultsDashboard", "data_id": "eval-9821" }`).
- The React frontend receives the command, fetches the authoritative state directly from the FastAPI backend, and passes verified data props into the UI component.

---

### 3.2 Module 2 — Inherent Risk Profiling Engine (Zack/Wukongtai Model)

#### FR-2.1 The 5 Core Dimension Scorer
The engine must compute an AI Solution's Inherent Risk Score based on 5 quantitative dimensions scored 1 (Low), 3 (Medium), or 5 (High):

| Dimension | Low (1 Pt) | Medium (3 Pts) | High (5 Pts) |
|---|---|---|---|
| **1. Facing** | Internal Ops / Security | Public-Facing Internal Ops (HR/Loans) | Direct Public Interaction (External Users) |
| **2. Jurisdiction** | No AI Laws (General IT) | Standard Privacy (GDPR/CCPA) | Strict AI Laws (EU AI Act, State AI Laws) |
| **3. Agency** | Pure Drafting / Generation | Human-in-the-Loop (Approve/Reject) | Autonomous System Execution |
| **4. Business Impact** | Productivity Inconvenience | Operational Breakdown / Moderate Fine | Financial Ruin / Safety / Critical Fines |
| **5. Data Sensitivity** | Public / Non-PII Data | Internal / Confidential / PII | Top Secret / Biometrics / Financial PII |

#### FR-2.2 The Black-Box Complexity Toggle
- **Trigger Rule:** If calculated Tier is Tier 1 (Critical, Score 20-25) or Tier 2 (High, Score 12-19) **AND** the AI model utilizes a Black-Box architecture (e.g., Deep Learning, Large Language Models), the system automatically enforces **Mandatory Explainability Controls** (SHAP, LIME, or Model Card attestations).
- For low-risk internal LLMs (Score < 12), the Explainability Control remains optional.

#### FR-2.3 Automatic Tier Assignment & Control Generation
- **Tier 1 (Critical, 20-25 pts):** Mandates Red Teaming, Mandatory Explainability, Third-Party Audit, and DeepEval Toxicity/Bias suites.
- **Tier 2 (High, 12-19 pts):** Mandates Demographic Parity Testing, Human-in-the-Loop approval workflows, Data Lineage tracking.
- **Tier 3 (Standard, 5-11 pts):** Basic Vulnerability Scan + Standard Usage Policy.

---

### 3.3 Module 3 — Principles-to-Grounded-Testing Pipeline

#### FR-3.1 Relational RCKG Schema Integration
The backend must maintain the relational mapping structure:
$$\text{AIPrinciple} \longrightarrow \text{Risk} \longrightarrow \text{Control} \longrightarrow \text{ControlAssessment}$$

- **`AIPrinciple`**: Top-level value (e.g., *Fairness & Bias Mitigation*, *Safety & Robustness*, *Privacy*).
- **`Risk`**: Identified threat (e.g., *Algorithmic Bias against protected demographics*).
- **`Control`**: Actionable requirement (Type: `TECHNICAL` or `PROCESS`).

#### FR-3.2 Bifurcated Control Validation Stream
- **Technical Controls:** Bound directly to DeepEval metric suites (e.g., `BiasMetric`, `ToxicityMetric`, `FaithfulnessMetric`, `HallucinationMetric`). Execution of an evaluation automatically updates `ControlAssessment` to `PASS` or `FAIL`.
- **Process Controls:** Validated via human upload of evidence artifacts (PDFs, policy docs, sign-off logs). `ControlAssessment` remains `PENDING` until human auditor approval.

---

### 3.4 Module 4 — Executive Principle Scoring & Board Dashboard

#### FR-4.1 Aggregate & Solution-Level Principle Scoring
The system must aggregate `ControlAssessment` outcomes to calculate dynamic Principle Scores (0.0% to 100.0%):
- **Solution Level:** `"Chatbot Alpha score against Fairness: 94% (Technical: 100% PASS, Process: 88% PASS)"`.
- **Organizational Level:** `"Global Corporate Alignment on Transparency across all 14 deployed AI systems: 87.5%"`.

#### FR-4.2 Board-Ready Artifact Rendering
Generative Canvas must support one-click rendering and export of:
- **NIST AI RMF Executive Radar Chart**
- **EU AI Act High-Risk System Compliance Ledger**
- **NIST OSCAL 1.1.3 JSON/YAML Machine-Readable Packages**

---

### 3.5 Module 5 — RCKG Graph Engine & Crosswalks

#### FR-5.1 Multi-Hop Cypher Graph Reasoning
Maintains Memgraph property graph containing:
`Framework -> ControlGroup -> ControlObjective <- ControlStatement -> Risk`
Supports Cypher multi-hop queries for regulatory gap detection, e.g., finding all NIST SP 800-53 controls that satisfy EU AI Act Article 10 data governance mandates.

---

### 3.6 Module 6 — Infrastructure & DGX Spark Deployment

#### FR-6.1 Bare-Metal DGX Spark Deployment
- **Target OS:** Ubuntu 24.04 LTS ARM64.
- **Hardware Drivers:** NVIDIA CUDA Toolkit 13.0, NVIDIA Container Toolkit.
- **Inference Engine:** Natively compiled **vLLM engine on ARM64** hosting `Llama-3.1-Nemotron-70B` locally with zero external API calls.
- **Automated CI/CD:** GitLab/Jenkins SSH pipeline executing automated rolling updates (`docker-compose -f docker-compose.yml -f docker-compose.dgx.yml up -d --build`).

---

## 4. Non-Functional Requirements (NFRs)

### NFR-1 — Performance & Latency
- Agentic Chat response streaming first-token latency **< 1.0s** on DGX Spark.
- Canvas widget data fetch and render time **< 300ms**.
- DeepEval technical metric execution suite completion **< 45s** for standard test batches.

### NFR-2 — Security & Air-Gap Compliance
- **Zero Remote Dependencies:** 100% of LLM inferencing, embedding generation, graph queries, and data processing must execute locally inside the DGX Spark environment.
- **Role-Based Access Control (RBAC):** Strict isolation between CISO (read-all/executive export), Auditor (evidence sign-off), and Engineer (test runner) roles.

### NFR-3 — Audit Traceability & Bitemporality
- All graph nodes, control assessments, and audit logs must retain bitemporal timestamps (`valid_from`, `valid_to`, `ingested_at`) to enable historical compliance reconstruction for any specified historical date.
