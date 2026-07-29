# OBSERV-3: Audit Log Aggregation

**Type**: Story
**Sprint**: Sprint 9
**Story Points**: 4
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, audit, logging

---

## User Story

> As a **compliance officer**, I want an immutable audit log of all system actions, so that I can demonstrate audit trail compliance for regulatory examinations.

---

## Context and Background

Per TRD Section 11.4 and Section 16.2, audit logging must:
- Log all agent actions, graph writes, user queries
- Be immutable and append-only
- Include: actor_id, action, resource_id, timestamp, ip_address, user_agent
- Retain logs for 10 years (regulatory requirement)

---

## Acceptance Criteria

1. Given an action occurs, when audit logging is enabled, then a row is inserted into `audit_log` table
2. Given a log entry is created, when an attempt is made to modify or delete it, then the operation is rejected
3. Audit log includes: `id`, `event_type`, `actor_id`, `resource_type`, `resource_id`, `action`, `metadata` (JSONB), `timestamp`, `ip_address`, `user_agent`
4. Query audit logs via API: `GET /api/v1/audit?event_type=...&actor_id=...&from_date=...`
5. Audit log retention: 10 years (archival to cold storage after 1 year)
6. Audit logs are searchable and filterable via Grafana Loki or Elasticsearch

---

## Technical Notes

- Audit log table schema:
  ```sql
  CREATE TABLE audit_log (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      event_type VARCHAR(100) NOT NULL,
      actor_id UUID NOT NULL,
      resource_type VARCHAR(100),
      resource_id UUID,
      action VARCHAR(100) NOT NULL,
      metadata JSONB,
      timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      ip_address INET,
      user_agent TEXT
  );
  ```
- Audit log decorator for automatic logging
- Create indexes on event_type, actor_id, timestamp

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for audit logging
- [ ] Integration tests for audit log queries
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: INFRA-2
- **Blocks**: None
