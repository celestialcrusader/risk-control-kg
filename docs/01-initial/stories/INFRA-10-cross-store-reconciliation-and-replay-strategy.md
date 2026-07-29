# INFRA-10: Cross-Store Reconciliation and Replay Strategy

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Lead
**Labels**: infrastructure, reliability, replay

---

## User Story

> As a **system architect**, I want a defined cross-store reconciliation and replay strategy, so that we can recover from partial failures across PostgreSQL, Memgraph, Qdrant, and MinIO without data corruption or ghost records.

---

## Context and Background

The CTO review identified a critical gap: no reconciliation strategy exists for the 5 sources of truth (PostgreSQL, Memgraph, Qdrant, MinIO, Kafka). Without this, a failure like "Kafka emits event OK, Extraction writes to Postgres FAIL, Qdrant write succeeds OK" leaves ghost embeddings with no source truth.

This story defines:
1. Idempotent write patterns for all stores
2. Replay mechanism from Bronze layer
3. Consistency checks between stores
4. Checkpoint-based recovery for workflows

---

## Acceptance Criteria

1. Given a partial failure occurs, when the replay script is executed with a `document_id`, then all stores are reconstructed to a consistent state
2. Given a workflow fails, when the Temporal workflow is replayed, then it resumes from the last checkpoint without re-executing completed activities
3. Given a cross-store consistency check is run, when discrepancies are found, then they are logged to `reconciliation_dlq` for manual review
4. All write operations are idempotent (running twice produces the same result as running once)
5. A `replay_from_bronze.py` script exists that can reconstruct Silver, Gold, Qdrant, and Memgraph from Bronze layer data
6. Checkpoint metadata stored in PostgreSQL `workflow_checkpoints` table

---

## Definition of Done

- [x] Idempotent write patterns documented and implemented
- [x] Replay script working (tested with sample document)
- [x] Checkpoint table created and integrated with Temporal
- [x] Consistency check script with daily cron job
- [x] Documentation in `docs/01-initial/replay-strategy.md`

---

## Dependencies

- **Blocked by**: INFRA-2, INFRA-4, INFRA-9 (all stores must exist)
- **Blocks**: None (runs in parallel with feature development)

---

## Technical Notes

- Idempotent writes use UPSERT (ON CONFLICT DO UPDATE) for all database writes
- Temporal replay: Just re-run the workflow with the same workflow_id
- Checkpoint schema includes: checkpoint_id UUID, workflow_id, stage, data_hash (SHA-256), created_at
- Reconciliation script: `python scripts/replay_from_bronze.py --document-id doc-123`
- Consistency check: `python scripts/check_consistency.py --daily-run`
