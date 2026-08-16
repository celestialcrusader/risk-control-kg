# Sprint Plan: Sprint L — Production Regulatory Compiler & Defensible Crosswalk Engine

## Executive Summary & Context
Following expert review of the MVP semantic mapping results (`test-run-results-2.md`), the current crosswalk generation pipeline surfaces several critical flaws that prevent it from being accepted as an authoritative, audit-grade GRC deliverable:
1. **Conflation of "Enables/Supports" with "Satisfies/Covers"**: 77.4% of edges were labeled `SUPERSET_OF` because the model treated general governance or budgeting controls (e.g. `NIST-SA-2 Allocation of Resources`) as satisfying specific technical mandates (e.g. `MAS-1.4(b).2 Preserve CIA of IT systems`).
2. **Inconsistent Edge Directionality**: The definition of `SUPERSET_OF` vs `SUBSET_OF` varied depending on whether the judge evaluated from MAS-perspective or NIST-perspective.
3. **Withdrawn & Blank Control Ingestion**: Withdrawn NIST Rev 5 controls (`NIST-RA-4`, `NIST-SA-12`) had empty text in the catalog but were still matched with 0.85 confidence.
4. **Retrieval Blindspots on Short Queries**: Strict 5-kNN dense search on short 6-word clauses (e.g., *"enforce MFA"*) missed textbook canonical NIST controls (`IA-2`).

Sprint L establishes a **Two-Dimensional Crosswalk Architecture** (Semantic Relationship + Assurance Coverage), implements **Hybrid Retrieval (Dense + BM25 Top-15)**, sanitizes the control catalog, and enforces **strict directional audit defensibility**.

---

## Step 1: Sprint Planning Principles
- **Sprint Identifier**: Sprint L
- **Sprint Duration**: 2 Weeks
- **Team Composition**: 1 Senior AI Architect, 1 Backend/Data Engineer, 1 GRC Domain Specialist, 1 QA Automation Engineer
- **Total Story Points**: **18 SP**
- **Sprint Goal**: Transform the crosswalk engine from an exploratory similarity tool into a mathematically consistent, two-dimensional Regulatory Knowledge Compiler that distinguishes *Semantic Support* from *Assurance Satisfaction* with 100% audit defensibility.

---

## Step 2: Sprint Structure & Stories

| Story ID | Story Title | Priority | SP | Status | Assigned |
|---|---|---|---|---|---|
| `STORY-COMP-201` | Two-Dimensional Ontology & Directional Schema Migration | P0 | 5 | ✅ Done (QA Approved) | SWE / QA |
| `STORY-COMP-202` | Catalog Sanitizer & Inactive/Withdrawn Control Filter | P0 | 3 | ✅ Done (QA Approved) | SWE / QA |
| `STORY-COMP-203` | Hybrid Candidate Retriever (Dense + BM25 Top-15 Recall Net) | P0 | 5 | ✅ Done (QA Approved) | SWE / QA |
| `STORY-COMP-204` | Dual-Judge Assurance Evaluator & Defensible Audit Rationale | P0 | 5 | ✅ Done (QA Approved) | AI / Backend Engineer |

---

## Step 3: Detailed Story Tickets

---

### [STORY-COMP-201] Two-Dimensional Ontology & Directional Schema Migration

**Type**: Architecture / Schema Migration  
**Sprint**: Sprint L  
**Story Points**: 5 SP  
**Priority**: High (P0)  
**Assigned To**: Backend / Data Engineer  
**Labels**: `backend`, `database`, `ontology`, `postgres`, `memgraph`

#### User Story
> As a **GRC Compliance Auditor**, I want the knowledge graph to distinguish between **Semantic Relationship** (*how concepts relate*) and **Assurance Coverage** (*whether NIST evidence satisfies MAS*), so that I can rely on crosswalk edges without false-positive compliance claims.

#### Context and Background
Currently, the database only stores a single `set_theory_relation` enum (`EQUIVALENT_TO`, `SUPERSET_OF`, `SUBSET_OF`, `INTERSECTS_WITH`, `NO_RELATIONSHIP`). This forces the engine to conflate "NIST SA-2 enables MAS CIA preservation" with "NIST SA-2 satisfies MAS CIA preservation". Furthermore, directionality was unanchored. This story migrates PostgreSQL and Memgraph schemas to a formal two-dimensional representation anchored strictly from the **Source (Obligation) perspective**.

