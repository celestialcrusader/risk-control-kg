# INFRA-2: PostgreSQL Schema and Three-Layer Vault

This document describes the PostgreSQL database schema implementation for the RCKG platform's three-layer vault architecture.

## Overview

The RCKG platform uses a three-layer data architecture (Bronze/Silver/Gold) as specified in TRD Section 6. This architecture ensures data quality, traceability, and audit compliance throughout the data pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Three-Layer Vault                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │    Bronze    │───▶│    Silver    │───▶│     Gold     │      │
│  │   (Raw)      │    │  (Semantic)  │    │ (Verified)   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

| Layer | Table | Purpose | Data Source |
|-------|-------|---------|-------------|
| **Bronze** | `staging_controls` | Raw document storage | PDF parsing, OCR, document upload |
| **Silver** | `semantic_controls` | AI-extracted structure | De Jure extraction pipeline |
| **Gold** | `golden_controls` | Human-verified controls | Manual review, high-confidence AI |

## Schema Details

### Bronze Layer: `staging_controls`

Stores the original parsed regulatory documents before any AI processing.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `uuid` | UUID | Unique identifier (duplicated from id for distributed systems) |
| `canonical_id` | VARCHAR(255) | Canonical document identifier |
| `raw_file_content` | JSONB | Complete parsed document structure |
| `created_at` | TIMESTAMPTZ | When document was ingested |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

**Indexes:**
- `ix_staging_canonical_id` - Fast lookup by canonical ID
- `ix_staging_created_at` - Time-based queries
- `ix_staging_raw_content` - GIN index for JSONB full-text search

### Silver Layer: `semantic_controls`

Contains AI-extracted structured control data from the De Jure pipeline.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `uuid` | UUID | Unique identifier |
| `framework_name` | VARCHAR(255) | Regulatory framework name |
| `framework_version` | VARCHAR(50) | Framework version |
| `group_id` | VARCHAR(255) | Control group identifier |
| `control_id` | VARCHAR(255) | Unique control identifier (unique) |
| `control_name` | VARCHAR(512) | Human-readable control name |
| `objective_text` | TEXT | High-level control objective |
| `statement_text` | TEXT | Detailed control statement |
| `action_verb` | VARCHAR(100) | Extracted action verb |
| `subject_noun` | VARCHAR(255) | Extracted subject noun |
| `extraction_confidence` | VARCHAR(10) | AI extraction confidence score |
| `source_document_id` | UUID | Reference to bronze document |
| `section_reference` | VARCHAR(512) | Original section location |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

**Indexes:**
- `ix_semantic_control_id` - Unique index on control_id
- `ix_semantic_framework` - Composite index on framework
- `ix_semantic_created_at` - Time-based queries
- `ix_semantic_action_verb` - Action-based filtering
- `ix_semantic_subject` - Subject-based filtering

### Gold Layer: `golden_controls`

Final, production-ready control data with bitemporal support.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `uuid` | UUID | Unique identifier |
| `control_id` | VARCHAR(255) | Unique control identifier (primary key) |
| `control_name` | VARCHAR(512) | Human-readable control name |
| `framework_name` | VARCHAR(255) | Regulatory framework |
| `framework_version` | VARCHAR(50) | Framework version |
| `group_id` | VARCHAR(255) | Control group |
| `objective_text` | TEXT | Control objective |
| `statement_text` | TEXT | Control statement |
| `action_verb` | VARCHAR(100) | Action verb |
| `subject_noun` | VARCHAR(255) | Subject noun |
| **`valid_from`** | **TIMESTAMPTZ** | **Event time: When control became valid** |
| **`valid_to`** | **TIMESTAMPTZ** | **Event time: When control became invalid** |
| **`ingested_at`** | **TIMESTAMPTZ** | **System time: When record was ingested** |
| `status` | VARCHAR(50) | active, superseded, draft, archived |
| `verification_level` | VARCHAR(50) | ai_confident, human_verified, pending_review |
| `verification_confidence` | VARCHAR(10) | Final verification confidence |
| `owner` | VARCHAR(255) | Control owner |
| `implementation_method` | VARCHAR(255) | How control is implemented |
| `created_at` | TIMESTAMPTZ | System creation timestamp |
| `updated_at` | TIMESTAMPTZ | System update timestamp |

**Bitemporal Support (TRD Section 6.2):**
- **Event Time (`valid_from`/`valid_to`)**: When the control was/wasn't valid in the real world
- **System Time (`ingested_at`)**: When the system recorded the fact

**Indexes:**
- `ix_golden_framework` - Framework-based queries
- `ix_golden_status` - Status filtering
- `ix_golden_valid_range` - Temporal queries
- `ix_golden_ingested_at` - Ingestion-based queries
- `ix_golden_verb_subject` - Semantic queries

