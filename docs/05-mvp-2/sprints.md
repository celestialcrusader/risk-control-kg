# MVP-2 Sprint & Story Breakdown

**Source of Truth:** [requirements.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/requirements.md)  
**Sprint Length:** 2 weeks  
**Team:** 2 engineers (1 lead AI/infra, 1 backend)  
**Assumed Velocity:** ~21 story points per sprint (2-person team, conservative)  
**Total Planned:** 61 points across 3 sprints

---

## Sprint 1: Ingestion Pipeline — Parse Real PDFs, Extract Real Obligations

**Goal:** A compliance officer can upload a PDF and receive structured, LLM-extracted obligations stored in the Silver layer — with no fake/heuristic results.

**Sprint Points:** 21  
**Definition of Done:** Upload a NIST SP 800-53 PDF via API → get back structured obligations with real LLM-extracted `action_verb`, `subject_noun`, `clause_citation` → obligations stored in `semantic_controls` table → test passes against a real 10-page PDF.

---

### MVP2-101 — MinerU PDF-to-Markdown Integration

**Type:** Feature  
**Story Points:** 8 (large — external library integration with unknown dependencies)  
**Traces to:** FR-02, FR-03, C-01, C-02  
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-101.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-101.md) | QA Report: [qa-report-MVP2-101.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-101.md))

**As a** compliance officer,  
**I want** the system to convert my uploaded PDF to structured Markdown preserving headings and tables,  
**so that** downstream extraction can work from clean, structured text instead of raw PDF bytes.

**Acceptance Criteria:**
- [x] `_run_mineru()` in `pdf_to_markdown.py` calls the `magic-pdf` library instead of raising `RuntimeError`
- [x] `_run_marker()` in `pdf_to_markdown.py` calls the Marker library instead of raising `RuntimeError`
- [x] Fallback logic triggers Marker when MinerU confidence < 0.85 (existing architecture preserved)
- [x] Output Markdown contains all H1-H6 headings from a test PDF with 3+ heading levels
- [x] Output Markdown contains table content from a test PDF with at least 1 table
- [x] Conversion completes in < 60 seconds for a 10-page PDF (NFR-02)
- [x] pytest test using a real PDF fixture validates heading count and table presence
- [x] If `magic-pdf` installation fails (R-01), Marker is promoted to primary with a 2-day timebox

---

### MVP2-102 — Eliminate Fabricated Extraction Fallback

**Type:** Bug Fix / Safety  
**Story Points:** 3  
**Traces to:** FR-07, C-03, U-04
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-102.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-102.md) | QA Report: [qa-report-MVP2-102.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-102.md))

**As a** compliance officer,  
**I want** the system to clearly tell me when extraction failed rather than silently making up obligations from regex,  
**so that** I never unknowingly rely on fabricated compliance data.

**Acceptance Criteria:**
- [x] When `_call_llm()` fails or returns unparseable response, `extract_obligations()` returns empty list with `extraction_method: "FAILED"` metadata
- [x] The `process-pdf` endpoint ([extract.py:L203-223](file:///home/zackchow/coding/rckg/backend/app/api/extract.py#L203-L223)) does NOT fall back to `facet_extractor.extract_facets()` to fabricate obligations
- [x] API response includes `degraded: true` flag when LLM was unavailable
- [x] `log_degradation_event()` is called with `service: "Extraction"`, `method_used: "FAILED"`
- [x] pytest test mocks LLM failure → verifies empty result, not fabricated result

---

### MVP2-103 — Harden Extraction Pipeline End-to-End

**Type:** Feature (integration)  
**Story Points:** 5  
**Traces to:** FR-04, FR-05, FR-06, C-03
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-103.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-103.md) | QA Report: [qa-report-MVP2-103.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-103.md))

**As a** compliance officer,  
**I want** to upload a PDF via `POST /documents` and have the system automatically parse it, chunk it, and extract obligations,  
**so that** I get structured compliance data from a single API call.

**Acceptance Criteria:**
- [x] `POST /documents` → PDF stored in MinIO → conversion via MinerU/Marker → chunking via `ClauseBoundaryExtractor` → extraction via `extract_obligations()` → obligations stored in `semantic_controls` table
- [x] Each extracted obligation has all 6 required fields: `prose`, `action_verb`, `subject_noun`, `clause_citation`, `section_reference`, `modality_facet`
- [x] The 3-tier document type dispatch works: `REGULATORY_GUIDELINE` → obligations, `ENTERPRISE_POLICY` → control objectives, `PROCEDURE_SOP` → control activities
- [x] Integration test: upload a 5-page PDF fixture → verify ≥ 3 obligations extracted with non-empty fields
- [x] Bronze layer audit log records the upload event with checksum

