# First-Principles BRD Compliance Audit — RCKG Codebase

**Auditor Posture:** Independent, neutral, first-principles  
**BRD Version:** 2.0 — End-State Architecture Alignment (2026-04-13)  
**Codebase Snapshot:** 2026-08-08  
**Method:** Requirement → Expected Behavior → Code Investigation → Verdict

---

## Step 1 — Requirements Inventory

Each BRD requirement is decomposed into atomic, testable items.

| ID | Source | Atomic Requirement |
|---|---|---|
| REQ-001 | BR-01 | System shall continuously ingest regulatory documents from authoritative sources |
| REQ-002 | BR-01 | System shall parse documents into structured, machine-readable formats |
| REQ-003 | BR-01 | System shall preserve all hierarchical structure, tables, and clause relationships during parsing |
| REQ-004 | BR-02 | System shall extract discrete, structured rule units from regulatory text |
| REQ-005 | BR-02 | Extraction shall require no human annotation or domain-specific prompting per regulation |
| REQ-006 | BR-03 | System shall maintain a versioned registry of all regulatory frameworks |
| REQ-007 | BR-03 | Registry shall track publication date, effective date, supersession relationships, and jurisdiction |
| REQ-008 | BR-04 | System shall support ingestion of documents in 84+ languages (multilingual) |
| REQ-009 | BR-05 | System shall use MinerU for high-fidelity PDF-to-Markdown conversion |
| REQ-010 | BR-05 | Marker shall be fallback for complex layouts |
| REQ-011 | BR-05 | Conversion shall achieve zero-loss heading hierarchy and table preservation |
| REQ-012 | BR-06 | System shall automatically map controls to obligations using set-theory classifications: Equivalent-to, Superset-of, Subset-of, Intersects-with, No-relationship |
| REQ-013 | BR-07 | System shall identify and surface all compliance gaps (Subset-of and No-relationship) |
| REQ-014 | BR-07 | Gaps shall have sufficient context for remediation without manual re-review |
| REQ-015 | BR-08 | System shall execute crosswalks across 10,000+ controls vs 5,000+ clauses in near real-time |
| REQ-016 | BR-08 | ColBERT late-interaction retrieval shall achieve >90% classification accuracy |
| REQ-017 | BR-09 | Single evidenced control shall propagate to satisfy all overlapping regulatory requirements |
| REQ-018 | BR-10 | Bitemporal data model: `valid_from`/`valid_to` (event time) + `ingested_at` (system time) on all nodes and edges |
| REQ-019 | BR-11 | System shall generate OSCAL artifacts (XML, JSON, YAML) from graph state |
| REQ-020 | BR-12 | System shall provide explainable, path-traceable compliance query answers |
| REQ-021 | BR-13 | Temporal compliance queries: reconstruct compliance posture at any prior point |
| REQ-022 | BR-14 | No obligation record, control mapping, or evidence shall ever be permanently deleted |
| REQ-023 | BR-15 | Hot/cold graph separation: Memgraph (32GB hot) + PostgreSQL cold store (90TB+) |
| REQ-024 | BR-16 | Configurable data governance layer with metadata-level access controls |
| REQ-025 | BR-17 | Declarative governance specs (`agents.md`, `skills.md`) constraining agent behavior |
| REQ-026 | BR-18 | Integration with tier-1 enterprise GRC platform via bidirectional API sync |
| REQ-027 | BR-19 | Self-hosted deployment in air-gapped environments |
| REQ-028 | BR-20 | Temporal.io workflow orchestration with HITL approval gates and pause/resume |
| REQ-029 | BR-21 | DPO fine-tuning pipeline ingesting human corrections from HITL review sessions |
| REQ-030 | BR-22 | ESG risk dimension tracking with ESRS, GRI, TCFD crosswalks |
| REQ-031 | BR-23 | Third-party vendor risk tracking with `ThirdParty` nodes and `VENDOR_OF` edges |
| REQ-032 | Constraint | Dual-Judge validation: Logic Judge (>0.95 semantic faithfulness) + Technical Judge (100% parameter accuracy) before production commit |
| REQ-033 | Constraint | All AI models must be open-source with zero external API dependencies |
| REQ-034 | Constraint | No AI determination committed without dual-judge pass |
| REQ-035 | BO-06 | Dual-Judge: independent Logic + Technical judges; failures trigger HITL review |
| REQ-036 | BO-01 | Continuous compliance monitoring without human-triggered initiation |

---

## Step 2 — Expected Behavior & Step 3–4 — Investigation + Verdict

### Requirements Traceability Matrix

