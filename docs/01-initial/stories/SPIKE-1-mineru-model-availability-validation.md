# SPIKE-1: MinerU Model Availability Validation

**Type**: Spike
**Sprint**: Sprint 0
**Story Points**: 3
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: spike, research, pdf-parsing

---

## User Story

> As a **ML engineer**, I want to validate MinerU model availability for local deployment, so that the document ingestion pipeline can proceed with a confirmed parsing approach.

---

## Context and Background

This is a time-boxed investigation to validate whether the MinerU PDF parsing model can be downloaded, installed, and run locally. If MinerU is unavailable or impractical, the spike must evaluate alternative parsers (Marker, pdfplumber, etc.) and recommend a fallback.

This spike must complete before Sprint 2 can begin, as INGEST-2 (MinerU PDF-to-Markdown Conversion) depends on this decision.

---

## Acceptance Criteria

1. Given the spike is complete, when the decision document is reviewed, then it contains a clear recommendation (MinerU or alternative) with supporting evidence
2. Given the POC is executed, when a sample PDF is passed through the parser, then valid Markdown output is produced
3. Given the decision is "MinerU", when `pip install mineru` is executed, then the installation completes without external API dependencies
4. Given the decision is "Marker", when `pip install marker-pdf` is executed, then the installation completes without external API dependencies
5. Given the spike output, the team can proceed to Sprint 2 without blockers

---

## Definition of Done

- [x] Decision document written and peer-reviewed
- [x] POC script produced (working code)
- [x] Recommendation presented to team
- [x] Sprint 0 sign-off from Scrum Master

---

## Dependencies

- **Blocked by**: None (can run in parallel with INFRA-1)
- **Blocks**: INGEST-2

---

## Technical Notes

- **Timebox**: 4 hours maximum. If the investigation requires more time, the spike extends by 4 hours with team consensus.
- **Deliverables**:
  1. Decision document at `docs/01-initial/mineru-validation.md`
  2. POC script: `/scripts/poc_mineru.py` or `/scripts/poc_marker.py`
  3. Integration recommendation for INGEST-2
- **Investigation Questions**:
  1. Can MinerU models be downloaded via pip/huggingface without external dependencies?
  2. What are the GPU requirements for MinerU inference?
  3. Are there licensing restrictions for MinerU models?
  4. What is the fallback if MinerU fails (Marker confidence < 0.85)?
  5. Can MinerU run on CPU for development environments?