---

### MVP2-104 — Delete Guards for Compliance Data

**Type:** Safety  
**Story Points:** 2  
**Traces to:** FR-16, C-10
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-104.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-104.md) | QA Report: [qa-report-MVP2-104.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-104.md))

**As a** system administrator,  
**I want** the system to prevent accidental deletion of compliance data,  
**so that** audit trail integrity is preserved per BR-14.

**Acceptance Criteria:**
- [x] `MinIOStorage.delete_file()` raises `OperationNotPermitted` when `bucket` is `source-regulations` or `bronze-layer`
- [x] `QdrantVectorDB.delete_collection()` raises `OperationNotPermitted` when collection is the compliance collection
- [x] Other buckets/collections remain deletable (no over-broad guard)
- [x] pytest tests verify guard triggers and passes for non-protected resources

---

### MVP2-105 — LLM Endpoint Locality Validation

**Type:** Safety  
**Story Points:** 3  
**Traces to:** FR-17, C-11
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-105.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-105.md) | QA Report: [qa-report-MVP2-105.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-105.md))

**As a** security officer,  
**I want** the system to warn me if the LLM endpoint points to a public API,  
**so that** compliance data is not inadvertently sent to external services.

**Acceptance Criteria:**
- [x] At application startup, system resolves `LLM_ENDPOINT` hostname and checks if IP is in RFC 1918 private ranges or loopback
- [x] If `LLM_ENDPOINT` resolves to a public IP, system logs a `WARNING`-level message: `"LLM_ENDPOINT resolves to public IP — compliance data may leave network boundary"`
- [x] If `LLM_ENDPOINT` is `localhost` or `127.0.0.1` or `10.x`/`172.16-31.x`/`192.168.x`, no warning
- [x] Fix `repair.py:L34` default `LLM_ENDPOINT` from `:8000` to `:8001` to eliminate port collision (OQ-04)
- [x] pytest test with monkeypatched env vars verifies warning vs no-warning

---

## Sprint 2: Classification & Judge Gate — Map With Real AI, Gate With Real Judge

**Goal:** Extracted obligations are classified against existing controls using LLM-based NLI, validated by dual-judge before graph commit, with gaps surfaced — no heuristic shortcuts.

**Sprint Points:** 21  
**Definition of Done:** Extract obligations from Sprint 1 → classify against seed framework controls → dual-judge validates each → approved mappings committed to Memgraph → gaps created for Subset-of and No-relationship → test verifies end-to-end with golden-50 fixture.

---

### MVP2-201 — Eliminate Keyword NLI Fallback, Enforce Honest Failure

**Type:** Bug Fix / Safety  
**Story Points:** 5  
**Traces to:** FR-08, FR-09, C-04, FINDING-007, U-04
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-201.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-201.md) | QA Report: [qa-report-MVP2-201.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-201.md))

**As a** compliance officer,  
**I want** the NLI classification to either give me a real AI assessment or honestly tell me it couldn't classify,  
**so that** I never see a 0.95 confidence score that came from keyword matching.

**Acceptance Criteria:**
- [x] `NliSetTheoryEngine.evaluate_pair()` keyword fallback (L85-180) is replaced: when LLM fails, return `NliResult(set_theory_relation="PENDING_CLASSIFICATION", confidence_score=0.0, metadata={"method": "FAILED"})`
- [x] `is_auto_committed` is `False` for all failed classifications
- [x] `log_degradation_event()` called on LLM failure with full context
- [x] No code path produces confidence > 0.0 without an actual LLM call
- [x] pytest test: mock LLM failure → verify `PENDING_CLASSIFICATION` at confidence 0.0
- [x] pytest test: mock LLM success → verify real classification returned
- [x] The 6 categories list remains unchanged: `EQUIVALENT_TO`, `SUPERSET_OF`, `SUBSET_OF`, `CONTINGENT_SATISFIES`, `INTERSECTS_WITH`, `NO_RELATIONSHIP` (OQ-01: keep CONTINGENT_SATISFIES)