| ID | Requirement (short) | Verdict | Evidence (file:line) | Notes |
|---|---|---|---|---|
| REQ-001 | Continuous ingestion from authoritative sources | **NOT MET** | `document_upload.py:L54-215` | Manual upload only. BRD §9 says "automated monitoring is future phase — manual upload supported initially." But BR-01 says "continuously ingest." Ambiguity between BR-01 and §9. |
| REQ-002 | Parse into structured formats | **PARTIALLY MET** | `pdf_to_markdown.py:L185-308` | Parse pipeline exists with MinerU→Marker fallback. But `_run_mineru()` (L162) and `_run_marker()` (L182) both raise `RuntimeError` — production parsing is **stubbed out**. |
| REQ-003 | Preserve hierarchical structure/tables/clauses | **PARTIALLY MET** | `pdf_to_markdown.py:L101-143` | `_MinerUResult` tracks headings, tables, footnotes. But actual conversion functions are stubs. No runtime evidence of preservation. |
| REQ-004 | Extract structured rule units | **PARTIALLY MET** | `extraction.py:L283-326` | `extract_obligations()` calls LLM for extraction and validates via Pydantic. Works when LLM is available. No fallback if LLM is down — returns empty list. |
| REQ-005 | No human annotation per regulation | **MET** | `extraction.py:L54-67` | Prompt templates are generic per document type (REGULATORY_GUIDELINE, ENTERPRISE_POLICY, PROCEDURE_SOP). No per-regulation prompting required. |
| REQ-006 | Versioned registry of regulatory frameworks | **NOT MET** | `models/rckg_nodes.py:L72-96` | `ObligationNode` has `framework_name` and `framework_version`, but no dedicated framework registry table/service exists. |
| REQ-007 | Registry tracks publication date, effective date, supersession, jurisdiction | **NOT MET** | Full codebase | No `publication_date`, `effective_date`, `jurisdiction`, or `supersedes` fields exist anywhere in ORM models. |
| REQ-008 | 84+ language support (multilingual ingestion) | **NOT VERIFIABLE** | `storage/qdrant.py:L49` | Qdrant configured with BGE-M3 vector size (1024-dim). BGE-M3 supports 100+ languages. But no actual BGE-M3 embedding service is implemented. |
| REQ-009 | MinerU for PDF conversion | **PARTIALLY MET** | `pdf_to_markdown.py:L30-62` | `MinerUConverter` class exists with correct interface. But `_run_mineru()` at L162 is a stub: `raise RuntimeError`. |
| REQ-010 | Marker as fallback | **PARTIALLY MET** | `pdf_to_markdown.py:L65-98, L240-255` | `MarkerFallbackConverter` exists. Fallback logic triggers when confidence < 0.85. But `_run_marker()` at L182 is also a stub. |
| REQ-011 | Zero-loss heading hierarchy + table preservation | **NOT VERIFIABLE** | `pdf_to_markdown.py:L101-143` | Result classes track headings/tables/footnotes, but production conversion is stubbed. |
| REQ-012 | Set-theory mapping classifications | **MET** | `rckg_nodes.py:L34-49` | `SetTheoryRelation` enum covers all 5 BRD-specified relations. Additionally includes `CONTINGENT_SATISFIES` (6th). Mapping tables carry `set_theory_relation` column. |
| REQ-013 | Identify and surface compliance gaps | **PARTIALLY MET** | `graph_compiler.py:L75-88, rckg_nodes.py:L286-318` | `RuleBasedGraphCompiler` creates `CREATE_GAP` for disjoint entities (cosine < 0.30). BRD says gaps on Subset-of AND No-relationship, but compiler only creates gaps for cosine < 0.30. |
| REQ-014 | Gaps have sufficient context for remediation | **PARTIALLY MET** | `graph_compiler.py:L77-87` | Gap metadata includes `gap_type` and `gap_severity`. No regulatory clause text or remediation context attached. |
| REQ-015 | 10K controls × 5K clauses in near real-time | **NOT VERIFIABLE** | `cold_start_pipeline.py:L36-130` | Pairwise comparisons exist but use naive token overlap (L110-L113), not scalable retrieval index. No benchmarks. |
| REQ-016 | ColBERT >90% classification accuracy | **PARTIALLY MET** | `retrieval/colbert_service.py:L66-121` | `ColBERTReranker` implements MaxSim scoring. Uses synthetic embeddings (hash-seeded random vectors, L33-L50), not actual ColBERTv2 model. |
| REQ-017 | Single control propagates to all overlapping requirements | **NOT MET** | Full codebase | No evidence propagation or transitive coverage logic found. |
| REQ-018 | Bitemporal on all nodes and edges | **PARTIALLY MET** | `rckg_nodes.py:L89-92, models/__init__.py:L261-263` | `ObligationNode` has `valid_from`/`valid_to`. `GoldenControl` has all three. 5 of 7 node types and all edge types lack bitemporal fields. |
| REQ-019 | OSCAL artifact generation | **NOT MET** | Full codebase | Zero references to "OSCAL" in entire backend directory. |
| REQ-020 | Explainable path-traceable queries | **PARTIALLY MET** | `graph/rckg_queries.py:L12-253` | Cypher queries link nodes with metadata. No user-facing API returning explanation chains. |
| REQ-021 | Temporal compliance queries | **PARTIALLY MET** | `models/__init__.py:L323-329, embedding_sync.py:L39-51` | `GoldenControl.is_valid_at()` enables point-in-time check. No full compliance posture reconstruction API. |
| REQ-022 | No permanent deletion | **PARTIALLY MET** | `rckg_queries.py:L204-213, storage/__init__.py:L242-253` | SUPERSEDE/DEPRECATE use soft-delete. But `delete_file()`, `delete_collection()`, `delete_bucket()` exist unguarded. |
| REQ-023 | Hot/cold graph separation | **PARTIALLY MET** | `docker-compose.yml:L82, L51` | Both stores configured. No cold archival service, no monthly retention cycle, no migration pipeline. |
| REQ-024 | Data governance with metadata access controls | **PARTIALLY MET** | `governance_engine.py:L28-119` | Graph-mutation governance exists. No document/source access governance. |
| REQ-025 | Declarative governance via agents.md/skills.md | **NOT MET** | Full codebase | No agents.md/skills.md in application runtime. No parser or enforcement engine. |
| REQ-026 | GRC platform integration | **NOT MET** | Full codebase | Zero GRC integration code. |
| REQ-027 | Self-hosted air-gapped deployment | **PARTIALLY MET** | `docker-compose.yml, extraction.py:L37-39` | All services containerized, open-source images. No air-gap deployment docs. Langfuse may need external deps. |
| REQ-028 | Temporal.io with HITL pause/resume | **PARTIALLY MET** | `workflows/base.py:L30-116` | BaseWorkflow has pause/approve signals. No concrete workflow subclass. `execute()` raises `NotImplementedError`. |
| REQ-029 | DPO fine-tuning pipeline | **PARTIALLY MET** | `dual_judge_async.py:L100-138` | PreferenceAccumulatorWorker accumulates pairs. `_publish_retrain_trigger_event()` is a stub (logs only). |
| REQ-030 | ESG/ESRS/GRI/TCFD tracking | **NOT MET** | Full codebase | Zero ESG references in backend. |
| REQ-031 | ThirdParty nodes + VENDOR_OF edges | **PARTIALLY MET** | `shapes/third_party.ttl` | SHACL shape exists. No ORM model, no VENDOR_OF edge, no risk scoring. |
| REQ-032 | Dual-Judge >0.95 / 100% before commit | **PARTIALLY MET** | `dual_judge_async.py:L19-97` | Scores exist but threshold is 0.85, not 0.95/1.00. Arithmetic fallback auto-approves. |
| REQ-033 | Open-source AI, zero external API | **PARTIALLY MET** | `extraction.py:L39, judge.py:L37` | Mistral 8B + Llama 3.1 used. No hard guard against external API use. |
| REQ-034 | No commit without dual-judge pass | **NOT MET** | `memgraph_service.py:L115-173` | Graph commits happen without any judge check. Dual-judge is separate/async. |
| REQ-035 | Independent Logic + Technical judges; failures → HITL | **PARTIALLY MET** | `judge.py:L256-321` | Single LLM call (not independent). Threshold 0.80. No HITL escalation. |
| REQ-036 | Continuous monitoring without human trigger | **NOT MET** | Full codebase | No scheduled or autonomous monitoring. All processing requires explicit API calls. |