#### Acceptance Criteria
1. Given an obligation mapping in PostgreSQL, when querying `obligation_framework_mappings`, then it must contain two separate enum columns: `semantic_relation` (`EQUIVALENT`, `OVERLAPS`, `SUPPORTS`, `RELATED`, `NONE`) and `assurance_coverage` (`FULL_COVERAGE`, `PARTIAL_COVERAGE`, `NO_COVERAGE`).
2. Given a `:CROSSWALKS_TO` edge in Memgraph, when querying graph relationships, then both `semantic_relation` and `assurance_coverage` properties must exist on the edge.
3. Given a directional evaluation between Obligation A (Source) and Control B (Target), when Obligation A is broader than Control B, then `semantic_relation` must be explicitly stored as `SUPERSET_OF` (Source contains Target); when Control B is broader than Obligation A, it must be stored as `SUBSET_OF` (Source is subsumed by Target).
4. Given existing database tables, when executing Alembic migrations, then old mappings are cleanly migrated or re-initialized without data corruption.

#### Technical Notes
- Anchor all relations strictly from **Source (Obligation) $\rightarrow$ Target (Control)**:
  - `EQUIVALENT`: Scope, intent, and actionable requirements are 1-to-1 identical.
  - `SUBSET_OF`: Target control completely satisfies Source obligation plus additional requirements ($A \subseteq B$).
  - `SUPERSET_OF`: Source obligation is broader than Target control; Target only covers a component ($A \supseteq B$).
  - `OVERLAPS`: Substantial conceptual overlap, but neither strictly subsumes the other.
  - `SUPPORTS`: Target provides enabling mechanisms/governance (e.g. budgeting, training) but does not satisfy the technical control itself.
  - `NONE`: Unrelated.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|---|---|
| `backend/app/models/rckg_nodes.py` | Add `SemanticRelation` and `AssuranceCoverage` enums; update `ObligationFrameworkMapping` model |
| `backend/alembic/versions/20260816_01_two_dim_ontology.py` | [NEW] Migration script adding two-dimensional columns |
| `backend/app/core/memgraph.py` | Update Memgraph Cypher constraints and edge creation query |

##### Relevant Code Blocks

**`backend/app/models/rckg_nodes.py`** — Add Enums and Update Model
```python
# Locate SetTheoryRelation (around line 20) and replace with:
class SemanticRelation(str, enum.Enum):
    EQUIVALENT = "EQUIVALENT"
    SUBSET_OF = "SUBSET_OF"        # Source is subset of Target (Target satisfies Source)
    SUPERSET_OF = "SUPERSET_OF"    # Source is superset of Target (Target partially addresses Source)
    OVERLAPS = "OVERLAPS"          # Material overlap without strict containment
    SUPPORTS = "SUPPORTS"          # Target enables/supports Source without satisfying it
    NONE = "NONE"

class AssuranceCoverage(str, enum.Enum):
    FULL_COVERAGE = "FULL_COVERAGE"        # Evidence of Target fully satisfies Source
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"  # Evidence of Target satisfies part of Source
    NO_COVERAGE = "NO_COVERAGE"            # Evidence of Target does NOT satisfy Source

# Update ObligationFrameworkMapping table definition:
class ObligationFrameworkMapping(Base):
    __tablename__ = "obligation_framework_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    obligation_id = Column(UUID(as_uuid=True), ForeignKey("obligations.id", ondelete="CASCADE"), nullable=False)
    framework_objective_id = Column(UUID(as_uuid=True), ForeignKey("framework_control_objectives.id", ondelete="CASCADE"), nullable=False)
    
    # [NEW] Two-Dimensional Edge Attributes
    semantic_relation = Column(Enum(SemanticRelation), nullable=False, default=SemanticRelation.NONE)
    assurance_coverage = Column(Enum(AssuranceCoverage), nullable=False, default=AssuranceCoverage.NO_COVERAGE)
    
    confidence_score = Column(Numeric(4, 2), nullable=False)
    status = Column(Enum(MappingStatus), nullable=False, default=MappingStatus.PROBABILISTIC_AI)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

##### Migration / Schema Changes
```sql
-- migrations/20260816_two_dimensional_ontology.sql
ALTER TABLE obligation_framework_mappings 
  DROP COLUMN IF EXISTS set_theory_relation;

