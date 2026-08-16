# Sprint Plan: Atomic Assurance Verification & TEVV Crosswalk Engine (Sprint N)

**Sprint ID:** `SPRINT-COMP-N`  
**Goal:** Eliminate false-positive `FULL_COVERAGE` / `EQUIVALENT` assertions via an Atomic Coverage Verifier Gate, unfreeze confidence scoring with multi-signal Bayesian calibration, bind canonical MFA controls (`NIST-IA-2`), and enforce a structured 4-part audit-defensible rationale standard.  
**Estimated Velocity:** 15 Story Points  
**Target Completion Date:** 2026-08-16  
**Execution Workflow:** `/tdd-story-execution` (Red-Green-Refactor + Independent QA Review)  

---

## 1. Executive Summary & Expert Audit Remediation

Based on expert audit review findings on `test-run-results-4.md`, Sprint N delivers the definitive assurance verification layer:
1. **Atomic Coverage Verifier Gate (`Action-Object-Scope`)**:
   - `FULL_COVERAGE` is strictly gated: only permitted when the source obligation's material Action, Object, and Scope are explicitly satisfied by the target control.
   - Converts false full coverage matches (`NIST-AU-4`, `IR-6`, `SC-16`, `MP-7`) to accurate `PARTIAL_COVERAGE` or `NO_COVERAGE`.
2. **1-to-1 Transitivity Enforcement for `EQUIVALENT`**:
   - Ensures an obligation cannot be `EQUIVALENT` to multiple non-identical target controls (e.g. `PM-9` vs `PM-1`). Only the single best candidate retains `EQUIVALENT`.
3. **Retail Banking Customer Gap Classifier**:
   - Identifies retail customer-facing requirements (e.g. `MAS-14.3.3.a` fraud notification) that have no equivalent in federal IT system catalogs and classifies them transparently as true gaps rather than laundering them into `PARTIAL_COVERAGE`.
4. **Canonical MFA Binding (`MAS-14.2.1` $\rightarrow$ `NIST-IA-2`)**:
   - Explicitly ensures `NIST-IA-2` (Identification and Authentication: Multi-Factor Authentication) is retrieved and linked.
5. **Dynamic Multi-Signal Confidence Scoring**:
   - Eliminates frozen `0.85` confidence by calculating composite confidence across LLM judgment, dense cosine similarity, and atomic token overlap ($0.65 - 0.98$).
6. **Structured 4-Part Defensible Rationale Standard**:
   - Every rationale includes: MAS Requirement, NIST Mechanism, Element Breakdown (Covered vs Missing), and Assurance Conclusion.

---

## 2. Sprint Backlog & Story Tickets

| Story ID | Title | Points | Priority | Status |
|---|---|---|---|---|
| **`STORY-COMP-401`** | Atomic Coverage Verifier Gate & False FULL/EQUIVALENT Prevention | 5 SP | P0 (Blocker) | ✅ Done (QA Approved) |
| **`STORY-COMP-402`** | Retail Banking Customer Gap Classifier & Canonical MFA IA-2 Binding | 5 SP | P0 (Blocker) | ✅ Done (QA Approved) |
| **`STORY-COMP-403`** | Dynamic Bayesian Confidence Calibrator & Structured 4-Part Rationale Standard | 5 SP | P0 (Blocker) | ✅ Done (QA Approved) |

---

## 3. Detailed Story Specifications

### `STORY-COMP-401`: Atomic Coverage Verifier Gate & False FULL/EQUIVALENT Prevention
- **Goal**: Implement `AtomicCoverageVerifier` in `backend/app/services/coverage_verifier.py` to prevent over-asserted `FULL_COVERAGE` and protect `EQUIVALENT` transitivity.
- **Acceptance Criteria**:
  - `AC-401.1`: Detects Action/Object mismatches (e.g. log change activities vs allocate storage capacity in `AU-4`) and downgrades `FULL_COVERAGE` to `PARTIAL_COVERAGE` or `NO_COVERAGE`.
  - `AC-401.2`: Detects incident lifecycle mismatch (roles across lifecycle in `MAS-7.7.3.c` vs incident reporting in `IR-6`) and prevents `EQUIVALENT` promotion.
  - `AC-401.3`: Enforces 1-to-1 uniqueness: only 1 candidate per MAS clause can hold `EQUIVALENT`.

### `STORY-COMP-402`: Retail Banking Customer Gap Classifier & Canonical MFA IA-2 Binding
- **Goal**: Identify retail banking customer mandates lacking NIST equivalents and guarantee canonical `NIST-IA-2` candidate for MFA.
- **Acceptance Criteria**:
  - `AC-402.1`: Customer communication mandates (e.g. notify customers of fraud) lacking federal system analogues are classified as `NO_COVERAGE` / `TRUE_REGULATORY_GAP`.
  - `AC-402.2`: `ClauseDecompounder` and `HybridCandidateRetriever` guarantee `NIST-IA-2` as candidate #1 for `MAS-14.2.1` (MFA login).

### `STORY-COMP-403`: Dynamic Bayesian Confidence Calibrator & Structured 4-Part Rationale Standard
- **Goal**: Implement continuous multi-signal confidence calculation and structured 4-part audit justification.
- **Acceptance Criteria**:
  - `AC-403.1`: Confidence varies continuously across edges ($0.65 \le \text{confidence} \le 0.98$) based on combined LLM, dense cosine, and lexical signals.
  - `AC-403.2`: Every committed crosswalk edge outputs a structured 4-part rationale (MAS Requirement, NIST Mechanism, Gap Analysis, Assurance Conclusion).
  - `AC-403.3`: Full production test run executes and outputs `docs/08-compare-upgrade/test-run-results-5.md` and `docs/07-update-parse/test-run-results-5.md`.
