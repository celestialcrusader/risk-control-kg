# INFRA-6: Temporal Workflow Engine Deployment

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 8
**Priority**: High
**Assigned To**: DevOps Engineer
**Labels**: infrastructure, temporal, workflow

---

## User Story

> As a **backend developer**, I want Temporal.io deployed with PostgreSQL backend, so that stateful workflows with HITL gates can be implemented and executed.

---

## Context and Background

Per TRD Section 19, Temporal.io is the primary workflow engine for:
- Stateful, long-running, human-in-the-loop workflows
- Pause/resume capabilities
- Event sourcing and replay

Temporal requires a PostgreSQL backend for durability.

---

## Acceptance Criteria

1. Given Temporal is running, when the `tctl` CLI is used to list namespaces, then the `rckg-production` namespace exists
2. Given Temporal is running, when a test workflow is started, then it completes successfully
3. Given a workflow is paused at a signal gate, when the workflow is queried, then its state shows `PAUSED` with active signal waiting
4. Temporal web UI accessible at `http://localhost:8233` with documented credentials
5. Temporal backend configured to use PostgreSQL on `localhost:5432`
6. `/backend/app/workflows/` directory initialized with base workflow templates

---

## Definition of Done

- [x] Code written and peer-reviewed
- [x] Unit tests for Temporal workflow registration
- [x] Integration tests for workflow execution
- [x] All acceptance criteria verified
- [x] Documentation updated

---

## Dependencies

- **Blocked by**: INFRA-1, INFRA-2
- **Blocks**: WORKFLOW-1, WORKFLOW-2

---

## Technical Notes

- Temporal Docker image: `temporalio/auto-setup:latest`
- Required ports: 7233 (gRPC), 8233 (Web UI)
- PostgreSQL namespace configuration:
  ```bash
  tctl namespace register --name rckg-production --description "RCKG production workflows"
  ```
- Create workflow task queue: `ingestion-task-queue`
