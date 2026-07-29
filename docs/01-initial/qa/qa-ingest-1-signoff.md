# QA Sign-Off Report: INGEST-1 (MinIO Document Upload API)

**Story**: INGEST-1: MinIO Document Upload API
**Story Points**: 5
**Sprint**: Sprint 2
**Reviewer**: QA Engineer (Automated)
**Date**: 2026-04-20
**Files Reviewed**:
- `/home/zackchow/coding/rckg/backend/app/api/documents.py` (API router)
- `/home/zackchow/coding/rckg/backend/app/services/document_upload.py` (Service layer)
- `/home/zackchow/coding/rckg/backend/tests/test_infra_10_document_upload.py` (Test suite, 971 lines)
- `/home/zackchow/coding/rckg/backend/app/storage/__init__.py` (MinIO client interface)
- `/home/zackchow/coding/rckg/backend/app/models/__init__.py` (AuditLog model)

---

## Overall Status: FAIL_WITH_CONCERNS

---

## Acceptance Criteria Verification

### AC-1: MinIO storage with key `documents/{sha256_hash}/{filename}` -- PASS

**Evidence**:
- `document_upload.py` line 105: `key = f"documents/{hash_hex}/{filename}"`
- `test_minio_uploads_with_correct_key_format` (line 537) verifies the exact key format.
- `test_minio_uses_source_regulations_bucket` (line 568) confirms the bucket name.

The key is constructed correctly using SHA-256 hex digest as the hash component. The MinIO `upload_file` call passes the bucket, key, and content_type.

---

### AC-2: Duplicate files return HTTP 200 with `{"status": "duplicate", "document_id": "..."}` -- PASS

**Evidence**:
- `document_upload.py` lines 111-147: When `minio.file_exists()` returns True, the service looks up the existing audit row and returns `{"status": "duplicate", "document_id": ..., "hash": ..., "key": ...}`.
- If no existing audit row is found, a new document_id is generated via `uuid.uuid4()` and an audit log entry is created with `status: "duplicate"`.
- Tests: `test_dedup_returns_duplicate_status` (line 204), `test_duplicate_response_includes_document_id` (line 238).

The endpoint returns the dict from the service layer directly, resulting in HTTP 200. Correct per the AC.

---

### AC-3: Audit log row with `event_type='document.uploaded'` -- PASS

**Evidence**:
- `document_upload.py` lines 161-175: New uploads create `AuditLog(event_type="document.uploaded", ...)`.
- `document_upload.py` lines 126-139: Duplicate uploads also create an `AuditLog` entry with the same event type.
- `test_audit_log_created_on_upload` (line 272) asserts `added_obj.event_type == "document.uploaded"`.
- `test_audit_log_event_data_contains_hash` (line 305) verifies event_data includes hash, filename, document_id.

Both new and duplicate uploads create proper audit entries.

---

### AC-4: Kafka event on `document.ingested` topic -- PASS

**Evidence**:
- `document_upload.py` lines 178-199: On successful upload, publishes to `topic="document.ingested"` with `document_id`, `hash`, `source_path` in message value.
- `test_kafka_published_on_upload` (line 374) verifies the topic name.
- `test_kafka_event_contains_document_id`, `test_kafka_event_contains_hash`, `test_kafka_event_contains_source_path` all verify individual fields.
- `test_kafka_event_contains_source_path` (line 468) verifies `source_path` equals `documents/{hash}/{filename}`.
- `test_no_kafka_on_duplicate` (line 500) verifies Kafka is NOT published for duplicates.
- `test_kafka_failure_does_not_block_upload` (line 900) verifies resilience -- Kafka failure does not prevent upload.

Kafka handling is well-implemented with proper resilience semantics.

---

### AC-5: Files > 100MB rejected with HTTP 413 -- PASS (with a minor gap)

**Evidence**:
- `document_upload.py` line 33: `MAX_FILE_SIZE = 100 * 1024 * 1024` (100 MB).
- `document_upload.py` line 89: `if file_size > MAX_FILE_SIZE` raises `ValueError`.
- API layer catches `ValueError` and returns HTTP 413 (lines 103-104).
- `test_endpoint_rejects_over_100mb` (line 132) uploads 101 MB and verifies 413.

