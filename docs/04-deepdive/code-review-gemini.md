# Deep-Dive Code Audit & Alignment Report: Pure RCKG Engine

**Document Version:** 2.0 — Fully Exhaustive Architectural & Code Audit  
**Target File:** `docs/04-deepdive/code-review-gemini.md`  
**Status:** Complete Audit — Critical Action Required  
**Date:** July 31, 2026  
**Auditor:** Gemini AI System Architect & Senior QA Lead  

---

## 1. Executive Summary & Project Objectives Alignment

The **Risk and Control Knowledge Graph (RCKG)** engine is specified across `docs/02-pickup/` (BRD v3.0, PRD v3.0, TRD v7.0, Delta v3.2) and `docs/03-mvp/mvp-sprint.md`. 

### Core Project Goals & Ingestion Taxonomy
Per **Delta §2.1** and **PRD §3.5**, the pure RCKG graph engine operates over a 3-tier document taxonomy:
1. **Tier 1 Regulatory Mandates / Statutory Guidelines** (e.g., EU AI Act, MAS TRM Guidelines): Extracted as **`:Obligation`** nodes. Syntax: *"The [Primary Actor] must [Action Verb] [Subject/Target] [Condition]."*
2. **Tier 2 Internal Corporate Policies** (e.g., Information Security Policy, AI Ethics Policy): Extracted as **`:ControlObjective`** nodes. Syntax: *"The organization shall establish [Control Objective] to satisfy [Domain]."*
3. **Tier 3 Process & Operational Procedures / SOPs** (e.g., User Provisioning SOP, Backup Standard): Extracted as **`:ControlActivity`** nodes. Syntax: *"The [Operator/System] must execute [Technical Step] using [Tool/Setting]."*

These nodes are linked through 5 canonical set-theory relationships (`EQUIVALENT_TO`, `SUPERSET_OF`, `SUBSET_OF`, `CONTINGENT_SATISFIES`, `INTERSECTS_WITH`) and managed via a 4-Stage Multistage Retrieval Funnel (BM25 $\rightarrow$ Bi-Encoder $\rightarrow$ ColBERTv2 $\rightarrow$ NLI Cross-Encoder), supported by a Bitemporal Graph Revert service and Dual-Tier Governance.

### Audit Summary
A rigorous line-by-line audit of `backend/app/` reveals that while the **Pydantic schemas and ORM models exist**, the **underlying service and API logic contains 27 distinct gaps, illogical processing choices, and implementation errors**.

> [!CAUTION]
> **Core Finding**: When end users test the platform with enterprise policies or SOPs, extraction fails to extract `ControlObjective` or `ControlActivity` nodes. The standard LLM extraction pipeline is hardcoded to extract *only* `Obligation` objects using a static regulatory prompt. The fast `process-pdf` endpoint bypasses the LLM entirely, generating fake/fabricated text via a regex pattern matching stub.

---

## 2. Exhaustive 27-Point Audit Breakdown

---

### Category 1: Gaps in Functionality (10 Items)

#### 1. Single-Prompt Extraction Lock (No `ControlObjective` or `ControlActivity` Extraction)
- **Severity:** 🔴 CRITICAL  
- **Files:** [`backend/app/prompts/extraction.md`](backend/app/prompts/extraction.md), [`backend/app/services/extraction.py`](backend/app/services/extraction.py)  
- **Requirement:** Delta §2.1, PRD §3.5 FR-5.1, `mvp-sprint.md` RCKG-203  
- **Details:** The prompt template in `prompts/extraction.md` instructs the LLM: *"Your task is to parse the provided regulatory text, identify all atomic obligations... Output JSON with an 'obligations' array."* There are no prompt templates for Policy Control Objectives or SOP Control Activities. 
- **Impact:** Processing an enterprise policy document or SOP through `POST /api/v1/extract` extracts `Obligation` nodes instead of `ControlObjective` or `ControlActivity` nodes.

