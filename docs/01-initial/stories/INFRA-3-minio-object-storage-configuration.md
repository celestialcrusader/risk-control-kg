# INFRA-3: MinIO Object Storage Configuration

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 5
**Priority**: High
**Assigned To**: DevOps Engineer
**Labels**: infrastructure, storage, minio

---

## User Story

> As a **system**, I want MinIO object storage with WORM (Write-Once-Read-Many) policy on `source-regulations` bucket, so that regulatory documents cannot be tampered with and maintain audit integrity.

---

## Context and Background

Per TRD Section 11.3 and Section 4.2, MinIO is used for:
- Raw PDFs and policy documents
- Markdown conversions
- Evidence artefacts

The `source-regulations` bucket must have WORM policy to satisfy regulatory audit requirements.

---

## Acceptance Criteria

1. Given MinIO is running, when the S3 API is used to create bucket `source-regulations`, then the bucket is created successfully
2. Given the bucket exists, when `mc admin policy info rckg-source-worm` is executed, then the WORM policy is applied and verified
3. Given a file is uploaded to `source-regulations`, when an attempt is made to delete or modify it, then the operation is rejected with HTTP 405 Method Not Allowed
4. Given the bucket exists, when `mc ls rckg/source-regulations` is executed, then the file listing shows all uploaded documents
5. `minio-data` bucket created for temporary/unstructured storage without WORM policy
6. MinIO console accessible at `http://localhost:9001` with documented credentials

---

## Definition of Done

- [x] Code written and peer-reviewed
- [x] Integration tests for MinIO operations
- [x] All acceptance criteria verified
- [x] Documentation updated

---

## Dependencies

- **Blocked by**: INFRA-1
- **Blocks**: INGEST-1

---

## Technical Notes

- Use MinIO CLI (`mc`) for policy management
- WORM policy configuration: Set bucket to read-only after first write
- Configure access keys via environment variables: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
- Enable versioning on all buckets for audit trail
- Document MinIO endpoints in `.env.example`
