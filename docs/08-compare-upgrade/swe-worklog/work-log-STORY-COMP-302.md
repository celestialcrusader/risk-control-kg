# SWE Work Log: STORY-COMP-302

## Story Metadata
- **Story ID**: `STORY-COMP-302`
- **Story Title**: Genuinely Decoupled Two-Dimensional Dual-Judge & Anti-Heuristic Gatekeeper
- **Sprint**: Sprint M (Audit-Defensible Regulatory Crosswalk Engine)
- **Assignee**: Software Engineering Agent
- **Status**: Completed (Green / Refactor)
- **Story Points**: 5 SP

---

## 1. Problem Addressed
In previous runs, when the LLM service was busy or restarting, the evaluator silently fell back to a bag-of-words keyword calculator that promoted mismatched pairs (`MAS-Annex B.B.1.a` ⟷ `NIST-PM-20`, `MAS-13.5.1` ⟷ `NIST-SA-20`) to `EQUIVALENT` with 0.90+ confidence. In addition, Dimension 2 was deterministically derived from Dimension 1.

## 2. Implementation Summary
1. **Anti-Heuristic Gatekeeper**:
   - The fallback heuristic is now strictly hard-capped at confidence $\le 0.30$ and labeled `UNVERIFIED_HEURISTIC_FALLBACK`.
   - Heuristic fallbacks are structurally barred from ever generating `EQUIVALENT` or `FULL_COVERAGE`.
2. **True Two-Dimensional Orthogonality**:
   - Removed all deterministic post-processing overrides.
   - Evaluator evaluates `semantic_relation` (scope overlap) and `assurance_coverage` (audit satisfaction) as independent variables.
3. **Resilient LLM Communication**:
   - Implemented retry with exponential backoff for vLLM completions to prevent unhandled dropped requests.

## 3. Test Execution Evidence
```bash
$ pytest tests/test_story_comp_302_anti_heuristic.py -v
========================== 2 passed in 0.93s ==========================
```