### Verdict Summary

| Verdict | Count |
|---|---|
| **MET** | 2 |
| **PARTIALLY MET** | 18 |
| **NOT MET** | 13 |
| **NOT VERIFIABLE** | 3 |

---

## Step 5 — Reverse Check (Undocumented Behavior)

| # | Undocumented Feature | Location | Risk |
|---|---|---|---|
| U-01 | `CONTINGENT_SATISFIES` 6th set-theory relation | `rckg_nodes.py:L47`, `nli_engine.py:L47` | LOW — scope creep, not in BRD's 5-relation spec |
| U-02 | Langfuse observability integration | `langfuse_tracing.py`, `docker-compose.yml:L204-225` | LOW — beneficial |
| U-03 | Redis 8GB cache layer | `core/cache.py`, `docker-compose.yml:L157-173` | LOW |
| U-04 | **Keyword-heuristic NLI fallback** | `nli_engine.py:L85-180` | **HIGH** — produces hardcoded high-confidence (0.88-0.95) classifications on keyword match. Misrepresents heuristic output as AI-validated. |
| U-05 | **Arithmetic dual-judge fallback** | `dual_judge_async.py:L82-85` | **HIGH** — self-referential approval: `logic_score = confidence * 1.02`. Can auto-approve without any AI evaluation. |
| U-06 | Golden Assertions regression guard | `governance_engine.py:L42-89` | LOW — protective |
| U-07 | Reconciliation DLQ | `models/__init__.py:L421-459` | LOW |
| U-08 | Graph Outbox dual-write pattern | `rckg_nodes.py:L519-531`, `memgraph_service.py:L115-173` | LOW — good practice |
| U-09 | ShortCircuitAuditLog for disjoint candidates | `rckg_nodes.py:L326-342` | LOW |
| U-10 | Format classifier | `format_classifier.py` | LOW |
| U-11 | `old_rckg/` directory at repo root | Root directory | MEDIUM — dead code |

