# EXTRACT-2: LLM-as-Judge Extraction Quality Check

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, validation, judge

---

## User Story

> As a **ML engineer**, I want an LLM-as-Judge quality check that scores extracted obligations across metadata accuracy, legal definition alignment, and rule semantics, so that low-confidence extractions can be repaired or rejected.

---

## Context and Background

Per TRD Section 7.4 Stage 3 (Multi-Criteria Evaluation), the LLM-as-Judge must score:
1. **Metadata Accuracy**: Are `action_verb`, `subject_noun`, `clause_ref` correctly extracted?
2. **Legal Definition Alignment**: Does the obligation align with standard compliance terminology?
3. **Rule Semantics**: Is the intent of the obligation preserved without semantic loss?

Threshold: Score >= 0.80 passes; < 0.80 triggers iterative repair.

---

## Acceptance Criteria

1. Given an extracted obligation, when `judge_extraction(obligation)` is called, then a score (0.0-1.0) is returned for each criterion
2. Given all criteria scores are >= 0.80, when the judgment is evaluated, then the obligation passes with status `approved`
3. Given any criterion score is < 0.80, when the judgment is evaluated, then the obligation is flagged for repair with `reason` field explaining the failure
4. LLM-as-Judge uses Llama 3.1 8B (local Ollama) for evaluation
5. Judge output includes detailed feedback: what was wrong and how to fix it
6. Scores logged to Langfuse with `trace_id` for audit trail

---

## Technical Notes

- Judge prompt template:
  ```
  Evaluate the following extracted obligation for quality.
  Score each criterion from 0.0 to 1.0.
  
  Obligation: {{obligation_json}}
  Original Text: {{original_markdown}}
  
  Criteria:
  1. Metadata Accuracy: Are action_verb, subject_noun, clause_ref correct?
  2. Legal Definition Alignment: Does it align with compliance terminology?
  3. Rule Semantics: Is the intent preserved without loss?
  
  Output JSON:
  {
    "metadata_accuracy": 0.95,
    "legal_alignment": 0.90,
    "semantics": 0.88,
    "overall_score": 0.91,
    "status": "approved",
    "feedback": "Extraction is high quality."
  }
  ```
- Average the three criterion scores for `overall_score`
- Use Pydantic model for validation: `/backend/app/schemas/judge.py`

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for judge with sample obligations
- [ ] Integration tests for LLM judge API
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: EXTRACT-1
- **Blocks**: EXTRACT-3