#### 2. Missing 4-Stage Multistage Candidate Retrieval Funnel
- **Severity:** 🔴 CRITICAL  
- **Files:** [`backend/app/services/retrieval/bm25_service.py`](backend/app/services/retrieval/bm25_service.py), [`backend/app/services/cold_start_pipeline.py`](backend/app/services/cold_start_pipeline.py)  
- **Requirement:** Delta §6, TRD §3.2, `mvp-sprint.md` RCKG-301  
- **Details:** `Bm25SparseSearchService._execute_es_http_query()` raises `RuntimeError` by default and falls back to an in-memory dictionary. `ColdStartPipelineOrchestrator` skips retrieval entirely and compares every clause to a single hardcoded target node (`OBL-NIST-AC-2`).  
- **Impact:** Graph bootstrapping cannot perform multi-stage candidate filtering across 50,000,000 candidate pairs as designed.

#### 3. Missing DeBERTa-v3 NLI Model Execution
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/services/nli_engine.py`](backend/app/services/nli_engine.py)  
- **Requirement:** Delta §4, `mvp-sprint.md` RCKG-303  
- **Details:** `NliSetTheoryEngine.evaluate_pair()` uses a hardcoded `if/elif` keyword check (e.g. checking if "only if" or "financial" are present in premise/hypothesis). If no keywords match, it defaults to `EQUIVALENT_TO` with confidence `0.88`. No PyTorch or Transformer model is loaded.  
- **Impact:** The engine cannot calculate true probabilistic NLI entailment logits.

#### 4. Async 70B Dual-Judge Service Is Arithmetic Mock
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/services/dual_judge_async.py`](backend/app/services/dual_judge_async.py)  
- **Requirement:** Delta §5.3, `mvp-sprint.md` RCKG-304  
- **Details:** `evaluate_pending_audits()` calculates `logic_score = min(1.0, conf * 1.02)` and `tech_score = min(1.0, conf * 0.98)` without invoking a 70B Teacher LLM.  
- **Impact:** No independent 70B verification or KTO/DPO training pair accumulation occurs.

#### 5. Mock Qdrant In-Memory Vector Store
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/services/embedding_sync.py`](backend/app/services/embedding_sync.py)  
- **Requirement:** Delta §7.6, `mvp-sprint.md` RCKG-404  
- **Details:** `EmbeddingSyncController` operates against `QdrantVectorStoreMock`, an in-memory Python dictionary (`self.points`). No actual Qdrant client connection is established.  
- **Impact:** Bitemporal `valid_to` vector payload updates disappear when the service process terminates.

#### 6. `GovernanceEngine` Has No Persistence (Golden Assertions Reset on Restart)
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/services/governance_engine.py`](backend/app/services/governance_engine.py)  
- **Requirement:** Delta §7.4, `mvp-sprint.md` RCKG-402  
- **Details:** Golden Assertions are stored in an in-memory Python set (`self._golden_assertions: Set[Tuple[str, str, str]] = set()`).  
- **Impact:** All pinned regression test assertions disappear when the FastAPI server restarts.

#### 7. `ColBERTv2Service` Is a Mock With No Model Loading
- **Severity:** 🟡 MODERATE  
- **File:** [`backend/app/services/retrieval/colbert_service.py`](backend/app/services/retrieval/colbert_service.py)  
- **Requirement:** Delta §6.2, `mvp-sprint.md` RCKG-302  
- **Details:** The service does not load a ColBERT model, compute token embeddings, or perform MaxSim reranking. It returns static mock scores.  
- **Impact:** Stage 2 reranking in the 4-stage funnel is non-functional.

