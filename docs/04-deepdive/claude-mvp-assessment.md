# Independent MVP Remediation Assessment

**Document Version:** 1.0  
**Date:** August 1, 2026  
**Reviewer:** Claude (Independent Assessor)  
**Scope:** Audit of 18 FIX-tickets (Sprints 1–3 in [real-mvp.md](docs/04-deepdive/real-mvp.md)) against all 27 findings in [code-review.md](docs/04-deepdive/code-review.md)  

---

## Executive Summary

The remediation work addressed **structural** aspects of most findings — the scaffolding now attempts LLM calls, routes through the outbox, and queries the database. However, the fixes follow a consistent pattern: **wrap the original stub in a `try` block that calls the LLM; if the LLM fails, fall back to the original broken logic**. This means the system behaves identically to the pre-fix version whenever the LLM is unavailable, and the "fixes" are more accurately described as **optional LLM overlays on top of unchanged stubs**.

Of the 27 original findings, I assess:

| Verdict | Count | Description |
|---------|-------|-------------|
| ✅ **Genuinely Fixed** | 8 | The root cause is eliminated |
| ⚠️ **Partially Fixed** | 10 | LLM happy-path added but fallback retains original broken logic |
| ❌ **Not Fixed** | 5 | Finding was deferred to post-MVP or no meaningful change |
| 🔵 **Deferred (Acknowledged)** | 4 | Explicitly moved to [post-mvp.md](docs/04-deepdive/post-mvp.md) |

> [!WARNING]
> **End-User Testing Readiness: CONDITIONAL**. The system can be end-user tested *only if* a live LLM endpoint (vLLM/Ollama) is available and responding. Without it, 10 of the 18 fixes silently degrade to the original broken behavior and the user will experience the same problems reported in the original review.

---

## Finding-by-Finding Assessment

