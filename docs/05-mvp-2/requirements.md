# MVP-2 Requirements — Gap Analysis & Scope Definition

**Document Version:** 1.0  
**Date:** 2026-08-09  
**Source of Truth:** [claude-first-principle.md](docs/04-deepdive/claude-first-principle.md)  
**Prior MVP Plan:** [mvp-sprint.md](docs/03-mvp/mvp-sprint.md) (Sprint 1–4, 140 pts, largely incomplete against BRD)  
**Prior Assessment:** [claude-mvp-assessment.md](docs/04-deepdive/claude-mvp-assessment.md) (8 genuinely fixed, 10 partially fixed, 5 not fixed)

---

## 1. Executive Summary

The MVP-2 proves one thing: **a compliance officer can upload a regulatory PDF, have the system parse and extract obligations from it, map those obligations against existing controls using AI-validated set-theory classification, and query the resulting graph to see gaps — with every determination traceable to source evidence and gated by dual-judge validation.**

This is the minimum end-to-end flow that demonstrates the core value proposition described in the BRD (BO-01 through BO-06). Everything else — OSCAL generation, GRC sync, ESG crosswalks, DPO fine-tuning, continuous monitoring — is either a reporting format on top of this core, an integration channel, or a self-improvement loop. None of those are required to prove the core thesis.

The codebase is architecturally sound but operationally incomplete. The audit found 2 of 36 BRD requirements MET, 18 PARTIALLY MET, and 13 NOT MET. The MVP-2 focuses narrowly on making the **critical path work end-to-end with real AI** — not heuristic fallbacks — while fixing the two highest-risk undocumented behaviors (keyword NLI fallback producing fake confidence, arithmetic dual-judge self-approval).

### Scoping Framework Inputs

| Parameter | Value | Source |
|---|---|---|
| **Target timeline** | 6 weeks (3 sprints × 2 weeks) | Assumed — prior plan was 4×2wk=8wk for a larger scope that shipped ~25%. Narrower scope, same cadence. |
| **Team size** | 1 lead engineer (AI/infra), 1 backend engineer, QA done by engineers via TDD | Assumed from prior sprint plan team composition, adjusted to realistic. |
| **Hard constraints** | Open-source models only (BRD §6); dual-judge must gate commits (BRD §6); air-gap capable (BRD §6); no permanent deletion (BR-14) | BRD §6 Constraints |
| **Known out-of-scope (BRD §9)** | Automated regulatory monitoring (manual upload initially); board dashboards; automated remediation; legal opinions | BRD §9 Out of Scope |

---

## 2. Core User Journey (Scoping Anchor)

Before scoping anything, this is the journey every Must-have must serve:

```
1. Upload   → Compliance officer uploads a regulatory PDF via API
2. Parse    → System converts PDF to structured Markdown (MinerU/Marker)
3. Extract  → System extracts discrete obligations from Markdown (LLM)
4. Map      → System maps obligations against existing controls (NLI + set-theory)
5. Gate     → Dual-judge validates each mapping before graph commit
6. Store    → Validated mappings persist to Memgraph (hot) + PostgreSQL (cold)
7. Surface  → Officer queries graph for gaps, gets traceable explanation
```

A feature is **Must-have** only if removing it breaks this 7-step chain. Everything else is explicitly downgraded.

---

## 3. Scope Table (Gap Analysis + MVP Decision)