CREATE TYPE semantic_relation_enum AS ENUM ('EQUIVALENT', 'SUBSET_OF', 'SUPERSET_OF', 'OVERLAPS', 'SUPPORTS', 'NONE');
CREATE TYPE assurance_coverage_enum AS ENUM ('FULL_COVERAGE', 'PARTIAL_COVERAGE', 'NO_COVERAGE');

ALTER TABLE obligation_framework_mappings
  ADD COLUMN semantic_relation semantic_relation_enum NOT NULL DEFAULT 'NONE',
  ADD COLUMN assurance_coverage assurance_coverage_enum NOT NULL DEFAULT 'NO_COVERAGE';
```

##### Where NOT to Touch
- Do **not** alter `obligations` or `framework_control_objectives` primary key definitions.

---

### [STORY-COMP-202] Catalog Sanitizer & Inactive/Withdrawn Control Filter

**Type**: Ingestion / Data Hygiene  
**Sprint**: Sprint L  
**Story Points**: 3 SP  
**Priority**: High (P1)  
**Assigned To**: Data Engineer  
**Labels**: `ingestion`, `oscal`, `nist`, `hygiene`

#### User Story
> As a **Security Architect**, I want the ingestion engine to exclude withdrawn, obsolete, or empty controls (such as `NIST-RA-4` or `NIST-SA-12`), so that the AI reasoning engine never evaluates against phantom requirements.

#### Context and Background
In NIST SP 800-53 Rev 5, several Rev 4 controls were formally withdrawn (`RA-4` folded into `RA-3`, `SA-12` carved into `SR` family). In our database, these rows exist with blank text (`""`). During vector search, length-diluted similarity caused the LLM judge to evaluate blank text and score them with 0.85 confidence.

#### Acceptance Criteria
1. Given an OSCAL YAML catalog or database extract, when a control is marked as `withdrawn` or has empty `objective_text` ($< 15$ characters), then the ingestion engine must exclude it from active framework controls.
2. Given a candidate retrieval query, when querying available NIST controls, then 0 withdrawn or blank controls are returned in the candidate pool.
3. Given `NIST-RA-4` and `NIST-SA-12`, when checking the active catalog table, then they must either be flagged with `status = 'WITHDRAWN'` or excluded from embedding indexes.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|---|---|
| `backend/app/services/oscal_parser.py` | Filter out controls with `status: withdrawn` or empty description |
| `scripts/clean_withdrawn_controls.py` | [NEW] Maintenance script to purge/flag blank controls in existing DB |

##### Relevant Code Blocks

**`backend/app/services/oscal_parser.py`** — Filter Withdrawn Controls
```python
# In process_control_node:
def is_control_active(control_dict: dict) -> bool:
    # Check for OSCAL props indicating withdrawal
    props = control_dict.get("props", [])
    for p in props:
        if p.get("name") == "status" and p.get("value") == "withdrawn":
            return False
    # Check for empty text
    parts = control_dict.get("parts", [])
    if not parts and not control_dict.get("description", "").strip():
        return False
    return True
