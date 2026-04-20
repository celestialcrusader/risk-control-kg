# INGEST-2: MinerU PDF-to-Markdown Conversion

**Type**: Story
**Sprint**: Sprint 2
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: backend, pdf, mineru, nlp

---

## User Story

> As a **backend developer**, I want MinerU to convert uploaded PDFs to structured Markdown with preserved heading hierarchies and tables, so that downstream LLM extraction can operate on clean, semantically-rich text.

---

## Context and Background

Per TRD Section 7.2, MinerU is the primary PDF parsing tool. It must preserve heading hierarchies, multi-column layouts, nested tables, and footnotes. A Marker fallback is available when MinerU confidence is below threshold.

---

## Acceptance Criteria

1. Given a PDF file is passed to `convert_pdf_to_markdown(pdf_path)`, then the output Markdown preserves the heading hierarchy (H1-H6)
2. Given a PDF contains tables, when converted to Markdown, then they are rendered in valid GitHub-Flavored Markdown table syntax
3. Given a PDF contains footnotes, when converted, then they are annotated inline or appended to their parent section
4. Given a complex PDF where MinerU confidence < 0.85, then the Marker fallback produces semantically equivalent output
5. Conversion time: < 30 seconds per document (< 100 pages)
6. Output stored in MinIO `markdown-conversions` bucket with key `conversions/{document_id}/{document_id}.md`

---

## Definition of Done

- [x] Code written with TDD (tests first)
- [x] Unit tests for PDF conversion with sample documents
- [x] Integration tests for MinerU and Marker
- [x] All acceptance criteria verified
- [x] Documentation in `docs/01-initial/parsing-pipeline.md`
- [x] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- **Blocked by**: INGEST-1
- **Blocks**: INGEST-3

---

## Technical Notes

- Create a service layer that wraps PDF conversion
- Async conversion to avoid API blocking
- Confidence scoring and Marker fallback logic
- Store output in MinIO `markdown-conversions` bucket
