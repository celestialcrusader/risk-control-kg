# OBSERV-1: Langfuse Tracing Integration (Sprint 3)

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 3
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: observability, llm, tracing

---

## User Story

> As a **ML engineer**, I want Langfuse tracing integrated into the extraction pipeline, so that I can see exactly what prompts went in, what came out, and debug hallucinations with `trace_id`.

---

## Context and Background

The CTO review identified that leaving observability until Sprint 9 creates a black-box AI development risk. This story shifts Langfuse integration forward to Sprint 3, right alongside extraction.

Langfuse takes less than an hour to integrate via their Python SDK. When accuracy drops, ML engineers need the `trace_id` to see the exact prompt version that caused the hallucination.

---

## Acceptance Criteria

1. Given the Langfuse client is initialized, when an extraction prompt is sent, then a trace is created with `trace_id`
2. Given a trace exists, when the extraction output is logged, then the span includes the full prompt, completion, and token usage
3. Given an extraction fails (score < 0.80), when the failure is logged, then the trace includes the judge feedback and repair attempts
4. Langfuse dashboard accessible at `http://localhost:3000` with documented credentials
5. All LLM calls (extraction, judge, repair) are traced with consistent `trace_id` linkage
6. Production Langfuse instance configured with project scoping for `dev` and `prod` environments

---

## Technical Notes

- Langfuse Python SDK integration:
  ```python
  from langfuse import Langfuse
  from langfuse.decorators import observe
  
  langfuse = Langfuse()
  
  @observe()
  def extract_obligations(markdown_content):
      trace = langfuse.trace(name="extraction", metadata={"document_id": doc_id})
      # ... extraction logic
      return output
  
  @observe()
  def judge_extraction(obligation):
      trace = langfuse.trace(name="judge", parent_observation_id=extraction_span.id)
      # ... judge logic
      return score
  ```
- Traced events:
  - `extraction.started` / `extraction.completed`
  - `judge.started` / `judge.completed`
  - `repair.started` / `repair.completed`
  - `extraction.completed` (Kafka event)
- Cost tracking: Log token usage and estimated cost per trace
- Retention: 30 days for development, 1 year for production

---

## Definition of Done

- [ ] Langfuse SDK integrated into extraction pipeline
- [ ] All LLM calls traced with `trace_id`
- [ ] Langfuse dashboard running and accessible
- [ ] Documentation in `docs/01-initial/observability.md`
- [ ] Unit tests for trace creation

---

## Dependencies

- **Blocked by**: INFRA-1 (Langfuse service running)
- **Blocks**: EXTRACT-2 (judge scoring)
