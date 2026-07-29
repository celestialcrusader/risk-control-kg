# UAT-05: Bronze Layer Storage in MinIO

**Covers**: INGEST-4
**Type**: Storage Verification Test
**Effort**: ~5 minutes

## Objective

Verify that chunked Markdown content is stored in the Bronze layer (MinIO `source-regulations` bucket) and that deduplication prevents duplicate storage.

## Prerequisites

- UAT-02 passes (document upload works)
- UAT-04 passes (you have generated Markdown chunks)

## Steps

### Step 1: Verify MinIO Bucket Exists

```bash
mc ls rckg/source-regulations/ 2>/dev/null || \
docker exec $(docker-compose ps -q minio) mc ls rckg/source-regulations/
```

**Expected**: Bucket listing shows uploaded documents under `documents/`.

### Step 2: Check Stored Files

```bash
mc tree rckg/source-regulations/ 2>/dev/null || \
docker exec $(docker-compose ps -q minio) mc tree rckg/source-regulations/
```

**Expected**: Directory structure like:
```
documents/
  <sha256>/
    sample_regulation.pdf
    sample_regulation.md
```

### Step 3: Verify File Content Retrieval

```bash
# Download the stored PDF back
mc cp rckg/source-regulations/documents/<sha256>/sample_regulation.pdf \
  /tmp/verified_upload.pdf

# Compare with original
diff /tmp/verified_upload.pdf tests/test_data/sample_regulation.pdf && \
  echo "Files match: content integrity verified"
```

### Step 4: Verify Deduplication

```bash
# Try uploading the same file again
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@tests/test_data/sample_regulation.pdf" | python3 -m json.tool
```

**Expected**: `{"status": "duplicate", ...}` — no new file is created in MinIO.

### Step 5: Verify Bronze Table (staging_controls)

```bash
docker exec -it $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT id, canonical_id, raw_file_content->>'filename' AS filename,
       raw_file_content->>'hash' AS hash,
       raw_file_content->>'source_path' AS source_path,
       created_at
FROM staging_controls
ORDER BY created_at DESC
LIMIT 10;
"
```

**Expected**: Rows with `raw_file_content` JSONB containing document metadata (filename, hash, source_path).

### Step 6: Test WORM Policy (Optional)

```bash
# Attempt to delete a stored file via MinIO API (should be blocked by WORM policy)
mc rm rckg/source-regulations/documents/<sha256>/sample_regulation.pdf 2>&1 || \
  echo "WORM policy enforced: delete rejected"
```

**Expected**: Delete operation is rejected (WORM policy active).

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Bucket exists | `mc ls` | `source-regulations` bucket visible |
| 2 | Files stored | `mc tree` | Documents under `documents/<sha256>/` |
| 3 | Content integrity | `diff` original vs downloaded | Files match exactly |
| 4 | Deduplication | Duplicate upload response | `status: duplicate`, no new file created |
| 5 | Bronze table | `staging_controls` query | Rows with correct JSONB metadata |
| 6 | WORM policy | Delete attempt | Operation rejected |

## Verification

- [ ] MinIO `source-regulations` bucket exists and contains uploaded files
- [ ] File structure follows `documents/<sha256>/<filename>` pattern
- [ ] Downloaded files match originals (content integrity)
- [ ] Duplicate uploads do not create new files in MinIO
- [ ] `staging_controls` table has rows with correct JSONB metadata

## Pass/Fail Criteria

- **PASS**: Steps 1-5 all succeed — files stored correctly, dedup works, Bronze table populated
- **FAIL**: Files missing from MinIO, content mismatch, or dedup not working

## Notes

- The WORM policy (Step 6) is optional — the primary Bronze layer requirement is correct storage and deduplication
- If the `rckg` MC alias is not configured, use the `docker exec` commands shown above
