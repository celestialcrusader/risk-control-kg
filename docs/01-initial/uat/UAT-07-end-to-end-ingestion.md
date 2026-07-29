# UAT-07: End-to-End Ingestion Pipeline

**Covers**: INGEST-1, INGEST-2, INGEST-3, INGEST-4, INGEST-5
**Type**: End-to-End Pipeline Test
**Effort**: ~15 minutes

## Objective

Verify the complete document ingestion pipeline: upload -> PDF-to-Markdown -> chunking -> Bronze storage -> Kafka event.

This is the primary UAT scenario for the ingestion pipeline. All other INGEST-* UATs can be run individually, but this validates the full flow.

## Prerequisites

- UAT-01 passes (all infrastructure healthy)
- MinerU or Marker model available for PDF conversion

## Steps

### Step 1: Upload a Regulatory PDF

```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@tests/test_data/sample_regulation.pdf")

echo "$RESPONSE" | python3 -m json.tool

# Extract document_id for later use
DOC_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['document_id'])")
HASH=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['hash'])")

echo "Document ID: $DOC_ID"
echo "Hash: $HASH"
```

**Expected**: Document uploaded successfully with status=uploaded.

### Step 2: Verify Document in MinIO (Bronze Layer)

```bash
docker exec $(docker-compose ps -q minio) mc ls rckg/source-regulations/documents/$HASH/
```

**Expected**: `sample_regulation.pdf` exists in the hashed directory.

### Step 3: Convert PDF to Markdown

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.pdf_to_markdown import convert_pdf_to_markdown

result = convert_pdf_to_markdown(
    "tests/test_data/sample_regulation.pdf",
    output_path="tests/test_data/output.md"
)
print(f"Status: {result['status']}")
print(f"Method: {result['method']}")
print(f"Output: {result['output_path']}")
PYEOF
```

**Expected**: Markdown file generated at `tests/test_data/output.md`.

### Step 4: Verify Markdown Content

```bash
echo "=== Markdown Output ==="
cat tests/test_data/output.md
echo ""
echo "=== Line Count ==="
wc -l tests/test_data/output.md
```

**Expected**: File contains structured Markdown with headings and regulation text.

### Step 5: Run Hybrid Chunking

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.hybrid_chunking import hybrid_chunk

with open("tests/test_data/output.md", "r") as f:
    markdown = f.read()

chunks = hybrid_chunk(markdown)

print(f"Generated {len(chunks)} chunks:")
for i, c in enumerate(chunks):
    print(f"  [{i+1}] method={c.get('method')} section={c.get('section')} text_len={len(c.get('text',''))}")

assert len(chunks) >= 1, "Must produce at least 1 chunk"
print("\nChunking passed.")
PYEOF
```

### Step 6: Store in Bronze Layer

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.bronze_layer import store_in_bronze_layer

with open("tests/test_data/output.md", "r") as f:
    markdown = f.read()

result = store_in_bronze_layer(
    markdown_content=markdown,
    document_id="test-doc",
    original_hash="test-hash",
)

print(f"Bronze storage result: {result}")
PYEOF
```

**Expected**: `staging_controls` table updated with the markdown content.

### Step 7: Verify Bronze Table

```bash
docker exec -it $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT id,
       raw_file_content->>'document_id' AS doc_id,
       length(raw_file_content->>'content') AS content_length,
       created_at
FROM staging_controls
ORDER BY created_at DESC
LIMIT 5;
"
```

**Expected**: Rows with content_length > 0, matching the markdown stored.

### Step 8: Verify Kafka Event

```bash
# Check that the event was published (from UAT-06)
docker exec $(docker-compose ps -q kafka) kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic document.ingested \
  --from-beginning \
  --timeout-ms 5000 | python3 -m json.tool
```

**Expected**: At least one event matching the document uploaded in Step 1.

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Upload | HTTP response | status=uploaded, document_id and hash returned |
| 2 | MinIO storage | File in bucket | File at `documents/<hash>/sample_regulation.pdf` |
| 3 | PDF conversion | Markdown generated | output.md exists with valid Markdown |
| 4 | Markdown content | File content | Headings and regulation text present |
| 5 | Chunking | Chunk count | At least 1 chunk with required fields |
| 6 | Bronze storage | `staging_controls` updated | Rows with content stored |
| 7 | Bronze table | Query result | content_length > 0 |
| 8 | Kafka event | Topic consumption | Event with correct document metadata |

## Verification

- [ ] Document uploads and returns valid document_id
- [ ] File exists in MinIO at the correct path
- [ ] PDF is converted to valid Markdown
- [ ] Hybrid chunking produces structured chunks
- [ ] Markdown content is stored in `staging_controls` (Bronze layer)
- [ ] Kafka event `document.ingested` contains correct document metadata

## Pass/Fail Criteria

- **PASS**: All 8 steps complete successfully with expected results
- **FAIL**: Any single step fails — note which step and the error

## Pipeline Flow Diagram

```
PDF File (test data)
    |
    v
[INGEST-1] POST /api/v1/documents/upload
    |-- SHA-256 hash & dedup
    |-- MinIO storage (source-regulations)
    |-- audit_log entry
    |-- Kafka event: document.ingested
    |
    v
[INGEST-2] PDF-to-Markdown conversion
    |-- MinerU (primary) / Marker (fallback)
    |-- Structured Markdown output
    |
    v
[INGEST-3] Hybrid chunking
    |-- Heading-based splits
    |-- Semantic splits (if embedding service available)
    |
    v
[INGEST-4] Bronze layer storage
    |-- Content stored in staging_controls table
    |-- JSONB metadata with document_id, hash, source_path
```