---

## Step 6 — Detailed Findings

### FINDING-001: MinerU/Marker Conversion is Completely Stubbed (REQ-009, REQ-010, REQ-011)

**Severity:** CRITICAL

Both conversion functions raise `RuntimeError`. The entire PDF ingestion pipeline is non-functional.

**Evidence:** `pdf_to_markdown.py:L157-182`

```python
def _run_mineru(pdf_path: str) -> _MinerUResult:
    raise RuntimeError("MinerU library not available in this environment")

def _run_marker(pdf_path: str) -> _MarkerResult:
    raise RuntimeError("Marker library not available in this environment")
```

The architecture (MinerU primary → confidence check → Marker fallback) is correct, but the actual conversion layer is absent.

---

### FINDING-002: No OSCAL Artifact Generation (REQ-019)

**Severity:** HIGH

`grep -r "OSCAL" backend/` returns zero results. No OSCAL schema, no serialization logic, no export endpoint. Complete omission of a primary business requirement (BR-11).

---

### FINDING-003: Dual-Judge Does Not Gate Production Commits (REQ-032, REQ-034)

**Severity:** CRITICAL

1. **Graph commits bypass judge:** `memgraph_service.py:L115-173` — `enqueue_and_execute()` checks governance engine but has no reference to dual-judge. Mutations commit immediately.

2. **Wrong thresholds:** BRD requires Logic >0.95 and Technical 100%. Code uses 0.80 (`judge.py:L44`) and 0.85 (`dual_judge_async.py:L84`).

3. **Not independent:** `judge.py` is a single LLM call returning multiple scores. BRD requires two independent specialized judges.

4. **Arithmetic fallback:** `dual_judge_async.py:L82-85` — when LLM unavailable, `logic_score = confidence * 1.02`, `tech_score = confidence * 0.98`. Self-referential approval loop.

---

### FINDING-004: No GRC Platform Integration (REQ-026)

**Severity:** HIGH

Zero GRC integration code. No API connectors, sync services, or configuration for any tier-1 GRC platform.

---

### FINDING-005: Bitemporal Model Incomplete (REQ-018)

**Severity:** MEDIUM-HIGH

**Has bitemporal fields:**
- `ObligationNode`: `valid_from`, `valid_to` ✓ (no `ingested_at` ✗)
- `GoldenControl`: `valid_from`, `valid_to`, `ingested_at` ✓

**Lacks bitemporal fields:**
- `ControlObjectiveNode` — only `created_at`, `updated_at`
- `ControlActivityNode` — only `created_at`, `updated_at`
- `FrameworkControlObjectiveNode` — only `created_at`, `updated_at`
- `FrameworkControlActivityNode` — only `created_at`, `updated_at`
- `RiskNode` — only `created_at`, `updated_at`
- All 5 mapping/edge tables — no bitemporal fields

BRD says "all graph nodes and edges." 5 of 7 node types and all edge types are non-compliant.

---

### FINDING-006: No Framework Registry (REQ-006, REQ-007)

**Severity:** MEDIUM

`ObligationNode.framework_name` and `framework_version` are plain string columns. No dedicated `Framework` entity, no `publication_date`, `effective_date`, `jurisdiction`, or `supersedes` fields.