---

### MVP2-202 — Synchronous Dual-Judge Gate Before Graph Commit

**Type:** Feature (critical)  
**Story Points:** 8 (large — wiring async service into sync path + threshold changes + fallback elimination)  
**Traces to:** FR-12, FR-13, FR-14, C-05, FINDING-003, U-05
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-202.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-202.md) | QA Report: [qa-report-MVP2-202.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-202.md))

**As a** compliance officer,  
**I want** every AI-generated mapping to be validated by dual-judge BEFORE it enters the production graph,  
**so that** I can trust that committed data meets audit-grade quality thresholds.

**Acceptance Criteria:**
- [x] `MemgraphService.enqueue_and_execute()` calls `DualJudgeService.evaluate()` synchronously BEFORE rendering Cypher and executing against Memgraph
- [x] Logic Judge threshold updated to ≥ 0.95 (from 0.80)
- [x] Technical Judge threshold updated to ≥ 1.00 (from 0.85)
- [x] Mappings failing either threshold: `outbox_entry.status = "PENDING_HITL_REVIEW"`, NOT committed to Memgraph
- [x] When judge LLM is unavailable: `outbox_entry.status = "PENDING_JUDGE_REVIEW"`, NOT committed. No arithmetic fallback (`confidence * 1.02` at `dual_judge_async.py:L82-85` is removed)
- [x] `GraphOutboxLog` gains a `judge_logic_score` and `judge_technical_score` column for audit trail
- [x] pytest test: mock judge pass → verify Memgraph commit
- [x] pytest test: mock judge fail (logic < 0.95) → verify NOT committed, status = `PENDING_HITL_REVIEW`
- [x] pytest test: mock judge LLM unavailable → verify NOT committed, status = `PENDING_JUDGE_REVIEW`

---

### MVP2-203 — Gap Creation for Subset-of Classifications

**Type:** Feature  
**Story Points:** 3  
**Traces to:** FR-10, FR-11, C-06, C-07
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-203.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-203.md) | QA Report: [qa-report-MVP2-203.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-203.md))

**As a** compliance officer,  
**I want** the system to create Gap nodes for both NO_RELATIONSHIP and SUBSET_OF mappings,  
**so that** I see every case where a control only partially covers a regulatory obligation.

**Acceptance Criteria:**
- [x] `RuleBasedGraphCompiler.compile_mutation()` creates `CREATE_GAP` primitive for `SUBSET_OF` results (in addition to existing cosine < 0.30 rule)
- [x] Gap metadata includes: `source_text` (obligation prose), `target_text` (control text), `clause_citation`, `set_theory_relation`, `gap_severity`
- [x] `gap_severity` for SUBSET_OF is `MEDIUM` (partial coverage); for NO_RELATIONSHIP remains `HIGH`
- [x] pytest test: input pair classified as SUBSET_OF → verify Gap node created with all metadata fields
- [x] pytest test: input pair classified as EQUIVALENT_TO → verify NO gap created

---

### MVP2-204 — Facet Extractor LLM Hardening

**Type:** Improvement  
**Story Points:** 5  
**Traces to:** C-12, supports FR-08
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-204.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-204.md) | QA Report: [qa-report-MVP2-204.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-204.md))

**As a** system,  
**I want** the facet extractor to produce meaningful facets from LLM analysis rather than 10 hardcoded verbs,  
**so that** the graph compiler's matching rules operate on semantically accurate input.

**Acceptance Criteria:**
- [x] `DeJureFacetExtractor.extract_facets()` LLM path returns all 6 facets from actual LLM analysis of clause text
- [x] When LLM fails, regex fallback sets `extraction_method: "REGEX_DEGRADED"` and caps confidence at 0.30 for all facets
- [x] `control_nature` is no longer hardcoded to `"PREVENTATIVE"` — LLM determines it from text
- [x] Regex fallback expands from 10 verbs to at least 25 covering common compliance verbs
- [x] pytest test: mock LLM success → verify all 6 facets populated from LLM
- [x] pytest test: mock LLM failure → verify `extraction_method: "REGEX_DEGRADED"`

---

## Sprint 3: Query API & Integration — Surface Gaps, Trace Reasoning

**Goal:** Compliance officer can query the system for gaps, see traceable reasoning paths, and the full end-to-end flow is validated against real regulatory data.