#### 8. `PreferenceAccumulatorWorker` Kafka Publish Is a Log Statement
- **Severity:** 🟡 MODERATE  
- **File:** [`backend/app/services/dual_judge_async.py`](backend/app/services/dual_judge_async.py#L103-L108)  
- **Requirement:** Delta §5.3  
- **Details:** `_publish_retrain_trigger_event()` executes a `logger.info()` statement instead of connecting to a Kafka producer.  
- **Impact:** No automated KTO/DPO student LLM retrain pipeline is triggered.

#### 9. No `document_type` Routing in Upload $\rightarrow$ Extract Pipeline
- **Severity:** 🟡 MODERATE  
- **Files:** [`backend/app/services/document_upload.py`](backend/app/services/document_upload.py), [`backend/app/api/extract.py`](backend/app/api/extract.py)  
- **Requirement:** Delta §2.1, §2.2  
- **Details:** Document upload saves files into MinIO without classifying or tagging document type. The main extraction endpoint (`POST /api/v1/extract`) lacks a document type parameter.  
- **Impact:** There is no automated end-to-end flow from upload to type-appropriate extraction.

#### 10. Seed Ingestion Does Not Write Edges to PostgreSQL or Memgraph
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/services/seed_ingestion.py`](backend/app/services/seed_ingestion.py#L140-L165)  
- **Requirement:** Delta §5.4, `mvp-sprint.md` RCKG-101  
- **Details:** `NistOlirXmlParser.parse()` extracts both nodes (~1,700) and edges (~3,100). However, `ComplianceSeedIngester.ingest_file()` only loops over `parsed_data["nodes"]` and completely ignores `parsed_data["edges"]`.  
- **Impact:** The ~3,100 seed crosswalk edges are never persisted to PostgreSQL or Memgraph.

---

### Category 2: Illogical Processing (9 Items)

#### 11. `process-pdf` Endpoint Generates Synthetic/Fabricated Text
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L130-L347)  
- **Requirement:** BRD BO-05, TRD §3.5  
- **Details:** Text is extracted via `pypdf`, but rather than passing chunks to the LLM extraction pipeline, it passes them to `DeJureFacetExtractor` (regex) and generates prose via Python template string interpolation:
  ```python
  standardized_prose = f"The {facets['target_role_facet']} must {facets['action_verb']} {facets['subject_noun']} under {chunk.section_reference}."
  ```
  This creates generic synthetic statements like *"The COMPLIANCE_OFFICER must manage system access under Section 3.1"* for all chunks, ignoring the actual text inside the PDF.  
- **Impact:** Graph nodes contain synthetic boilerplate rather than actual document requirements.

#### 12. `DeJureFacetExtractor` Is a Trivial Regex Stub
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/services/facet_extractor.py`](backend/app/services/facet_extractor.py)  
- **Requirement:** Delta §2, `mvp-sprint.md` RCKG-203b  
- **Details:** The extractor uses a ~10-word regex list for verbs and nouns, fallback defaults for missing matches (`manage`, `system access`), 3 hardcoded domains, and hardcodes `control_nature = "PREVENTATIVE"` for all inputs.  
- **Impact:** Facet classification produces default values for almost all real enterprise text.