| # | Capability | Audit Req | Audit Verdict | Current State | MVP-2 Priority | Rationale | Source |
|---|---|---|---|---|---|---|---|
| C-01 | **PDF → Markdown conversion (MinerU primary, Marker fallback)** | REQ-002, REQ-009, REQ-010 | PARTIAL | Architecture exists; both `_run_mineru()` and `_run_marker()` raise `RuntimeError`. [pdf_to_markdown.py:L157-182](backend/app/services/pdf_to_markdown.py#L157-L182) | **Must** | Step 2 of core journey. Nothing enters the system without this. FINDING-001. | BR-05 |
| C-02 | **Heading/table/clause structure preservation** | REQ-003, REQ-011 | PARTIAL | Result classes (`_MinerUResult`) track headings/tables; stubbed conversion means untested. [pdf_to_markdown.py:L101-143](backend/app/services/pdf_to_markdown.py#L101-L143) | **Must** | Quality of extraction depends on structural preservation. Ships with C-01. | BR-05 |
| C-03 | **LLM-based obligation extraction** | REQ-004, REQ-005 | PARTIAL | `extract_obligations()` works when LLM is available. 3-tier taxonomy (regulation/policy/SOP) in prompts. [extraction.py:L283-326](backend/app/services/extraction.py#L283-L326) | **Must** | Step 3 of core journey. Partially functional — needs hardening, not greenfield. | BR-02 |
| C-04 | **Set-theory NLI classification (real AI, not keyword heuristic)** | REQ-012 | PARTIAL | `NliSetTheoryEngine.evaluate_pair()` has LLM path + keyword fallback. Fallback produces fake 0.88-0.95 confidence. [nli_engine.py:L57-180](backend/app/services/nli_engine.py#L57-L180). FINDING-007, U-04. | **Must** | Step 4 of core journey. LLM path exists; keyword fallback must be eliminated or clearly flagged as degraded (not high-confidence). | BR-06, BO-03 |
| C-05 | **Dual-judge gating graph commits** | REQ-032, REQ-034, REQ-035 | PARTIAL / NOT MET | `AsynchronousDualJudgeService` exists but is async and disconnected from `MemgraphService.enqueue_and_execute()`. Thresholds wrong (0.80/0.85 vs BRD 0.95/1.00). Arithmetic fallback auto-approves. [memgraph_service.py:L115-173](backend/app/services/memgraph_service.py#L115-L173), [dual_judge_async.py:L82-85](backend/app/services/dual_judge_async.py#L82-L85). FINDING-003, U-05. | **Must** | BRD's hardest constraint. Step 5 of core journey. Must be synchronous gate before commit. | BRD §6 Constraint, BO-06 |
| C-06 | **Graph compiler rule engine** | REQ-012, REQ-013 | PARTIAL | `RuleBasedGraphCompiler` exists with 5 rules. Creates gaps for cosine < 0.30 only. [graph_compiler.py:L50-169](backend/app/services/graph_compiler.py#L50-L169) | **Must** | Step 4→6 of core journey. Functional — needs gap creation for Subset-of per BR-07. | BR-06, BR-07 |
| C-07 | **Gap surfacing with remediation context** | REQ-013, REQ-014 | PARTIAL | `GapNode` ORM exists. Gap metadata has `gap_type`/`gap_severity` but no clause text or evidence chain. [rckg_nodes.py:L286-318](backend/app/models/rckg_nodes.py#L286-L318), [graph_compiler.py:L77-87](backend/app/services/graph_compiler.py#L77-L87) | **Must** | Step 7 of core journey. Officer needs to see actionable gaps. | BR-07 |
| C-08 | **Compliance query API (gap listing + path tracing)** | REQ-020 | PARTIAL | Cypher queries exist in `RCKGCypherBuilder`. No user-facing API endpoint returning explanation chains. [rckg_queries.py:L12-253](backend/app/graph/rckg_queries.py#L12-L253) | **Must** | Step 7 of core journey. Without a query API, there is no user-visible output. | BR-12 |
| C-09 | **Memgraph + PostgreSQL dual-write (outbox pattern)** | REQ-023 | PARTIAL | `MemgraphService.enqueue_and_execute()` implements outbox. `GraphOutboxLog` model exists. Both stores in docker-compose. No hot→cold migration. [memgraph_service.py:L115-173](backend/app/services/memgraph_service.py#L115-L173) | **Must** | Step 6 of core journey. Core write path — functional, needs judge gate wired in. | BR-15 |
| C-10 | **Soft-delete only (no permanent deletion)** | REQ-022 | PARTIAL | SUPERSEDE/DEPRECATE patterns exist. `delete_file()`, `delete_collection()` exist unguarded. [rckg_queries.py:L204-213](backend/app/graph/rckg_queries.py#L204-L213), [storage/__init__.py:L242-253](backend/app/storage/__init__.py#L242-L253) | **Must** | BRD §6 constraint. Guard delete methods against compliance data. | BR-14 |
| C-11 | **Open-source models only, no external API guard** | REQ-033 | PARTIAL | Mistral 8B + Llama 3.1. No hard guard preventing `LLM_ENDPOINT` pointing to OpenAI. [extraction.py:L39](backend/app/services/extraction.py#L39) | **Must** | BRD §6 constraint. Add startup validation that `LLM_ENDPOINT` is local. | BRD §6 |
| C-12 | **Facet extractor with real AI** | (supports REQ-012) | NOT MET (Finding #3 in claude-mvp-assessment) | 10 hardcoded verbs, 10 nouns, 3 domains, `control_nature` always `PREVENTATIVE`. LLM try/catch added but regex fallback unchanged. [facet_extractor.py:L16-97](backend/app/services/facet_extractor.py#L16-L97) | **Should** | Improves mapping quality significantly. Not strictly blocking — graph compiler can work with LLM extraction output directly. | BR-06 |
| C-13 | **ColBERT with real model** | REQ-016 | PARTIAL | MaxSim architecture correct. Uses synthetic hash-seeded embeddings, not ColBERTv2 model. [colbert_service.py:L33-50](backend/app/services/retrieval/colbert_service.py#L33-L50). FINDING-008. | **Should** | Improves retrieval accuracy. Bi-encoder or BM25 can serve as interim. | BR-08 |
| C-14 | **Bitemporal fields on all node types + edges** | REQ-018 | PARTIAL | 2 of 7 node types have `valid_from`/`valid_to`. 0 edge tables have bitemporal. [rckg_nodes.py:L89-92](backend/app/models/rckg_nodes.py#L89-L92). FINDING-005. | **Should** | Data model correctness. Not blocking core flow but blocking temporal queries. Add columns in migration. | BR-10 |
| C-15 | **Framework registry with lifecycle metadata** | REQ-006, REQ-007 | NOT MET | `framework_name`/`framework_version` are plain strings on `ObligationNode`. No dedicated model. FINDING-006. | **Should** | Important for multi-framework management. Not blocking single-framework demo flow. | BR-03 |
| C-16 | **Temporal.io concrete workflow (ingestion pipeline)** | REQ-028 | PARTIAL | `BaseWorkflow` has pause/approve signals. `execute()` raises `NotImplementedError`. [workflows/base.py:L30-116](backend/app/workflows/base.py#L30-L116) | **Could** | Direct service calls work for MVP. Temporal adds resilience but not core value. | BR-20 |
| C-17 | **Evidence propagation (transitive coverage)** | REQ-017 | NOT MET | Mapping tables create 1:1 linkages. No transitive closure. FINDING-013. | **Could** | Significant value but complex graph algorithm. Can be built post-MVP once mappings exist. | BR-09 |
| C-18 | **Temporal compliance queries (point-in-time reconstruction)** | REQ-021 | PARTIAL | `GoldenControl.is_valid_at()` exists. No full reconstruction API. | **Could** | Requires C-14 (bitemporal on all types) first. Deferred. | BR-13 |
| C-19 | **Air-gap deployment documentation** | REQ-027 | PARTIAL | All containers open-source. No offline bundle or docs. | **Could** | Infra is ready; needs documentation, not code. | BR-19 |
| C-20 | **Multilingual support (BGE-M3 real embeddings)** | REQ-008 | NOT VERIFIABLE | Vector size configured for BGE-M3 (1024-dim). No embedding service. | **Won't** | English-only is sufficient for MVP demo. Multilingual is a deployment option. | BR-04 |
| C-21 | **OSCAL artifact generation** | REQ-019 | NOT MET | Zero OSCAL code. FINDING-002. | **Won't** | Reporting format on top of graph state. Not needed to prove core mapping + gap detection. | BR-11 |
| C-22 | **GRC platform integration** | REQ-026 | NOT MET | Zero GRC code. FINDING-004. | **Won't** | Integration channel. BRD A-01 notes dependency on GRC API access being confirmed. | BR-18 |
| C-23 | **DPO fine-tuning pipeline** | REQ-029 | PARTIAL | `PreferenceAccumulatorWorker` accumulates pairs. Publish is a stub. No training code. FINDING-012. | **Won't** | Self-improvement loop. Not needed to prove core thesis. | BR-21 |
| C-24 | **ESG/ESRS/GRI/TCFD tracking** | REQ-030 | NOT MET | Zero ESG code. FINDING-009. | **Won't** | Secondary objective (BO-17). Zero code exists. | BR-22 |
| C-25 | **ThirdParty nodes + VENDOR_OF edges** | REQ-031 | PARTIAL | SHACL shape only. No ORM, no edge type. FINDING-010. | **Won't** | Secondary objective (BO-16). Orthogonal to core flow. | BR-23 |
| C-26 | **Declarative agent governance (agents.md/skills.md runtime)** | REQ-025 | NOT MET | No runtime governance system. FINDING-011. | **Won't** | Dev tooling pattern. Not blocking compliance officer flow. | BR-17 |
| C-27 | **Continuous monitoring (autonomous detection)** | REQ-001, REQ-036 | NOT MET | All processing requires API calls. FINDING-014. | **Won't** | BRD §9 explicitly says "manual upload supported initially." | BR-01, BRD §9 |
| C-28 | **Data governance (metadata-level access controls)** | REQ-024 | PARTIAL | Graph-mutation governance exists. No document-source access governance. | **Won't** | Operational governance. Not blocking single-user MVP. | BR-16 |
| C-29 | **Hot→cold migration pipeline** | REQ-023 | NOT MET | Both stores configured. No archival service. | **Won't** | Retention lifecycle. Not blocking for 6-week demo. | BR-15 |

### Scope Summary

| Priority | Count | Description |
|---|---|---|
| **Must** | 11 | Core 7-step journey + BRD hard constraints |
| **Should** | 4 | Significant quality/correctness improvements |
| **Could** | 4 | Valuable but deferrable without breaking core flow |
| **Won't** | 10 | Secondary objectives, integration channels, self-improvement loops |

---

## 4. Functional Requirements

Each requirement is individually testable and traces to the scope table above.

### 4.1 Document Ingestion & Parsing

**FR-01** — System shall accept PDF uploads via `POST /documents` and store the original file in MinIO `source-regulations` bucket with SHA-256 deduplication.  
_Traces to: C-01 | Current state: Exists ([document_upload.py:L54-215](backend/app/services/document_upload.py#L54-L215)) | Work: None — already functional._

**FR-02** — System shall convert uploaded PDF to Markdown using MinerU as primary converter. If MinerU conversion confidence < 0.85, system shall automatically fall back to Marker.  
_Traces to: C-01 | Current state: Stubbed ([pdf_to_markdown.py:L157-182](backend/app/services/pdf_to_markdown.py#L157-L182)) | Work: Implement real MinerU/Marker calls — replace `RuntimeError` stubs with actual library integration._

**FR-03** — Converted Markdown shall preserve document heading hierarchy (H1→H6 nesting), tables (as Markdown tables or HTML), and footnotes. Acceptance: round-trip a 10-page PDF with 3+ heading levels and 1+ table; verify all headings and table cells present in output.  
_Traces to: C-02 | Current state: Result classes exist, untested | Work: Ships with FR-02._

**FR-04** — System shall chunk converted Markdown into clause-boundary-aligned segments using `ClauseBoundaryExtractor`, preserving section references.  
_Traces to: C-02 | Current state: Exists ([hybrid_chunking.py](backend/app/services/hybrid_chunking.py)) | Work: Verify against real MinerU output._

### 4.2 Obligation Extraction

**FR-05** — System shall extract structured obligations from Markdown chunks via LLM (Mistral 8B or configured open-source model). Each obligation shall include: `prose`, `action_verb`, `subject_noun`, `clause_citation`, `section_reference`, `modality_facet`.  
_Traces to: C-03 | Current state: Partially functional ([extraction.py:L283-326](backend/app/services/extraction.py#L283-L326)) | Work: Harden error handling. Ensure returned items have all 6 fields populated._

**FR-06** — System shall support 3 document types without per-regulation prompting: `REGULATORY_GUIDELINE` → obligations, `ENTERPRISE_POLICY` → control objectives, `PROCEDURE_SOP` → control activities.  
_Traces to: C-03 | Current state: Exists ([extraction.py:L46-51](backend/app/services/extraction.py#L46-L51)) | Work: None — already functional._

**FR-07** — When LLM is unavailable during extraction, system shall return an empty result with `extraction_method: "FAILED"` and HTTP 503 status. System shall NOT fabricate obligations from regex fallback.  
_Traces to: C-04, U-04 | Current state: Returns empty list silently | Work: Add explicit failure signal and disable regex fabrication path._

### 4.3 Set-Theory Classification & Mapping

**FR-08** — System shall classify each obligation↔control pair into exactly one of: `EQUIVALENT_TO`, `SUPERSET_OF`, `SUBSET_OF`, `INTERSECTS_WITH`, `NO_RELATIONSHIP` using the LLM-based NLI engine.  
_Traces to: C-04, C-06 | Current state: LLM path exists ([nli_engine.py:L62-76](backend/app/services/nli_engine.py#L62-L76)); keyword fallback produces fake confidence | Work: Remove keyword fallback or cap its confidence at 0.30 with `extraction_method: "HEURISTIC_DEGRADED"`._

**FR-09** — When the NLI LLM is unavailable, system shall mark the pair as `PENDING_CLASSIFICATION` with `confidence: 0.0` and `extraction_method: "FAILED"`. System shall NOT produce high-confidence scores from keyword heuristics.  
_Traces to: C-04, U-04 | Current state: Keyword fallback produces 0.88-0.95 confidence ([nli_engine.py:L85-180](backend/app/services/nli_engine.py#L85-L180)) | Work: Replace keyword fallback with explicit failure/pending state._

**FR-10** — Graph compiler shall create `Gap` nodes for both `NO_RELATIONSHIP` (cosine < 0.30) AND `SUBSET_OF` classifications, per BR-07.  
_Traces to: C-06, C-07 | Current state: Gaps only for cosine < 0.30 ([graph_compiler.py:L75-88](backend/app/services/graph_compiler.py#L75-L88)) | Work: Add gap creation rule for SUBSET_OF._

**FR-11** — Each `Gap` node shall include: source obligation text, target control text, set-theory relation, severity, and the regulatory clause citation that generated it.  
_Traces to: C-07 | Current state: `gap_type` and `gap_severity` only | Work: Add `source_text`, `target_text`, `clause_citation` to Gap metadata._

### 4.4 Dual-Judge Validation Gate

**FR-12** — Every graph mutation produced by the compiler shall pass through dual-judge validation **synchronously before** Memgraph commit. `MemgraphService.enqueue_and_execute()` shall call dual-judge and block on result.  
_Traces to: C-05 | Current state: Judge is async and disconnected from commit path ([memgraph_service.py:L115-173](backend/app/services/memgraph_service.py#L115-L173)) | Work: Wire `DualJudgeService.evaluate()` into `enqueue_and_execute()` before Cypher execution._

**FR-13** — Logic Judge threshold shall be ≥ 0.95 semantic faithfulness. Technical Judge threshold shall be 1.00 parameter accuracy. Mappings failing either threshold shall be marked `PENDING_HITL_REVIEW` and NOT committed to the production graph.  
_Traces to: C-05 | Current state: Thresholds are 0.80 and 0.85 ([judge.py:L44](backend/app/services/judge.py#L44), [dual_judge_async.py:L84](backend/app/services/dual_judge_async.py#L84)) | Work: Update threshold constants. Add `PENDING_HITL_REVIEW` status._

**FR-14** — When dual-judge LLM is unavailable, system shall mark the mapping as `PENDING_JUDGE_REVIEW` and NOT commit it. System shall NOT compute scores arithmetically from input confidence.  
_Traces to: C-05, U-05 | Current state: `logic_score = confidence * 1.02` ([dual_judge_async.py:L82-85](backend/app/services/dual_judge_async.py#L82-L85)) | Work: Replace arithmetic fallback with explicit pending state._

### 4.5 Graph Storage & Integrity

**FR-15** — Validated mutations shall be committed to Memgraph via transactional outbox pattern. `GraphOutboxLog` status shall be `EXECUTED` only after both Memgraph write AND PostgreSQL commit succeed.  
_Traces to: C-09 | Current state: Exists ([memgraph_service.py:L115-173](backend/app/services/memgraph_service.py#L115-L173)) | Work: None — already functional. Wire judge gate in front._

**FR-16** — `delete_file()` and `delete_collection()` in MinIO and Qdrant storage wrappers shall raise `OperationNotPermitted` when called on `source-regulations` or `bronze-layer` buckets / compliance collections.  
_Traces to: C-10 | Current state: Unguarded delete methods ([storage/__init__.py:L242-253](backend/app/storage/__init__.py#L242-L253)) | Work: Add bucket/collection guards._

**FR-17** — System shall validate at startup that `LLM_ENDPOINT` resolves to a local/private network address (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16). Log a WARNING if it resolves to a public IP.  
_Traces to: C-11 | Current state: No validation ([extraction.py:L37](backend/app/services/extraction.py#L37)) | Work: Add startup check in app initialization._

### 4.6 Compliance Query API

**FR-18** — `GET /api/gaps` shall return all active Gap nodes with: gap_id, severity, source obligation text, target control text, set-theory relation, clause citation, and creation timestamp.  
_Traces to: C-08 | Current state: No gap query endpoint | Work: New API endpoint + Cypher query._

**FR-19** — `GET /api/gaps/{gap_id}/trace` shall return the full reasoning path: source document → extracted obligation → NLI classification → judge scores → gap determination.  
_Traces to: C-08 | Current state: No trace endpoint | Work: New API endpoint joining outbox log + judge results + gap metadata._

**FR-20** — `GET /api/controls/{control_id}/mappings` shall return all obligation mappings for a given control, including set-theory relation, confidence score, and judge pass/fail status.  
_Traces to: C-08 | Current state: No control query endpoint | Work: New API endpoint._

---

## 5. Non-Functional Requirements

**NFR-01 — Availability:** System shall operate with LLM endpoint available. When LLM is down, system shall degrade gracefully: all AI-dependent operations return explicit failure status, never heuristic results. _Traces to: FR-07, FR-09, FR-14, U-04, U-05._

**NFR-02 — Performance:** PDF-to-Markdown conversion shall complete in < 60 seconds for documents ≤ 100 pages. Extraction of obligations from a 50-chunk document shall complete in < 5 minutes. _Traces to: BRD §8 KPIs._

**NFR-03 — Observability:** All degradation events (LLM failure, NLI fallback, judge unavailability) shall be logged via `log_degradation_event()` with `service`, `method_used`, `error`, and `context` fields. _Traces to: Existing pattern in [nli_engine.py:L78-84](backend/app/services/nli_engine.py#L78-L84). Already partially implemented._

**NFR-04 — Data Integrity:** No SQL/Cypher injection possible via user-supplied document content. All Cypher queries shall use parameterized templates (already the case in [rckg_queries.py](backend/app/graph/rckg_queries.py)). All MinIO keys shall be validated against path traversal ([bronze_layer.py:L22](backend/app/services/bronze_layer.py#L22) pattern already exists).

**NFR-05 — Testability:** All Must-have requirements shall have corresponding pytest tests. Tests shall not depend on a live LLM — LLM calls shall be mockable via dependency injection or environment variable.

---

## 6. Explicitly Out of Scope — With Reasons

| # | Capability | Reason for Exclusion |
|---|---|---|
| OOS-01 | OSCAL artifact generation (REQ-019) | Reporting format on graph output. Core graph must exist first. Deferred to post-MVP. |
| OOS-02 | GRC platform integration (REQ-026) | Integration channel. Depends on BRD assumption A-01 (GRC API access). Zero code exists. |
| OOS-03 | ESG/ESRS/GRI/TCFD crosswalks (REQ-030) | Secondary objective (BO-17). Zero code exists. Orthogonal to core compliance flow. |
| OOS-04 | ThirdParty nodes + VENDOR_OF edges (REQ-031) | Secondary objective (BO-16). Only SHACL shape exists. Orthogonal to core flow. |
| OOS-05 | DPO fine-tuning pipeline (REQ-029) | Self-improvement loop. Not needed to prove core extraction + mapping works. |
| OOS-06 | Continuous regulatory monitoring (REQ-036) | BRD §9 explicitly defers: "manual upload supported initially." |
| OOS-07 | Multilingual ingestion (REQ-008) | English-only sufficient for MVP demo. BGE-M3 can be added as deployment config. |
| OOS-08 | Declarative agent governance runtime (REQ-025) | Dev tooling pattern. No runtime governance system needed for single-user MVP. |
| OOS-09 | Metadata-level access controls (REQ-024) | Multi-user governance. Single-user MVP. |
| OOS-10 | Hot→cold migration pipeline (REQ-023 partial) | Retention lifecycle. Both stores run in parallel; no archival needed for 6-week demo. |
| OOS-11 | Board-level executive dashboard (BRD BO-18) | BRD §9 explicitly defers. |
| OOS-12 | Temporal.io concrete workflows (REQ-028) | Direct service calls work for MVP. Base workflow scaffold preserved. |
| OOS-13 | Evidence propagation / transitive coverage (REQ-017) | Complex graph algorithm. Requires working mappings to exist first. Post-MVP. |
| OOS-14 | Point-in-time compliance reconstruction (REQ-021) | Requires complete bitemporal model (C-14). C-14 is Should, not Must. |

---

## 7. Assumptions & Open Questions

### Assumptions

| ID | Assumption | Impact if Invalid |
|---|---|---|
| A-01 | A vLLM or Ollama endpoint running Mistral 8B (extraction) and Llama 3.1 (judge) will be available during development and demo. | All AI-dependent features cannot be tested end-to-end. Tests use mocks but integration requires live LLM. |
| A-02 | MinerU Python package (`magic-pdf`) is installable in the development environment. | FR-02 cannot be implemented. Marker-only fallback would need to be promoted to primary. |
| A-03 | Marker Python package is installable as secondary parser. | If both MinerU and Marker fail, manual Markdown upload remains as escape hatch. |
| A-04 | Team composition is 2 engineers (1 lead AI/infra, 1 backend). No dedicated QA — TDD is the quality gate. | Velocity estimates assume this. More engineers = faster delivery; fewer = cut Should items. |
| A-05 | Sprint length is 2 weeks. | Standard cadence from prior plan. |
| A-06 | The NLI engine will use the same LLM (Mistral 8B or Llama 3.1) for classification, not a separate DeBERTa model. | DeBERTa is mentioned in code comments/docstrings but no actual model loading code exists. LLM proxy is the practical path for MVP. |

### Open Questions

| ID | Question | Impact |
|---|---|---|
| OQ-01 | Should `CONTINGENT_SATISFIES` (6th relation, U-01) be kept or removed? BRD specifies 5 relations. Code implements 6. | Affects FR-08 classification set. Recommendation: keep for now, document as extension. |
| OQ-02 | What is the minimum set of test PDFs for FR-03 validation? Do we have real regulatory PDFs in the repo? | Need 2-3 representative PDFs for integration testing. |
| OQ-03 | FR-13 requires Logic Judge ≥ 0.95 and Technical Judge = 1.00. Should the MVP relax Technical Judge to ≥ 0.95 since 100% may be unrealistic with current models? | BRD says 100%. Recommend implementing as stated and measuring real-world performance to inform post-MVP threshold tuning. |
| OQ-04 | The `LLM_ENDPOINT` default in `repair.py` is still `:8000` (collides with FastAPI). Should repair service be in MVP scope? | Not in core journey. But the port collision is a bug that should be fixed opportunistically. |
| OQ-05 | The `old_rckg/` directory at repo root (U-11) — should it be deleted as part of MVP cleanup? | Low priority but reduces confusion. Recommend deleting in Sprint 1. |

---

## 8. Dependencies & Risks

### Dependencies

| ID | Dependency | Owner | Status | Mitigation |
|---|---|---|---|---|
| D-01 | MinerU (`magic-pdf`) Python package installable on target platform | External (open-source) | Uncertain — BRD AMB-02 | Validate in Sprint 1, Day 1. If blocked, Marker becomes primary and manual Markdown upload is escape hatch. |
| D-02 | vLLM or Ollama endpoint with Mistral 8B + Llama 3.1 models loaded | Internal infra | Assumed available | Document setup steps. Provide Ollama docker-compose service as fallback. |
| D-03 | Memgraph container accessible and schema initialized | Internal infra | Available ([docker-compose.yml:L60-82](docker-compose.yml#L60-L82)) | Already containerized. |
| D-04 | PostgreSQL with schema migrations applied | Internal infra | Available ([docker-compose.yml:L30-55](docker-compose.yml#L30-L55)) | Already containerized. |

### Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | MinerU package has undocumented GPU dependencies or large model downloads that delay Sprint 1 | MEDIUM | HIGH — blocks all ingestion | Timebox to 2 days. If blocked, use Marker as primary and defer MinerU. |
| R-02 | Dual-judge at BRD thresholds (0.95/1.00) rejects too many valid mappings, making the system unusable | MEDIUM | MEDIUM | Measure rejection rate on golden-50 dataset. Report to stakeholder for threshold review. |
| R-03 | Synchronous dual-judge call adds unacceptable latency to graph commit path | LOW | MEDIUM | Judge LLM call is single inference. < 5s per call expected. Batch optimization available post-MVP. |
| R-04 | Removing keyword NLI fallback means the system is non-functional without LLM | HIGH (by design) | LOW (correct behavior) | This is the intended behavior per BO-03. Document clearly. NFR-01 governs graceful degradation. |
