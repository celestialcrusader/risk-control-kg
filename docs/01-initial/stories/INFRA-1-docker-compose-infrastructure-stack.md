# INFRA-1: Docker Compose Infrastructure Stack

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 8
**Priority**: High
**Assigned To**: DevOps Engineer
**Labels**: infrastructure, devops, docker

---

## User Story

> As a **developer**, I want a fully documented Docker Compose stack that spins up all infrastructure services with one command, so that I can start development immediately without manual setup.

---

## Context and Background

Per TRD Section 4.2 and Section 18.1, the platform requires PostgreSQL 16, Memgraph, Qdrant, MinIO, Redis, Temporal, and Langfuse. This story establishes the base docker-compose.yml with all services, proper networking, volumes, and environment configuration.

---

## Acceptance Criteria

1. Given a clean checkout, when `docker-compose up -d` is executed, then all 9 infrastructure services start successfully within 5 minutes
2. Given all services are running, when `docker-compose ps` is executed, then all containers show status "healthy" or "running"
3. Given the stack is running, when the PostgreSQL health check endpoint is queried, then it returns HTTP 200 with database connectivity
4. Given the stack is running, when the Memgraph REST API is queried, then it returns the service status
5. Given the stack is running, when the Qdrant REST API is queried, then it returns the service version
6. Documentation in `docs/01-initial/setup-guide.md` includes commands to start, stop, and view logs

---

## Definition of Done

- [x] Code written and peer-reviewed
- [x] Integration tests for docker-compose stack
- [x] All acceptance criteria verified
- [x] Documentation updated

---

## Dependencies

- **Blocked by**: None
- **Blocks**: INFRA-2, INFRA-3

---

## Technical Notes

- Use official Docker Hub images for all services
- Configure proper health checks for each service
- Set memory limits: PostgreSQL 64GB, Memgraph 32GB, Qdrant auto
- Use named volumes for data persistence: `postgres_data`, `memgraph_data`, `qdrant_storage`, `minio_data`
- Network: Create dedicated `rckg-net` bridge network
- Environment variables should reference a `.env.example` file