The threshold is strictly greater-than (`>`), so a file of exactly 100 MB is accepted. This is technically compliant with AC-5 ("files > 100MB rejected"). However, no test verifies the exact boundary: a 100 MB file should be accepted and 100 MB + 1 byte should be rejected.

---

### AC-6: Content-Type validation -- PASS (with a critical bug)

**Evidence**:
- `ALLOWED_CONTENT_TYPES` in `document_upload.py` lines 26-30 contains exactly the three required MIME types.
- Tests `test_accepts_pdf`, `test_accepts_word_2003`, `test_accepts_word_2007` verify all three types.
- `test_endpoint_rejects_unsupported_content_type` (line 76) uploads `text/plain` and verifies 415.
- `test_endpoint_rejects_image_upload` (line 100) uploads `image/png` and verifies 415.

**Critical Bug Found (BLOCKER)**: The `_detect_content_type` helper in the API layer infers content type from file extension when the client omits the Content-Type header. However, the API layer validates the *inferred* content type and raises 415, but then passes the *original* `UploadFile` object (with its unchanged `.content_type` attribute) to the service layer. If a client sends a file with no Content-Type header:

1. API layer infers the type from extension (e.g., `.pdf` -> `application/pdf`)
2. Validates the inferred type -- passes
3. Passes the unchanged `file.content_type` (still `None` or empty) to the service layer
4. Service layer sees empty content type, which is NOT in `ALLOWED_CONTENT_TYPES`, raises `ValueError`

In the test environment, `TestClient` always provides a Content-Type header based on the multipart form data, so this bug is not caught by the test suite. It only manifests in production when a client sends a file with an empty/missing Content-Type header.

**Fix applied in this review**: Added content-type propagation in the API layer after validation:
```python
if file.content_type != detected_ct:
    file.content_type = detected_ct
```

---

## Test Coverage Assessment

**Total test count**: 27 tests across 9 test classes

| Test Class | Tests | Coverage |
|---|---|---|
| `TestContentValidation` | 6 | AC-6: Good MIME type coverage |
| `TestFileSizeValidation` | 3 | AC-5: Covers over-limit; missing exact-boundary test |
| `TestSHA256Deduplication` | 3 | AC-1, AC-2: Key format and dedup behavior |
| `TestAuditLog` | 3 | AC-3: New and duplicate audit entries |
| `TestKafkaEvent` | 5 | AC-4: Topic, all payload fields, duplicate exclusion, resilience |
| `TestMinIOUpload` | 2 | AC-1: Key format and bucket name |
| `TestEndpointIntegration` | 5 | Full endpoint: success, duplicate, empty file, missing field |
| `TestDocumentUploadServiceUnit` | 4 | SHA-256 determinism, response fields, requestor_id |
| `TestEdgeCases` | 5 | Word docs, CSV rejection, Kafka resilience, file_exists guard, 64-char hex |

### Strengths
- Comprehensive test coverage across all acceptance criteria.
- Tests verify actual values (not just status codes). E.g., Kafka message contains exact `source_path`, audit log `event_type` matches, hash is 64-char hex string.
- Good mix of unit tests (mocking MinIO, Kafka, DB) and integration tests (TestClient with full router).
- Edge cases covered: empty file, missing file field, Kafka failure resilience, file_exists prevents duplicate upload.

### Weaknesses
1. **Test `test_100_mb_file_rejected`** (line 126) tests the constant value, not the endpoint behavior at the 100 MB boundary. The docstring says "File exactly 100 MB is rejected" but the code accepts files exactly at 100 MB (threshold is strictly greater-than). The test name is misleading.
2. **No test for the content-type propagation bug**: Since `TestClient` always provides a Content-Type header, the gap between API-layer validation and service-layer reception was never tested.
3. **Mock chain fragility**: DB mocks use `.filter.return_value.filter.return_value` which works for the current SQLAlchemy two-filter chain but would silently break if the query pattern changed. No test asserts on the actual SQL/query structure.
4. **Unused `to_dict` mocks**: Several tests configure `mock_audit.to_dict.return_value` but the service code reads `.id` directly, never calling `.to_dict()`. These are dead code in tests.

---

## Issues Found

### BLOCKER

**1. Content-type propagation gap** (API router -> service layer)

When a client sends a file without a Content-Type header, the API layer's `_detect_content_type` correctly infers the type and validates it. However, the original `UploadFile.content_type` attribute is not updated, so the service layer receives the empty/None value and rejects the upload.

