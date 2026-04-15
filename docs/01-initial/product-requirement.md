# Product Requirements Document (PRD)
## Risk and Control Knowledge Graph (RCKG) Platform

**Document Version:** 2.0 — End-State Architecture Alignment  
**Status:** Draft  
**Classification:** Internal — Confidential  
**Last Updated:** April 13, 2026  
**Linked BRD:** business-requirement.md v2.0  
**Linked TRD:** master_tech_req.md v6.0

---

## 1. Product Vision

The **Risk and Control Knowledge Graph (RCKG)** is an AI-native enterprise compliance platform that represents regulations, internal corporate policies, operational risks, and mitigating controls as explicitly interconnected nodes in a dynamic, queryable knowledge graph. The platform enables compliance officers, auditors, and risk managers to conduct multi-hop reasoning, automated gap detection, and systemic control mapping — transitioning GRC from a reactive annual exercise into a continuous, data-driven strategic function.

**Core Value Proposition:** One unified graph. Every regulation. Every control. Every relationship. Fully traceable. Always current.

---

## 2. User Personas

### 2.1 Compliance Officer — "Cameron"

- **Goal:** Maintain continuous awareness of the organization's compliance posture across all active frameworks without manually reviewing each regulation.
- **Pain Points:** Manually tracking overlapping regulatory requirements; spending weeks preparing for audits; receiving stale compliance reports.
- **Key Jobs-to-be-Done:**
  - Query compliance status for any regulation at any point in time
  - Identify and prioritize unmitigated compliance gaps
  - Generate auditable compliance evidence packages

### 2.2 Internal Auditor — "Alex"

- **Goal:** Rapidly generate complete, traceable audit evidence packages and conduct gap analyses for multiple simultaneous frameworks.
- **Pain Points:** Collecting duplicate evidence across frameworks; inability to trace AI-generated compliance conclusions; manual OSCAL document preparation.
- **Key Jobs-to-be-Done:**
  - Run automated crosswalk analysis between internal controls and new regulations
  - Export audit evidence in OSCAL-compliant machine-readable formats
  - Review historical compliance posture for a specific date range

### 2.3 Risk Manager — "Riley"

- **Goal:** Identify emerging unmitigated risks as regulatory frameworks evolve and prioritize remediation efforts.
- **Pain Points:** No real-time signal when a new regulatory update creates a gap in the control library; manual gap-to-risk translation.
- **Key Jobs-to-be-Done:**
  - Receive proactive alerts when a framework update creates a new compliance gap
  - Visualize risk exposure across the control library
  - Assign and track remediation actions for identified gaps

### 2.4 GRC Platform Administrator — "Avery"

- **Goal:** Configure integrations, manage document ingestion pipelines, and maintain the health of the knowledge graph.
- **Pain Points:** Complex Python orchestration scripts requiring specialist knowledge to maintain; no visibility into pipeline health.
- **Key Jobs-to-be-Done:**
  - Ingest new regulatory documents with minimal configuration
  - Monitor pipeline health and agent task completion
  - Manage data governance rules for document access permissions

---

## 3. Product Scope and Modules

The RCKG platform is composed of six integrated product modules:

