# INFRA-8: AI Model Download and Local Registry Setup

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 8
**Priority**: High
**Assigned To**: ML/AI Engineer
**Labels**: infrastructure, ml, models

---

## User Story

> As a **ML engineer**, I want 3 AI models downloaded, validated, and stored locally on the filesystem, so that the system can run fully offline in air-gapped environments without external API dependencies.

---

## Acceptance Criteria

1. Given the `scripts/download_models.py` script is executed, then 3 models are downloaded and verified against SHA-256 checksums
2. `models/manifest.json` tracks model versions, checksums, and download timestamps
3. Air-gapped deployment checklist documented in `docs/01-initial/model-setup.md`
4. GPU routing configuration documented (sequential judge execution via vLLM)
5. Local model loading from `models/` directory works at runtime without MinIO

### Models Required

| Model | Purpose | Storage Path |
|---|---|---|
| `BAAI/bge-m3` | Dense embeddings | `models/embeddings/bge-m3` |
| `colbertv2.0-adept` | Token-level embeddings | `models/embeddings/colbertv2.0` |
| `BAAI/bge-reranker-v2-m3` | Reranking | `models/reranker/bge-reranker` |

Note: `Qwen/Qwen3.6-35B` is already installed and running in vLLM on the DGX. It is not part of this download story.

---

## Definition of Done

- [ ] Model download script with checksum verification (`scripts/download_models.py`)
- [ ] `models/manifest.json` tracks model versions, checksums, and download timestamps
- [ ] Air-gapped deployment checklist in `docs/01-initial/model-setup.md`
- [ ] GPU routing documentation (sequential judge execution via vLLM)
- [ ] All acceptance criteria verified
- [ ] **QA Checkpoint**: Verify all assertions are meaningful.

---

## Dependencies

- Blocked by: INFRA-1 (base infrastructure must be running)
- Blocks: EXTRACT-1, DUALJUDGE-1