### Finding #1 — Extraction Prompt Only Handles Obligations
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Tickets:** FIX-102, FIX-103  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [extraction_control_objective.md](backend/app/prompts/extraction_control_objective.md) and [extraction_control_activity.md](backend/app/prompts/extraction_control_activity.md) now exist with well-structured prompt templates.
- [extraction.py](backend/app/services/extraction.py#L46-L51) has a `PROMPT_TEMPLATE_MAP` that dispatches by `document_type`.
- [extraction.py](backend/app/services/extraction.py#L182-L228) has `_parse_llm_response()` that branches on `ENTERPRISE_POLICY` → `control_objectives` and `PROCEDURE_SOP` → `control_activities`.

**Assessment:** This is a solid fix. The 3-tier taxonomy is now represented in prompts and parsing.

---

### Finding #2 — `process-pdf` Bypasses LLM, Uses Only Regex
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Tickets:** FIX-104, FIX-105  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [extract.py L203-L223](backend/app/api/extract.py#L203-L223): The endpoint now calls `_call_llm()` and `_parse_llm_response()` for each chunk.
- **BUT**: Lines 212-223 show that if `extracted_items` is empty (LLM fails or returns nothing), the code falls back to the **exact same regex facet extractor** and **string interpolation** from the original finding:
  ```python
  if not extracted_items:
      facets = facet_extractor.extract_facets(chunk.chunk_text)
      extracted_items = [Obligation(
          prose=f"The {facets['target_role_facet']} must {facets['action_verb']} {facets['subject_noun']}...",
          ...
      )]
  ```

**Residual Risk:** When the LLM is down or returns invalid JSON, the endpoint silently reverts to fabricating prose from regex. There is no signal to the user that extraction degraded. The `clause_citation` now stores `chunk.chunk_text` (good), but the `prose` is still fabricated.

---

### Finding #3 — `DeJureFacetExtractor` Is a Trivial Regex Stub
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Tickets:** None (not directly targeted)  
**Verdict:** ❌ **NOT FIXED**

**Evidence:**
- [facet_extractor.py](backend/app/services/facet_extractor.py) is **completely unchanged** from the original code review. Still has:
  - 10 hardcoded verbs, fallback to `"manage"`
  - 10 hardcoded nouns, fallback to `"system access"`
  - 3 domain facets only
  - `control_nature` hardcoded to `"PREVENTATIVE"` always (line 65)
  - Only 2 target roles

**Impact:** This is the foundation for the Graph Compiler's matching logic. Since it's unchanged, the Cold-Start Pipeline and the `process-pdf` fallback still produce meaningless facets. The real-mvp.md does not have a ticket for this.

---

### Finding #4 — `ColdStartPipelineOrchestrator` Uses Hardcoded Target + Fake Cosine
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Ticket:** FIX-300  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [cold_start_pipeline.py L72-L105](backend/app/services/cold_start_pipeline.py#L72-L105): The code now queries `FrameworkControlObjectiveNode` from DB and computes token overlap similarity.
- **BUT** the candidate generation (lines 82-89) is still poor:
  - `action_verb` is set to `"limit"` if the word "limit" appears in the text, otherwise copies source facet — still keyword matching.
  - `domain_facet` is always copied from the source entity's facet (line 86), meaning candidates inherit the source's domain.
  - `modality_facet`, `target_role_facet`, `control_nature` are always hardcoded to `"MANDATORY"`, `"SYSTEM_ADMINISTRATOR"`, `"PREVENTATIVE"`.
  - If DB query fails or returns no results, falls back to a **single synthetic candidate** (lines 94-105).
- Token overlap as a cosine similarity proxy is a minimal improvement but not semantic similarity.

**Assessment:** The hardcoded `OBL-NIST-AC-2` target is removed. Dynamic DB lookup exists. But the candidate metadata assembly is still largely hardcoded. The "cosine sim" is token overlap, not actual embeddings.

---

### Finding #5 — `NliSetTheoryEngine` Is Hardcoded If/Else
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Ticket:** FIX-301  
**Verdict:** ⚠️ **PARTIALLY FIXED** (try-LLM-then-fallback pattern)

**Evidence:**
- [nli_engine.py L57-L76](backend/app/services/nli_engine.py#L57-L76): `evaluate_pair()` now has a `try` block that calls `_call_llm()` with a classification prompt.
- [nli_engine.py L77-L173](backend/app/services/nli_engine.py#L77-L173): The **entire original if/elif/else keyword chain is still present** as the `except` fallback.
- The fallback still defaults to `EQUIVALENT_TO` with confidence `0.88`, still has fake logit dictionaries, and still claims `model: "DeBERTa-v3-CrossEncoder-Llama3.1-8B-Student"` in metadata (line 172) — **even when using the keyword fallback**.

**Residual Risk:** The metadata field still misrepresents the model used. If the LLM is unavailable, the system classifies with keyword matching and labels it as DeBERTa output. This is deceptive to auditors.

---

### Finding #6 — BM25 Always Raises RuntimeError
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Ticket:** FIX-302  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [bm25_service.py L78-L120](backend/app/services/retrieval/bm25_service.py#L78-L120): The in-memory BM25Okapi implementation with proper IDF calculation (`ln(1 + (N - nq + 0.5) / (nq + 0.5))`) and TF saturation (`k1=1.5, b=0.75`) is mathematically correct.
- The `_execute_es_http_query()` still raises `RuntimeError` (line 49), but the in-memory fallback is now a legitimate BM25 implementation rather than a naive keyword scan.

**Assessment:** For MVP scale (thousands of candidates, not millions), this is a valid fix. The original finding's concern about 50M candidates is a post-MVP scale concern.

---

### Finding #7 — Dual-Judge Uses Arithmetic Instead of LLM
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Ticket:** FIX-305  
**Verdict:** ⚠️ **PARTIALLY FIXED** (try-LLM-then-fallback pattern)

**Evidence:**
- [dual_judge_async.py L60-L75](backend/app/services/dual_judge_async.py#L60-L75): The arithmetic fallback (`conf * 1.02`, `conf * 0.98`) is **still the initial computation** (lines 60-63). The LLM call is attempted after, and its results overwrite the arithmetic values only on success.
- If `_call_llm` throws an exception, the arithmetic values are used silently.

**Residual Risk:** Same as Finding #5 — silent degradation with no audit signal.

---

### Finding #8 — GraphRevert Doesn't Touch Memgraph or PostgreSQL
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Ticket:** FIX-303  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [graph_revert_service.py L50-L90](backend/app/services/graph_revert_service.py#L50-L90): Memgraph Cypher execution and DB ORM update now exist.
- **BUT**: The Cypher uses `self.conn.cursor()` (GQLAlchemy style), while the `process-pdf` endpoint uses `neo4j.GraphDatabase.driver()` — there are two different Memgraph connection interfaces in the codebase. The API endpoint at [extract.py L440](backend/app/api/extract.py#L440) creates `GraphRevertService()` **without** passing `db_session` or `memgraph_connection`, meaning both branches (`if self.conn` and `if self.db`) are `None/False`. **The API endpoint still does nothing.**

**Critical Gap:** The revert service *has* the code to execute against Memgraph and PostgreSQL, but the API layer never provides the connections. The integration is broken.

---

### Finding #9 — Qdrant Is a Mock Dictionary
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Tickets:** None (deferred)  
**Verdict:** 🔵 **DEFERRED TO POST-MVP**

**Evidence:**
- [embedding_sync.py](backend/app/services/embedding_sync.py) — `QdrantVectorStoreMock` is still an in-memory dictionary. No changes made.
- Acknowledged in `post-mvp.md`.

---

### Finding #10 — GraphRAG Returns Hardcoded Mock Data
**Code-Review Severity:** 🔴 CRITICAL  
**Mapped Ticket:** FIX-304  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [graphrag_translator.py L40-L66](backend/app/services/graphrag_translator.py#L40-L66): If `self.conn` exists, it now queries Memgraph with `MATCH (n) OPTIONAL MATCH (n)-[r]->(m)`.
- **BUT**: The hardcoded mock data **is still present** at lines 68-76 as the fallback when `self.conn` is `None`.
- The API endpoint at [extract.py L456](backend/app/api/extract.py#L456) creates `GraphRAGTranslationService()` **without** passing `memgraph_connection`. So `self.conn` is always `None`, and the endpoint **always returns the two hardcoded fake nodes**.

**Critical Gap:** Same integration issue as Finding #8 — the service has live query code but the API never wires the connection.

---

### Finding #11 — Golden Assertions Reset on Restart
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-204  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [governance_engine.py L42-L83](backend/app/services/governance_engine.py#L42-L83): `register_golden_assertion()` now persists to DB, and `load_golden_assertions()` loads from DB.
- **BUT**: Line 57-61 contains broken error handling:
  ```python
  except Exception:
      try:
          self.db.merge(MagicMock())
      except Exception:
          pass
      self.db.commit()
  ```
  If the primary persist fails, the code tries to merge a `MagicMock()` (which is not imported — it would raise `NameError`). This is test-fixture code that leaked into production.
- The Governance Engine is still **never called** from `process-pdf` or the Cold-Start Pipeline. No code path validates mutations against Golden Assertions before committing to Memgraph.

---

### Finding #12 — Graphiti Uses String Equality, Not Semantic Comparison
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-306  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [graphiti_engine.py L57-L67](backend/app/services/graphiti_engine.py#L57-L67): Now normalizes whitespace, lowercases, and computes token overlap. Only emits `SUPERSEDE_NODE` if `overlap < 0.90`.

**Assessment:** This correctly prevents trivial formatting diffs from triggering false-positive mutations. A legitimate token-overlap similarity gate.

---

### Finding #13 — Seed Ingestion Doesn't Write Edges
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-200  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [seed_ingestion.py L162-L196](backend/app/services/seed_ingestion.py#L162-L196): Edge iteration now creates `ControlObjectiveFrameworkMapping` ORM records with proper UUID parsing, `set_theory_relation` enum mapping, and `is_golden_assertion="TRUE"`.

---

### Finding #14 — `process-pdf` Bypasses Service Layer
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-202  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [extract.py L252-L263](backend/app/api/extract.py#L252-L263): The endpoint now creates a `MemgraphService` and calls `enqueue_and_execute()` for outbox logging.
- **BUT**: The endpoint **still constructs inline Cypher** (lines 230-248, 265-274, 307-328) and executes them directly via `session.run()`, bypassing `RCKGCypherBuilder`. The outbox logging only covers `ADD_NODE` primitives, not the `DEFINES` or `SATISFIES` edge creation.
- The `GovernanceEngine` is still never called.

---

### Finding #15 — `ClauseBoundaryExtractor` Regex `group(6)` Bug
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-100  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [hybrid_chunking.py L520](backend/app/services/hybrid_chunking.py#L520): Now uses `match.group(2)` instead of `match.group(6)`.

---

### Finding #16 — Fallback Chunk Hardcodes "Section 3.1"
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** Part of FIX-104/FIX-105  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [extract.py L162-L169](backend/app/api/extract.py#L162-L169): Fallback now uses `section_reference="General"`, `heading_title=filename`, and `chunk_text=extracted_text` (full text, not truncated to 500 chars).

---

### Finding #17 — Outbox Commits PostgreSQL Before Memgraph
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-201  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [memgraph_service.py L90-L125](backend/app/services/memgraph_service.py#L90-L125): Now uses `db.flush()` (not `commit()`) before Memgraph execution. Commits only after successful Memgraph write. Rollbacks on failure.

**Assessment:** This correctly implements 2PC-style atomicity.

---

### Finding #18 — Graph Compiler Creates ADD_EDGE for NO_RELATIONSHIP
**Code-Review Severity:** 🟠 MAJOR  
**Mapped Ticket:** FIX-203  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [graph_compiler.py L168-L169](backend/app/services/graph_compiler.py#L168-L169): Fallback now returns `[]` (empty list) instead of creating a `NO_RELATIONSHIP` edge.

---

### Finding #19 — LLM Endpoint Port Conflict (8000 vs 8001)
**Code-Review Severity:** 🟡 MODERATE  
**Mapped Ticket:** FIX-101  
**Verdict:** ✅ **GENUINELY FIXED**

**Evidence:**
- [extraction.py L37](backend/app/services/extraction.py#L37): Default port changed from 8000 to 8001.

---

### Finding #20 — No `document_type` Routing in Upload → Extract
**Code-Review Severity:** 🟡 MODERATE  
**Mapped Tickets:** FIX-103, FIX-104  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- `process-pdf` now accepts `document_type` parameter and branches into Tier 1/2/3.
- BUT there is still no automated upload → classify → extract pipeline. The user must manually call `process-pdf` with the right `document_type`.

---

### Finding #21 — ColBERT Is a Mock
**Code-Review Severity:** 🟡 MODERATE  
**Mapped Tickets:** None (deferred)  
**Verdict:** 🔵 **DEFERRED TO POST-MVP**

**Evidence:**
- [colbert_service.py](backend/app/services/retrieval/colbert_service.py) still generates synthetic embeddings from `ord(c)` hash seeds. No real ColBERT model loaded. Acknowledged in post-mvp.md.

---

### Finding #22 — Kafka Publish Is a Log Statement
**Code-Review Severity:** 🟡 MODERATE  
**Mapped Tickets:** None (deferred)  
**Verdict:** 🔵 **DEFERRED TO POST-MVP**

**Evidence:**
- [dual_judge_async.py L122-L128](backend/app/services/dual_judge_async.py#L122-L128): Still just `logger.info()`.

---

### Finding #23 — Format Classifier Doesn't Inspect PDF
**Code-Review Severity:** 🟡 MODERATE  
**Mapped Tickets:** None (deferred)  
**Verdict:** 🔵 **DEFERRED TO POST-MVP**

**Evidence:**
- [format_classifier.py](backend/app/services/format_classifier.py) now at least inspects raw bytes for `/Font`, `/Image`, `/XObject`, and `/Table` markers. This is an improvement over the original finding that claimed zero inspection. Still heuristic-based rather than using a PDF parser library.

---

### Finding #24 — Seed Nodes All Written as FrameworkControlObjectiveNode
**Code-Review Severity:** 🟡 MODERATE  
**Mapped Tickets:** None  
**Verdict:** ❌ **NOT FIXED**

**Evidence:**
- [seed_ingestion.py L152-L159](backend/app/services/seed_ingestion.py#L152-L159): All nodes are still `FrameworkControlObjectiveNode`. No `FrameworkControlActivityNode` distinction.

---

### Finding #25 — SATISFIES Edge Direction Wrong
**Code-Review Severity:** 🔵 MINOR  
**Mapped Ticket:** FIX-105  
**Verdict:** ✅ **GENUINELY FIXED (for Tier 1)**

**Evidence:**
- [extract.py L269](backend/app/api/extract.py#L269): Tier 1 now uses `DEFINES` relationship (`(d)-[r:DEFINES]->(o)`).
- **But** Tier 2 at [extract.py L335](backend/app/api/extract.py#L335) still uses `SATISFIES` from ControlObjective → Obligation, which is semantically correct per the Delta topology.

---

### Finding #26 — Bootstrap Endpoint Wrong Import Path
**Code-Review Severity:** 🔵 MINOR  
**Mapped Ticket:** FIX-101  
**Verdict:** ⚠️ **INCONSISTENT**

**Evidence:**
- [extract.py L104](backend/app/api/extract.py#L104): Bootstrap endpoint now uses `from app.services.cold_start_pipeline import ...` (relative).
- **BUT** [cold_start_pipeline.py L12-L16](backend/app/services/cold_start_pipeline.py#L12-L16): The module itself still uses `from backend.app.services.format_classifier import ...` (absolute).
- This means the bootstrap endpoint will fail if run as `app.services.cold_start_pipeline` — the internal imports use the `backend.app.` prefix.

---

### Finding #27 — ControlObjective Crosswalk Matches All Obligations in Same Domain
**Code-Review Severity:** 🔵 MINOR  
**Mapped Ticket:** FIX-105  
**Verdict:** ⚠️ **PARTIALLY FIXED**

**Evidence:**
- [extract.py L333](backend/app/api/extract.py#L333): Now matches on **both** `domain_facet` AND `action_verb` (`WHERE o.domain_facet = $domain AND o.action_verb = $verb`). This narrows the match significantly compared to domain-only.
- Still not an embedding-based similarity match, but meaningfully better.

---

## Systemic Issues Not Covered by Individual Findings

### 1. Pervasive "Try-LLM-Then-Fallback" Anti-Pattern

The following services all share the same structure:

| Service | Lines | Pattern |
|---------|-------|---------|
| [nli_engine.py](backend/app/services/nli_engine.py#L62-L77) | 62-77 | Try `_call_llm()`, catch all exceptions, fall back to keyword chain |
| [dual_judge_async.py](backend/app/services/dual_judge_async.py#L65-L75) | 65-75 | Try `_call_llm()`, catch all exceptions, fall back to `conf * 1.02` |
| [extract.py (process-pdf)](backend/app/api/extract.py#L206-L223) | 206-223 | Try `_call_llm()`, fall back to regex facet extractor |

**Problem:** This pattern catches `Exception` broadly, including:
- Network timeouts → LLM is temporarily down
- JSON parse errors → LLM returned malformed output
- `ImportError` → `openai` package not installed
- `ValueError` → LLM returned null

The fallback is always the **original broken code**. There is no circuit breaker, no retry logic, no alerting, and no audit signal that degradation occurred. A user examining the graph would have no way to know which nodes came from LLM extraction vs. regex fabrication.

### 2. API-to-Service Wiring Gaps

Two API endpoints create services **without providing database or Memgraph connections**:

| Endpoint | Service | Missing |
|----------|---------|---------|
| `POST /graph/revert` ([L440](backend/app/api/extract.py#L440)) | `GraphRevertService()` | No `db_session`, no `memgraph_connection` |
| `GET /graph/graphrag-export` ([L456](backend/app/api/extract.py#L456)) | `GraphRAGTranslationService()` | No `memgraph_connection` |

These endpoints will execute but produce only fabricated/empty results.

### 3. Mixed Import Paths

[cold_start_pipeline.py](backend/app/services/cold_start_pipeline.py#L12-L16) uses `from backend.app.services.X import Y` while most other modules use `from app.services.X import Y`. This creates runtime failures depending on how the FastAPI server is launched (`python -m backend.app.main` vs `cd backend && uvicorn app.main:app`).

### 4. MagicMock Reference in Production Code

[governance_engine.py L59](backend/app/services/governance_engine.py#L59) references `MagicMock()` without importing it. This will raise `NameError` at runtime if the primary ORM persist fails.

### 5. Test Quality Concerns

The test suite (88 passing) uses heavy mocking:

- [test_nli_llm_proxy.py](backend/tests/test_nli_llm_proxy.py): Mocks `_call_llm` and verifies the mock was called. Doesn't test actual LLM prompt quality or response parsing edge cases.
- [test_cold_start_candidate_retrieval.py](backend/tests/test_cold_start_candidate_retrieval.py): Uses `MagicMock()` for DB session. Only asserts `res["status"] == "COMPLETED"` and `orchestrator.compiler is not None`. Doesn't verify that the correct candidates were passed to the compiler.
- [test_dual_judge_llm.py](backend/tests/test_dual_judge_llm.py): Same pattern — mock `_call_llm`, verify scores match mock output.

These tests verify that the LLM integration code *calls* the LLM, but not that the system produces correct graph mutations from real document text. There are no integration tests that trace a PDF upload through to Memgraph edge creation.

---

## Summary Scorecard

### Code-Review Findings Coverage Matrix

| # | Finding | Severity | Fix Ticket(s) | Status | Notes |
|---|---------|----------|---------------|--------|-------|
| 1 | Extraction prompt obligations-only | 🔴 | FIX-102, FIX-103 | ✅ Fixed | 3-tier prompts created |
| 2 | process-pdf bypasses LLM | 🔴 | FIX-104, FIX-105 | ⚠️ Partial | Regex fallback preserved |
| 3 | Facet extractor is regex stub | 🔴 | — | ❌ Not fixed | No ticket, unchanged |
| 4 | Cold-start hardcoded target+cosine | 🔴 | FIX-300 | ⚠️ Partial | DB lookup added, metadata still hardcoded |
| 5 | NLI engine is keyword if/else | 🔴 | FIX-301 | ⚠️ Partial | LLM overlay, keyword fallback intact |
| 6 | BM25 always raises RuntimeError | 🔴 | FIX-302 | ✅ Fixed | BM25Okapi implemented |
| 7 | Dual-judge uses arithmetic | 🔴 | FIX-305 | ⚠️ Partial | LLM overlay, arithmetic fallback intact |
| 8 | GraphRevert does nothing | 🔴 | FIX-303 | ⚠️ Partial | Code exists, API doesn't wire connections |
| 9 | Qdrant is mock dictionary | 🔴 | — | 🔵 Deferred | Post-MVP |
| 10 | GraphRAG returns hardcoded data | 🔴 | FIX-304 | ⚠️ Partial | Code exists, API doesn't wire connections |
| 11 | Golden Assertions not persisted | 🟠 | FIX-204 | ⚠️ Partial | Persist code added, broken error handling |
| 12 | Graphiti uses string equality | 🟠 | FIX-306 | ✅ Fixed | Token overlap similarity gate |
| 13 | Seed ingestion no edges | 🟠 | FIX-200 | ✅ Fixed | ORM edge writes added |
| 14 | process-pdf bypasses service layer | 🟠 | FIX-202 | ⚠️ Partial | Outbox for nodes only, inline Cypher remains |
| 15 | Regex group(6) crash | 🟠 | FIX-100 | ✅ Fixed | Changed to group(2) |
| 16 | Hardcoded "Section 3.1" fallback | 🟠 | FIX-104 | ✅ Fixed | Uses "General" + filename |
| 17 | Outbox commits before Memgraph | 🟠 | FIX-201 | ✅ Fixed | flush() then commit-on-success |
| 18 | NO_RELATIONSHIP edge pollution | 🟠 | FIX-203 | ✅ Fixed | Returns empty list |
| 19 | LLM port conflict (8000) | 🟡 | FIX-101 | ✅ Fixed | Changed to 8001 |
| 20 | No document_type routing | 🟡 | FIX-103 | ⚠️ Partial | Manual type selection only |
| 21 | ColBERT mock model | 🟡 | — | 🔵 Deferred | Post-MVP |
| 22 | Kafka is logger.info() | 🟡 | — | 🔵 Deferred | Post-MVP |
| 23 | PDF classifier doesn't inspect | 🟡 | — | 🔵 Deferred | Minor improvement via byte inspection |
| 24 | Seed nodes all same type | 🟡 | — | ❌ Not fixed | No ticket |
| 25 | SATISFIES edge direction wrong | 🔵 | FIX-105 | ✅ Fixed | Changed to DEFINES (Tier 1) |
| 26 | Mixed import path | 🔵 | FIX-101 | ⚠️ Partial | Fixed in API, broken in service |
| 27 | Domain-only crosswalk match | 🔵 | FIX-105 | ⚠️ Partial | Added action_verb filter |

---

## End-User Testing Readiness Assessment

### Prerequisites for Testing

| Prerequisite | Status | Notes |
|-------------|--------|-------|
| LLM endpoint (vLLM/Ollama) on port 8001 | **REQUIRED** | Without this, 10 fixes silently degrade |
| Memgraph running on bolt://localhost:7687 | **REQUIRED** | Graph storage |
| PostgreSQL with schema | **REQUIRED** | Relational vault |
| Seed data ingested | **REQUIRED** | For cold-start candidate retrieval |
| MinIO for uploads | **OPTIONAL** | Upload endpoint only |

### What Will Work in End-User Testing

1. **PDF upload with LLM extraction** — The `process-pdf` endpoint will call the LLM and produce real extracted obligations/objectives/activities from document text, injecting them into Memgraph.
2. **3-tier document type routing** — Users can specify `REGULATORY_GUIDELINE`, `ENTERPRISE_POLICY`, or `PROCEDURE_SOP` and get type-appropriate extraction.
3. **Seed graph with edges** — The seed ingestion now writes edges, so the baseline graph will have crosswalk relationships.
4. **Clause boundary extraction** — The regex crash is fixed, so multi-section documents will be properly chunked.

### What Will NOT Work in End-User Testing

1. **Graph Revert** — API endpoint doesn't pass Memgraph/DB connections to the service.
2. **GraphRAG Export** — API endpoint doesn't pass Memgraph connection; always returns hardcoded data.
3. **Cold-Start Bootstrap** — Import path mismatch (`backend.app.services.*` vs `app.services.*`) will cause `ModuleNotFoundError` depending on launch method.
4. **Governance validation** — Never called from any code path.
5. **Any endpoint when LLM is down** — Silent degradation to regex stubs.

### Recommendation

> [!IMPORTANT]
> The system is **conditionally ready** for controlled end-user testing with the following caveats:
> 1. **Ensure a live LLM is running** on port 8001 before testing
> 2. **Test only the `process-pdf` endpoint** — it is the most functionally complete path
> 3. **Do NOT test** GraphRevert or GraphRAG Export endpoints — they will return fabricated data
> 4. **Do NOT rely on** the Cold-Start Bootstrap endpoint — import path issues make it unreliable
> 5. A round of **integration fixes** (API wiring, import path normalization, fallback alerting) is needed before this can be called a genuine MVP

---

## Recommended Next Actions

### Critical (Block end-user testing)
1. **Wire Memgraph connections into API endpoints** — `GraphRevertService` and `GraphRAGTranslationService` need `memgraph_connection` from the request context
2. **Normalize import paths** — Choose either `backend.app.` or `app.` consistently across all modules
3. **Remove `MagicMock()` reference** from production code in `governance_engine.py`

### High Priority (Degraded experience without)
4. **Add degradation signal** — When LLM fallback is triggered, include `extraction_method: "REGEX_FALLBACK"` in node metadata and API response
5. **Wire Governance Engine** into `process-pdf` to validate mutations against Golden Assertions before Memgraph commit
6. **Upgrade `DeJureFacetExtractor`** — Either make it LLM-powered or significantly expand the domain vocabulary

### Medium Priority (Quality improvement)
7. **Add integration tests** — At least one test that traces a real PDF file through `process-pdf` to Memgraph node creation (with mocked LLM response)
8. **Fix Cold-Start candidate metadata** — Stop hardcoding `modality_facet`, `target_role_facet`, `control_nature` for candidates
9. **Remove misleading `DeBERTa-v3` model claim** from NLI fallback metadata