**Location**: `documents.py` line 96 (before passing to `upload_document`)
**Fix applied**: Added `file.content_type = detected_ct` after validation passes.

---

### MAJOR

**2. Misleading test `test_100_mb_file_rejected`** (test file, line 126)

The test name and docstring say "File exactly 100 MB is rejected" but the code uses strictly greater-than (`file_size > MAX_FILE_SIZE`), so 100 MB is accepted. The test only asserts `MAX_FILE_SIZE == 100 * 1024 * 1024` -- a constant value check, not an endpoint behavior test.

**Recommendation**: Rename the test to `test_max_file_size_constant`, and add a new test `test_100_mb_file_accepted` that uploads a 100 MB file via the endpoint and verifies it is not rejected with 413.

**3. Duplicate audit logging with new UUID** (service layer, lines 121-147)

When a duplicate is detected and no existing audit row is found, the service creates a new `AuditLog` with a fresh `uuid.uuid4()` as the document_id. The returned `document_id` in the response does not match the original upload's document_id. Downstream consumers might expect the document_id to be the same as the original upload.

**Recommendation**: Consider whether duplicate uploads should return the original upload's document_id (from the MinIO key or a content-addressable lookup) rather than generating a new one.

**4. No transaction rollback on audit failure** (service layer, lines 158-175)

The MinIO upload (line 151) happens before the audit log entry is committed. If `session.add()` fails (e.g., DB connection loss), the file is already in MinIO but has no audit trail. The DB session context manager handles commit/rollback, but the failure path leaves an orphaned MinIO object.

**Recommendation**: Write the audit log entry first (before MinIO upload), or use a two-phase approach where both operations are tracked and a reconciliation process handles orphans.

---

### MINOR

**5. Unused `calculate_sha256` function in upload flow** (service layer, line 36)

The `calculate_sha256` function is defined and tested but never called in the actual `upload_document` flow. The hash is calculated inline at line 104 via `hashlib.sha256(content).hexdigest()`. The standalone function exists for testability but is not wired up. Either wire it up or remove it to avoid confusion.

**6. Typo: `any` instead of `Any`** (service layer, line 56)

The parameter type annotation uses Python's built-in `any` instead of `typing.Any`. This was a typo. Fixed during this review.

**7. Inconsistent event_data fields** (service layer, lines 128-135 vs 164-171)

New uploads store `content_type` in `event_data` but duplicate uploads do not. This creates inconsistent audit trail format.

**Recommendation**: Add `content_type` to duplicate upload event_data for consistency.

**8. Unused `to_dict` mock configurations** (test file, multiple lines)

Tests configure `mock_audit.to_dict.return_value = {...}` but the service code never calls `.to_dict()` on the AuditLog object. These mock configurations are unnecessary dead code.

---

### NIT

**9. Event type string repetition**

`"document.uploaded"` appears in the model enum (`EventType.DOCUMENT_UPLOADED`), the service layer, and every test. A shared constant in a module like `app.core.constants` would reduce risk of typos.

**10. Large test file** (971 lines, 27 tests)

The test file could benefit from fixture-based parametrization to reduce duplication between the many similar mock setups.

---

## Files Modified During This Review

1. `/home/zackchow/coding/rckg/backend/app/api/documents.py` -- Added content-type propagation after validation
2. `/home/zackchow/coding/rckg/backend/app/services/document_upload.py` -- Fixed `any` to `Any` type import

---

## Recommendation

**FAIL_WITH_CONCERNS -- requires fixes before merge.**

The core implementation is solid and all acceptance criteria are addressed in the code. The test suite is comprehensive and well-structured. However:

1. **The content-type propagation bug is a real production risk.** If any client uploads a file without a Content-Type header, the upload will fail after passing API-layer validation. A fix has been applied.

2. **The misleading boundary test** (`test_100_mb_file_rejected`) should be renamed and the behavior should be explicitly tested for the 100 MB boundary.

3. **Consider adding an integration test** that exercises the full upload flow without mocking the DB session, which would have caught the content-type propagation bug.

**Post-merge recommendations**:
- Wire up the standalone `calculate_sha256` function in the upload flow (or remove it).
- Add `content_type` to duplicate upload event_data for consistency.
- Plan for the transaction ordering issue (MinIO upload before audit log) to be addressed when a reconciliation framework is built.
