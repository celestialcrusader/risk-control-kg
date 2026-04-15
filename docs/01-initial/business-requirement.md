# Business Requirements Document (BRD)
## Risk and Control Knowledge Graph (RCKG) Platform

**Document Version:** 2.0 — End-State Architecture Alignment  
**Status:** Draft  
**Classification:** Internal — Confidential  
**Last Updated:** April 13, 2026  
**Linked TRD:** `docs/01-initial/master_tech_req.md` v6.0 — End-State Architecture

---

## 1. Executive Summary

Global regulatory complexity has reached an inflection point. Overlapping mandates — including the EU AI Act, DORA, NIS 2, Colorado SB 24-205, and Texas HB 149 — impose thousands of granular, continuously evolving obligations that traditional compliance methodologies cannot absorb at the required velocity. Manual spreadsheet-driven crosswalks, annual audit cycles, and siloed relational databases have reached their functional limits.

This document defines the business requirements for the **Risk and Control Knowledge Graph (RCKG)** platform: an AI-native, graph-augmented compliance architecture designed to transition the organization from a reactive, manual compliance posture into a **continuous, deterministic, and fully traceable operational compliance state**.

---

## 2. Business Context and Problem Statement

### 2.1 Current State Pain Points

| Pain Point | Business Impact |
|---|---|
| Manual control-to-regulation mapping across overlapping frameworks | Months of effort per audit cycle; high error rate; severe audit fatigue |
| Static, siloed compliance databases | No cross-framework correlation; duplicate evidence collection |
| Annual audit cadence | Real-time regulatory changes go undetected; gaps accumulate |
| Legacy OCR-based document ingestion | Loss of regulatory clause structure; misinterpretation of obligations |
| No temporal governance on outdated regulations | Stale obligations remain active; historical audit trails are destroyed on update |
| Brittle Python orchestration scripts for compliance workflows | High maintenance cost; poor portability; specialist dependency |
| Lack of audit-grade traceability for AI-generated compliance determinations | Regulatory bodies reject black-box AI outputs; no explanation of reasoning path |
| Inability to reconstruct historical compliance posture for legal audits | Cannot demonstrate "compliance as of date X" for regulatory examination |

### 2.2 Regulatory Drivers

The following regulatory frameworks create overlapping, simultaneous compliance obligations that the RCKG must address:

- **EU AI Act** — Risk classification and documentation mandates for AI systems
- **Digital Operational Resilience Act (DORA)** — ICT risk management and incident reporting
- **NIS 2 Directive** — Network and information security obligations
- **Colorado SB 24-205 / Texas HB 149** — US state-level AI governance mandates
- **NIST Cybersecurity Framework (CSF)** — Foundational control library
- **NIST SP 800-53** — Security and privacy controls for federal information systems
- **ISO/IEC 27001** — Information security management requirements
- **ISO 42001** — AI management system requirements (new 2023 standard)
- **SOC 2** — Trust Services Criteria for cloud and SaaS operations
- **SOX** — Internal financial controls and audit requirements
- **ESRS (EU)** — European Sustainability Reporting Standards for ESG compliance
- **TCFD** — Task Force on Climate-related Financial Disclosures

---

## 3. Business Objectives

### 3.1 Primary Objectives

**BO-01 — Continuous Compliance Monitoring**  
Transition the compliance function from an annual audit exercise into a real-time, continuous operational capability. The system shall monitor, detect, and surface control gaps against all registered regulatory frameworks on an ongoing basis without human-triggered initiation.

**BO-02 — Eliminate Audit Fatigue Through Automated Crosswalks**  
Automate the mapping of internal corporate controls to external regulatory obligations across all registered frameworks. A single evidenced control must automatically satisfy all overlapping regulatory requirements it covers, eliminating redundant evidence collection.

**BO-03 — Deterministic, Traceable Compliance Reasoning**  
All compliance status determinations must be fully explainable, traceable to a verifiable source, and auditable at the reasoning-path level. The system must eliminate hallucination risk inherent in pure probabilistic AI inference.

**BO-04 — Reduce Compliance Engineering Overhead**  
Reduce the engineering effort required to maintain, update, and extend compliance logic by abstracting orchestration into human-readable declarative specifications (agents.md, skills.md) rather than hardcoded programmatic scripts.

