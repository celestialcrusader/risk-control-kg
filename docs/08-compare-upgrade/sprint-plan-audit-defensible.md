# Sprint Plan: Audit-Defensible Regulatory Crosswalk Engine (Sprint M)

**Sprint ID:** `SPRINT-COMP-M`  
**Goal:** Eliminate heuristic keyword masking, achieve genuine two-dimensional decoupling (Semantic Relation $\perp$ Assurance Coverage), generate defensible comparative rationales, and decompound multi-threat regulatory obligations for high-recall precision.  
**Estimated Velocity:** 15 Story Points  
**Target Completion Date:** 2026-08-16  
**Execution Workflow:** `/tdd-story-execution` (Red-Green-Refactor + Independent QA Review)  

---

## 1. Executive Summary & Expert Audit Remediation

Following expert audit reviews on `test-run-results-3.md`, this sprint addresses four critical architectural defects:
1. **Zero Silent Heuristic Promotion**: The bag-of-words fallback engine must never assign `EQUIVALENT` or `FULL_COVERAGE`. All candidate pairs must be evaluated by the genuine LLM judge or flagged as unverified heuristic with $< 0.40$ confidence.
2. **True Two-Dimensional Orthogonal Reasoning**: Decouple `semantic_relation` from `assurance_coverage`. Ensure `EQUIVALENT`, `SUBSET_OF`, `SUPERSET_OF`, and `OVERLAPS` can yield varied assurance tiers based on independent audit satisfaction criteria.
3. **Defensible Comparative Rationale**: Every edge must contain a comparative explanation citing specific mechanisms in Requirement A and Control B. Tautological phrases (*"Evaluated as X with Y"*) and generic keyword metrics are strictly prohibited and rejected.
4. **Multi-Intent Clause Decompounding**: Compound clauses (e.g. `MAS-14.1.2`, `MAS-14.1.3`) are decomposed into sub-intent queries during candidate retrieval to ensure critical controls like `NIST-SC-8`, `SI-3`, `SC-5`, and `SI-10` are captured in the top recall pool.

---

## 2. Sprint Backlog & Story Tickets

| Story ID | Title | Points | Priority | Status |
|---|---|---|---|---|
| **`STORY-COMP-301`** | Multi-Intent Clause Decompounder & Precision Query Expansion | 5 SP | P0 (Blocker) | ✅ Done (QA Approved) |
| **`STORY-COMP-302`** | Genuinely Decoupled Two-Dimensional Dual-Judge & Anti-Heuristic Gatekeeper | 5 SP | P0 (Blocker) | ✅ Done (QA Approved) |
| **`STORY-COMP-303`** | Defensible Comparative Rationale Generator & Tautology Rejection Filter | 5 SP | P0 (Blocker) | ✅ Done (QA Approved) |

---

## 3. Story Ticket Specifications

### `STORY-COMP-301`: Multi-Intent Clause Decompounder & Precision Query Expansion
- **Goal**: Implement `ClauseDecompounder` to break down multi-threat/compound regulatory clauses into atomic technical requirements during hybrid retrieval.
- **Acceptance Criteria**:
  - `AC-301.1`: `ClauseDecompounder.decompose(clause_text)` detects multi-sentence or conjunctive threat mandates (e.g., encryption in transit, injection, malware, DDoS) and produces atomic search queries.
  - `AC-301.2`: `HybridCandidateRetriever` executes sub-query search union so that `MAS-14.1.2` retrieves `NIST-SC-8` and `MAS-14.1.3` retrieves `NIST-SI-3`, `NIST-SC-5`, and `NIST-SI-10` in Top-15.
  - `AC-301.3`: Unit tests verify atomic query generation and candidate inclusion.

### `STORY-COMP-302`: Genuinely Decoupled Two-Dimensional Dual-Judge & Anti-Heuristic Gatekeeper
- **Goal**: Refactor `NliBatchCrosswalkEvaluator` and vLLM integration to eliminate keyword fallback promotion and evaluate orthogonal dimensions.
- **Acceptance Criteria**:
  - `AC-302.1`: Anti-heuristic gatekeeper ensures fallback heuristic NEVER outputs `EQUIVALENT` or `FULL_COVERAGE`. Maximum fallback confidence is capped at $0.35$.
  - `AC-302.2`: Dual-judge prompts ask two independent questions with no deterministic hardcoded mapping in post-processing.
  - `AC-302.3`: Concurrency throttled to $2$ workers with retry logic to match vLLM `max_num_seqs: 4` without worker disconnects.
  - `AC-302.4`: Unit tests verify orthogonal distribution and heuristic capping.

### `STORY-COMP-303`: Defensible Comparative Rationale Generator & Tautology Rejection Filter
- **Goal**: Ensure all committed crosswalk edges contain case-specific comparative rationales and filter out canned/tautological strings.
- **Acceptance Criteria**:
  - `AC-303.1`: Rationales must explicitly contrast the source requirement against the target control mechanisms.
  - `AC-303.2`: Tautology validator rejects rationales matching `"Evaluated semantic relationship as..."`, `"Shared domain concepts..."`, or generic placeholders.
  - `AC-303.3`: Full production evaluation suite execution outputs `docs/08-compare-upgrade/test-run-results-4.md` and `docs/07-update-parse/test-run-results-4.md`.
