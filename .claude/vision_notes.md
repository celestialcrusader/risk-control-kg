# Vision & Roadmap: DeepEval UI to GRC Suite

## The Grand Vision
1. **Current State:** GenAI Evaluation Testkit (DeepEval Wrapper)
2. **Immediate Goal:** AI Governance Suite
3. **Mid-Term Goal:** IT Governance Platform
4. **Long-Term Goal:** Overall GRC (Governance, Risk, Compliance) Suite

---

## Phase 2: AI Governance Suite (Current Focus)

### Pillar 1: Business Capabilities & Features

#### Core Architecture: The "Principles to Grounded Testing" Pipeline
The fundamental goal of this phase is to bridge high-level organizational AI Policies with actual, verifiable evidence (both process-based and technical).

**1. Risk & Control Knowledge Graph (Static MVP)**
*   **Requirement:** An internal library mapping Risks to Controls.
*   **Implementation:** We will implement a relational SQLModel adaptation of the RCKG schema (`docs/tech_req/schema_architecture.md`).
    *   **AI Principle** (Top level organizational value, e.g., "Fairness")
    *   **Risk** (Mapped to Principle, e.g., "Algorithmic Bias")
    *   **Control** (Mapped to Risk, actionable requirement, Type: Process or Technical)
*   **Future Scope:** Integration with the external Memgraph/Postgres RCKG project.

**2. Organization AI Principles Definition**
*   **Requirement:** Organizations must be able to define their core AI principles (e.g., "Fairness", "Transparency", "Privacy", "Robustness").
*   **Implementation:** A management module where principles are defined and weighted.

**3. Inherent Risk Profiling Engine**
*   **Requirement:** A classification engine to categorize AI solutions based on characteristic variables to determine their inherent risk level.
*   **Variables:**
    *   Public-facing vs. Internal
    *   Level of Agency (Human-in-the-loop vs. Autonomous)
    *   Business Criticality
    *   Regulatory Jurisdictions
    *   Platform (Approved Low-Code vs. Custom Build)
    *   Data Sensitivity (PII, PHI, Confidential)
*   **Output:** Determines prioritization and the required strictness of the control environment.

**4. The Profiling Questionnaire & Control Mapping**
*   **Requirement:** High-inherent-risk systems trigger an assessment workflow.
*   **Flow:**
    1. AI Principles map to identified Risks (from the static RCKG).
    2. Risks map to suggested Controls (from the static RCKG).
    3. Organization's custom RCKG overrides the static MVP when available in the future.

**5. Bifurcated Control Validation**
*   **Requirement:** Controls are split into two validation streams.
    *   **Process-Based Controls:** Validated via human-in-the-loop questionnaires and document evidence uploads (extending the current `GovernanceModule`).
    *   **Technical Controls:** Validated via the existing DeepEval testkit engine (e.g., verifying a "Toxicity Control" triggers the `ToxicityMetric` test suite).

**6. The "Principle Scoring" Dashboard (Solution & Aggregate Levels)**
*   **Requirement:** Closing the loop. The results of the Bifurcated Control Validations (Pass/Fail/Score) roll up into the defined AI Principles.
*   **Views:**
    *   **Solution Level:** "How does *Chatbot Alpha* score against our principle of *Fairness* based on its technical bias metrics and process documentation?"
    *   **Aggregate Level:** "How is our entire organization doing on *Transparency* across all deployed AI?"
*   **Future Scope:** Live monitoring drift directly impacting the Principle Score.

**7. Baseline Organizational Governance (The Foundation)**
*   **Requirement:** General controls that apply to the organization, not tied to a specific AI deployment (e.g., "Does the org have an AI Ethics Board?").
*   **Implementation:** Separate from Solution-level tracking, mapping to a macro "AI Governance Maturity Benchmark."

### Pillar 2: Agentic AI & Generative UI (UX/UI Overhaul)

#### Core Architecture: The "Tri-Panel Copilot"
The static dashboard is replaced by an interactive, agent-driven workspace divided into three core sections.

**1. Interaction Section (The Chat)**
*   **Purpose:** The primary interface for the Auditor to give natural language instructions (e.g., "Profile the Alpha Chatbot," "Show me the technical control failures for the Fairness principle").
*   **Function:** Accepts text input and displays conversational responses from the AI Agent guiding the audit.

**2. Reasoning Section (Chain-of-Thought / Logs)**
*   **Purpose:** Transparency and Auditability.
*   **Function:** Displays the "Thinking Process" of the agent in real-time. It logs tools called, database queries executed, and shows the raw JSON data extracted (via MCP) before it gets rendered. Allows auditors to verify the Agent isn't hallucinating its actions.

**3. Generative UI Section (The Canvas)**
*   **Purpose:** Context-aware data visualization.
*   **Function:** High-fidelity React components (templates, charts, tables, forms) dynamically rendered based on the current interaction context. Instead of LLMs throwing markdown tables into a chat, the Agent passes structured JSON into curated React templates (e.g., passing a JSON risk profile to a styled `RadarChartComponent`).

#### Technical Guardrails & State Management
*   **Source of Truth:** All information shown in the Generative UI must strictly map to data fetched from the stateful PostgreSQL database. The Agent does *not* invent data; it fetches and formats it.
*   **Model Context Protocol (MCP):** Extraction of information and execution of actions are managed strictly via registered MCP tools (e.g., `get_inherent_risk_profile()`, `run_deepeval_test()`).
*   **Strict State Enforcement:** The UI/Agent enforces workflow dependencies. For example, the `run_deepeval_test` MCP tool will *fail* or the 'Run' button in the Generative UI will be *disabled* if the database state shows the `AISolution` lacks a completed `SystemRiskProfile`. The Agent cannot bypass the defined GRC lifecycle.
