# Static RCKG Schema Design (DeepEval UI Integration)

Based on the RCKG `schema_architecture.md`, the canonical graph structure is:
`Framework -> ControlGroup -> ControlObjective <- ControlStatement -> Risk`

For the **AI Governance Suite (Phase 2 static implementation)** within DeepEval UI, we need to adapt this to support organization-specific *AI Principles* and *Inherent Risk Profiling*.

## Proposed Relational Database Schema (SQLModel)

This schema connects high-level organizational principles down to testable DeepEval metrics.

### 1. `AIPrinciple` (New)
The organization's top-level values.
*   `id`: UUID
*   `name`: str (e.g., "Fairness & Bias Mitigation")
*   `description`: str
*   `weight`: float (for aggregate scoring)

### 2. `Risk` (From RCKG)
Threats to the AI system or organization.
*   `id`: UUID
*   `principle_id`: UUID (Foreign Key to AIPrinciple)
*   `name`: str (e.g., "Algorithmic Bias against protected groups")
*   `description`: str
*   `severity_level`: Enum (LOW, MEDIUM, HIGH, CRITICAL)

### 3. `Control` (Targeting RCKG's "ControlStatement")
Actionable requirements to mitigate the risk.
*   `id`: UUID
*   `risk_id`: UUID (Foreign Key to Risk)
*   `name`: str (e.g., "Demographic Parity Testing")
*   `description`: str
*   `type`: Enum (PROCESS, TECHNICAL)
*   *If Process:* `evidence_required`: str (e.g., "Upload Bias Impact Assessment PDF")
*   *If Technical:* `deepeval_metric`: str (e.g., "bias")

### 4. `SystemRiskProfile` (New)
The output of the Inherent Risk Profiling Questionnaire for a specific `AISolution`.
*   `id`: UUID
*   `ai_solution_id`: UUID (Foreign Key to existing AISolution)
*   `deployment_type`: Enum (INTERNAL, PUBLIC)
*   `agency_level`: Enum (HITL, AUTONOMOUS)
*   `data_sensitivity`: Enum (PUBLIC, CONFIDENTIAL, PII)
*   `calculated_inherent_risk`: Enum (LOW, MEDIUM, HIGH)

### 5. `ControlAssessment` (Bridge Table)
Records the actual pass/fail state of a Control for a specific AI Solution.
*   `id`: UUID
*   `ai_solution_id`: UUID
*   `control_id`: UUID
*   `status`: Enum (PENDING, PASS, FAIL, N/A)
*   `evidence_link`: str (URL to uploaded doc, or ID of DeepEval `AuditRun`)
*   `assessed_by`: str (Auditor ID or "System")
*   `assessed_at`: timestamp

## The "Principles to Grounded Testing" Flow

1.  **Define:** Org defines `AIPrinciple` -> maps to possible `Risk`s -> mapped to mitigating `Control`s.
2.  **Profile:** A new `AISolution` is registered and profiled (`SystemRiskProfile`). If `calculated_inherent_risk` is HIGH, the system fetches all relevant `Controls`.
3.  **Assess (Process):** Auditor manually reviews Process Controls, uploads evidence, and marks `status` in `ControlAssessment`.
4.  **Assess (Technical):** Auditor triggers a DeepEval `AuditRun`. The system automatically checks the `TestCaseResult`. If the linked `deepeval_metric` (e.g., Bias) passes the threshold, the `ControlAssessment` status auto-updates to PASS.
5.  **Score:** The system aggregates `ControlAssessment` results grouping by `Risk` and rolling up to the `AIPrinciple` to generate the final dashboard score.