#### 13. Hardcoded Cold-Start Target Node and Similarity Score
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/services/cold_start_pipeline.py`](backend/app/services/cold_start_pipeline.py#L71-L84)  
- **Requirement:** Delta §7.1, `mvp-sprint.md` RCKG-204  
- **Details:** Every extracted text chunk is paired against `node_id: "OBL-NIST-AC-2"` with a hardcoded `cosine_sim = 0.88`.  
- **Impact:** All uploaded documents link exclusively to a single dummy NIST node.

#### 14. `GraphRevertService` Fabricates Release Tag Without Mutating Databases
- **Severity:** 🔴 CRITICAL  
- **File:** [`backend/app/services/graph_revert_service.py`](backend/app/services/graph_revert_service.py)  
- **Requirement:** Delta §7.5, `mvp-sprint.md` RCKG-403  
- **Details:** `execute_revert()` constructs a string like `v1.2.0 [REVERT diff-8921]` and returns a Pydantic object without executing Cypher queries in Memgraph or updating PostgreSQL.  
- **Impact:** Graph reverts report success in the API response while leaving the graph completely unchanged.

#### 15. GraphRAG Export Endpoint Returns Hardcoded Fallback JSON
- **Severity:** 🔴 CRITICAL  
- **Files:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L372-L382), [`backend/app/services/graphrag_translator.py`](backend/app/services/graphrag_translator.py)  
- **Requirement:** Delta §7.7, `mvp-sprint.md` RCKG-405  
- **Details:** `GET /api/v1/extract/graph/graphrag-export` calls `export_subgraph()` without arguments. The translator defaults to 2 hardcoded nodes (`GDPR Article 32` and `SecOps Data Protection Policy`).  
- **Impact:** GraphRAG query engines receive mock data instead of the active Memgraph topology.

#### 16. `RuleBasedGraphCompiler` Generates `ADD_EDGE` for `NO_RELATIONSHIP`
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/services/graph_compiler.py`](backend/app/services/graph_compiler.py#L168-L179)  
- **Requirement:** Delta §3.1, §7.3  
- **Details:** When two entities have no relationship, the compiler emits a `GraphMutationDiff` with `primitive = ClosedSetPrimitive.ADD_EDGE` and `relationship_type = "NO_RELATIONSHIP"`.  
- **Impact:** Creates explicit graph edges for disjoint/unrelated nodes, cluttering the graph database.

#### 17. `process-pdf` Endpoint Writes Raw Cypher Strings Bypassing Architecture
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L188-L335)  
- **Requirement:** Delta §7.3, TRD §2  
- **Details:** The endpoint directly opens Neo4j drivers and executes inline Cypher, bypassing `MemgraphService`, `RCKGCypherBuilder`, `GovernanceEngine`, and `GraphMutationDiff`.  
- **Impact:** No audit logs in `graph_outbox_log` and no governance validation.

