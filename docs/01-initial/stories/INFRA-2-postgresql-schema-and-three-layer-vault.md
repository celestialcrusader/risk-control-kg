# INFRA-2: PostgreSQL Schema and Three-Layer Vault

**Type**: Story
**Sprint**: Sprint 1
**Story Points**: 13
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, database, postgresql

---

## User Story

> As a **backend developer**, I want the PostgreSQL database to have a complete schema with Bronze/Silver/Gold staging layers, so that data can flow through the three-tier quality model as specified in the TRD.

---

## Context and Background

Per TRD Section 6 (Data Architecture - Three-Layer PostgreSQL Vault), the platform requires:
- `staging_controls` (Bronze) - raw unstructured text
- `semantic_controls` (Silver) - AI-extracted structure
- `golden_controls` (Gold) - human-verified or highly-confident AI-validated data

Additionally, bitemporal tagging (`valid_from`, `valid_to`, `ingested_at`) must be applied to all nodes.

---

## Acceptance Criteria

1. Given the PostgreSQL container is running, when the schema migration script executes, then all tables (staging_controls, semantic_controls, golden_controls) are created
2. Given the schema is applied, when the `staging_controls` table is queried, then it has columns: `id`, `uuid`, `canonical_id`, `raw_file_content` (JSONB), `created_at`
3. Given the schema is applied, when the `semantic_controls` table is queried, then it has columns: `id`, `framework_name`, `group_id`, `objective_text`, `statement_text`, `action_verb`, `subject_noun`, `created_at`
4. Given the schema is applied, when the `golden_controls` table is queried, then it has bitemporal columns: `valid_from`, `valid_to`, `ingested_at`, plus all semantic_controls fields
5. Given the schema is applied, when the audit_log table is queried, then it has columns: `id`, `event_type`, `event_data` (JSONB), `actor_id`, `timestamp`, `ip_address`
6. SQL migration scripts are idempotent and can be run multiple times without error

---

## Definition of Done

- [x] Code written and peer-reviewed
- [x] Unit tests written with coverage meeting project standard
- [x] Integration tests written where applicable
- [x] All acceptance criteria verified by the developer
- [x] Code merged to the main/development branch
- [x] No new linting errors or warnings introduced
- [x] Relevant documentation updated (API docs, README, inline comments)
- [x] Story demoed or verified by Product Owner / Scrum Master

---

## Dependencies

- **Blocked by**: INFRA-1
- **Blocks**: INFRA-3, INGEST-1

---

## Technical Notes

- Use SQLAlchemy for ORM definitions in `/backend/app/models/`
- Use Alembic for migration management
- Create index on `canonical_id` for fast lookups
- Create GIN index on JSONB columns for full-text search
- Bitemporal columns should use `TIMESTAMP WITH TIME ZONE`
- `raw_file_content` JSONB schema should include: `document_id`, `hash`, `source_path`, `content`, `metadata`
