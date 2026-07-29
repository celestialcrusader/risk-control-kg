# DUALJUDGE-2: Technical Judge (Parameter Precision)

**Type**: Story
**Sprint**: Sprint 4
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, judge, technical

---

## User Story

> As a **ML engineer**, I want a Technical Judge (DeepSeek-R1 72B) that audits technical/mathematical accuracy of extracted parameters, so that incorrect numerical or parameter values are caught before graph commit.

---

## Context and Background

Per TRD Section 7.2 and Section 19.3, the Technical Judge must:
- Use DeepSeek-R1 72B (quantized, via vLLM)
- Evaluate: "Does 'Hourly' properly reconcile to '3600 seconds' in OSCAL parameters?"
- Threshold: Score must be 1.0 (exact match) - any error triggers human review
- Output: Technical accuracy score (0.0-1.0) + detailed feedback

---

## Acceptance Criteria

1. Given an obligation with parameters (e.g., time frequencies, numerical thresholds), when `technical_judge(obligation)` is called, then a technical accuracy score is returned
2. Given all parameters are technically correct, when judged, then the score is 1.0 and status is `approved`
3. Given any parameter is technically incorrect, when judged, then the score is < 1.0 and status is `requires_human_review`
4. Technical Judge uses DeepSeek-R1 72B quantized model via vLLM API
5. Judge output includes specific parameter errors and corrections
6. Scores logged to Langfuse with traceability to extraction ID

---

## Technical Notes

- Technical Judge prompt:
  ```
  Evaluate whether all technical parameters in this obligation are accurate and properly formatted.
  
  Extracted Obligation:
  {{obligation_json}}
  
  Criteria:
  1. Time frequencies (e.g., "Hourly" = 3600 seconds)
  2. Numerical thresholds (e.g., "> 100" is properly formatted)
  3. Date formats (e.g., ISO 8601)
  4. OSCAL parameter compatibility
  
  Output JSON:
  {
    "technical_accuracy_score": 1.0,
    "status": "approved",
    "feedback": "All parameters are technically accurate.",
    "parameter_errors": []
  }
  ```
- Use strict JSON parsing with error handling
- If any parameter errors are found, set score to 0.0
- Log all parameter checks to Langfuse

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for Technical Judge with sample obligations
- [ ] Integration tests for vLLM/DeepSeek API
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: DUALJUDGE-1
- **Blocks**: DUALJUDGE-3
