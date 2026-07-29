# UAT-02: Document Upload with Dedup and Validation

**Covers**: INGEST-1
**Type**: API Functional Test
**Effort**: ~10 minutes

## Objective

Verify the document upload endpoint accepts valid PDF/Word files, rejects invalid types, detects duplicates, and enforces file size limits.

## Prerequisites

- UAT-01 passes (all infrastructure healthy)
- A sample PDF file for testing

## Test Data Setup

```bash
# Create a small test PDF if you don't have one
mkdir -p tests/test_data
python3 -c "
import weasyprint
html = '<html><body><h1>Sample Regulation</h1><p>The organization must implement access controls.</p></body></html>'
weasyprint.HTML(string=html).write_pdf('tests/test_data/sample_regulation.pdf')
"
```

## Steps

### Step 1: Upload a Valid PDF

```bash
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@tests/test_data/sample_regulation.pdf" | python3 -m json.tool
```

**Expected**: HTTP 200 with:
```json
{
  "status": "uploaded",
  "document_id": "<uuid>",
  "hash": "<64-char sha256 hex>",
  "key": "documents/<sha256>/sample_regulation.pdf"
}
```

### Step 2: Upload the Same File Again (Duplicate Detection)

```bash
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@tests/test_data/sample_regulation.pdf" | python3 -m json.tool
```

**Expected**: HTTP 200 with:
```json
{
  "status": "duplicate",
  "document_id": "<same UUID as Step 1>",
  "hash": "<same hash as Step 1>",
  "key": "documents/<sha256>/sample_regulation.pdf"
}
```

### Step 3: Reject Non-PDF/Word Files (Content-Type Validation)

```bash
echo "not a document" > /tmp/readme.txt
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@/tmp/readme.txt" -F "filename=readme.txt"
echo ""
```

**Expected**: HTTP 415 with detail mentioning unsupported content type.

### Step 4: Reject Empty File

```bash
touch /tmp/empty.pdf
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@/tmp/empty.pdf" -F "filename=empty.pdf"
echo ""
```

**Expected**: HTTP 400 with detail about empty file.

### Step 5: Verify Audit Log Entry

```bash
docker exec -it $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT event_type,
       event_data->>'filename' AS filename,
       event_data->>'hash' AS hash,
       event_data->>'status' AS status,
       event_data->>'document_id' AS document_id
FROM audit_log
ORDER BY timestamp DESC
LIMIT 5;
"
```

**Expected**: At least 2 rows — one `uploaded`, one `duplicate`.

## Expected Results Summary

| # | Step | HTTP Status | Expected Response |
|---|------|-------------|-------------------|
| 1 | Valid PDF upload | 200 | `{"status": "uploaded", "document_id": "...", ...}` |
| 2 | Duplicate upload | 200 | `{"status": "duplicate", "document_id": "<same as #1>", ...}` |
| 3 | Non-PDF/Word rejection | 415 | `{"detail": "Unsupported content_type: ..."}` |
| 4 | Empty file rejection | 400 | `{"detail": "File is empty: ..."}` |
| 5 | Audit log | 200 (PSQL) | 2 rows: 1 uploaded, 1 duplicate |

## Verification

- [ ] Valid PDF uploads successfully with correct response structure
- [ ] Duplicate file returns same document_id and status=duplicate
- [ ] Non-PDF/Word content type is rejected with HTTP 415
- [ ] Empty file is rejected with HTTP 400
- [ ] Audit log contains entries for both successful upload and duplicate attempt

## Pass/Fail Criteria

- **PASS**: All 5 steps return expected HTTP status codes and response structures
- **FAIL**: Any step returns unexpected status code or missing fields in response