**Sprint Points:** 19  
**Definition of Done:** `GET /api/gaps` returns actionable gaps with source text → `GET /api/gaps/{id}/trace` returns full reasoning chain → `GET /api/controls/{id}/mappings` returns all mappings → integration test covers upload → parse → extract → classify → judge → commit → query.

---

### MVP2-301 — Gap Query API Endpoint

**Type:** Feature  
**Story Points:** 5  
**Traces to:** FR-18, C-08
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-301.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-301.md) | QA Report: [qa-report-MVP2-301.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-301.md))

**As a** compliance officer,  
**I want** to query `GET /api/gaps` and see all compliance gaps with enough context to start remediation,  
**so that** I don't need to re-read source documents to understand what's missing.

**Acceptance Criteria:**
- [x] `GET /api/gaps` returns JSON list of active Gap nodes
- [x] Each gap includes: `gap_id`, `severity`, `source_obligation_text`, `target_control_text`, `set_theory_relation`, `clause_citation`, `created_at`
- [x] Supports query parameter `?severity=HIGH` to filter by severity
- [x] Supports query parameter `?framework=NIST-800-53` to filter by source framework
- [x] Empty result returns `[]`, not an error
- [x] pytest test: insert 3 Gap nodes → verify API returns all 3 with correct fields
- [x] pytest test: filter by severity=HIGH → verify only HIGH gaps returned

---

### MVP2-302 — Reasoning Trace API Endpoint

**Type:** Feature  
**Story Points:** 5  
**Traces to:** FR-19, C-08
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-302.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-302.md) | QA Report: [qa-report-MVP2-302.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-302.md))

**As a** auditor,  
**I want** to query `GET /api/gaps/{gap_id}/trace` and see the full chain of reasoning that produced a gap,  
**so that** I can verify the system's determination is correct and present it as audit evidence.

**Acceptance Criteria:**
- [x] Response includes: `source_document` (filename, upload date), `extracted_obligation` (prose, clause_citation), `nli_classification` (relation, confidence, method), `judge_scores` (logic_score, technical_score, pass/fail), `gap_determination` (type, severity)
- [x] Data is assembled from: `AuditLog` (upload), `SemanticControl`/`ObligationNode` (extraction), `GraphOutboxLog` (judge result), `GapNode` (gap)
- [x] Returns 404 if gap_id does not exist
- [x] pytest test: create full chain (upload → extract → classify → judge → gap) → verify trace returns all steps

---

### MVP2-303 — Control Mappings Query API

**Type:** Feature  
**Story Points:** 3  
**Traces to:** FR-20, C-08
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-303.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-303.md) | QA Report: [qa-report-MVP2-303.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-303.md))

**As a** compliance officer,  
**I want** to query `GET /api/controls/{control_id}/mappings` to see all obligations mapped to a specific control,  
**so that** I can assess control coverage across regulatory frameworks.

**Acceptance Criteria:**
- [x] Response includes list of mappings, each with: `obligation_id`, `obligation_prose`, `framework_name`, `set_theory_relation`, `confidence_score`, `judge_status` (APPROVED / PENDING_HITL_REVIEW / PENDING_JUDGE_REVIEW)
- [x] Returns empty list if control has no mappings
- [x] pytest test: create 2 mappings for a control → verify API returns both with correct fields

---

### MVP2-304 — End-to-End Integration Test

**Type:** Test / Validation  
**Story Points:** 5  
**Traces to:** All Must-have FRs
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-304.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-304.md) | QA Report: [qa-report-MVP2-304.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-304.md))

**As a** engineering lead,  
**I want** a single integration test that exercises the complete flow from PDF upload to gap query,  
**so that** I can verify the MVP works end-to-end before demo.

**Acceptance Criteria:**
- [x] Test uploads a regulatory PDF fixture via `POST /documents`
- [x] Verifies PDF is stored in MinIO with SHA-256 hash
- [x] Verifies Markdown conversion produced structured output (heading count > 0)
- [x] Verifies ≥ 2 obligations extracted with non-empty `prose` and `action_verb`
- [x] Verifies NLI classification ran (no `PENDING_CLASSIFICATION` results when LLM is mocked as available)
- [x] Verifies dual-judge evaluated each mapping (judge scores recorded in outbox log)
- [x] Verifies at least 1 mapping committed to Memgraph (APPROVED status)
- [x] Verifies `GET /api/gaps` returns results (may be 0 gaps if all are EQUIVALENT_TO, which is valid)
- [x] Verifies `GET /api/controls/{id}/mappings` returns the committed mapping
- [x] Test uses mocked LLM responses (deterministic) — does not require live LLM
- [x] Test cleans up after itself (uses test database/fixtures)

