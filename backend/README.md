# RCKG Backend

Backend services for the Risk and Control Knowledge Graph platform.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── database.py       # Database connection and session management
│   │   └── ...
│   └── models/
│       ├── __init__.py       # SQLAlchemy ORM models
│       └── ...
├── alembic/
│   ├── env.py                # Alembic environment configuration
│   ├── versions/             # Migration scripts
│   └── ...
├── tests/
│   ├── test_infra_2_postgres_schema.py
│   └── ...
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
└── README.md
```

## Dependencies

- Python 3.11+
- SQLAlchemy 2.0+
- Alembic 1.12+
- psycopg2-binary 2.9+

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Database Setup

### Using Docker Compose

The easiest way to start the database is via the main `docker-compose.yml`:

```bash
# From project root
docker compose up -d postgres
```

The schema is automatically initialized via `infra/postgres/init.sql` on first startup.

### Using Alembic

```bash
# Navigate to backend directory
cd backend

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_infra_2_postgres_schema.py -v
```

## SQLAlchemy ORM Models

The ORM models are defined in `app/models/__init__.py` and implement the three-layer vault architecture:

- **StagingControl** - Bronze layer (raw documents)
- **SemanticControl** - Silver layer (AI-extracted structure)
- **GoldenControl** - Gold layer (verified controls with bitemporal support)
- **AuditLog** - System audit trail
- **WorkflowCheckpoint** - Workflow state tracking
- **ReconciliationDLQ** - Cross-store reconciliation failures
- **SchemaMigration** - Migration version tracking

## Alembic Migrations

### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <version>
```

## Configuration

Environment variables for database connection:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://rckg:rckg_secret_password@localhost:5432/rckg_db` | PostgreSQL connection string |

## API Reference

### Database Session

```python
from app.core.database import get_db_session

with get_db_session() as session:
    # Use session for database operations
    results = session.query(GoldenControl).all()
```

## See Also

- [PostgreSQL Schema Documentation](../docs/01-initial/postgres-schema.md)
- [TRD Section 6: Data Architecture](../docs/01-initial/master_tech_req.md)