## Additional Tables

### Audit Log: `audit_log`

Immutable log of all system events.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `event_type` | VARCHAR(100) | Type of event |
| `event_data` | JSONB | Event payload |
| `actor_id` | VARCHAR(255) | User/system that performed action |
| `actor_type` | VARCHAR(50) | user, system, agent |
| `timestamp` | TIMESTAMPTZ | Event timestamp |
| `ip_address` | INET | Source IP |
| `user_agent` | VARCHAR(512) | Client user agent |
| `request_id` | UUID | Request correlation ID |

### Workflow Checkpoints: `workflow_checkpoints`

Enables idempotent workflow execution and replay.

| Column | Type | Description |
|--------|------|-------------|
| `checkpoint_id` | UUID | Primary key |
| `workflow_id` | VARCHAR(255) | Workflow identifier |
| `stage` | VARCHAR(50) | Workflow stage name |
| `data_hash` | VARCHAR(64) | SHA-256 of processed data |
| `metadata` | JSONB | Additional stage metadata |
| `created_at` | TIMESTAMPTZ | Checkpoint creation time |
| `updated_at` | TIMESTAMPTZ | Last update time |

**Unique Constraint:** `(workflow_id, stage)` - One checkpoint per stage per workflow

### Reconciliation DLQ: `reconciliation_dlq`

Dead letter queue for cross-store reconciliation failures.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `store_type` | VARCHAR(50) | PostgreSQL, Memgraph, Qdrant, MinIO |
| `record_id` | VARCHAR(255) | Record identifier |
| `discrepancy_type` | VARCHAR(100) | Type of discrepancy |
| `discrepancy_details` | JSONB | Detailed discrepancy information |
| `status` | VARCHAR(50) | pending, acknowledged, resolved, archived |
| `reviewed_by` | VARCHAR(255) | Human who reviewed |
| `reviewed_at` | TIMESTAMPTZ | Review timestamp |
| `created_at` | TIMESTAMPTZ | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | Update timestamp |

### Schema Migrations: `schema_migrations`

Tracks applied migrations for idempotency.

| Column | Type | Description |
|--------|------|-------------|
| `version` | VARCHAR(50) | Migration version (primary key) |
| `applied_at` | TIMESTAMPTZ | Migration application time |
| `description` | TEXT | Migration description |
| `checksum` | VARCHAR(64) | SHA-256 of migration script |

## ORM Models

SQLAlchemy ORM models are defined in `/backend/app/models/__init__.py`.

### Usage Example

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base, GoldenControl, ControlStatus

# Create engine
engine = create_engine("postgresql://rckg:rckg_secret_password@localhost:5432/rckg_db")

# Create tables (if not using Alembic)
Base.metadata.create_all(bind=engine)

# Create session
with Session(engine) as session:
    # Create a new control
    control = GoldenControl(
        control_id="ISO27001-A.9.2.1",
        control_name="User Access Management",
        framework_name="ISO 27001",
        framework_version="2022",
        statement_text="User access provisioning and de-provisioning processes are established",
        valid_from="2024-01-01",
        status=ControlStatus.ACTIVE,
        verification_level="human_verified"
    )
    
    session.add(control)
    session.commit()
    
    # Query controls valid as of a specific date
    from datetime import datetime
    controls = session.query(GoldenControl).filter(
        GoldenControl.valid_from <= datetime(2024, 6, 15),
        (GoldenControl.valid_to.is_(None)) | 
        (GoldenControl.valid_to >= datetime(2024, 6, 15))
    ).all()
```

## Running Migrations

### Using Alembic

```bash
# Navigate to backend directory
cd /home/zackchow/coding/rckg/backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current

# Downgrade to a specific version
alembic downgrade -1
```

### Using init.sql (Development)

```bash
# The schema is automatically created when PostgreSQL starts for the first time
# via the mounted init.sql script in docker-compose.yml
```

## Idempotency

All schema creation is idempotent:
- `CREATE TABLE IF NOT EXISTS` statements
- `CREATE INDEX IF NOT EXISTS` statements
- `ON CONFLICT DO NOTHING` for inserts
- Unique constraints on workflow checkpoints

Running the schema initialization multiple times will not cause errors.

## Testing

Run the test suite to verify schema correctness:

```bash
cd /home/zackchow/coding/rckg/backend

# Run INFRA-2 tests
pytest tests/test_infra_2_postgres_schema.py -v
```

## References

- TRD Section 6: Data Architecture - Three-Layer PostgreSQL Vault
- TRD Section 6.2: Bitemporal Data Model
- Sprint Plan: INFRA-2 Story