```

---

### [STORY-COMP-203] Hybrid Candidate Retriever (Dense + BM25 Top-15 Recall Net)

**Type**: Search / Retrieval  
**Sprint**: Sprint L  
**Story Points**: 5 SP  
**Priority**: High (P0)  
**Assigned To**: AI Search Engineer  
**Labels**: `qdrant`, `bm25`, `hybrid-search`, `recall`

#### User Story
> As an **AI Compliance Engineer**, I want candidate generation to use **Hybrid Retrieval (Dense Neural + Lexical BM25)** with a **Top-15 Recall Net**, so that short canonical clauses (like *"enforce MFA"* $\rightarrow$ `NIST-IA-2` or *"IT audit"* $\rightarrow$ `NIST-CA-2`) are never dropped prior to LLM evaluation.

#### Context and Background
Dense bi-encoders (`bge-small`) on short 5-word queries experience token dispersion and push high-exactness keyword matches outside the top 5 nearest neighbors. Expert review revealed that `MAS-OBL-01` (*"The organization must enforce MFA"*) produced 0 matches because `IA-2` was dropped at rank #8. Hybrid reciprocal rank fusion (RRF) between dense cosine and BM25 scores guarantees that domain-specific keywords and semantic paraphrases both reach the Dual-Judge.

#### Acceptance Criteria
1. Given a short MAS obligation (e.g. *"The organization must enforce MFA"*), when executing candidate retrieval, then `NIST-IA-2` must rank in the Top 5 candidates.
2. Given any MAS obligation, when candidate generation executes, then exactly **15 candidate controls** are passed to the Dual-Judge evaluation queue using Reciprocal Rank Fusion (RRF).
3. Given a candidate NIST control, when formatted for the Dual-Judge, then the **full normative statement text** (without boilerplate XML parameters) is provided without mid-sentence truncation.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|---|---|
| `backend/app/services/hybrid_retriever.py` | [NEW] Implements BM25 + Dense Qdrant RRF fusion |
| `backend/app/services/qdrant_service.py` | Add dense vector upsert with full clean control text payload |

##### New Files to Create

**`backend/app/services/hybrid_retriever.py`** — [NEW]
```python
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Tuple, Dict, Any

class HybridCandidateRetriever:
    """Combines Dense Neural Vector Search with Lexical BM25 via Reciprocal Rank Fusion (RRF)."""

    def __init__(self, nist_controls: List[Any], embedder_fn):
        self.controls = nist_controls
        self.embedder_fn = embedder_fn
        
        # Tokenize for BM25
        self.corpus = [
            f"{c.framework_obj_id} {c.objective_name} {c.objective_text}".lower().split()
            for c in nist_controls
        ]
        self.bm25 = BM25Okapi(self.corpus)
        
        # Precompute dense vectors
        dense_texts = [f"{c.framework_obj_id} {c.objective_name}: {c.objective_text[:400]}" for c in nist_controls]
        self.control_vectors = self.embedder_fn(dense_texts)

    def retrieve_top_k(self, query_text: str, top_k: int = 15) -> List[Tuple[Any, float, str]]:
        # 1. Lexical BM25 Scores
        query_tokens = query_text.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        bm25_ranks = np.argsort(bm25_scores)[::-1]

        # 2. Dense Vector Scores
        q_vec = self.embedder_fn([query_text])[0]
        dense_scores = np.dot(self.control_vectors, q_vec)
        dense_ranks = np.argsort(dense_scores)[::-1]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k = 60
        for rank, idx in enumerate(bm25_ranks[:50]):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k + rank + 1))
        for rank, idx in enumerate(dense_ranks[:50]):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k + rank + 1))

        top_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            ctrl = self.controls[idx]
            sim = float(dense_scores[idx])
            results.append((ctrl, sim, f"RRF Score: {rrf_scores[idx]:.4f} (Dense: {sim:.2f})"))
        return results
