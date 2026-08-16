# Sprint Plan: Definitive Audit Explainability & TEVV Calibration (Sprint O)

**Sprint ID:** `SPRINT-COMP-O`  
**Goal:** Eliminate mail-merge boilerplate rationales with dynamic per-edge element extraction, calibrate containment directionality (e.g. `MAS-7.6.1` $\subseteq$ `NIST-AC-5`), prune superficial `OVERLAPS`, reconcile gap integrity reporting, and showcase canonical MFA `NIST-IA-2` in the final audit document.  
**Estimated Velocity:** 15 Story Points  
**Target Completion Date:** 2026-08-16  
**Execution Workflow:** `/tdd-story-execution` (Red-Green-Refactor + Independent QA Review)  

---

## 1. Executive Summary & Expert Audit Remediation

Based on expert audit review findings on `test-run-results-5.md`, Sprint O delivers the final polish for audit explainability and data integrity:
1. **Dynamic Granular Element Extractor & Zero-Template 4-Part Rationale**:
   - Updates the Dual-Judge prompt and schema to extract pair-specific `covered_mechanisms`, `missing_gaps`, and `comparative_justification`.
   - Completely removes static boilerplate fallback strings (`[Core technical controls...]` and `[Framework-specific reporting...]`) from `format_structured_rationale`.
2. **Directional Containment Calibration**:
   - Corrects containment directionality: narrow domain-specific requirements (e.g. `MAS-7.6.1` software release separation of duties) mapped to broad enterprise controls (`NIST-AC-5`) are strictly assigned `SUBSET_OF` ($A \subseteq B$).
3. **Superficial `OVERLAPS` Pruning Gate**:
   - Prunes non-substantive edges (e.g. `MAS-7.2.2` configuration review vs `NIST-SC-8` transmission encryption) where `AssuranceCoverage == NO_COVERAGE` and actionable mechanism overlap is absent.
4. **Reconciled Gap Reporting & Canonical Baseline Showcase**:
   - Reconciles Section C into: **Category A: Unmatched Obligations (0 candidates)** vs **Category B: Retail Consumer Mandates (`NO_COVERAGE`)**.
   - Explicitly showcases canonical baseline mappings (`MAS-14.2.1` MFA $\leftrightarrow$ `NIST-IA-2`, `MAS-7.6.1` $\leftrightarrow$ `NIST-AC-5`, `MAS-1.3.a` $\leftrightarrow$ `NIST-RA-3`) in Section B.

---

## 2. Sprint Backlog & Story Tickets

| Story ID | Title | Estimate | Status | Owner |
| :--- | :--- | :--- | :--- | :--- |
| `STORY-COMP-501` | Dynamic Granular Element Extractor & Zero-Template 4-Part Rationale Engine | 5 SP | **Done (QA Approved)** | SWE / QA |
| `STORY-COMP-502` | Directional Containment Calibrator & Superficial OVERLAPS Pruning Gate | 5 SP | **Done (QA Approved)** | SWE / QA |
| `STORY-COMP-503` | Reconciled Gap Integrity & Canonical MFA IA-2 Sample Showcase | 5 SP | **Done (QA Approved)** | SWE / QA |

---

## 3. Detailed Story Specifications

### `STORY-COMP-501`: Dynamic Granular Element Extractor & Zero-Template 4-Part Rationale Engine
- **Goal**: Ensure every crosswalk edge has unique, dynamic covered mechanisms and missing gaps extracted by the LLM without static template fallbacks.
- **Acceptance Criteria**:
  - `AC-501.1`: `TwoDimensionalEvaluation` model contains `covered_mechanisms` and `missing_gaps`.
  - `AC-501.2`: `format_structured_rationale` rejects static template placeholders and populates dynamic elements.

### `STORY-COMP-502`: Directional Containment Calibrator & Superficial OVERLAPS Pruning Gate
- **Goal**: Calibrate containment direction ($A \subseteq B$ vs $A \supseteq B$) and prune meaningless `OVERLAPS` + `NO_COVERAGE` edges.
- **Acceptance Criteria**:
  - `AC-502.1`: `MAS-7.6.1` $\leftrightarrow$ `NIST-AC-5` is evaluated as `SUBSET_OF`.
  - `AC-502.2`: `MAS-7.2.2` (config review) $\leftrightarrow$ `NIST-SC-8` (transmission encryption) is pruned to `NONE` (dropped).

### `STORY-COMP-503`: Reconciled Gap Integrity & Canonical MFA IA-2 Sample Showcase
- **Goal**: Reconcile Section C reporting categories and showcase canonical baseline controls in Section B samples.
- **Acceptance Criteria**:
  - `AC-503.1`: Section C differentiates between 0 candidates retrieved vs retail consumer mandates.
  - `AC-503.2`: `MAS-14.2.1` $\leftrightarrow$ `NIST-IA-2` is guaranteed a prominent spot in Section B.
  - `AC-503.3`: Produces `docs/08-compare-upgrade/test-run-results-6.md` and `docs/07-update-parse/test-run-results-6.md`.