**BO-05 — Preserve Full Temporal Audit Trail**  
The system must never destroy historical compliance states when regulations are updated or superseded. All prior compliance postures must remain queryable for legal auditability.

**BO-06 — Dual-Judge AI Validation for Audit-Grade Confidence**  
All AI-generated compliance determinations must be independently validated by two specialized AI judges (Logic Judge for semantic faithfulness, Technical Judge for parameter precision) before committing to the production graph. Any determination failing the dual-judge threshold must trigger human-in-the-loop review.

**BO-07 — Self-Hosted, Air-Gap Compliant Deployment**  
The platform must be fully deployable in air-gapped environments with zero external API dependencies. All AI models, embedding services, and orchestration engines must be capable of running on-premises or within classified network boundaries.

**BO-08 — Continuous Model Improvement via HITL Feedback Loop**  
Human corrections from HITL review sessions must automatically feed a Direct Preference Optimization (DPO) fine-tuning pipeline that continuously improves extraction and classification accuracy over time without manual retraining cycles.

### 3.2 Secondary Objectives

**BO-11** — Support multi-language regulatory ingestion for global operations (84+ languages via BGE-M3 multilingual embeddings)  
**BO-12** — Enable compliance-as-code workflows integrated with CI/CD pipelines  
**BO-13** — Reduce manual audit preparation time from months to days  
**BO-14** — Generate machine-readable compliance artifacts (OSCAL JSON/XML/YAML) automatically  
**BO-15** — Provide hot/cold graph separation for 10-year historical retention with sub-second active queries  
**BO-16** — Enable third-party vendor risk tracking with `ThirdParty` node integration and `VENDOR_OF` edges  
**BO-17** — Support ESG risk dimension with ESRS, GRI, and TCFD crosswalks  
**BO-18** — Provide executive dashboard with real-time board-level compliance posture visualization

---

## 4. Stakeholders

### 4.1 Primary Stakeholders

| Stakeholder Group | Role | Key Interest |
|---|---|---|
| Chief Compliance Officer (CCO) | Executive Sponsor | Continuous compliance posture visibility; regulatory exposure reduction |
| Chief Information Security Officer (CISO) | Co-Sponsor | Control coverage mapping; security framework alignment |
| Internal Audit Leadership | Primary User | Automated evidence collection; audit trail completeness |
| Risk Management Team | Primary User | Real-time risk identification; gap detection and remediation tracking |
| Legal & Regulatory Affairs | Advisory | Regulatory interpretation accuracy; temporal obligation management |

### 4.2 Secondary Stakeholders

| Stakeholder Group | Key Interest |
|---|---|
| GRC Platform Administrators | System configuration; integration management |
| Enterprise Architecture | Technology stack alignment; data governance |
| DevSecOps / Engineering | CI/CD integration; compliance-as-code pipelines |
| External Auditors | Artifact quality; traceability; OSCAL output compatibility |
| Board / Audit Committee | Executive reporting; strategic risk posture |

---

## 5. Business Requirements

### 5.1 Regulatory Intelligence and Ingestion

**BR-01** — The system shall continuously ingest, parse, and normalize regulatory documents from authoritative sources into structured, machine-readable formats, preserving all hierarchical structure, tables, and clause relationships.

**BR-02** — The system shall support automated extraction of discrete, structured rule units from regulatory text with no requirement for human annotation or domain-specific prompting per regulation.

**BR-03** — The system shall maintain a versioned registry of all regulatory frameworks, tracking publication date, effective date, supersession relationships, and jurisdiction.

**BR-04** — The system shall support ingestion of regulatory documents in multiple languages, with a minimum coverage of 84 languages for international regulatory mandates.

**BR-05** — The system shall use MinerU for high-fidelity PDF-to-Markdown conversion, with Marker as fallback for complex layouts, achieving zero-loss heading hierarchy and table preservation.

### 5.2 Control Mapping and Gap Analysis

**BR-06** — The system shall automatically map internal corporate controls to regulatory obligations using formal set-theory alignment classifications: Equivalent-to, Superset-of, Subset-of, Intersects-with, and No-relationship.

**BR-07** — The system shall identify and surface all compliance gaps (Subset-of and No-relationship mappings) with sufficient context for a compliance officer to initiate remediation without manual re-review of source documents.

