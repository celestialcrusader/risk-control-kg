# Deep-Dive Code Review: RCKG Codebase vs. Requirements Alignment

**Document Version:** 1.0  
**Status:** Engineering Review — Action Required  
**Date:** July 31, 2026  
**Reviewer:** AI Code Review Agent  
**Scope:** Full `backend/app/` codebase audited against:
- BRD v3.0 — [01-business-requirement-doc.md](docs/02-pickup/01-business-requirement-doc.md)
- PRD v3.0 — [02-product-requirement-doc.md](docs/02-pickup/02-product-requirement-doc.md)
- TRD v7.0 — [03-technical-requirement-doc.md](docs/02-pickup/03-technical-requirement-doc.md)
- Delta v3.2 — [06-delta.md](docs/02-pickup/06-delta.md)
- MVP Sprint v2.0 — [mvp-sprint.md](docs/03-mvp/mvp-sprint.md)

---

## Executive Summary

The codebase has correct *structural scaffolding* — file names, class names, Pydantic models, and API endpoints all reference the right concepts from the specification documents. However, the **implementations behind those scaffolds are overwhelmingly hollow stubs, hardcoded mock values, and illogical processing shortcuts** that make the system non-functional for real-world end-user testing.

Of the ~26 service modules audited, **zero** contain production-grade logic. The system will appear to "work" on trivial test fixtures but fails catastrophically on real regulatory documents (e.g., MAS TRM Guidelines PDF).

> [!CAUTION]
> **Critical Finding**: The platform currently has **no real AI/ML inference anywhere in the pipeline**. Every component that claims to use DeBERTa, ColBERT, BM25, or LLM classification is either a hardcoded mock, a regex stub, or raises `RuntimeError` on invocation. The only real LLM call exists in `extraction.py` but it **only extracts Obligations** — not ControlObjectives or ControlActivities as specified by the Delta document.

---

## Severity Classification

| Severity | Description | Count |
|----------|-------------|-------|
| 🔴 **CRITICAL** | Core pipeline broken / produces wrong output / security risk | 12 |
| 🟠 **MAJOR** | Missing functionality that blocks end-user testing | 9 |
| 🟡 **MODERATE** | Partial implementation that degrades quality | 6 |
| 🔵 **MINOR** | Cosmetic or low-impact deviations | 3 |

---

## 1. Extraction Prompt Only Handles Obligations, Not ControlObjectives or ControlActivities

> **Severity:** 🔴 CRITICAL  
> **Files:** [extraction.md](backend/app/prompts/extraction.md), [extraction.py](backend/app/services/extraction.py)  
> **Requirement:** Delta §2.1 Ingestion Taxonomy, PRD §3.5 FR-5.1

### Problem

The extraction prompt template instructs the LLM to extract **only `obligations`** — atomic regulatory mandates from statutory documents. There is **no prompt for extracting `ControlObjective` from enterprise policy documents** or **`ControlActivity` from SOP/procedure documents**.

The Delta document (§2.1) explicitly defines a **3-tier ingestion taxonomy**:

| Document Category | Target Node Type | Node Label |
|---|---|---|
| Regulatory Mandates | Obligation | `:Obligation` |
| Internal Corporate Policies | Control Objective | `:ControlObjective` |
| Process & Operational Docs | Control Activity | `:ControlActivity` |

Yet the extraction pipeline hardcodes `obligations` extraction regardless of document type. Even though `obligation.py` defines `ControlObjective` and `ControlActivity` Pydantic schemas, and `ExtractedObligationsResponse` has `control_objectives` and `control_activities` fields, the prompt never asks the LLM to produce them.

### Impact

When a user uploads a **corporate policy document** (e.g., "Information Security Policy") and selects `ENTERPRISE_POLICY`, the system falls through to the `process-pdf` endpoint which uses the **regex-based facet extractor** instead of the LLM. The LLM-powered extraction path (`POST /api/v1/extract`) always produces Obligation nodes regardless of document type.

### Required Fix

1. Create `prompts/extraction_control_objective.md` — a prompt template for policy ControlObjective extraction.
2. Create `prompts/extraction_control_activity.md` — a prompt template for SOP ControlActivity extraction.
3. Modify `extraction.py` to accept a `document_type` parameter and dispatch to the appropriate prompt template.
4. Parse the LLM response's `control_objectives` and `control_activities` arrays.