---

### MVP2-305 — Bitemporal Columns on Remaining Node Types

**Type:** Data Model  
**Story Points:** 3 (if no Should items are cut)  
**Traces to:** C-14, FR-15 (supports), FINDING-005  
**Status:** **COMPLETED** (Work Log: [work-log-MVP2-305.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/swe-worklog/work-log-MVP2-305.md) | QA Report: [qa-report-MVP2-305.md](file:///home/zackchow/coding/rckg/docs/05-mvp-2/qa-worklog/qa-report-MVP2-305.md))

**As a** system,  
**I want** all graph node types to have `valid_from`, `valid_to`, and `ingested_at` columns,  
**so that** the data model is consistent and temporal queries can work across all entity types.

**Acceptance Criteria:**
- [x] `ControlObjectiveNode`, `ControlActivityNode`, `FrameworkControlObjectiveNode`, `FrameworkControlActivityNode`, `RiskNode` gain `valid_from` (DateTime, server_default=now), `valid_to` (DateTime, nullable), `ingested_at` (DateTime, server_default=now)
- [x] All 5 mapping/edge tables gain `valid_from`, `valid_to`
- [x] Alembic migration created for schema change
- [x] Existing `SUPERSEDE_NODE` Cypher sets `valid_to` on all node types, not just Obligation
- [x] pytest test: create a ControlObjectiveNode → verify `valid_from` is set, `valid_to` is null

---

## Sprint Dependency Map

```
Sprint 1 (Ingestion)              Sprint 2 (Classification + Judge)     Sprint 3 (Query + Integration)
─────────────────────             ──────────────────────────────────     ──────────────────────────────
MVP2-101 (MinerU/Marker) ──┐
MVP2-102 (No fabrication) ──┤
MVP2-103 (E2E ingestion) ──┼───→ MVP2-201 (No keyword NLI) ──┐
MVP2-104 (Delete guards)   │     MVP2-202 (Judge gate) ───────┤
MVP2-105 (LLM locality)   │     MVP2-203 (Subset-of gaps) ───┤
                           │     MVP2-204 (Facet LLM) ────────┼───→ MVP2-301 (Gap query API)
                           │                                  │     MVP2-302 (Trace API)
                           │                                  │     MVP2-303 (Control mappings API)
                           │                                  ├───→ MVP2-304 (E2E integration test)
                           │                                  │     MVP2-305 (Bitemporal cols) [Should]
                           └──────────────────────────────────┘
```

**Key dependency chain:** Nothing in Sprint 2 works without Sprint 1's PDF parsing and extraction. Nothing in Sprint 3's query APIs works without Sprint 2's classification and judge gate writing data to the graph.

---

## Story Point Summary

| Sprint | Stories | Points | Must-have Points | Should Points |
|---|---|---|---|---|
| Sprint 1 | MVP2-101 through MVP2-105 | 21 | 21 | 0 |
| Sprint 2 | MVP2-201 through MVP2-204 | 21 | 16 | 5 (MVP2-204) |
| Sprint 3 | MVP2-301 through MVP2-305 | 21 | 18 | 3 (MVP2-305) |
| **Total** | **14 stories** | **63** | **55** | **8** |

If velocity is lower than estimated, cut Should items first: MVP2-204 (facet extractor, 5 pts) then MVP2-305 (bitemporal columns, 3 pts). Core journey still works without them.

---

## Risk Escalation Protocol

| Trigger | Action |
|---|---|
| MinerU install fails by Sprint 1 Day 3 | Pivot to Marker-only. Create `SPIKE-MVP2-001` to investigate MinerU in parallel. |
| Dual-judge at BRD thresholds rejects > 80% of golden-50 mappings | Measure and report to stakeholder. Do NOT lower thresholds without approval. |
| Sprint 2 velocity < 15 points | Cut MVP2-204 (facet extractor). Core flow works with existing LLM-fallback-to-degraded facets. |
| Sprint 3 velocity < 15 points | Cut MVP2-305 (bitemporal). Core flow works with `created_at`/`updated_at` on non-Obligation nodes. |