**BR-08** — The system shall execute framework crosswalks across a minimum of 10,000 internal controls mapped against 5,000 regulatory clauses in near real-time, using ColBERT late-interaction retrieval for >90% classification accuracy.

**BR-09** — The system shall eliminate duplicate evidence collection by automatically propagating a single evidenced control to satisfy all overlapping regulatory requirements it covers.

**BR-10** — The system shall implement bitemporal data modeling with `valid_from`/`valid_to` (event time) and `ingested_at` (system time) properties on all graph nodes and edges.

### 5.3 Compliance Reporting and Auditability

**BR-11** — The system shall generate auditable compliance artifacts in NIST OSCAL format (XML, JSON, and YAML) automatically from the knowledge graph state, without manual document compilation.

**BR-12** — The system shall provide explainable, path-traceable answers to compliance queries, identifying the exact regulatory clause, control mapping, and evidence chain that underpins each determination.

**BR-13** — The system shall support temporal compliance queries, enabling auditors to reconstruct the organization's exact compliance posture at any prior point in time (e.g., "What was our data privacy control posture in Q3 2023?").

**BR-14** — The system shall maintain unbroken historical audit trails; no regulatory obligation record, control mapping, or evidence record shall ever be permanently deleted.

**BR-15** — The system shall implement hot/cold graph separation with Memgraph for active queries (32GB hot graph) and PostgreSQL cold store (90TB+ capacity) for historical archival with monthly retention cycles.

### 5.4 Operational and Governance Requirements

**BR-16** — The system shall provide a configurable data governance layer that programmatically controls which documents and data sources are permitted for agentic retrieval, using metadata-level access controls embedded in source files.

**BR-17** — The system shall constrain autonomous AI agent behavior through declarative governance specifications (`agents.md`, `skills.md`), preventing agents from modifying source compliance files, audit findings, or production graph data without explicit authorization.

**BR-18** — The system shall integrate with at least one tier-1 enterprise GRC platform (MetricStream, ServiceNow GRC, AuditBoard, or Riskonnect) as the authoritative system of record, with bidirectional API synchronization.

**BR-19** — The system shall support self-hosted deployment in air-gapped environments for organizations with strict data residency or classification requirements.

**BR-20** — The system shall implement Temporal.io workflow orchestration with human-in-the-loop (HITL) approval gates for low-confidence AI determinations, with stateful pause/resume capabilities and callback integration.

**BR-21** — The system shall continuously improve AI model performance via a DPO (Direct Preference Optimization) fine-tuning pipeline that ingests human corrections from HITL review sessions into a structured training dataset.

**BR-22** — The system shall support ESG risk dimension tracking with dedicated crosswalks against ESRS, GRI, and TCFD frameworks.

**BR-23** — The system shall track third-party vendor risk with `ThirdParty` nodes and `VENDOR_OF` edges, enabling supplier risk scoring and assessment evidence collection.

---

## 6. Business Constraints

| Constraint | Description |
|---|---|
| **Data Sovereignty** | Regulatory documents classified as sensitive must not leave designated geographic boundaries |
| **Auditability** | All AI-generated compliance determinations must be explainable and traceable; black-box outputs are not acceptable |
| **Regulatory Accuracy** | A misread regulatory clause or lost keyword that leads to a compliance failure is categorically unacceptable |
| **No Downtime** | Continuous controls monitoring must operate 24/7; scheduled maintenance windows require advance regulatory risk assessment |
| **Vendor Independence** | Core compliance logic must not be locked into a single LLM provider's proprietary API |
| **Open-Source Only** | All infrastructure and AI models must be 100% open-source capable with zero external API dependencies |
| **Dual-Judge Validation** | No AI-generated compliance determination may commit to production graph without passing Logic Judge (>0.95 semantic faithfulness) and Technical Judge (100% parameter accuracy) thresholds |

---

## 7. Business Assumptions

- **A-01:** The organization has licensed access to at least one enterprise GRC platform that exposes a documented REST or GraphQL API.
- **A-02:** Internal control libraries are documented in a structured format (spreadsheet, GRC platform export, or equivalent) that can be ingested programmatically.
- **A-03:** Legal and regulatory affairs teams will provide human-in-the-loop validation for Intersects-with mappings flagged by the AI system.
- **A-04:** The organization accepts that AI-generated OSCAL artifacts require a final human review before submission to external auditors.
- **A-05:** Regulatory source documents are publicly available or the organization holds valid licenses for all ingested frameworks.

