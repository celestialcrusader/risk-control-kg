# INGEST-3: Hybrid Chunking Strategy

**Type**: Story
**Sprint**: Sprint 2
**Story Points**: 8
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, nlp, chunking

---

## User Story

> As a **backend developer**, I want documents split into semantically-meaningful chunks using a hybrid strategy, so that vector embeddings and graph traversal can operate on the right granularity of text.

---

## Context and Background

Per TRD Section 7.3, raw Markdown from conversion is too large for effective retrieval. A hybrid chunking strategy that respects heading boundaries, paragraph breaks, and table cells produces chunks that are semantically coherent.

---

## Acceptance Criteria

1. Given a Markdown document, when `chunk_document(markdown, doc_id)` is called, then chunks are split at heading boundaries (H1-H6)
2. Given a chunk is created, each chunk has metadata: `doc_id`, `chunk_index`, `heading_path`, `char_count`, `table_ref`
3. Given a Markdown document contains tables, each table is chunked as a separate unit with a `table_ref` metadata field
4. Given a document is chunked, when chunks are returned, then each chunk's char count is between `min_chunk_size` (default 100) and `max_chunk_size` (default 1000)
5. Given a document is chunked, then chunks are stored in MinIO `markdown-conversions` bucket with key `chunks/{doc_id}/{doc_id}_chunk_{N}.md`
6. Given a chunked document, then a manifest JSON is stored with key `chunks/{doc_id}/manifest.json` listing all chunks and their metadata

---

## Definition of Done

- [x] Code written with TDD (tests first)
- [x] Unit tests for chunking with sample Markdown documents
- [x] All acceptance criteria verified
- [x] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- **Blocked by**: INGEST-2
- **Blocks**: INGEST-4

---

## Technical Notes

- Parse Markdown headings using regex `^#{1,6}\s` to determine chunk boundaries
- Detect tables using `|` pipe syntax
- Configurable `min_chunk_size` and `max_chunk_size` via environment variables
- Store chunk manifest as JSON for fast lookup
