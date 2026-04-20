# INGEST-5: Kafka Event Publishing

**Type**: Story
**Sprint**: Sprint 2
**Story Points**: 8
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, kafka, event-bus

---

## User Story

> As a **backend developer**, I want the document ingestion pipeline to publish status events to Kafka topics, so that downstream consumers (extraction, validation, export) can react to each stage of the pipeline.

---

## Context and Background

Per TRD Section 7.4, the Kafka event bus coordinates the ingestion pipeline. After each stage completes (upload, conversion, chunking, Bronze storage), an event is published to a specific topic so downstream services know when to process.

---

## Acceptance Criteria

1. Given a document is uploaded, when a `document.ingested` event is published, then consumers receive `{doc_id, hash, source_path, uploaded_at}`
2. Given a document is converted, when a `document.converted` event is published, then consumers receive `{doc_id, chunks, md5_hash, conversion_time_ms}`
3. Given a document is chunked, when a `document.chunked` event is published, then consumers receive `{doc_id, chunk_count, manifest_uri}`
4. Given a document is stored in Bronze, when a `document.bronzed` event is published, then consumers receive `{doc_id, bronze_uri, checksum}`
5. Given a Kafka broker is unavailable, when an event is published, then the error is logged and a retry with exponential backoff is attempted (up to 3 times)
6. Given a message cannot be delivered after retries, then it is sent to the DLQ topic with original payload and error information

---

## Definition of Done

- [x] Code written with TDD (tests first)
- [x] Unit tests for each event type and payload
- [x] Integration tests for Kafka publishing and DLQ
- [x] All acceptance criteria verified
- [x] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- **Blocked by**: INGEST-4
- **Blocks**: EXTRACT-1 (Sprint 3)

---

## Technical Notes

- Use the existing Kafka producer from INFRA-7
- Topics: `document.ingested`, `document.converted`, `document.chunked`, `document.bronzed`
- Implement retry with exponential backoff (base delay 1s, max 3 retries)
- DLQ topic: `document.dlq` — same schema as INFRA-7
- Events must include a `pipeline_stage` field for tracing