```
┌─────────────────────────────────────────────────────────┐
│                    RCKG Platform                        │
├─────────────┬──────────────┬──────────────┬────────────┤
│  Module 1   │   Module 2   │   Module 3   │  Module 4  │
│  Document   │  Knowledge   │  Compliance  │  Temporal  │
│  Ingestion  │    Graph     │  Crosswalk   │  Memory &  │
│  Pipeline   │    Engine    │    Engine    │  Pruning   │
├─────────────┴──────────────┴──────────────┴────────────┤
│              Module 5: Agentic Orchestration            │
├─────────────────────────────────────────────────────────┤
│            Module 6: Compliance Reporting & UI          │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Feature Requirements

### 4.1 Module 1 — Document Ingestion Pipeline

#### FR-1.1 High-Fidelity PDF-to-Markdown Conversion
**Priority:** P0 — Must Have

The platform must convert regulatory PDFs into structured Markdown with preservation of:
- Heading hierarchies (H1 through H6)
- Multi-column layouts and their reading order
- Nested and borderless tables
- Footnotes associated with their parent paragraphs
- Cross-references between clauses and sections
- Embedded figures and diagrams (stored as references)

**Acceptance Criteria:**
- Zero loss of heading hierarchy in the output Markdown for any tested regulatory document
- Tables rendered in valid GitHub-Flavored Markdown table syntax
- Footnotes annotated inline and/or appended to their parent section
- A compliance officer can read the Markdown output and confirm the semantic structure matches the original PDF

#### FR-1.2 Multi-Format Regulatory Source Support
**Priority:** P0 — Must Have

The ingestion pipeline must accept the following input formats:
- PDF (including scanned/image-based documents via OCR)
- Microsoft Word (.docx)
- Plain text (.txt)
- HTML (with automated noise stripping)
- Excel/CSV (for control library imports)

#### FR-1.3 Automated Metadata Tagging
**Priority:** P1 — Should Have

Each ingested document must receive a standardized metadata header containing:
- `framework_id`: Unique identifier for the regulatory framework
- `version`: Document version or publication date
- `jurisdiction`: Geographic/regulatory scope
- `effective_date`: Date the regulation becomes enforceable
- `supersedes`: Reference to prior version (if applicable)
- `ai-input`: Permission flag for agentic retrieval (`yes` / `no`)
- `language`: ISO 639-1 language code

#### FR-1.4 Automated Rule Unit Extraction (De Jure Pipeline)
**Priority:** P0 — Must Have

Following Markdown conversion, the system must decompose regulatory text into discrete, structured rule units through a four-stage automated pipeline:

1. **Normalization** — Confirm Markdown structural fidelity before proceeding
2. **Semantic Decomposition** — LLM-driven extraction of atomic rule units from regulatory text (Mistral 8B base model)
3. **Multi-Criteria Evaluation** — Automated scoring of extracted rules across metadata accuracy, legal definition alignment, and rule semantics dimensions
4. **Iterative Repair** — Automatically re-process low-scoring extractions with upstream context corrections before graph ingestion

**Acceptance Criteria:**
- Extracted rules preferred over prior methodology outputs in > 80% of evaluator-model assessments
- Each rule unit includes: rule text, parent section reference, applicable definitions, jurisdiction, and effective date
- Hybrid chunking strategy using Markdown header hierarchies + semantic cosine distance threshold (>0.75) for forced splits

---

### 4.2 Module 2 — Knowledge Graph Engine

#### FR-2.1 Property Graph Model
**Priority:** P0 — Must Have

The knowledge graph must implement a Property Graph Model with the following node types:

| Node Type | Description | Key Properties |
|---|---|---|
| `Regulation` | A specific regulatory framework | framework_id, name, jurisdiction, version, status, effective_date, supersedes |
| `ControlGroup` | High-level domain grouping (e.g., "Access Control") | group_id, title, framework_id |
| `ControlObjective` | High-level intent of a control group | objective_id, text, impact_category, obligation_type |
| `Obligation` | A discrete rule unit extracted from a regulation | obligation_id, text, effective_date, clause_ref, action_verb, subject_noun, gov_domain |
| `Control` | An internal corporate control | control_id, name, description, owner, status, implementation_method |
| `Risk` | An identified operational risk | risk_id, name, category, likelihood (1-5), impact (1-5), residual_risk_score, esg_dimension |
| `Policy` | An internal corporate policy | policy_id, name, version, owner |
| `Evidence` | Documented proof of control operation | evidence_id, type, date, artifact_path, hash |
| `Framework` | A compliance framework (e.g., ISO 27001) | framework_id, version, domain |
| `ThirdParty` | External vendor or supplier | vendor_id, name, risk_score, assessment_status |
| `Gap` | Identified compliance gap | gap_id, obligation_id, severity, state (NEW/ASSIGNED/ACCEPTED/REMEDIATED/CLOSED), due_date |
| `ControlEffectiveness` | Runtime control testing results | test_id, control_id, test_date, result, tester_id |

#### FR-2.2 Relationship Types (Edges)
**Priority:** P0 — Must Have

The graph must support and enforce the following explicit edge types:

| Edge | Source → Target | Description |
|---|---|---|
| `FRAMEWORK_HAS_GROUP` | Framework → ControlGroup | Groups controls by domain |
| `GROUP_CONTAINS` | ControlGroup → ControlObjective | Objective belongs to group |
| `ACHIEVES` | Obligation → ControlObjective | Obligation satisfies objective |
| `MANDATED_BY` | Obligation → Regulation | Links obligation to its source regulation |
| `MITIGATES` | Control → Risk | Control addresses a risk |
| `SATISFIES` | Control → Obligation | Control covers a regulatory obligation. **Key property: `mapping_type`** with enum values: EQUIVALENT_TO, SUPERSET_OF, SUBSET_OF, INTERSECTS_WITH, NO_RELATIONSHIP |
| `SUPERSEDES` | Regulation → Regulation | Temporal version relationship |
| `EVIDENCED_BY` | Control → Evidence | Links control to its audit evidence |
| `GOVERNED_BY` | Control → Policy | Links control to authorizing policy |
| `VENDOR_OF` | ThirdParty → Control | Third-party vendor relationship |
| `ASSESSED_BY` | ThirdParty → ControlEffectiveness | Vendor assessment record |
| `HAS_GAP` | Obligation → Gap | Links obligation to its compliance gap |
| `MITIGATED_BY` | Gap → Control | Remediation control assigned to gap |
| `TESTED_BY` | Control → ControlEffectiveness | Control testing record |

> **IMPORTANT:** The set-theory classification values (EQUIVALENT_TO, SUPERSET_OF, SUBSET_OF, INTERSECTS_WITH, NO_RELATIONSHIP) are **NOT separate edge types**. They are **enum values of the `mapping_type` property on the single `SATISFIES` edge**. This design minimizes graph complexity while maintaining full expressivity.

#### FR-2.3 Hybrid Retrieval Architecture
**Priority:** P0 — Must Have

The system must implement a multi-stage hybrid retrieval architecture:

**Stage 1 — ColBERT Late-Interaction Retrieval:**
- Token-level embeddings via ColBERTv2.0 for exact MaxSim semantic matching
- Index controls in Qdrant with SQ8 quantization for scalability
- Retrieve top-20 candidates for any obligation query

**Stage 2 — BGE-M3 Dense Vector Reranking:**
- Apply BGE-Reranker-V2-M3 to top-20 candidates
- Re-rank to top-5 with dense embedding semantics

**Stage 3 — LLM Set-Theory Classification:**
- LLM classifies relationship as EQUIVALENT/SUPERSET/SUBSET/INTERSECTS/NO_RELATIONSHIP
- Dual-Judge verification (Logic Judge >0.95, Technical Judge 100%)

**Stage 4 — GraphRAG Query Synthesis:**
- **Stage 1:** Dense vector search (BGE-M3) to identify top-K candidate nodes
- **Stage 2:** One-hop graph traversal from candidate nodes to extract semantic subgraph
- **Stage 3:** Combined result passed to LLM for grounded synthesis

#### FR-2.4 SHACL Constraint Validation
**Priority:** P1 — Should Have

Before any newly inferred relationship is permanently materialized in the graph, the system must validate it against SHACL (Shapes Constraint Language) rules. Relationships that violate pre-defined compliance business logic must be quarantined for human review rather than auto-committed.

#### FR-2.5 Hot/Cold Graph Separation
**Priority:** P1 — Should Have

The system must implement a hot/cold graph separation architecture:
- **Hot Graph (Memgraph):** 32GB RAM limit for active nodes (last 90 days); sub-500ms query latency
- **Cold Store (PostgreSQL):** 90TB+ capacity for superseded nodes and historical archival
- **Monthly Archival:** Automated migration of nodes >90 days old from Memgraph to PostgreSQL
- **Bitemporal Tags:** All nodes carry `event_time` (valid_from/valid_to) and `ingestion_time`

---

### 4.3 Module 3 — Compliance Crosswalk Engine

#### FR-3.1 Automated Control-to-Obligation Mapping
**Priority:** P0 — Must Have

The engine must automatically evaluate every internal control against every registered regulatory obligation using a three-stage pipeline:

**Stage 1 — ColBERT MaxSim Retrieval:**
- Generate token-level embeddings for all controls in Qdrant
- For each obligation, compute MaxSim similarity against control index
- Retrieve top-20 candidate controls

**Stage 2 — BGE-Reranker V2-M3 Re-ranking:**
- Apply cross-encoder reranking to top-20 candidates
- Select top-5 for final classification

**Stage 3 — LLM Set-Theory Classification with Dual-Judge:**
- LLM classifies relationship: EQUIVALENT_TO / SUPERSET_OF / SUBSET_OF / INTERSECTS_WITH / NO_RELATIONSHIP
- Logic Judge (Llama 3.1 70B) validates semantic faithfulness (threshold >0.95)
- Technical Judge (DeepSeek-R1 72B) validates parameter precision (threshold = 1.00)
- Any mapping failing dual-judge thresholds triggers HITL review

**Acceptance Criteria:**
- Classification accuracy > 90% on a held-out validation set of manually annotated control-obligation pairs
- All Subset-of and No-relationship mappings generate an associated gap record automatically
- Dual-Judge fail rate < 5% of total mappings (indicates model readiness for DPO fine-tuning)

#### FR-3.2 Multi-Framework Gap Detection
**Priority:** P0 — Must Have

When a new regulatory framework is registered or an existing framework is updated, the engine must automatically:
1. Re-evaluate all existing control mappings against changed or new obligations
2. Identify any net-new compliance gaps introduced by the update
3. Notify assigned compliance officers of new gaps within 24 hours of framework update ingestion

#### FR-3.3 Single-Control Multi-Framework Coverage
**Priority:** P0 — Must Have

When a control satisfies an obligation in Framework A, the system must automatically identify all obligations in all other registered frameworks that the same control covers, eliminating the need for duplicate evidence collection.

#### FR-3.4 MECE-Driven Gap Narrative Generation
**Priority:** P1 — Should Have

For each identified gap (Subset-of mapping), the system must generate a structured gap narrative using Mutually Exclusive, Collectively Exhaustive (MECE) logic, describing:
- The specific unmet portion of the obligation
- Suggested remediation approach (additional control or policy amendment)
- Risk severity of the uncovered obligation

---

### 4.4 Module 4 — Temporal Memory and Pruning

#### FR-4.1 Bitemporal Data Model
**Priority:** P0 — Must Have

All nodes and edges in the knowledge graph must carry a dual-timestamp system:
- **Event Time:** When the regulation, policy, or control became active or inactive in the real world
- **Ingestion Time:** When the system recorded the fact

No node or edge shall ever be hard-deleted. Superseded or invalidated facts must be marked with an `invalidated_at` timestamp and excluded from active compliance queries while remaining accessible for historical queries.

#### FR-4.2 Temporal Compliance Query Support
**Priority:** P0 — Must Have

The system must allow users to specify a `as_of_date` parameter on any compliance query to retrieve the exact compliance posture that existed at that point in time.

**Example query:** "What was our compliance posture against DORA Article 11 as of January 1, 2024?"

#### FR-4.3 Regulatory Update Propagation
**Priority:** P0 — Must Have

When a new version of a registered regulation is ingested:
1. New regulation node is created with a `SUPERSEDES` edge pointing to the prior version
2. All obligations from the prior version are marked `status: superseded` with the effective supersession date
3. New obligations from the updated version are extracted, mapped to the graph, and crosswalk re-evaluation is triggered automatically

---

### 4.5 Module 5 — Agentic Orchestration

#### FR-5.1 Declarative Agent Skill Library (skills.md)
**Priority:** P0 — Must Have

All complex compliance workflows must be packaged as portable, human-readable Agent Skills governed by a `SKILL.md` specification file. The platform must ship with a baseline skill library including:

| Skill ID | Skill Name | Description |
|---|---|---|
| `iso27001-access-review` | ISO 27001 Access Review | Automated access control review against AWS/Azure infrastructure |
| `dora-gap-analysis` | DORA Gap Analysis | Full gap analysis against DORA ICT risk obligations |
| `oscal-export` | OSCAL Artifact Export | Compiles knowledge graph state into OSCAL JSON/XML |
| `framework-crosswalk` | Framework Crosswalk | Runs crosswalk between two specified frameworks |
| `evidence-collector` | Evidence Collection | Extracts and packages audit evidence for a control set |
| `regulatory-ingest` | Regulatory Document Ingestion | Full De Jure pipeline from PDF to graph node |

Each skill must implement the Progressive Disclosure Pattern:
- **Level 1 (Discovery):** ~100-token metadata header loaded at agent startup
- **Level 2 (Activation):** Full instruction body loaded on semantic match (< 5,000 tokens)
- **Level 3 (Execution):** On-demand loading of scripts and reference templates from the `/scripts` and `/references` subdirectories

#### FR-5.2 Governance Boundaries via agents.md
**Priority:** P0 — Must Have

Agent behavior must be constrained by a root-level `agents.md` file that defines:
- **Read-only zones:** Agents must not modify source regulatory documents or the production graph without explicit authorization
- **Write zones:** Agents may only write to designated output directories (e.g., `audit-findings/`, `oscal-exports/`)
- **Escalation rules:** Conditions under which agents must halt and escalate to a human reviewer
- **Prohibited actions:** Direct modification of control status, deletion of evidence records, or alteration of mapping classifications

#### FR-5.3 Agent Swarm Coordination
**Priority:** P1 — Should Have

The platform must support concurrent deployment of multiple specialized agents (e.g., one ingestion agent, one crosswalk agent, one reporting agent) with:
- Task handoff protocols defined in `agents.md`
- Shared read access to the knowledge graph
- Isolated write access scoped to each agent's designated output zone
- Conflict detection when two agents attempt to modify the same node

#### FR-5.4 Temporal Workflow Orchestration
**Priority:** P0 — Must Have

The platform must implement stateful workflow orchestration using Temporal.io with the following capabilities:

**Workflow Registry:**
| Workflow ID | Trigger | Human Gates | Timeout |
|---|---|---|---|
| `document_ingestion_workflow` | Kafka `document.ingested` | None | 15 min |
| `extraction_validation_workflow` | Kafka `extraction.completed` | `review_required` if confidence < 0.70 | 48 hours |
| `dual_judge_validation_workflow` | Kafka `validation.completed` | `hitl_review` if Logic Score < 0.95 | 72 hours |
| `mapping_workflow` | Kafka `mapping.completed` | `low_confidence` if LLM score < 0.85 | 72 hours |
| `human_approval_workflow` | Signal `approval_callback` | **Signal: `submission_received`**<br>**Signal: `approval_callback`** | Configurable |

**HITL Integration:**
- Workflows pause at approval gates and await callback signals
- Callbacks include decision (approve/reject/modify), reviewer_id, and timestamp
- Upon callback, workflow resumes and applies changes to graph/PostgreSQL
- Dead-letter queue for approvals exceeding timeout thresholds

#### FR-5.5 DPO Fine-Tuning Pipeline
**Priority:** P1 — Should Have

The platform must implement a continuous improvement loop using Direct Preference Optimization (DPO):

**Pipeline Steps:**
1. Extract reject pairs from Langfuse (confidence < 0.70)
2. Format as DPO training dataset (JSONL)
3. Split: 80% train, 10% validation, 10% test
4. Submit fine-tuning job via vLLM + Axolotl
5. A/B test on benchmark (precision/recall/F1)
6. Promote model if improvement > 2% over baseline
7. Deploy to GPU worker pool with canary rollout

**Data Format:**
- `input_prompt`: Original LLM input
- `rejected_output`: Low-confidence AI output
- `preferred_output`: Human-corrected output
- `reason`: Explanation of why preferred is better
- `reviewer_id` and `reviewed_at`: Audit trail

---

### 4.6 Module 6 — Compliance Reporting and UI

#### FR-6.1 Compliance Dashboard
**Priority:** P1 — Should Have

A web-based dashboard providing:
- Overall compliance coverage percentage per registered framework
- Heatmap of gap severity across the control library
- Timeline view of regulatory updates and their impact on compliance posture
- Active gap list with owner assignment and remediation status

#### FR-6.5 ESG Compliance Module
**Priority:** P2 — Nice to Have

A dedicated ESG reporting module with:
- `esg_dimension` tag on Risk nodes for ESG-specific categorization
- Crosswalks against ESRS (EU), GRI (Global), and TCFD (Climate) standards
- ESG compliance posture dashboard with trend analysis
- Automated POA&M generation for ESG gaps

#### FR-6.6 Third-Party Risk Module
**Priority:** P2 — Nice to Have

A vendor risk management module with:
- `ThirdParty` nodes with `VENDOR_OF` edges to controls
- `ASSESSED_BY` edges linking vendors to control effectiveness tests
- Supplier risk scoring based on control coverage and remediation history
- Third-party assessment evidence collection workflow

#### FR-6.2 Natural Language Compliance Query Interface
**Priority:** P1 — Should Have

A conversational query interface allowing users to ask compliance questions in plain English:
- "Which controls satisfy GDPR Article 32?"
- "What gaps exist in our SOC 2 Type II coverage?"
- "Show me the evidence chain for Control CC-019 against ISO 27001 A.9.4"

Every response must include the source node, edge path, and evidence references that produced the answer.

#### FR-6.3 OSCAL Export
**Priority:** P0 — Must Have

One-click generation of validated OSCAL artifacts including:
- System Security Plan (SSP)
- Plan of Action and Milestones (POA&M) for identified gaps
- Security Assessment Report (SAR)
- Component Definition for each registered control

Output must be validated against NIST OSCAL schema before delivery.

#### FR-6.4 GRC Platform Synchronization
**Priority:** P1 — Should Have

Bidirectional synchronization with at least one tier-1 GRC platform (MetricStream, ServiceNow GRC, AuditBoard, or Riskonnect), including:
- Push of gap findings as action items or issues in the GRC platform
- Pull of control status updates from the GRC platform into the knowledge graph
- Configurable sync cadence (real-time webhook or scheduled batch)

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Requirement |
|---|---|
| Crosswalk completion (10,000 controls × 5,000 obligations) | < 10 minutes end-to-end |
| Compliance query response time (natural language) | < 5 seconds p95 |
| OSCAL artifact generation | < 60 minutes for full SSP |
| PDF-to-Markdown conversion | < 30 seconds per document (< 100 pages) |
| Graph node query (single hop, hot graph) | < 500ms |
| ColBERT MaxSim retrieval (top-20) | < 1 second |
| Dual-Judge inference time | < 30 seconds per mapping |
| Temporal workflow pause/resume | < 100ms signal latency |

### 5.2 Accuracy

| Metric | Baseline | Target |
|---|---|---|
| Control-to-obligation mapping classification accuracy | ~70% | > 90% |
| Regulatory rule extraction accuracy (De Jure pipeline) | N/A | Preferred in > 80% of evaluations |
| Logic Judge agreement rate | N/A | > 95% semantic faithfulness |
| Technical Judge pass rate | N/A | 100% parameter accuracy |
| End-to-end mapping F1 score | ~71% | > 85% |
| Zero hallucinated compliance determinations | N/A | All answers traceable to explicit graph path |

### 5.3 Scalability

- Knowledge graph must support a minimum of 1,000,000 nodes and 5,000,000 edges without degradation in query performance
- Hot graph (Memgraph) must support 32GB active dataset with sub-500ms single-hop queries
- Cold store (PostgreSQL) must support 90TB+ for historical archival with monthly retention cycles
- Ingestion pipeline must support parallel processing of up to 100 concurrent regulatory documents
- Embedding model must support horizontal scaling during crosswalk computation
- Qdrant cluster must support 10M+ ColBERT embeddings with SQ8 quantization

### 5.4 Security and Data Governance

- All document-level access controls enforced via metadata flags (`ai-input: yes/no`)
- Role-based access control (RBAC) at the framework, control, and evidence levels
- All data at rest encrypted (AES-256 minimum); all data in transit encrypted (TLS 1.3)
- Full audit log of all agent actions, graph writes, and user queries, immutable and append-only
- Self-hosted deployment option with no external API calls for air-gapped environments
- HashiCorp Vault integration for secrets management in production deployments
- WORM (Write-Once-Read-Many) bucket policy for MinIO raw document storage

### 5.5 Availability and Resilience

- System availability SLA: 99.9% for the compliance query and monitoring functions
- Knowledge graph reads must remain available during ingestion pipeline maintenance
- All failed agent tasks must be retried with exponential backoff and dead-letter queued for human review
- Temporal workflow durability: workflows survive restarts and maintain state across node failures
- Kafka event retention: 7 days for real-time topics, 30 days for alert topics
- Monthly automated archival from hot to cold graph with data integrity validation

---

## 6. Acceptance Criteria Summary

| Feature | Acceptance Test |
|---|---|
| PDF-to-Markdown | Heading hierarchy preserved; tables valid; footnotes associated |
| Rule Extraction | > 80% evaluator preference over baseline |
| Control Mapping | > 90% classification accuracy on benchmark (ColBERT + Dual-Judge) |
| Temporal Query | Correct posture returned for any specified historical date |
| OSCAL Export | Output validates against NIST OSCAL schema without errors |
| Agent Governance | Agents cannot write outside designated output directories |
| Gap Detection | New gaps surfaced within 24 hours of framework update |
| Dual-Judge Validation | Logic Judge > 95% semantic faithfulness; Technical Judge 100% parameter accuracy |
| Hot/Cold Graph Separation | Monthly archival succeeds with data integrity validation; cold store queryable |
| Temporal Workflow HITL | Workflows pause at approval gates; resume within 100ms of callback signal |
| DPO Pipeline | Monthly fine-tuning cycle completes; model improvement > 2% threshold validated |
| Third-Party Risk | ThirdParty nodes created; VENDOR_OF edges established; risk scores calculated |
| ESG Crosswalks | ESRS/GRI/TCFD mappings generated; esg_dimension tags applied to Risk nodes |
| ColBERT Retrieval | Top-20 candidates retrieved in < 1 second with MaxSim scoring |
| Bitemporal Tags | All nodes/edges carry valid_from, valid_to, and ingested_at properties |
| Air-Gapped Deployment | Full stack deploys without external API calls; models pre-loaded via MinIO |

---

## 8. API Security and Authentication

### 8.1 Authentication Mechanisms

| Mechanism | Use Case | Implementation |
|---|---|---|
| **OAuth 2.0 / OIDC** | User authentication via enterprise identity provider | Microsoft Entra ID, Okta, or Google Workspace |
| **API Keys** | Machine-to-machine authentication (agents, integrations) | HMAC-SHA256 signed requests; stored in HashiCorp Vault |
| **Bearer Tokens** | Short-lived session tokens (24hr expiry) | JWT signed with RSA-256; rotated every 24 hours |
| **Mutual TLS (mTLS)** | Air-gapped deployments with certificate-based auth | Client certificates issued by internal CA |

### 8.2 Role-Based Access Control (RBAC)

| Role | Permissions | Access Scope |
|---|---|---|
| `compliance_admin` | Full CRUD on all resources | All frameworks, controls, gaps, users |
| `compliance_auditor` | Read-only on compliance data; write on evidence | All frameworks; no gap modification |
| `risk_owner` | Update assigned gaps only | Own risk domain only |
| `read_only` | View-only access to coverage metrics | Framework overview, no sensitive data |
| `system_agent` | Write to `/oscal-exports/`, `/gap-reports/` only | Designated output zones per `agents.md` |

### 8.3 Audit Logging

All API requests are logged with:
- `request_id` (UUID for tracing)
- `user_id` or `api_key_id`
- `endpoint` and `method`
- `status_code`
- `response_time_ms`
- `ip_address` (or internal service identifier)
- `user_agent` (for API clients: `rckg-agent/1.0`)

Logs are stored in PostgreSQL `api_audit_log` table with 2-year retention, then forwarded to SIEM for 7-year archival.

---

## 9. Compliance Dashboard and Access Control

### 9.1 Dashboard Components

| Component | Description | Data Source | Update Frequency |
|---|---|---|---|
| Coverage Percentage | Overall compliance coverage per framework | `SATISFIES` edge aggregation | Real-time |
| Gap Heatmap | Severity distribution across control library | `Gap` node lifecycle_state + severity | Real-time |
| Regulatory Timeline | Timeline of framework updates and impact | `Regulation` supersession dates | On update |
| Active Gaps List | Owner-assigned gaps with remediation status | `Gap` node with OPEN/IN_REMEDIATION state | Real-time |
| Coverage Trend | Historical coverage score over time | Coverage history table | Daily |

### 9.2 Access Control

- **Compliance Admin**: Full access to all dashboard components
- **Compliance Auditor**: Read-only access to coverage and gap data
- **Risk Owner**: Access only to gaps assigned to them
- **Read-Only**: View-only access to coverage percentages (no gap details)

---

## 10. Third-Party Risk and ESG Compliance Modules

### 10.1 Third-Party Risk Module

The platform must support third-party vendor risk assessment through the following capabilities:

| Feature | Description | Data Model |
|---|---|---|
| Third-Party Nodes | `ThirdParty` node type with vendor metadata | `party_id`, `name`, `category`, `country`, `criticality_tier` |
| Vendor-Of Relationships | `VENDOR_OF` edges linking vendors to controls they provide | Edge property: `relationship_type` (direct/indirect) |
| Control Effectiveness Tests | `ControlEffectiveness` nodes for vendor assessments | `effectiveness_id`, `test_date`, `result`, `score` |
| Assessed-By Relationships | `ASSESSED_BY` edges from vendor to their assessment records | Edge property: `assessment_framework` |
| Risk Scoring | Automated vendor risk scoring based on control coverage | Formula: (unmitigated_obligations × severity_weight) / total_controls |

### 10.2 ESG Compliance Module

The platform must support ESG-specific compliance tracking through:

| Feature | Description | Data Model |
|---|---|---|
| ESG Dimension Tag | `esg_dimension` property on Risk nodes (E/S/G/null) | Enum: `environmental`, `social`, `governance`, `null` |
| ESRS Crosswalk | Mapping to EU Sustainability Reporting Standards | `SATISFIES` edge with framework=ESRS |
| GRI Crosswalk | Mapping to Global Reporting Initiative standards | `SATISFIES` edge with framework=GRI |
| TCFD Crosswalk | Mapping to Task Force on Climate-related Financial Disclosures | `SATISFIES` edge with framework=TCFD |
| ESG Dashboard | Dedicated ESG compliance posture view | Aggregated ESG coverage metrics |

---

| Role | Name | Signature | Date |
|---|---|---|---|
| Chief Compliance Officer | | | |
| Chief Information Security Officer | | | |
| Head of Internal Audit | | | |
| Enterprise Architecture Lead | | | |
| Project Sponsor | | | |

---

## 11. Data Governance and Compliance

### 11.1 Data Classification

| Classification | Examples | Access Control | Retention |
|---|---|---|---|
| **Public** | Framework documentation (ISO 27001, NIST CSF) | No restriction | Per source |
| **Internal** | Control library, internal policies | Authenticated users | 10 years |
| **Confidential** | Gap reports, audit findings | RBAC required | 10 years |
| **Restricted** | Evidence artifacts, vendor assessments | Admin approval + mTLS | 7 years minimum |

### 11.2 Privacy and Data Residency

| Requirement | Implementation |
|---|---|
| **GDPR Compliance** | Data subject request handling (export, delete); consent tracking on evidence collection |
| **Data Residency** | All data stored in designated region (EU: Frankfurt; US: N. Virginia); no cross-region replication without approval |
| **PII Handling** | No PII stored in knowledge graph; evidence artifacts hashed and stored separately with access audit trail |
| **Right to be Forgotten** | PII can be anonymized in evidence; compliance graph structure (obligations, controls) retained per regulatory requirement |

### 11.3 Third-Party Vendor Data

When ingesting data from third-party sources (GRC platform integrations, external audits):

- Data source is tagged with `data_source` property on `Document` nodes
- `ai_input_permission` flag set based on vendor contract terms
- Automatic PII detection on ingestion; flagged data routed to restricted zone
- Vendor contract expiry triggers data review workflow

---

## 12. Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-04-12 | Architecture Team | Initial draft — foundation architecture |
| **2.0** | **2026-04-13** | **End-State Architecture Synthesis** | **END-STATE ALIGNMENT:** Enhanced node types (ControlGroup, ControlObjective, ThirdParty, Gap, ControlEffectiveness); Expanded edge types (FRAMEWORK_HAS_GROUP, GROUP_CONTAINS, ACHIEVES, MITIGATES, VENDOR_OF, ASSESSED_BY, MITIGATED_BY, TESTED_BY); ColBERT + BGE-M3 + LLM 3-stage crosswalk pipeline; Dual-Judge validation requirement (Logic Judge >0.95, Technical Judge 100%); Temporal workflow orchestration with HITL gates; DPO fine-tuning pipeline; Hot/cold graph separation (FR-2.5); ESG and Third-Party risk modules; Enhanced performance/accuracy/scalability metrics with baseline/target columns; Phase 4 advanced capabilities (Months 13-18); Air-gapped deployment package requirement |

### Phase 1 — Foundation (Months 1–4)

| Deliverable | Feature Requirements |
|---|---|
| **Infrastructure Provisioning** | Docker Compose stack (PostgreSQL, Memgraph, Qdrant, MinIO, Temporal, Langfuse) |
| **Document Ingestion Pipeline** | FR-1.1 (PDF-to-Markdown), FR-1.2 (multi-format), FR-1.3 (metadata tagging) |
| **De Jure Rule Extraction** | FR-1.4 (hybrid chunking + LLM extraction + iterative repair) |
| **Knowledge Graph Core** | FR-2.1 (property model), FR-2.2 (edge types) |
| **Bitemporal Data Model** | FR-4.1 (`valid_from`/`valid_to` + `ingested_at` on all nodes/edges) |
| **Bronze/Silver/Gold Layers** | PostgreSQL vault staging with three-tier quality model |

### Phase 2 — Intelligence (Months 5–8)

| Deliverable | Feature Requirements |
|---|---|
| **Hybrid Retrieval Engine** | FR-2.3 (ColBERT + BGE-M3 reranking + GraphRAG synthesis) |
| **Automated Crosswalk Engine** | FR-3.1 (3-stage ColBERT/Lee/Judge pipeline), FR-3.2 (gap detection), FR-3.3 (multi-framework coverage) |
| **Temporal Query Support** | FR-4.2 (`as_of_date` queries), FR-4.3 (regulatory update propagation) |
| **Agent Skill Library** | FR-5.1 (6 baseline skills), FR-5.2 (agents.md governance), FR-5.4 (Temporal workflows with HITL) |
| **Dual-Judge Validation** | Logic Judge (Llama 3.1 70B), Technical Judge (DeepSeek-R1 72B) with thresholds |
| **Hot/Cold Graph Separation** | FR-2.5 (Memgraph 32GB hot, PostgreSQL cold, monthly archival) |
| **SHACL Constraint Validation** | FR-2.4 (pre-commit graph validation with quarantine pattern) |

### Phase 3 — Operations (Months 9–12)

| Deliverable | Feature Requirements |
|---|---|
| **OSCAL Export Engine** | FR-6.3 (SSP, POA&M, SAR, Component Definition with provenance metadata) |
| **Compliance Dashboard** | FR-6.1 (coverage %, gap heatmap, timeline view, active gap list) |
| **Natural Language Query Interface** | FR-6.2 (GraphRAG-based answers with source tracing) |
| **GRC Platform Integration** | FR-6.4 (bidirectional sync with ServiceNow/MetricStream/AuditBoard) |
| **DPO Fine-Tuning Pipeline** | FR-5.5 (Langfuse reject pair extraction, DPO dataset, vLLM training, A/B testing) |
| **Agent Swarm Coordination** | FR-5.3 (concurrent specialized agents with conflict detection) |
| **Third-Party Risk Module** | FR-6.6 (ThirdParty nodes, VENDOR_OF edges, supplier risk scoring) |
| **ESG Compliance Module** | FR-6.5 (ESRS/GRI/TCFD crosswalks, esg_dimension tags) |
| **Production Kubernetes Deployment** | EKS cluster with HPA, RDS Aurora, MSK Kafka, S3, Qdrant sharding |
| **Air-Gapped Deployment Package** | Full offline stack with Harbor registry, internal CA, pre-loaded models |

### Phase 4 — Advanced Capabilities (Months 13–18, Optional)

| Capability | Description |
|---|---|
| **External Auditor Portal** | Read-only API with OSCAL export self-service, auditor-scoped RBAC |
| **Automated Remediation Workflows** | Jira/ServiceNow ticket auto-creation for gap remediation |
| **Predictive Risk Analytics** | ML model trained on historical gap patterns for emerging compliance gaps |
| **Digital Twin Integration** | Connect RCKG control graph to infrastructure digital twin for real-time control effectiveness monitoring |
| **OSCAL 2.0 + Agentic AI Extensions** | Integration with NIST CSWP 53 OSCAL 2.0 for autonomous risk reasoning |
| **Multi-Language UI** | 84+ language support via BGE-M3 multilingual embeddings |
| **Executive Dashboard** | Board-level compliance posture visualization, framework coverage heat maps, gap trend analysis |