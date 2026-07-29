# Clear Trace (CT) & RCKG Platform — Pickup Documentation

**Location:** `docs/02-pickup/`  
**Last Updated:** July 28, 2026  
**Status:** Baseline Established — Strategic Alignment & Pure RCKG Delta Complete  

---

## Overview

This directory contains the authoritative pickup documentation for the **Risk and Control Knowledge Graph (RCKG)** platform and **Clear Trace (CT)** suite. It documents the current state of the codebase, synthesizes the requirements, provides code audits, and defines the **Pure RCKG Delta Plan (`06-delta.md`)** focusing strictly on multi-source ingestion, 5-linkage graph topologies, mathematical set-theory classification, and AI agentic pruning.

---

## Included Documents

| File | Description | Key Focus |
|---|---|---|
| **[06-delta.md](file:///home/zackchow/coding/rckg/docs/02-pickup/06-delta.md)** | **Pure RCKG Strategic Realignment & Delta Plan** | **100% pure focus on Risk Control Knowledge Graphing**. Defines multi-source ingestion taxonomy, 5 explicit graph linkages, mathematical set-theory engine ($\equiv, \supset, \subset, \cap, \emptyset$), agentic pruning, current state delta, and next steps. (Defers Wukongtai / UI Copilot). |
| **[01-business-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/01-business-requirement-doc.md)** | Business Requirement Document (BRD v3.0) | Executive Control Tower vision, Provable Governance value prop, regulatory drivers (EU AI Act, NIST AI RMF, ISO 42001), DGX Spark infrastructure requirements, and business objectives. |
| **[02-product-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/02-product-requirement-doc.md)** | Product Requirement Document (PRD v3.0) | Product scope, user personas (CISO, Auditor, AI Owner, Risk Officer), Tri-Panel Copilot UX (Chat, Reasoning Trace, Generative Canvas), Zack/Wukongtai Risk Tiering model, and bifurcated control validation. |
| **[03-technical-requirement-doc.md](file:///home/zackchow/coding/rckg/docs/02-pickup/03-technical-requirement-doc.md)** | Technical Requirement Document (TRD v7.0) | System architecture, static RCKG SQLModel schema (`AIPrinciple`, `Risk`, `Control`, `SystemRiskProfile`, `ControlAssessment`), 3-layer vault, Vercel AI SDK v4 integration specs, Agent API (`/api/v1/agent/chat`), MCP tools, and DGX Spark bare-metal/vLLM specs. |
| **[04-current-state-of-code.md](file:///home/zackchow/coding/rckg/docs/02-pickup/04-current-state-of-code.md)** | State of the Code Audit | Line-by-line audit of existing backend Python code, ORM models, ingestion/extraction/judge/repair services, test suite coverage (25 test modules), Docker stack, frontend status, and identified gap matrix. |
| **[05-next-steps.md](file:///home/zackchow/coding/rckg/docs/02-pickup/05-next-steps.md)** | Actionable Next Steps & Execution Plan | Structured sprint plan (Sprint 0: DGX Spark infra & vLLM; Sprint 1: Static RCKG DB & Agent API; Sprint 2: Tri-Panel React Frontend; Sprint 3: DeepEval & E2E UAT) with detailed stories and acceptance criteria. |

---

## Strategic Alignment Summary (Pure RCKG Engine)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PURE RCKG GRAPH PROCESSING ENGINE                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. MULTI-SOURCE INGESTION TAXONOMY                                                     │
│    • Regulatory Docs       ──► Obligation                                              │
│    • Corporate Policies    ──► Control Objective                                       │
│    • Process/SOP/Guides    ──► Control Activity                                        │
│    • Industry Frameworks   ──► Framework Control Objective & Activity (ISO/NIST/IM8)   │
│    • Risk Inventories      ──► Risk                                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. EXPLICIT 5-LINKAGE TOPOLOGY                                                         │
│    • [Risk]              ◄──(MITIGATES / RISK_OF)──►     [Control Objective]           │
│    • [Obligation]         ◄──(SATISFIES / SATISFIED_BY)─►  [Control Objective]           │
│    • [Control Objective]  ◄──(OPERATIONALIZED_BY)────►    [Control Activity]            │
│    • [Control Objective]  ◄──(CROSSWALKS_TO_OBJ)─────►    [Framework Control Objective] │
│    • [Control Activity]   ◄──(CROSSWALKS_TO_ACT)─────►    [Framework Control Activity]  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. MATHEMATICAL SET-THEORY LINKAGE ENGINE (∀ Linkages)                                │
│    • EQUIVALENT_TO (≡)    │ SUPERSET_OF (⊃)     │ SUBSET_OF (⊂)                      │
│    • INTERSECTS_WITH (∩)  │ NO_RELATIONSHIP (∅)                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. AI AGENTIC PRUNING & TOPOLOGY BUILDER                                               │
│    • Dense/Sparse Candidate Edge Retrieval                                             │
│    • Dual-Judge Validation & Set-Theory Scoring                                        │
│    • Agentic Transitive Reduction & Redundancy Pruning                                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
