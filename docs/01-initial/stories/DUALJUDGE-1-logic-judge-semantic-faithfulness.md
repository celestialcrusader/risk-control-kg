# DUALJUDGE-1: Logic Judge (Semantic Faithfulness)

**Type**: Story
**Sprint**: Sprint 4
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, judge, semantic

---

## User Story

> As a **ML engineer**, I want a Logic Judge (Llama 3.1 70B) that evaluates semantic faithfulness of extracted obligations, so that obligations that lose intent during extraction are caught before graph commit.

---

## Context and Background

Per TRD Section 7.2 and Section 19.3, the Logic Judge must:
- Use Llama 3.1 70B (quantized, via vLLM)
- Evaluate: "Did the mapper lose the actual intent of the control?"
- Threshold: Score < 0.95 triggers human review
- Output: Semantic faithfulness score (0.0-1.0) + detailed feedback

---

## Acceptance Criteria

1. Given an obligation from Silver layer, when `logic_judge(obligation, original_text)` is called, then a semantic faithfulness score is returned
2. Given the obligation preserves the original intent, when judged, then the score is >= 0.95 and status is `approved`
3. Given the obligation loses intent, when judged, then the score is < 0.95 and status is `requires_human_review`
4. Logic Judge uses Llama 3.1 70B quantized model via vLLM API: `http://localhost:8000/v1/chat/completions`
5. Judge output includes detailed feedback explaining what was lost or distorted
6. Scores logged to Langfuse with traceability to extraction ID

---

## Technical Notes

- vLLM configuration:
  ```python
  vllm.LLM(
      model="/models/llama-3.1-70b-q4_0",
      tensor_parallel_size=1,
      gpu_memory_utilization=0.4
  )
  ```
- Judge prompt:
  ```
  Evaluate whether this extracted obligation preserves the semantic intent of the original regulatory text.
  
  Original Text:
  {{original_text}}
  
  Extracted Obligation:
  {{obligation_json}}
  
  Question: Did the extraction lose, distort, or add any semantic content?
  
  Output JSON:
  {
    "semantic_faithfulness_score": 0.97,
    "status": "approved",
    "feedback": "The extraction accurately preserves the intent of the original text."
  }
  ```
- Temperature: 0.1 for consistent judgment
- Use Pydantic model for output validation: `/backend/app/schemas/logic_judge.py`

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for Logic Judge with sample obligations
- [ ] Integration tests for vLLM/Llama API
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/dual-judge.md`

---

## Dependencies

- **Blocked by**: EXTRACT-5, INFRA-1
- **Blocks**: DUALJUDGE-2
