# Business Requirement Document (BRD)
## Clear Trace (CT) & Risk Control Knowledge Graph (RCKG) Suite

**Document Version:** 3.0 — Clear Trace Executive Control Tower Pivot  
**Status:** Approved / Active Baseline  
**Classification:** Internal — Confidential  
**Last Updated:** July 27, 2026  
**Supersedes:** `docs/01-initial/business-requirement.md` v2.0  
**Linked Requirements:**
- PRD: [02-product-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/02-product-requirement-doc.md) v3.0
- TRD: [03-technical-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/03-technical-requirement-doc.md) v7.0

---

## 1. Executive Summary

Global regulatory oversight of Artificial Intelligence and information security has reached a critical tipping point. High-stakes mandates — including the **EU AI Act**, **NIST AI Risk Management Framework (AI RMF 1.0)**, **ISO/IEC 42001**, **Digital Operational Resilience Act (DORA)**, **NIS 2**, **Colorado SB 24-205**, and **Texas HB 149** — demand that enterprise leaders move beyond paper attestations and manual surveys.

Historically, organizations relied on static Governance, Risk, and Compliance (GRC) tools built around annual manual surveys, self-certifications, and spreadsheet crosswalks. This approach creates severe organizational risk: executives receive stale compliance scores detached from actual production systems, while engineering teams suffer immense audit fatigue.

**Clear Trace (CT)** transforms the underlying **Risk and Control Knowledge Graph (RCKG)** platform into an **Agentic Executive Control Tower** for CIOs, CISOs, and Compliance Officers. Clear Trace establishes **"Provable Governance"**: bridging top-level organizational AI principles (e.g., *"Our AI must be Fair, Robust, and Safe"*) directly to verifiable, automated technical tests (e.g., DeepEval evaluation suites, drift metrics) and structured process evidence.

---

## 2. Business Context & Problem Statement

### 2.1 The "Checklist Governance" Problem

| Legacy Pain Point | Business Risk & Impact | Clear Trace Resolution |
|---|---|---|
| **Manual Survey Attestation** | Compliance relies on human questionnaires that are inaccurate, outdated within days, and easy to pencil-whip. | **Continuous Grounded Proof**: Directly links controls to automated technical tests (DeepEval) and auditable evidence. |
| **Siloed Relational Data** | Controls, regulations, and risk profiles live in disparate systems with no cross-framework alignment. | **Knowledge Graph Core**: Single interconnected graph linking Principles → Risks → Controls → Metrics → Evidence. |
| **Opaque Black-Box UI** | Executive dashboards show static green checkmarks without explainable proof or lineage. | **Tri-Panel Copilot**: Chat + Chain-of-Thought Reasoning Trace + Generative Canvas for live board-ready reporting. |
| **High Audit Overhead** | Engineering teams waste months re-testing identical controls for overlapping regulations. | **Automated Crosswalk Engine**: A single passed control automatically satisfies all mapped regulatory clauses. |
| **Air-Gap & On-Prem Blind Spots** | Third-party cloud SaaS GRC engines expose sensitive IP and violate sovereignty rules. | **DGX Spark Bare-Metal Deployment**: Self-hosted stack running native local vLLM (Llama-3.1-Nemotron-70B). |

### 2.2 Key Regulatory & Market Drivers

1. **EU AI Act Enforcement (2026)**: Mandates formal risk classification, mandatory bias mitigation, post-market monitoring, and strict technical log retention for High-Risk AI systems.
2. **NIST AI RMF 1.0 & ISO 42001**: Require continuous mapping, measuring, managing, and governing of AI risks across the full system lifecycle.
3. **Executive & Board Liability**: CISOs and CIOs face personal regulatory accountability for AI system failures, requiring undeniable audit trails and mathematical proof of compliance effort.
4. **Autonomous AI & Agentic Deployment**: Rapid adoption of autonomous LLM agents necessitates real-time guardrails and dynamic risk profiling rather than static annual assessments.

---

## 3. Core Business Vision & Value Proposition

```
   ┌─────────────────────────────────────────────────────────────┐
   │            CLEAR TRACE (CT) EXECUTIVE CONTROL TOWER         │
   │                                                             │
   │  "Bridge Organizational AI Principles directly to Live,    │
   │   Verifiable Technical Metric Evidence on DGX Spark."       │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
    ┌─────────────────────────────┴─────────────────────────────┐
    ▼                                                           ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐
│   TRI-PANEL AGENTIC WORKSPACE│              │ GROUNDED PRINCIPLES TO PROOF │
│ • Executive Natural Chat     │              │ • 5-Dim Risk Tiering Engine  │
│ • Real-time CoT Audit Trace  │              │ • DeepEval Technical Metrics │
│ • Generative Canvas Visuals  │              │ • Bifurcated Process Proof   │
└──────────────────────────────┘              └──────────────────────────────┘
```

