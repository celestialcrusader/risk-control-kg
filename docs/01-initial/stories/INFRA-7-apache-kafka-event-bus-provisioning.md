# INFRA-7: Apache Kafka Event Bus Provisioning

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 8
**Priority**: High
**Assigned To**: DevOps Engineer
**Labels**: infrastructure, kafka, messaging

---

## User Story

> As a **system**, I want Apache Kafka provisioned with proper topic configurations, so that the event-driven pipeline can asynchronously trigger downstream workflows (extraction, validation, crosswalk) without tight coupling.

---

## Acceptance Criteria

1. Given Kafka is deployed via Docker Compose, when `docker-compose ps` is executed, then the Kafka container shows status "running"
2. Given Kafka is running, when a test message is published to `document.ingested`, then the message is successfully consumed by a test consumer
3. All 5 required topics are pre-created with correct retention settings
4. `/backend/app/kafka/producer.py` includes working Kafka producer with schema validation
5. Topic creation script in `/infra/kafka/create-topics.sh`
6. Producer config uses `acks=all` for durability

### Required Topics
| Topic | Retention | Partitions | Purpose |
|---|---|---|---|
| `document.ingested` | 7 days | 3 | Triggers ingestion workflow |
| `extraction.completed` | 7 days | 3 | Triggers extraction validation |
| `validation.completed` | 7 days | 3 | Triggers graph build workflow |
| `mapping.completed` | 7 days | 3 | Triggers gap detection |
| `coverage.alert` | 30 days | 1 | Alerting on coverage threshold breach |

---

## Definition of Done

- [ ] Kafka Docker Compose service added (already done in INFRA-1)
- [ ] Topic creation script in `/infra/kafka/create-topics.sh`
- [ ] Kafka producer working in backend code
- [ ] Integration tests for Kafka producer
- [ ] All acceptance criteria verified
- [ ] **QA Checkpoint**: Verify all assertions are meaningful (not `or True`).

---

## Dependencies

- Blocked by: INFRA-1 (Docker Compose)
- Blocks: INGEST-5, EXTRACT-5
