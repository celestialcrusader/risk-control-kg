# EXTRACT-4: Silver Layer Storage

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, database, silver

---

## User Story

> As a **system**, I want validated extraction results to be stored in the PostgreSQL Silver layer, so that structured obligation data is preserved before dual-judge validation.

---

## Context and Background

Per TRD Section 6.2, the Silver layer (`semantic_controls`) stores:
- AI-extracted structured data
- Fields: `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun` (Facets)

This is the intermediate layer before Gold promotion.

---

## Acceptance Criteria

1. Given a validated extraction passes LLM-as-Judge, when `write_silver_record(obligation)` is called, then a row is inserted into `semantic_controls` table
2. Given a Silver record is created, when the row is queried, then it has all facet fields: `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun`
3. Given a Silver record is created, when the `status` field is checked, then it is set to `pending_validation`
4. Given a Silver record is created, when it is linked to a Bronze record, then the `bronze_record_id` FK is set correctly
5. Silver records are versioned: updates create new rows with `version` increment
6. SQLAlchemy model in `/backend/app/models/semantic.py` with proper ORM definitions

---

## Technical Notes

- Silver schema:
  ```sql
  CREATE TABLE semantic_controls (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      bronze_record_id UUID REFERENCES staging_controls(id),
      framework_name VARCHAR(255),
      group_id VARCHAR(50),
      objective_text TEXT,
      statement_text TEXT,
      action_verb VARCHAR(100),
      subject_noun VARCHAR(255),
      status VARCHAR(50) DEFAULT 'pending_validation',
      version INTEGER DEFAULT 1,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```
- Index on `bronze_record_id` for fast lookup
- Use application-level versioning (no DB trigger - increment `version` in the ORM `before_insert` hook)

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for Silver layer insertion
- [ ] Integration tests for database operations
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: EXTRACT-3, INFRA-2
- **Blocks**: DUALJUDGE-1