**Core Value Proposition:** *One unified platform. Zero paper attestations. Every AI solution continuously profiled, evaluated against DeepEval metrics, mapped to global standards, and rendered in executive board-ready dashboards.*

---

## 4. Primary Business Objectives (BO)

### BO-01 — Executive AI Control Tower ("Provable Governance")
Establish an interactive Executive Control Tower that translates complex GRC topologies into actionable executive insights. The platform must replace static dashboards with an Agentic Tri-Panel Workspace capable of executing natural language audit requests, streaming reasoning traces, and rendering dynamic compliance canvases.

### BO-02 — Principles-to-Grounded-Testing Pipeline
Connect organizational AI Principles (*Fairness, Privacy, Safety, Accountability, Transparency*) down to testable engineering metrics. If a High-Risk AI system claims compliance with *Fairness*, the system must automatically execute and verify underlying DeepEval technical metrics (e.g., Demographic Parity, Bias Score < 0.05) and surface human process evidence.

### BO-03 — Zack/Wukongtai Minimum Viable Risk Tiering
Implement a standardized 5-dimension risk profiling engine (Facing, Jurisdiction, Agency, Business Impact, Data Sensitivity) coupled with a Black-Box Complexity Toggle. The engine must classify AI solutions into Tier 1 (Critical), Tier 2 (High), or Tier 3 (Standard), automatically triggering mandatory control sets without imposing unnecessary bureaucratic overhead on low-risk internal tools.

### BO-04 — High-Throughput DGX Spark Bare-Metal Infrastructure
Deploy the Clear Trace suite onto local NVIDIA DGX Spark infrastructure to support high-throughput, low-latency agent reasoning and local LLM evaluation. The stack must operate 100% on-premises with native vLLM (Llama-3.1-Nemotron-70B ARM64/CUDA 13.0) and automated CI/CD SSH rolling deployments.

### BO-05 — Dual-Write Graph & Relational Vault Architecture
Maintain an immutable dual-write data layer consisting of PostgreSQL (for transactional audit logs, static RCKG tables, and system risk profiles) and Memgraph (for multi-hop graph crosswalks and regulatory clause relationships), ensuring zero data loss and sub-second historical query response times.

### BO-06 — Continuous Regulatory Crosswalks & OSCAL Export
Automate the crosswalk mapping between internal corporate controls and major regulatory frameworks (NIST AI RMF, EU AI Act, ISO 42001, SOC 2). The system must natively generate NIST OSCAL 1.1.3 JSON/YAML machine-readable artifacts for instant external regulator submissions.

---

## 5. Stakeholder Matrix & Impact Analysis

| Stakeholder Persona | Key Needs & Objectives | Clear Trace Impact |
|---|---|---|
| **Chief Information Security Officer (CISO)** | Real-time visibility into AI deployment risks, regulatory non-compliance liabilities, and board reporting. | Instant executive scorecards by AI Principle; live audit-grade evidence trace. |
| **Chief Risk / Compliance Officer (CRO / CCO)** | Elimination of manual audit fatigue; compliance across overlapping EU AI Act & NIST frameworks. | 80% reduction in audit prep time via automated single-control crosswalks. |
| **AI System Owner / Product Manager** | Rapid risk profiling for new AI applications without slowing down release velocity. | 60-second risk profiling questionnaire with dynamic control triggering. |
| **Lead AI Engineer / Developer** | Clear technical requirements for AI guardrails; integration with evaluation tools (DeepEval). | Executable test definitions mapped directly to unit test / CI pipelines. |
| **External Regulator / Lead Auditor** | Unbroken lineage from regulatory clause down to code execution and evidence document hash. | Immutable bitemporal audit logs, Cypher graph query traces, and OSCAL export. |

---

## 6. Business Success Metrics (KPIs)

1. **Audit Preparation Velocity**: Reduce time required to assemble full multi-framework audit packages from **6 weeks to < 2 hours**.
2. **Evaluation Groundedness**: Achieve **100% technical control verification** against actual DeepEval runtime metric execution (zero ungrounded green status).
3. **Risk Tiering Efficiency**: Complete AI Solution risk profiling in **< 3 minutes** per application.
4. **Deployment Latency**: Achieve **< 5-second end-to-end response time** for agentic reasoning and canvas updates on DGX Spark vLLM.
5. **Cross-Framework Mapping Precision**: Maintain **> 90% precision** on regulatory crosswalk edge creations between internal controls and framework clauses.
