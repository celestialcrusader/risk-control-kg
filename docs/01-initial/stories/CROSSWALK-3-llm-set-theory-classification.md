# CROSSWALK-3: LLM Set-Theory Classification

**Type**: Story
**Sprint**: Sprint 5
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, classification, crosswalk

---

## User Story

> As a **ML engineer**, I want an LLM classifier to assign set-theory relationship types (EQUIVALENT_TO, SUPERSET_OF, SUBSET_OF, INTERSECTS_WITH, NO_RELATIONSHIP) to control-obligation pairs, so that compliance mappings can be established with formal mathematical semantics.

---

## Context and Background

Per TRD Section 8.3, the LLM classifier must:
- Accept top-5 BGE-reranked candidates
- Classify each pair into one of 5 set-theory categories
- Output confidence score (0.0-1.0)
- Trigger dual-judge verification for all classifications

---

## Acceptance Criteria

1. Given a control-obligation pair, when `classify_relationship(control_text, obligation_text)` is called, then a relationship type is assigned
2. Given the classification, when confidence is evaluated, then it is output as a score (0.0-1.0)
3. Given the classification is SUPERSET_OF or EQUIVALENT_TO, then it is marked as "Requirement Met" with no gap
4. Given the classification is SUBSET_OF or INTERSECTS_WITH, then a gap is flagged for remediation
5. Given the classification is NO_RELATIONSHIP, then a critical gap is flagged for immediate action
6. Classification uses Mistral 8B (local Ollama) with temperature 0.2 for deterministic output

---

## Technical Notes

- Classification prompt:
  ```
  Classify the relationship between this control and obligation using set-theory semantics.
  
  Control Text:
  {{control_text}}
  
  Obligation Text:
  {{obligation_text}}
  
  Options:
  - EQUIVALENT_TO: Full 1:1 coverage
  - SUPERSET_OF: Control exceeds requirement (Requirement Met)
  - SUBSET_OF: Partial coverage (Gap Flagged)
  - INTERSECTS_WITH: Partial overlap with distinct goals (Kicks to Human Review)
  - NO_RELATIONSHIP: Control completely misses the mark (Critical Gap Flagged)
  
  Output JSON:
  {
    "relationship_type": "SUPERSET_OF",
    "confidence": 0.92,
    "rationale": "The control covers all obligation requirements and adds additional safeguards..."
  }
  ```
- Use Pydantic model for validation: `/backend/app/schemas/crosswalk_classification.py`
- Store classification results in PostgreSQL `control_obligation_mappings` table

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for LLM classification with sample pairs
- [ ] Integration tests for Ollama/Mistral API
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: CROSSWALK-2
- **Blocks**: CROSSWALK-4
