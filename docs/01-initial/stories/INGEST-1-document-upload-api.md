# INGEST-1: MinIO Document Upload API

**Type**: Story
**Sprint**: Sprint 2
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, api, minio

---

## User Story

> As a **compliance officer**, I want to upload regulatory PDFs via a REST API, so that they are stored in MinIO with SHA-256 deduplication and registered in the audit log.

---

## Context and Background

Per TRD Section 7.1, the ingestion pipeline begins with document upload. The API must accept PDF files, calculate SHA-256 for deduplication, store in MinIO `source-regulations` bucket, register metadata in PostgreSQL audit_log, and trigger a Kafka event.

---

## Acceptance Criteria

1. Given a valid PDF file is uploaded via `POST /api/v1/documents/upload`, then the file is stored in MinIO with key `documents/{sha256_hash}/{filename}`
2. Given a duplicate file (same SHA-256) is uploaded, then the API returns HTTP 200 with message `{"status": "duplicate", "document_id": "doc-123"}` without re-uploading
3. Given a file is uploaded, when the audit_log table is queried, then a new row with `event_type='document.uploaded'` is created
4. Given a file is uploaded, when the Kafka topic `document.ingested` is consumed, then a message with `document_id`, `hash`, `source_path` is received
5. File size validation: files > 100MB are rejected with HTTP 413
6. Content-Type validation: only `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document` are accepted

---

## Definition of Done

- [ ] Code written with TDD (tests first)
- [ ] Unit tests for file upload and deduplication
- [ ] Integration tests for MinIO and Kafka
- [ ] All acceptance criteria verified
- [ ] OpenAPI documentation generated
- [ ] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- **Blocked by**: INFRA-1, INFRA-2, INFRA-3
- **Blocks**: INGEST-2

---

## Technical Notes

- Use FastAPI `UploadFile` for file handling
- SHA-256 calculation: `hashlib.sha256(file.read()).hexdigest()`
- MinIO client: `minio.Minio(endpoint, access_key, secret_key, secure=False)`
- Kafka producer: use the existing Kafka event bus from INFRA-7
- Include requestor_id in audit_log for traceability
- Content-Type validation must check both file extension AND MIME type