---

### FINDING-007: NLI Engine Uses Hardcoded Keyword Heuristics (REQ-012, REQ-016)

**Severity:** HIGH

`nli_engine.py:L85-180` — When LLM unavailable, NLI falls back to keyword matching:

```python
elif "encrypt" in p_lower and "encrypt" in h_lower and "pii" in p_lower:
    relation = "EQUIVALENT_TO"
    confidence = 0.95
```

These are test-fixture-specific heuristics producing high-confidence scores (0.88-0.95) that downstream systems treat as AI-validated.

---

### FINDING-008: ColBERT Uses Synthetic Embeddings (REQ-016)

**Severity:** HIGH

`colbert_service.py:L33-50` — Token embeddings are pseudo-random vectors from character hash seeds, not from a trained ColBERTv2 model. MaxSim scores are meaningless for semantic similarity.

---

### FINDING-009: No ESG/ESRS/GRI/TCFD Support (REQ-030)

**Severity:** MEDIUM

Zero ESG references in backend code. Complete omission of BR-22.

---

### FINDING-010: ThirdParty/VENDOR_OF Partial (REQ-031)

**Severity:** MEDIUM

SHACL shape exists (`shapes/third_party.ttl`). No ORM model, no `VENDOR_OF` edge type, no supplier risk scoring.

---

### FINDING-011: Declarative Agent Governance Absent (REQ-025)

**Severity:** MEDIUM

No `agents.md`/`skills.md` in application runtime path. No parser or enforcement engine.

---

### FINDING-012: DPO Pipeline Stubbed (REQ-029)

**Severity:** MEDIUM

`dual_judge_async.py:L132-137` — `_publish_retrain_trigger_event()` only logs a message. No Kafka event, no training pipeline, no model fine-tuning.

---

### FINDING-013: Evidence Propagation Not Implemented (REQ-017)

**Severity:** MEDIUM-HIGH

Mapping tables create 1:1 linkages. No transitive closure, no evidence deduplication across overlapping frameworks.

---

### FINDING-014: Continuous Monitoring Absent (REQ-036)

**Severity:** HIGH

All processing requires explicit API calls. No scheduled tasks, event-driven monitors, or autonomous detection.

---

## Open Questions / Ambiguities

| # | Ambiguity | Impact |
|---|---|---|
| AMB-01 | BR-01 says "continuously ingest" but §9 says "automated monitoring is future phase — manual upload initially." Contradictory. | REQ-001 verdict |
| AMB-02 | BR-05 names "MinerU" but doesn't specify the Python package. Is the stub acceptable as "architecture-ready"? | REQ-009 verdict |
| AMB-03 | BR-08 says ">90% accuracy" without specifying evaluation dataset, methodology, or what "classification" means. | REQ-016 testability |
| AMB-04 | BR-17 says `agents.md`/`skills.md` — is this runtime governance or dev tooling? | REQ-025 interpretation |
| AMB-05 | BR-20 says "Temporal.io" but doesn't define which workflows must use Temporal vs. direct calls. | REQ-028 completeness |

---

## Overall Assessment

**Compliance State: SUBSTANTIALLY INCOMPLETE**

The RCKG codebase demonstrates a well-architected foundation with correct structural decisions — the data model, graph schema, service decomposition, and technology choices align with BRD intent. However, the implementation is in an **early-to-mid development state**, with critical capability gaps between the architecture and the BRD's operational requirements:

1. **Critical gaps (business-blocking):** Dual-Judge does not gate production commits (violates the BRD's hardest constraint). PDF parsing is fully stubbed. OSCAL generation is absent. Continuous monitoring does not exist. These four items represent the core value propositions of the platform and none are operational.

2. **Structural gaps (non-trivial to remediate):** Bitemporal modeling is incomplete across 5 of 7 node types and all edge types. No framework registry exists. No GRC integration. No evidence propagation logic. These require data model changes and new services.

3. **High-risk undocumented behavior:** The keyword-heuristic NLI fallback and arithmetic dual-judge fallback can silently produce high-confidence classifications without any AI evaluation, creating a false sense of compliance coverage that directly contradicts BO-03 (deterministic, traceable reasoning).

Of 36 atomic requirements: **2 MET, 18 PARTIALLY MET, 13 NOT MET, 3 NOT VERIFIABLE.** The codebase is approximately 20-30% complete against the full BRD, with the implemented portions concentrated in the ingestion/extraction pipeline and graph schema rather than the compliance intelligence and reporting capabilities that constitute the BRD's primary business value.