---

## 8. Success Metrics and KPIs

| KPI | Baseline (Current) | Target State |
|---|---|---|
| Time to complete a full framework crosswalk | 3–6 months (manual) | < 5 business days (automated) |
| Control-to-regulation mapping accuracy | ~70% (heuristic/manual) | > 90% (AI-validated with ColBERT + Dual-Judge) |
| Audit preparation time | 8–12 weeks | < 2 weeks |
| Duplicate evidence collection events | High (unmeasured) | 0 (single-control coverage) |
| Time to detect new regulatory gaps after framework update | Weeks to months | < 24 hours |
| Historical compliance posture query capability | None | 100% temporal coverage (10-year bitemporal retention) |
| OSCAL artifact generation time | Manual (days) | Automated (< 1 hour) |
| Logic Judge agreement rate | N/A | > 95% semantic faithfulness threshold |
| Technical Judge pass rate | N/A | 100% parameter accuracy |
| HITL review callback SLA | N/A | Extraction: 48hrs, Mapping: 72hrs, Gap Resolution: 30 days |
| Model improvement cycle | Ad-hoc | Monthly DPO fine-tuning with >2% precision gain threshold |
| Graph query latency (active graph) | N/A | < 500ms p95 for single-hop traversal |
| PDF-to-Markdown conversion | N/A | < 30 seconds per document (< 100 pages) |

---

## 9. Out of Scope

- Direct integration with external auditor portals (future phase)
- Automated regulatory change monitoring via web scraping (future phase — manual upload supported initially)
- Real-time board-level executive dashboards (future phase)
- Automated remediation of identified control gaps (system identifies and surfaces; remediation remains a human-owned workflow)
- Legal advice or formal legal opinions on compliance determinations

---

## 10. Assumptions and Dependencies

### 10.1 Key Assumptions

| Assumption | ID | Impact if Invalid |
|---|---|---|
| The organization has licensed access to at least one enterprise GRC platform with documented REST/GraphQL API | A-01 | BR-18 cannot be fulfilled; workaround via CSV import required |
| Internal control libraries are documented in structured format (spreadsheet, GRC platform export, or equivalent) | A-02 | BR-09 and FR-3.1 require structured input; manual data entry would be needed |
| Legal and regulatory affairs teams will provide human-in-the-loop validation for Intersects-with mappings | A-03 | FR-3.1 would have higher rejection rate; DPO pipeline would be starved of training data |
| The organization accepts that AI-generated OSCAL artifacts require final human review before external submission | A-04 | BR-11 would need additional validation layer; audit confidence would decrease |
| Regulatory source documents are publicly available or the organization holds valid licenses for all ingested frameworks | A-05 | Ingestion pipeline would fail for licensed-only frameworks |

### 10.2 External Dependencies

| Dependency | Owner | Status | Mitigation |
|---|---|---|---|
| Enterprise GRC platform API access | GRC Platform Admin | To be confirmed | Contract review; alternative manual import workflow |
| LLM inference infrastructure (GPU hardware) | DevOps | To be procured | Cloud-hosted vLLM endpoint as interim solution |
| MinerU model availability for PDF parsing | External (open-source) | Uncertain | SPIKE-1 to validate; Marker fallback documented |
| vLLM model serving for LLM inference | Internal | To be configured | CPU fallback (llama.cpp) for development environments |

---

## 11. Approval and Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Chief Compliance Officer | | | |
| Chief Information Security Officer | | | |
| Head of Internal Audit | | | |
| Enterprise Architecture Lead | | | |
| Project Sponsor | | | |

---

## 12. Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-04-12 | Architecture Team | Initial draft — foundation architecture |
| **2.0** | **2026-04-13** | **End-State Architecture Synthesis** | **END-STATE ALIGNMENT:** Dual-Judge AI validation requirement; Self-hosted air-gap constraint; HITL & DPO fine-tuning pipeline; Hot/cold graph separation; Third-party/ESG dimensions; Updated regulatory drivers (NIST 800-53, ISO 42001, ESRS, TCFD); Enhanced success metrics with baseline/target columns; 10-year temporal retention requirement; MinerU/Marker parsing specification |