#### 18. `GraphitiSemanticChangeDetector` Uses Naive String Equality
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/services/graphiti_engine.py`](backend/app/services/graphiti_engine.py#L57)  
- **Requirement:** Delta §7.1 Phase 2, `mvp-sprint.md` RCKG-401  
- **Details:** Steady-state change detection uses `if old_content != new_content:` (exact string match).  
- **Impact:** Minor formatting or wording changes trigger unnecessary `SUPERSEDE_NODE` mutations.

#### 19. `process-pdf` Hardcodes Fallback Chunk Metadata
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L172-L181)  
- **Requirement:** Delta §2.2  
- **Details:** When clause extraction yields no chunks, the fallback creates a single chunk with hardcoded `section_reference="Section 3.1"`, `heading_title="Access Control & Security"`, and truncates text to the first 500 characters.  
- **Impact:** Large documents lose 99%+ of content when clause chunking falls back.

---

### Category 3: Errors in Processing (8 Items)

#### 20. Regex Capture Group Index Out of Range in `ClauseBoundaryExtractor`
- **Severity:** 🔴 CRITICAL / 🟠 MAJOR  
- **File:** [`backend/app/services/hybrid_chunking.py`](backend/app/services/hybrid_chunking.py#L487-L520)  
- **Requirement:** `mvp-sprint.md` RCKG-203  
- **Details:** `CLAUSE_HEADER_PATTERN` has 2 capture groups. Line 520 attempts to access `match.group(6)`:
  ```python
  current_heading = match.group(6).strip() if match.group(6) else current_sec_ref
  ```
- **Impact:** Parsing documents with matching clause headers triggers an uncaught `IndexError: no such group` at runtime.

#### 21. LLM Endpoint Default Port Collision
- **Severity:** 🟡 MODERATE  
- **File:** [`backend/app/services/extraction.py`](backend/app/services/extraction.py#L37)  
- **Requirement:** TRD §1  
- **Details:** `LLM_ENDPOINT` defaults to `"http://localhost:8000/v1"`. Port 8000 is used by FastAPI itself.  
- **Impact:** If `LLM_ENDPOINT` is unset in the environment, extraction calls hit FastAPI instead of vLLM, causing HTTP errors or timeouts.

#### 22. Outbox Log Committed Prior to Memgraph Writes (Atomicity Failure)
- **Severity:** 🟠 MAJOR  
- **File:** [`backend/app/services/memgraph_service.py`](backend/app/services/memgraph_service.py#L97-L119)  
- **Requirement:** Delta §7.3, BRD BO-05  
- **Details:** `enqueue_and_execute()` executes `self.db.commit()` for `GraphOutboxLog` *before* executing the Cypher query against Memgraph.  
- **Impact:** PostgreSQL outbox entries are marked processed even if Memgraph execution fails.

#### 23. `format_classifier.py` Does Not Inspect PDF Internal Structure
- **Severity:** 🟡 MODERATE  
- **File:** [`backend/app/services/format_classifier.py`](backend/app/services/format_classifier.py)  
- **Requirement:** Delta §2.2  
- **Details:** `classify()` passes 0 for `text_char_count`, `image_count`, and `table_cell_count` when callers pass raw bytes without feature counts.  
- **Impact:** All PDFs default to `NATIVE_PDF`, bypassing `SCANNED_PDF` and `COMPLEX_MATRIX` routes.

#### 24. Seed Ingestion Ignores `FrameworkControlActNode` Distinction
- **Severity:** 🟡 MODERATE  
- **File:** [`backend/app/services/seed_ingestion.py`](backend/app/services/seed_ingestion.py#L152-L159)  
- **Requirement:** Delta §5.4  
- **Details:** All seed nodes are persisted as `FrameworkControlObjectiveNode`, ignoring the `FrameworkControlActNode` entity model.  
- **Impact:** Standardized control activity benchmarks are mis-classified as objectives.

#### 25. Incorrect Edge Direction (`SATISFIES` from `StatutoryRequirement` $\rightarrow$ `Obligation`)
- **Severity:** 🔵 MINOR  
- **File:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L237-L247)  
- **Requirement:** Delta §3.1  
- **Details:** Line 241 executes `MERGE (d:StatutoryRequirement)-[r:SATISFIES]->(o:Obligation)`. A requirement defines/contains obligations; it does not satisfy them.  
- **Impact:** Misaligns with the canonical 5-linkage topology.

#### 26. Bootstrap Endpoint Import Module Path Inconsistency
- **Severity:** 🔵 MINOR  
- **File:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L116)  
- **Requirement:** N/A  
- **Details:** Uses `from backend.app.services.cold_start_pipeline import ...` whereas other endpoints use `from app.services...`.  
- **Impact:** Risk of `ModuleNotFoundError` depending on entrypoint execution directory.

#### 27. Over-Linking in `ControlObjective` $\rightarrow$ `Obligation` Domain Match
- **Severity:** 🔵 MINOR  
- **File:** [`backend/app/api/extract.py`](backend/app/api/extract.py#L280-L289)  
- **Requirement:** Delta §3.1  
- **Details:** Matches all obligations sharing a domain string (`MATCH (o:Obligation) WHERE o.domain_facet = $domain`).  
- **Impact:** A single policy objective links to every obligation in that broad domain.

---

## 3. Side-by-Side Verification Matrix

| # | Finding Description | Reported in `code-review.md` | Reported in `code-review-gemini.md` v2.0 |
|---|---|:---:|:---:|
| 1 | Single-Prompt Extraction Lock (No ControlObjective/ControlActivity) | ✅ | ✅ |
| 2 | Missing 4-Stage Multistage Candidate Retrieval Funnel | ✅ | ✅ |
| 3 | Missing DeBERTa-v3 NLI Model Execution | ✅ | ✅ |
| 4 | Async 70B Dual-Judge Service Is Arithmetic Mock | ✅ | ✅ |
| 5 | Mock Qdrant In-Memory Vector Store | ✅ | ✅ |
| 6 | GovernanceEngine Has No Persistence | ✅ | ✅ |
| 7 | ColBERTv2Service Is a Mock | ✅ | ✅ |
| 8 | PreferenceAccumulatorWorker Kafka Publish Is a Log Statement | ✅ | ✅ |
| 9 | No document_type Routing in Upload -> Extract Pipeline | ✅ | ✅ |
| 10 | Seed Ingestion Does Not Write Edges | ✅ | ✅ |
| 11 | process-pdf Endpoint Generates Synthetic/Fabricated Text | ✅ | ✅ |
| 12 | DeJureFacetExtractor Is a Trivial Regex Stub | ✅ | ✅ |
| 13 | Hardcoded Cold-Start Target Node & Similarity | ✅ | ✅ |
| 14 | GraphRevertService Fabricates Release Tag | ✅ | ✅ |
| 15 | GraphRAG Export Endpoint Returns Hardcoded Fallback JSON | ✅ | ✅ |
| 16 | RuleBasedGraphCompiler Generates ADD_EDGE for NO_RELATIONSHIP | ✅ | ✅ |
| 17 | process-pdf Endpoint Writes Raw Cypher Strings Bypassing Architecture | ✅ | ✅ |
| 18 | GraphitiSemanticChangeDetector Uses Naive String Equality | ✅ | ✅ |
| 19 | process-pdf Hardcodes Fallback Chunk Metadata | ✅ | ✅ |
| 20 | Regex Capture Group Index Out of Range in ClauseBoundaryExtractor (group(6)) | ✅ | ✅ |
| 21 | LLM Endpoint Default Port Collision (Port 8000) | ✅ | ✅ |
| 22 | Outbox Log Committed Prior to Memgraph Writes (Atomicity Failure) | ✅ | ✅ |
| 23 | format_classifier.py Does Not Inspect PDF Internal Structure | ✅ | ✅ |
| 24 | Seed Ingestion Ignores FrameworkControlActNode Distinction | ✅ | ✅ |
| 25 | Incorrect Edge Direction (StatutoryRequirement -> Obligation SATISFIES) | ✅ | ✅ |
| 26 | Bootstrap Endpoint Import Module Path Inconsistency | ✅ | ✅ |
| 27 | Over-Linking in ControlObjective -> Obligation Domain Match | ✅ | ✅ |

---

## 4. Remediation Action Plan

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          RCKG TECHNICAL REMEDIATION ROADMAP                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STEP 1: FIX RUNTIME BUGS                                                               │
│ • Fix match.group(6) -> match.group(2) in hybrid_chunking.py                           │
│ • Change LLM_ENDPOINT default port from 8000 to 8008 / 8001 in extraction.py           │
│                                                                                        │
│ STEP 2: EXPAND EXTRACTION PROMPTS & SCHEMAS                                            │
│ • Add policy_extraction.md (ControlObjective) & sop_extraction.md (ControlActivity)    │
│ • Update extraction.py to support document_type parameter ('STATUTORY' | 'POLICY' | 'SOP')│
│                                                                                        │
│ STEP 3: INTEGRATE LLM INTO PROCESS-PDF PIPELINE                                        │
│ • Modify process-pdf endpoint to call LLM decomposition rather than regex templates    │
│ • Ensure real extracted prose and citations are persisted to Memgraph & PostgreSQL     │
│                                                                                        │
│ STEP 4: SEED GRAPH EDGE PERSISTENCE                                                    │
│ • Update ComplianceSeedIngester to persist seed edges to PostgreSQL and Memgraph        │
│                                                                                        │
│ STEP 5: CONNECT SERVICE LAYER STUBS TO LIVE ENGINES                                    │
│ • Wire ColdStartPipelineOrchestrator to real candidate retrieval                       │
│ • Implement Memgraph Cypher execution in GraphRevertService & GraphRAGTranslator       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
