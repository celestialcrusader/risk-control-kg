# Parsing Pipeline: MinerU + Marker Fallback

## Overview

The RCKG parsing pipeline converts uploaded PDF documents into structured Markdown that preserves semantic information for downstream LLM extraction and embedding. The pipeline uses a primary/fallback strategy with MinerU as the primary parser and Marker as a fallback when MinerU confidence falls below a threshold.

## Architecture

```
PDF Upload (INGEST-1)
        |
        v
+------------------------+
|   PDF-to-Markdown      |
|   (INGEST-2)           |
|                        |
|  1. MinerUConverter    |
|     (primary parser)   |
|                        |
|  2. Confidence Check   |
|     threshold: 0.85    |
|                        |
|  3. MarkerFallback     |
|     (if confidence     |
|      < 0.85)           |
+------------------------+
        |
        v
MinIO storage (markdown-conversions bucket)
        |
        v
Hybrid Chunking (INGEST-3)
```

## Primary Parser: MinerU

MinerU is the primary PDF parsing tool selected in the TRD Section 7.2. It preserves:

- **Heading hierarchies (H1-H6)**: All heading levels are extracted with their text, level, and position.
- **Multi-column layouts**: Reading order is maintained across columns.
- **Nested and borderless tables**: Tables are rendered in GitHub-Flavored Markdown (GFM) pipe-delimited syntax.
- **Footnotes**: Footnotes are captured with their id, text, anchor, and parent section.

### API

```python
from app.services.pdf_to_markdown import MinerUConverter, convert_pdf_to_markdown

# Direct converter usage
converter = MinerUConverter()
result = converter.convert("/path/to/document.pdf")

# Top-level function with Marker fallback
result = convert_pdf_to_markdown(
    pdf_path="/path/to/document.pdf",
    document_id="doc-12345",
)
```

### Result Structure

Each conversion result contains:

| Field               | Type   | Description                                    |
|---------------------|--------|------------------------------------------------|
| `document_id`       | `str`  | Unique document identifier                     |
| `markdown_uri`      | `str`  | MinIO key for the stored Markdown file         |
| `confidence_score`  | `float`| Conversion confidence (0.0 to 1.0)             |
| `conversion_time_ms`| `int`  | Total conversion time in milliseconds          |
| `heading_count`     | `int`  | Number of headings extracted                   |
| `table_count`       | `int`  | Number of tables extracted                     |
| `footnotes_count`   | `int`  | Number of footnotes extracted                  |
| `converter_used`    | `str`  | `"mineru"` or `"marker"`                       |

## Fallback Parser: Marker

When MinerU's confidence score is below the threshold of **0.85**, the Marker library (`marker_single`) is invoked automatically. Marker produces semantically equivalent output with better reliability on complex PDF layouts.

### Fallback Trigger

```
MinerU confidence >= 0.85  ->  Use MinerU output
MinerU confidence <  0.85  ->  Invoke Marker, use Marker output
```

The threshold is inclusive: a confidence of exactly 0.85 does NOT trigger fallback (only strictly less than).

## Storage

Converted Markdown files are stored in MinIO:

- **Bucket**: `markdown-conversions`
- **Key pattern**: `conversions/{document_id}/{document_id}.md`
- **Content-Type**: `text/markdown`
- **Encoding**: UTF-8

## Input Validation

The pipeline validates inputs before processing:

1. **document_id**: Must be non-empty and match `^[\w][\w.-]*$`. Characters like `/`, `..`, and other path traversal sequences are rejected.
2. **file extension**: Only `.pdf` files are accepted.

### Path Traversal Protection

Invalid document IDs include:

- `../etc/passwd` (parent directory traversal)
- `doc/sneaky` (forward slash)
- Empty strings or `None`
- Any character outside `[a-zA-Z0-9_.-]` (starting with an alphanumeric)

## Error Handling

- **FileNotFoundError**: Raised when the PDF file does not exist at the given path.
- **ValueError**: Raised for invalid `document_id` or non-PDF file extensions.
- **RuntimeError**: Wraps MinerU or Marker library failures. The original exception is chained via `raise ... from exc`.

## Configuration

| Variable              | Default                        | Description                   |
|-----------------------|--------------------------------|-------------------------------|
| `CONFIDENCE_THRESHOLD`| `0.85`                         | Min confidence to use MinerU  |
| `MINIO_ENDPOINT_URL`  | `http://localhost:9000`        | MinIO server URL              |
| `MINIO_ACCESS_KEY`    | `rckg_admin`                   | MinIO access key              |
| `MINIO_SECRET_KEY`    | `rckg_secret_password`         | MinIO secret key              |
| `MINIO_REGION`        | `us-east-1`                    | AWS region                    |

## Performance

- Target: Under 30 seconds per document (< 100 pages)
- Conversion time is tracked and returned in `conversion_time_ms`
- In production, consider wrapping conversion in an async task (Celery/Temporal) to avoid API blocking

## Downstream Integration

The Markdown output feeds into:

1. **INGEST-3 (Hybrid Chunking)**: Splits Markdown at heading boundaries and applies semantic splitting via BGE-M3 embeddings.
2. **EMBED-1 (Embedding)**: Generates vector embeddings for chunks and stores them in Qdrant.
3. **INGEST-4 (Bronze Layer)**: Stores raw artifacts in MinIO for auditability.
