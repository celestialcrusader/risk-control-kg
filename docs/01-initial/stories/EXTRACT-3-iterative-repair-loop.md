# EXTRACT-3: Iterative Repair Loop

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 8
**Priority**: Medium
**Assigned To**: ML/AI Engineer
**Labels**: backend, llm, repair, extraction

---

## User Story

> As a **ML engineer**, I want an iterative repair loop that re-processes low-confidence extractions with upstream context corrections, so that the system can automatically fix most quality issues without human intervention.

---

## Context and Background

Per TRD Section 7.4 Stage 4 (Iterative Repair), the repair loop must:
1. Receive feedback from LLM-as-Judge on failed extractions
2. Augment the extraction prompt with context from parent sections
3. Re-run extraction with corrected prompt
4. Repeat up to 3 times before escalating to dead-letter queue

---

## Acceptance Criteria

1. Given a failed extraction (score < 0.80), when `repair_extraction(obligation, feedback)` is called, then the extraction is re-run with feedback incorporated into the prompt
2. Given the repaired extraction, when it is re-judged, then if score >= 0.80, the status is updated to `approved`
3. Given 3 repair attempts all fail, when the third judgment is received, then the obligation is moved to dead-letter queue with `reason: max_repair_attempts_exceeded`
4. Each repair attempt logs the feedback and new extraction to Langfuse
5. Context augmentation: Include parent section heading and 2 preceding paragraphs in the repair prompt
6. Maximum 3 repair attempts per obligation (configurable via environment variable)

---

## Technical Notes

- Repair prompt augmentation:
  ```
  Context from parent section:
  {{parent_section_heading}}
  {{preceding_paragraphs}}
  
  Previous extraction failed because: {{judge_feedback}}
  
  Re-extract with this context.
  ```
- Dead-letter queue: Store in PostgreSQL `extraction_dlq` table with fields: `obligation_id`, `original_text`, `feedback`, `attempt_count`, `timestamp`
- Use Temporal workflow for repair loop: `extraction_validation_workflow` with signal for retry

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for repair loop with sample failures
- [ ] Integration tests for iterative extraction
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: EXTRACT-2
- **Blocks**: EXTRACT-4
