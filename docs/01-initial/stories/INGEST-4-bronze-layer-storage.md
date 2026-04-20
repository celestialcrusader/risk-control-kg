# INGEST-4: Bronze Layer Storage

**Type**: Story
**Sprint**: Sprint 2
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, database, minio

---

## User Story

> As a **backend developer**, I want raw parsed chunks stored in a Bronze layer (immutable, append-only storage), so that the data pipeline has a reliable source of truth for reprocessing.

---

## Context and Background

Per TRD Section 8 (Three-Layer Vault), the Bronze layer stores raw, immutable copies of ingested data. This provides an audit trail and enables reprocessing from raw data without re-uploading.

---

## Acceptance Criteria

1. Given a chunked document, when `store_in_bronze(doc_id, chunks)` is called, then each chunk is persisted in MinIO `bronze-layer` bucket with key `bronze/{doc_id}/{chunk_id}.json`
2. Given a chunk is stored in Bronze, then a `staging_controls` row is created with `event_type='bronze.store'` and the raw JSON content
3. Given a chunk is already in Bronze (same doc_id), then the system skips duplicate storage
4. Given the Bronze layer is queried, then all entries are append-only — no modifications or deletions are allowed
5. Given a document is stored in Bronze, then a checksum record is written to `staging_controls` with the hash of the raw content

---

## Definition of Done

- [x] Code written with TDD (tests first)
- [x] Unit tests for Bronze storage and deduplication
- [x] All acceptance criteria verified
- [x] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- **Blocked by**: INGEST-3
- **Blocks**: INGEST-5

---

## Technical Notes

- Use MinIO for immutable storage
- Create `staging_controls` rows via SQLAlchemy
- Implement dedup via `doc_id` lookup before inserting
- Store content hash alongside content for integrity verification