```

---

### [STORY-COMP-204] Dual-Judge Assurance Evaluator & Defensible Audit Rationale

**Type**: AI / Reasoning Engine  
**Sprint**: Sprint L  
**Story Points**: 5 SP  
**Priority**: High (P0)  
**Assigned To**: AI / Backend Engineer  
**Labels**: `llm`, `dual-judge`, `qwen`, `nli`, `audit`

#### User Story
> As a **Compliance Officer**, I want the Dual-Judge LLM to evaluate **both Semantic Relationship and Assurance Coverage independently** and produce non-generic, citable audit rationales, so that every crosswalk in the graph is legally defensible.

#### Context and Background
The prompt previously asked a single question that led to generic fallback rationales (`"LLM NLI Judgement"`) and anchored confidence to a narrow band (`0.75 - 0.90`). This story updates the reasoning prompt to ask two structured questions, enforce calibrated scoring, and output complete regulatory justifications.

#### Acceptance Criteria
1. Given an obligation pair, when evaluated by the Dual-Judge, then the output must contain both `semantic_relation` and `assurance_coverage` with explicit justification.
2. Given a governance/enabling control (e.g. `NIST-SA-2 Allocation of Resources` vs `MAS-1.4(b).2 CIA Preservation`), when evaluated, then `semantic_relation` must be `SUPPORTS` and `assurance_coverage` must be `NO_COVERAGE`.
3. Given a generic fallback rationale (e.g. `"LLM Semantic Evaluation"`), then the evaluator must reject the candidate or retry, ensuring 0 placeholder rationales enter the database.
4. Given an active evaluation, when completing all candidate pairs, then throughput remains $\ge 20$ pairs/sec on local GPU hardware.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|---|---|
| `backend/app/services/nli_evaluator.py` | Update prompt schema, parse two-dimensional output, calibrate confidence |
| `scripts/run_production_evaluation_suite.py` | Wire hybrid retriever and two-dimensional evaluator to generate `test-run-results-3.md` |

##### Relevant Code Blocks

**`backend/app/services/nli_evaluator.py`** — Two-Dimensional Prompt
```python
# Update prompt template inside NliBatchCrosswalkEvaluator:
prompt = f'''<|im_start|>system
You are a Senior Regulatory Compliance Auditor and Knowledge Graph Compiler.
Analyze the relationship between Source Obligation (Requirement A) and Target Control (Control B).

You must answer TWO separate questions from the perspective of Requirement A (Source):

1. SEMANTIC RELATIONSHIP:
   - "EQUIVALENT": Scope, intent, and actionable mandates are 1-to-1 identical.
   - "SUBSET_OF": Control B completely satisfies Requirement A plus additional requirements (A ⊆ B).
   - "SUPERSET_OF": Requirement A is broader; Control B only addresses a sub-component (A ⊇ B).
   - "OVERLAPS": Material conceptual overlap, but neither strictly covers the other.
   - "SUPPORTS": Control B provides enabling governance/budgeting/support, but does not implement the mandate.
   - "NONE": Unrelated.

2. ASSURANCE COVERAGE:
   - "FULL_COVERAGE": Implementing Control B completely satisfies Requirement A for audit purposes.
   - "PARTIAL_COVERAGE": Implementing Control B satisfies part of Requirement A, but gaps remain.
   - "NO_COVERAGE": Implementing Control B does NOT satisfy Requirement A (e.g. only supports/enables).

Return JSON only.<|im_end|>
<|im_start|>user
Source Requirement A: "{source_text}"
Target Control B: "{target_text}"
<|im_end|>
<|im_start|>assistant
<think>
</think>
{{
  "semantic_relation": "'''
```

---

## Step 4: Sprint Plan Summary & Backlog Health Check

### Backlog Metrics
- **Total Sprints in Roadmap**: Sprint J (Foundation) $\rightarrow$ Sprint K (Topology & AI NLI) $\rightarrow$ **Sprint L (Compiler & Defensible Crosswalk)**
- **Total Stories in Sprint L**: 4 Stories
- **Total Story Points**: **18 SP**
- **Estimated Completion**: 2 Weeks

### Delivery Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| **Ambiguity in Edge Semantics** | High | Hardcode Source-to-Target directional documentation and test cases verifying that $A \subseteq B$ is always labeled `SUBSET_OF`. |
| **GPU Generation Latency with Top-15** | Medium | Use the `<think>\n</think>\n{` prefill optimization on vLLM to maintain $\ge 20$ evaluations/second across the 1,275 pairs ($85 \times 15$). |
| **Overfitting on Specific Clause Formats** | Low | Validate against diverse clause types: governance, technical cryptography, incident reporting, and third-party risk. |

---

### Definition of Done (Sprint L)
- [ ] Schema migration executed with `semantic_relation` and `assurance_coverage` in PostgreSQL and Memgraph.
- [ ] Withdrawn Rev 5 controls (`RA-4`, `SA-12`) purged from active candidate index.
- [ ] Hybrid Retriever (Dense + BM25 Top-15) operational and retrieving `NIST-IA-2` for MFA.
- [ ] 0 placeholder rationales in database; all 1-to-N and N-to-1 links explainable.
- [ ] `docs/07-update-parse/test-run-results-3.md` generated and reviewed.
