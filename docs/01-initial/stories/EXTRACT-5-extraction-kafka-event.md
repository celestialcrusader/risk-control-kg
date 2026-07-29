# EXTRACT-5: Extraction Kafka Event

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, kafka, event-driven

---

## User Story

> As a **system**, I want a Kafka event to be published after successful extraction, so that downstream pipelines (dual-judge validation, embedding) can react asynchronously.

---

## Context and Background

Per TRD Section 19.1, the `extraction.completed` topic is published when:
- Extraction finishes successfully
- Contains: `obligation_ids[]`, `document_id`, `extraction_scores[]`

This event triggers the dual-judge validation workflow.

---

## Acceptance Criteria

1. Given extraction completes successfully, when `publish_extraction_completed(document_id, obligation_ids, scores)` is called, then a message is published to `extraction.completed` topic
2. Given a message is published, when the Kafka topic is consumed, then the message has fields: `obligation_ids[]`, `document_id`, `extraction_scores[]`
3. Given the message is published, when Langfuse tracing is checked, then a trace with `event_type='extraction.completed'` is created
4. Message key is the `document_id` for partitioning
5. If extraction has any obligations in dead-letter queue, include `dlq_count` in the message
6. Message schema validated before publish

---

## Technical Notes

- Kafka message schema:
  ```json
  {
    "document_id": "doc-123",
    "obligation_ids": ["obl-1", "obl-2", "obl-3"],
    "extraction_scores": [0.92, 0.88, 0.95],
    "dlq_count": 0,
    "timestamp": "2026-04-13T10:00:00Z"
  }
  ```
- Use the same Kafka producer configured in INGEST-5
- Add Langfuse trace: `langfuse.trace(name="extraction.completed", ...)`

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for Kafka event publishing
- [ ] Integration tests for message consumption
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: EXTRACT-4
- **Blocks**: DUALJUDGE-1