---

## 2. `process-pdf` Endpoint Bypasses LLM Entirely — Uses Only Regex Facet Extraction

> **Severity:** 🔴 CRITICAL  
> **File:** [extract.py](backend/app/api/extract.py#L130-L347)  
> **Requirement:** Delta §2.2 Upstream Format Classifier, BRD BO-05

### Problem

The `POST /api/v1/extract/process-pdf` endpoint (lines 130–347) performs the full end-to-end pipeline (PDF parse → chunk → extract → inject into Memgraph), but it **never calls the LLM**. Instead, it uses the [`DeJureFacetExtractor`](backend/app/services/facet_extractor.py) which is a **pure regex pattern matcher** with ~10 hardcoded verb patterns and ~10 noun patterns.

The resulting "obligation prose" is a **template string**, not extracted from the actual document text:

```python
# Line 209 — This is NOT LLM extraction, it's string interpolation
standardized_prose = f"The {facets['target_role_facet']} must {facets['action_verb']} {facets['subject_noun']} under {chunk.section_reference}."
```

This produces generic garbage like:
> "The COMPLIANCE_OFFICER must manage system access under Section 3.1."

instead of the actual regulatory obligation from the document.

### Impact

Every node injected into Memgraph by this endpoint contains **fabricated prose** that does not match the source document. This fundamentally violates BRD BO-05 (Dual-Write Graph & Relational Vault Architecture) and the entire "Provable Governance" mission — the system manufactures compliance statements rather than extracting them.

### Required Fix

1. Route the extracted text chunks through the LLM extraction pipeline (`_extract_obligations_with_storage()`) instead of the regex facet extractor.
2. Use the LLM-extracted prose, action_verb, and subject_noun in the Memgraph MERGE statements.
3. Store the original `chunk.chunk_text` as `clause_citation` for audit traceability.

---

## 3. `DeJureFacetExtractor` Is a Trivial Regex Stub, Not a Real 6-Facet Engine

> **Severity:** 🔴 CRITICAL  
> **File:** [facet_extractor.py](backend/app/services/facet_extractor.py)  
> **Requirement:** Delta §2, Sprint 2 RCKG-203b, MVP mvp-sprint.md RCKG-203b

### Problem

The `DeJureFacetExtractor` claims to extract "6 orthogonal facets from legal and policy text chunks" but is implemented as:

- **`action_verb`**: Regex matching against 10 hardcoded verbs (`limit|restrict|encrypt|monitor|audit|review|authorize|authenticate|retain|delete`). **Falls back to `"manage"`** for anything else.
- **`subject_noun`**: Regex matching against 10 hardcoded nouns (`access|credentials|pii|data|backups|logs|networks|systems|privileges`). **Falls back to `"system access"`** for anything else.
- **`domain_facet`**: Simple keyword check — if "access" in text → `IDENTITY_ACCESS_MANAGEMENT`, if "encrypt" or "data" → `DATA_PROTECTION`, else `GENERAL_COMPLIANCE`.
- **`target_role_facet`**: If "officer" or "administrator" in text → `SYSTEM_ADMINISTRATOR`, else `COMPLIANCE_OFFICER`.
- **`control_nature`**: **Hardcoded to `"PREVENTATIVE"` always** (line 65).

This means:
- Any regulation about "risk assessment", "incident reporting", "business continuity", "vendor management", etc. will default to `action_verb="manage"`, `subject_noun="system access"`.
- The `control_nature` facet is never actually classified — it always returns `PREVENTATIVE`, ignoring `DETECTIVE`, `CORRECTIVE`, and `COMPENSATING` control natures.
- Only 3 domain facets exist vs. the dozens of GRC domains in reality.

### Impact

The facet extractor is the **foundation** for the Graph Compiler's matching logic. Since facets are almost always defaults, the compiler produces incorrect set-theory classifications, and the resulting graph edges are meaningless.

### Required Fix

This should be an LLM-assisted extraction (or at minimum a much richer NLP pipeline using spaCy dependency parsing). The 6-facet model needs to cover the full domain vocabulary of GRC.

---

## 4. `ColdStartPipelineOrchestrator` Uses Hardcoded Target Node and Fake Cosine Similarity

> **Severity:** 🔴 CRITICAL  
> **File:** [cold_start_pipeline.py](backend/app/services/cold_start_pipeline.py#L65-L84)  
> **Requirement:** Delta §7.1 Phase 1 Cold-Start Bootstrap, Sprint 2 RCKG-204

### Problem

The core Cold-Start Pipeline (lines 65–84) has two fatal issues:

**Issue A: Hardcoded target node.** Every chunk in every document is compared against the **same single hardcoded target**:

```python
# Line 72-80 — ALWAYS the same target for every chunk
target_candidate = {
    "node_id": "OBL-NIST-AC-2",
    "action_verb": "limit",
    "subject_noun": "system access",
    "domain_facet": facets["domain_facet"],
    ...
}
```

This means the pipeline does not actually retrieve candidate nodes from the graph or any index. It always pairs every source chunk with `OBL-NIST-AC-2`.

**Issue B: Hardcoded cosine similarity.** Line 83:

```python
cosine_sim = 0.88  # Hardcoded — no embedding or similarity computation
```

There is no bi-encoder, no embedding computation, no vector similarity — the cosine similarity is always `0.88`.

### Impact

The pipeline cannot produce a meaningful knowledge graph. Every document chunk creates an edge to the same target node with the same similarity score. The "4-Stage Funnel" (BM25 → Bi-Encoder → ColBERT → NLI) specified in the Delta does not exist in this code path.

### Required Fix

1. Stage 1: Query BM25/Elasticsearch index for candidate target nodes.
2. Stage 1.5: Compute dense bi-encoder embeddings and filter by cosine similarity.
3. Stage 2: Rerank with ColBERT MaxSim.
4. Stage 2.5: NLI cross-encoder classification.
5. Pass real similarity scores to the Graph Compiler.

---

## 5. `NliSetTheoryEngine` Is a Hardcoded If/Else Chain, Not a Real NLI Model

> **Severity:** 🔴 CRITICAL  
> **File:** [nli_engine.py](backend/app/services/nli_engine.py)  
> **Requirement:** Delta §4 Probabilistic NLI Set-Theory Engine, Sprint 3 RCKG-303

### Problem

The `NliSetTheoryEngine.evaluate_pair()` method (line 54–151) does **not load or call any DeBERTa-v3 model**. It is a chain of `if/elif` keyword checks:

- If text contains "only if" → `CONTINGENT_SATISFIES` with confidence `0.88`
- If text contains "financial" + "firewall" → `NO_RELATIONSHIP` with confidence `0.15`
- If text contains "encrypt" + "pii" → `EQUIVALENT_TO` with confidence `0.95`
- If text contains "8 characters" + "16 characters" → `SUBSET_OF` with confidence `0.89`
- **Else → `EQUIVALENT_TO` with confidence `0.88`** (default fallback)

The `nli_entailment_logits` are hardcoded static dictionaries, not actual model outputs. The metadata claims `model: "DeBERTa-v3-CrossEncoder-Llama3.1-8B-Student"` but no model is loaded.

### Impact

The NLI engine is the **core intelligence** of the RCKG system — it determines the mathematical set-theory relationship between any two compliance statements. With a keyword-based stub, the system will classify most pairs as `EQUIVALENT_TO` (the default), producing a graph with meaningless edges.

### Required Fix

Load and inference a real DeBERTa-v3-large cross-encoder model (or at minimum, call the vLLM endpoint with a structured NLI prompt).

---

## 6. `Bm25SparseSearchService` Always Raises RuntimeError — Never Connects to Elasticsearch

> **Severity:** 🔴 CRITICAL  
> **File:** [bm25_service.py](backend/app/services/retrieval/bm25_service.py#L46-L49)  
> **Requirement:** Delta §6.1, Sprint 3 RCKG-301

### Problem

The `_execute_es_http_query()` method (line 49):

```python
def _execute_es_http_query(self, query_text: str, top_k: int) -> Dict[str, Any]:
    raise RuntimeError("Elasticsearch cluster connection unavailable; triggering fallback.")
```

This method **always** throws an exception. The `search()` method catches this and falls back to a naive in-memory keyword scan. There is no actual Elasticsearch client integration.

### Impact

Stage 1 of the 4-Stage Funnel is non-functional. The in-memory fallback cannot scale to the 50M candidate pairs specified in the Delta §6.3 latency table.

---

## 7. `DualJudgeAsyncService` Uses Arithmetic Instead of 70B Teacher LLM

> **Severity:** 🔴 CRITICAL  
> **File:** [dual_judge_async.py](backend/app/services/dual_judge_async.py#L46-L68)  
> **Requirement:** Delta §5.3, Sprint 3 RCKG-304

### Problem

The `evaluate_pending_audits()` method computes judge scores as simple arithmetic on the input confidence:

```python
logic_score = min(1.0, conf * 1.02)   # Just multiply by 1.02
tech_score = min(1.0, conf * 0.98)    # Just multiply by 0.98
verdict = "APPROVED" if (logic_score >= 0.85 and tech_score >= 0.85) else "REJECTED"
```

No 70B LLM is called. No prompt is sent. No reasoning is performed. The Logic Judge and Technical Judge are supposed to be independent LLM evaluations per Delta §5.3.

### Impact

The Dual-Judge audit layer (Stage 4 of the funnel) provides zero quality assurance on graph mutations. Every pair with `confidence >= 0.84` will be auto-approved.

---

## 8. `GraphRevertService` Does Not Actually Revert Anything in Memgraph or PostgreSQL

> **Severity:** 🔴 CRITICAL  
> **File:** [graph_revert_service.py](backend/app/services/graph_revert_service.py)  
> **Requirement:** Delta §7.5, Sprint 4 RCKG-403

### Problem

The `execute_revert()` method (line 32–65):
1. Computes a release tag string.
2. Logs a message.
3. Returns a `RevertResult` Pydantic model.

It **never connects to Memgraph** to execute a revert Cypher query. It **never updates PostgreSQL** outbox or audit tables. It **never tags the graph version**. It is a pure data-fabrication function.

### Impact

The "First-Class Graph Revert" capability promised in the Delta is non-functional. Auditors cannot revert bad graph mutations.

---

## 9. `EmbeddingSyncController` Uses Mock Qdrant — No Real Vector DB Integration

> **Severity:** 🔴 CRITICAL  
> **File:** [embedding_sync.py](backend/app/services/embedding_sync.py)  
> **Requirement:** Delta §7.6, Sprint 4 RCKG-404

### Problem

The `QdrantVectorStoreMock` (line 21–51) is a Python dictionary (`self.points: Dict[str, Dict[str, Any]] = {}`) pretending to be Qdrant. No actual Qdrant client is imported or used. Bitemporal time-travel queries run against this in-memory dictionary.

### Impact

Vector payload synchronization on `SUPERSEDE_NODE` events does not persist. The AS-OF-DATE time-travel query capability is non-functional in production.

---

## 10. `GraphRAGTranslationService` Returns Hardcoded Mock Data

> **Severity:** 🔴 CRITICAL  
> **File:** [graphrag_translator.py](backend/app/services/graphrag_translator.py#L34-L39)  
> **Requirement:** Delta §7.7, Sprint 4 RCKG-405

### Problem

The `export_subgraph()` method (lines 34–39):

```python
raw_nodes = nodes or [
    {"node_id": "REG-01", "type": "StatutoryRequirement", "title": "GDPR Article 32"},
    {"node_id": "POL-01", "type": "InternalPolicy", "title": "SecOps Data Protection Policy"},
]
raw_edges = edges or [
    {"source_id": "REG-01", "target_id": "POL-01", "relation_type": "EQUIVALENT_TO", "confidence": 0.95},
]
```

When called without explicit parameters (as the API endpoint `GET /api/v1/graph/graphrag-export` does), it returns **two hardcoded fake nodes** instead of querying Memgraph.

### Impact

The downstream GraphRAG Translation Layer interface is non-functional. Executive Q&A over the knowledge graph will return fabricated compliance data.

---

## 11. `GovernanceEngine` Has No Persistence — Golden Assertions Reset on Restart

> **Severity:** 🟠 MAJOR  
> **File:** [governance_engine.py](backend/app/services/governance_engine.py)  
> **Requirement:** Delta §7.4, Sprint 4 RCKG-402

### Problem

Golden Assertions are stored in-memory:

```python
self._golden_assertions: Set[Tuple[str, str, str]] = set()
```

When the FastAPI server restarts, all registered Golden Assertions are lost. There is no persistence to PostgreSQL or Memgraph. The Governance Engine is never called from the Cold-Start Pipeline or the `process-pdf` endpoint.

### Impact

The Golden Assertions Snapshot Testing framework (critical for regression prevention) is non-functional in any persistent deployment.

---

## 12. `GraphitiSemanticChangeDetector` Uses Naive String Equality, Not Semantic Comparison

> **Severity:** 🟠 MAJOR  
> **File:** [graphiti_engine.py](backend/app/services/graphiti_engine.py#L57)  
> **Requirement:** Delta §7.1 Phase 2, Sprint 4 RCKG-401

### Problem

The Phase 2 Steady-State Maintenance Engine detects changes via:

```python
if old_content != new_content:  # Exact string match — not semantic
```

Two semantically identical statements with different wording (e.g., "must encrypt PII data" vs "shall apply encryption to personally identifiable information") will be treated as different, triggering unnecessary `SUPERSEDE_NODE` mutations.

### Impact

The Graphiti engine will produce excessive false-positive diffs, flooding the graph with unnecessary version mutations.

---

## 13. Seed Ingestion Does Not Write Edges to PostgreSQL or Memgraph

> **Severity:** 🟠 MAJOR  
> **File:** [seed_ingestion.py](backend/app/services/seed_ingestion.py#L148-L165)  
> **Requirement:** Delta §5.4, Sprint 1 RCKG-101

### Problem

The `ComplianceSeedIngester.ingest_file()` method (lines 148–165) processes parsed nodes and stores them in PostgreSQL via `db.merge()`. However:

1. **Edges are parsed but never written.** The parser returns `edges` with `source_id`, `target_id`, and `relation`, but `ingest_file()` never creates `ControlObjectiveFrameworkMapping` ORM records for them.
2. **No Memgraph writes.** Seed nodes and edges are never synced to Memgraph. The Delta specifies ~3,100 pre-validated crosswalk edges should be seeded as Golden Assertions.

### Impact

The seed graph bootstrap produces nodes-only, with no edges, rendering the crosswalk topology empty.

---

## 14. `process-pdf` Endpoint Writes Raw Cypher Strings, Not Parameterized Templates via Service Layer

> **Severity:** 🟠 MAJOR  
> **File:** [extract.py](backend/app/api/extract.py#L188-L335)  
> **Requirement:** Delta §7.3, TRD §2

### Problem

The `process-pdf` endpoint directly constructs `neo4j.GraphDatabase.driver()` connections and executes inline Cypher strings. It bypasses:

1. The `MemgraphService` (which provides the transactional outbox pattern).
2. The `RCKGCypherBuilder` (which provides parameterized Cypher templates).
3. The `GovernanceEngine` (which validates mutations against Golden Assertions).
4. The `GraphMutationDiff` model (which enforces Closed-Set Typed Primitives).

The endpoint is essentially a standalone script jammed into an API route, duplicating logic that should flow through the established service layer.

### Impact

- No audit trail in `graph_outbox_log` for nodes created via this endpoint.
- No governance validation on injected edges.
- Dual-write consistency between PostgreSQL and Memgraph is not maintained.

---

## 15. `ClauseBoundaryExtractor` Has a Regex Bug on Group Reference

> **Severity:** 🟠 MAJOR  
> **File:** [hybrid_chunking.py](backend/app/services/hybrid_chunking.py#L520)  
> **Requirement:** Sprint 2 RCKG-203

### Problem

Line 520:
```python
current_heading = match.group(6).strip() if match.group(6) else current_sec_ref
```

The regex `CLAUSE_HEADER_PATTERN` only defines **2 capture groups** (group 1 = section reference, group 2 = heading text). Referencing `match.group(6)` will raise an `IndexError` at runtime on any document that matches a clause header.

This should be `match.group(2)`.

### Impact

The clause boundary extractor will crash on any regulatory document with recognizable section headers (e.g., `Section 3.1 Access Control`), causing the fallback to return the entire document as a single chunk.

---

## 16. `process-pdf` Hardcodes Fallback Chunk Metadata Instead of Using Extracted Content

> **Severity:** 🟠 MAJOR  
> **File:** [extract.py](backend/app/api/extract.py#L172-L181)  
> **Requirement:** Delta §2.2

### Problem

When the chunker returns no results, the fallback creates a **single chunk** with hardcoded metadata:

```python
ClauseChunk(
    section_reference="Section 3.1",           # Hardcoded
    heading_title="Access Control & Security",  # Hardcoded
    chunk_text=extracted_text[:500],            # Only first 500 chars
    word_count=len(extracted_text.split()),
)
```

This means: for any document where clause boundary detection fails, only the first 500 characters are processed, with a fabricated section reference of "Section 3.1".

### Impact

Large PDF documents (100+ pages) lose 99%+ of their content. The fabricated section reference pollutes the graph.

---

## 17. `MemgraphService.enqueue_and_execute()` Commits Outbox Before Memgraph — Violates Atomicity

> **Severity:** 🟠 MAJOR  
> **File:** [memgraph_service.py](backend/app/services/memgraph_service.py#L97-L104)  
> **Requirement:** Delta §7.3, BRD BO-05

### Problem

Lines 97–104:
```python
outbox_entry = GraphOutboxLog(...)
self.db.add(outbox_entry)
self.db.commit()          # PostgreSQL committed
# ... then Memgraph execution ...
```

PostgreSQL is committed **before** Memgraph execution. If Memgraph fails, PostgreSQL has a `PENDING` outbox entry that was already committed, but no Memgraph write occurred. The status is then updated to `FAILED`, but the outbox log is already committed.

Per Delta §7.3, the Transactional Outbox pattern should ensure atomicity: PostgreSQL commit should only succeed **after** Memgraph execution succeeds, or a retry/compensation mechanism must exist.

### Impact

Dual-write consistency can diverge — PostgreSQL records edges that don't exist in Memgraph.

---

## 18. `RuleBasedGraphCompiler` Produces ADD_EDGE for NO_RELATIONSHIP Pairs

> **Severity:** 🟠 MAJOR  
> **File:** [graph_compiler.py](backend/app/services/graph_compiler.py#L168-L179)  
> **Requirement:** Delta §7.3

### Problem

The fallback at lines 168–179 creates an `ADD_EDGE` mutation with `relationship_type="NO_RELATIONSHIP"`:

```python
mutations.append(
    GraphMutationDiff(
        primitive=ClosedSetPrimitive.ADD_EDGE,
        ...
        relationship_type="NO_RELATIONSHIP",
        set_theory_relation="NO_RELATIONSHIP",
    )
)
```

Per the Delta §3.1 canonical topology, `NO_RELATIONSHIP` means disjoint sets (A ∩ B = ∅). Creating an **edge** for a pair that has no relationship is semantically wrong — it should either create a `CREATE_GAP` primitive or simply skip the pair.

### Impact

The graph is polluted with edges that explicitly state "these two things are unrelated" — confusing for downstream queries and GraphRAG reasoning.

---

## 19. Extraction Pipeline Port Conflict — `LLM_ENDPOINT` Defaults to Port 8000

> **Severity:** 🟡 MODERATE  
> **File:** [extraction.py](backend/app/services/extraction.py#L37)  
> **Requirement:** TRD §1

### Problem

```python
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8000/v1")
```

The FastAPI application itself runs on port 8000. The LLM endpoint default also points to port 8000. Unless the `LLM_ENDPOINT` env var is explicitly set, the extraction service will call **itself** instead of the vLLM inference server.

### Impact

LLM extraction calls will either infinite-loop or return HTML (the Swagger docs page) instead of LLM completions.

---

## 20. No `document_type` Routing in the Upload → Extract Pipeline

> **Severity:** 🟡 MODERATE  
> **Files:** [document_upload.py](backend/app/services/document_upload.py), [extract.py](backend/app/api/extract.py)  
> **Requirement:** Delta §2.1 Ingestion Taxonomy

### Problem

The upload endpoint (`POST /api/v1/upload`) stores files in MinIO but does not classify or tag the document type (Regulatory Guideline, Enterprise Policy, or SOP). The `process-pdf` endpoint accepts a `document_type` parameter, but the standard extraction endpoint (`POST /api/v1/extract`) does not. There is **no automated flow** from upload → classification → type-appropriate extraction → graph injection.

### Impact

Users must manually select the document type and manually trigger the right extraction endpoint. The BRD envisions an automated pipeline.

---

## 21. `ColBERTv2Service` Is a Mock With No Model Loading

> **Severity:** 🟡 MODERATE  
> **File:** [colbert_service.py](backend/app/services/retrieval/colbert_service.py)  
> **Requirement:** Delta §6.2, Sprint 3 RCKG-302

### Problem

The ColBERT service (Stage 2 of the 4-Stage Funnel) does not load a ColBERT model. Token embeddings are not pre-computed or cached. MaxSim late-interaction is not implemented. The service returns mock reranking scores.

### Impact

Stage 2 reranking is non-functional.

---

## 22. `PreferenceAccumulatorWorker` Kafka Publish Is a Log Statement

> **Severity:** 🟡 MODERATE  
> **File:** [dual_judge_async.py](backend/app/services/dual_judge_async.py#L103-L108)  
> **Requirement:** Delta §5.3

### Problem

The `_publish_retrain_trigger_event()` method just logs a message:

```python
def _publish_retrain_trigger_event(self) -> None:
    logger.info("Target threshold %d reached. Published KTO/DPO model retrain event...")
```

No Kafka producer is initialized, no event is published, no retrain workflow is triggered.

---

## 23. `format_classifier.py` Does Not Actually Inspect PDF Internal Structure

> **Severity:** 🟡 MODERATE  
> **File:** [format_classifier.py](backend/app/services/format_classifier.py)  
> **Requirement:** Delta §2.2

### Problem

The `classify()` method checks magic bytes for file type but calls `classify_pdf_features()` with **caller-provided feature counts** (text_char_count, image_count, table_cell_count). However, the `classify()` method itself passes **zero** for all these counts when the caller doesn't provide them, and the cold-start pipeline's call at `cold_start_pipeline.py:48` passes raw file bytes but the classifier never opens or parses the PDF to extract actual feature counts.

### Impact

All PDFs are classified as `NATIVE_PDF` by default since the fallback returns NATIVE_PDF with confidence 0.85. The SCANNED_PDF and COMPLEX_MATRIX routing paths are never activated.

---

## 24. Seed Ingestion Writes All Nodes as `FrameworkControlObjectiveNode` — Ignores Activity Distinction

> **Severity:** 🟡 MODERATE  
> **File:** [seed_ingestion.py](backend/app/services/seed_ingestion.py#L152-L159)  
> **Requirement:** Delta §5.4

### Problem

All seed nodes (both NIST SP 800-53 controls and ISO 27001 clauses) are persisted as `FrameworkControlObjectiveNode`. The Delta distinguishes between `FrameworkControlObj` (high-level objectives) and `FrameworkControlAct` (implementation-level activities, e.g., NIST SP 800-53 control enhancements). The parser does not differentiate.

---

## 25. `process-pdf` Constructs SATISFIES Edge From StatutoryRequirement → Obligation (Wrong Direction)

> **Severity:** 🔵 MINOR  
> **File:** [extract.py](backend/app/api/extract.py#L237-L247)  
> **Requirement:** Delta §3.1 Canonical 5-Linkage Topology

### Problem

Line 241:
```cypher
MERGE (d)-[r:SATISFIES]->(o)
```

A `StatutoryRequirement` node SATISFIES an `Obligation` node. But per the Delta topology, `:SATISFIES` is the relationship from `ControlObjective → Obligation` (meaning "this policy objective satisfies this regulatory obligation"). A statutory requirement **defines** obligations, it doesn't "satisfy" them.

The correct relationship should be `DEFINES` or `CONTAINS`, not `SATISFIES`.

---

## 26. Bootstrap Endpoint Import Uses Wrong Module Path

> **Severity:** 🔵 MINOR  
> **File:** [extract.py](backend/app/api/extract.py#L116)  
> **Requirement:** N/A (Code bug)

### Problem

```python
from backend.app.services.cold_start_pipeline import ColdStartPipelineOrchestrator
```

This uses the absolute `backend.app.` prefix, while other imports in the same file use relative `app.` imports. Depending on how the app is started, this may fail with `ModuleNotFoundError`.

---

## 27. `ControlObjective` → `Obligation` Crosswalk Uses Only Domain Facet Match

> **Severity:** 🔵 MINOR  
> **File:** [extract.py](backend/app/api/extract.py#L280-L289)  
> **Requirement:** Delta §3.1

### Problem

The ENTERPRISE_POLICY branch (line 282) creates a SATISFIES edge by matching `domain_facet`:

```cypher
MATCH (o:Obligation) WHERE o.domain_facet = $domain
```

This matches **all** Obligation nodes sharing the same domain facet (e.g., all `DATA_PROTECTION` obligations). Since the facet extractor only has 3 domain categories, a single ControlObjective could create edges to hundreds of unrelated Obligations.

---

## Summary of Findings by Category

### A. Gaps in Functionality (Missing Features)

| # | Gap | Requirement | Priority |
|---|-----|-------------|----------|
| 1 | No prompt or extraction logic for ControlObjective or ControlActivity | Delta §2.1 | 🔴 |
| 2 | No real 4-Stage Retrieval Funnel (BM25, Bi-Encoder, ColBERT, NLI) | Delta §6 | 🔴 |
| 3 | No real NLI cross-encoder model loaded or invoked | Delta §4 | 🔴 |
| 4 | No real 70B Teacher LLM Dual-Judge evaluation | Delta §5.3 | 🔴 |
| 5 | No real Qdrant vector DB integration | Delta §7.6 | 🔴 |
| 6 | No Kafka event publishing for KTO/DPO retraining | Delta §5.3 | 🟡 |
| 7 | No automated upload → classify → extract → inject pipeline | Delta §2.2 | 🟡 |
| 8 | Seed edges not persisted to PostgreSQL or Memgraph | Delta §5.4 | 🟠 |

### B. Illogical Processing (Wrong Behavior)

| # | Issue | Impact | Priority |
|---|-------|--------|----------|
| 1 | `process-pdf` bypasses LLM, fabricates obligation prose from regex | Fake graph data | 🔴 |
| 2 | Cold-start pipeline uses hardcoded target node + hardcoded cosine sim | Meaningless graph | 🔴 |
| 3 | GraphRevert doesn't touch Memgraph or PostgreSQL | No actual revert | 🔴 |
| 4 | GraphRAG export returns hardcoded mock data | Fabricated compliance data | 🔴 |
| 5 | Graph Compiler creates ADD_EDGE for NO_RELATIONSHIP pairs | Graph pollution | 🟠 |
| 6 | SATISFIES edge direction wrong (Statutory → Obligation) | Incorrect topology | 🔵 |
| 7 | ControlObjective crosswalk matches ALL obligations in same domain | Over-linking | 🔵 |

### C. Errors in Processing (Bugs)

| # | Bug | Impact | Priority |
|---|-----|--------|----------|
| 1 | `ClauseBoundaryExtractor` references `match.group(6)` — only 2 groups exist | Runtime crash | 🟠 |
| 2 | LLM_ENDPOINT default port 8000 conflicts with FastAPI server port | Self-call loop | 🟡 |
| 3 | Fallback chunk hardcodes "Section 3.1" and truncates to 500 chars | Data loss | 🟠 |
| 4 | Bootstrap endpoint uses mixed import path (`backend.app` vs `app`) | Import failure | 🔵 |
| 5 | Outbox commits PostgreSQL before Memgraph — violates atomicity | Data divergence | 🟠 |

---

## Recommended Priority Order for Remediation

1. **Fix the regex crash** in `ClauseBoundaryExtractor` (`group(6)` → `group(2)`) — immediate bug fix.
2. **Wire LLM extraction into `process-pdf`** — route chunks through `_extract_obligations_with_storage()` instead of regex facet extractor.
3. **Create document-type-specific prompts** for ControlObjective and ControlActivity extraction.
4. **Replace hardcoded target/cosine in Cold-Start Pipeline** with actual bi-encoder embeddings.
5. **Implement real Elasticsearch BM25 client** or switch to a lightweight in-process BM25 library (e.g., rank_bm25).
6. **Load a real NLI cross-encoder** (DeBERTa-v3-large) or use vLLM with a structured NLI prompt.
7. **Connect GraphRevert to Memgraph** — execute actual Cypher MATCH/DELETE/SET operations.
8. **Connect GraphRAG export to Memgraph** — query real nodes and edges.
9. **Persist Golden Assertions to PostgreSQL** so they survive restarts.
10. **Fix seed ingestion edge writes** — create `ControlObjectiveFrameworkMapping` records.
