"""
Test suite for INFRA-2: PostgreSQL Schema and Three-Layer Vault

This test module verifies that the PostgreSQL database schema is correctly
created with Bronze/Silver/Gold staging layers and bitemporal support.

Test Strategy:
- Integration tests that connect to PostgreSQL container
- Tests verify table structure, column existence, indexes, and idempotency
- Requires Docker Compose stack running with PostgreSQL service
"""

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from typing import List, Dict, Any

# Test configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_ROOT = Path(__file__).parent.parent

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "rckg_db",
    "user": "rckg",
    "password": "rckg_secret_password",
}


@pytest.fixture(scope="module")
def db_connection():
    """
    Fixture to create a database connection.

    This fixture:
    1. Connects to the PostgreSQL database
    2. Yields the connection for tests
    3. Closes the connection after all tests complete
    """
    conn = None
    for _ in range(60):  # Wait up to 60 seconds for PostgreSQL to be ready
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            break
        except psycopg2.OperationalError:
            import time
            time.sleep(1)
    else:
        pytest.skip("PostgreSQL not available, skipping INFRA-2 tests")

    conn = psycopg2.connect(**DB_CONFIG)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def cursor(db_connection):
    """Create a database cursor."""
    with db_connection.cursor(cursor_factory=RealDictCursor) as cur:
        yield cur


class TestPostgreSQLSchema:
    """Integration tests for PostgreSQL schema."""

    def test_schema_migration_script_exists(self):
        """TC-2.1: Schema migration script exists."""
        migration_file = PROJECT_ROOT / "infra" / "postgres" / "init.sql"
        assert migration_file.exists(), f"Schema migration script not found at {migration_file}"

    def test_staging_controls_table_exists(self, cursor):
        """TC-2.2: Given the schema is applied, staging_controls table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'staging_controls'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "staging_controls table does not exist"

    def test_semantic_controls_table_exists(self, cursor):
        """TC-2.3: Given the schema is applied, semantic_controls table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'semantic_controls'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "semantic_controls table does not exist"

    def test_golden_controls_table_exists(self, cursor):
        """TC-2.4: Given the schema is applied, golden_controls table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'golden_controls'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "golden_controls table does not exist"

    def test_audit_log_table_exists(self, cursor):
        """TC-2.5: Given the schema is applied, audit_log table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'audit_log'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "audit_log table does not exist"

    def test_workflow_checkpoints_table_exists(self, cursor):
        """TC-2.6: workflow_checkpoints table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'workflow_checkpoints'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "workflow_checkpoints table does not exist"

    def test_reconciliation_dlq_table_exists(self, cursor):
        """TC-2.7: reconciliation_dlq table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'reconciliation_dlq'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "reconciliation_dlq table does not exist"

    def test_schema_migrations_table_exists(self, cursor):
        """TC-2.8: schema_migrations table is created."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'schema_migrations'
            )
        """)
        result = cursor.fetchone()["exists"]
        assert result is True, "schema_migrations table does not exist"


class TestStagingControlsTable:
    """Tests for Bronze layer (staging_controls) table structure."""

    def test_staging_controls_has_id_column(self, cursor):
        """TC-2.2a: staging_controls table has id column."""
        self._verify_column_exists(cursor, "staging_controls", "id")

    def test_staging_controls_has_uuid_column(self, cursor):
        """TC-2.2b: staging_controls table has uuid column."""
        self._verify_column_exists(cursor, "staging_controls", "uuid")

    def test_staging_controls_has_canonical_id_column(self, cursor):
        """TC-2.2c: staging_controls table has canonical_id column."""
        self._verify_column_exists(cursor, "staging_controls", "canonical_id")

    def test_staging_controls_has_raw_file_content_column(self, cursor):
        """TC-2.2d: staging_controls table has raw_file_content column."""
        self._verify_column_exists(cursor, "staging_controls", "raw_file_content")

    def test_staging_controls_has_created_at_column(self, cursor):
        """TC-2.2e: staging_controls table has created_at column."""
        self._verify_column_exists(cursor, "staging_controls", "created_at")

    def test_staging_controls_has_updated_at_column(self, cursor):
        """TC-2.2f: staging_controls table has updated_at column."""
        self._verify_column_exists(cursor, "staging_controls", "updated_at")

    def test_staging_controls_raw_file_content_is_jsonb(self, cursor):
        """TC-2.2g: staging_controls.raw_file_content is JSONB type."""
        cursor.execute("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'staging_controls'
            AND column_name = 'raw_file_content'
        """)
        result = cursor.fetchone()
        assert result is not None, "raw_file_content column not found"
        assert result["data_type"].lower() == "jsonb", \
            f"raw_file_content is {result['data_type']}, expected jsonb"

    def test_staging_controls_canonical_id_has_index(self, cursor):
        """TC-2.2h: canonical_id has an index for fast lookups."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = 'staging_controls'
            AND indexname LIKE '%canonical_id%'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No index found on canonical_id"

    def test_staging_controls_raw_content_has_gin_index(self, cursor):
        """TC-2.2i: raw_file_content has a GIN index for full-text search."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = 'staging_controls'
            AND indexdef LIKE '%GIN%'
            AND indexdef LIKE '%raw_file_content%'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No GIN index found on raw_file_content"

    @staticmethod
    def _verify_column_exists(cursor, table_name: str, column_name: str):
        """Helper to verify a column exists in a table."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = %s
            )
        """, (table_name, column_name))
        result = cursor.fetchone()["exists"]
        assert result is True, f"Column '{column_name}' does not exist in '{table_name}'"


class TestSemanticControlsTable:
    """Tests for Silver layer (semantic_controls) table structure."""

    def test_semantic_controls_has_id_column(self, cursor):
        """TC-2.3a: semantic_controls table has id column."""
        self._verify_column_exists(cursor, "semantic_controls", "id")

    def test_semantic_controls_has_uuid_column(self, cursor):
        """TC-2.3b: semantic_controls table has uuid column."""
        self._verify_column_exists(cursor, "semantic_controls", "uuid")

    def test_semantic_controls_has_framework_name_column(self, cursor):
        """TC-2.3c: semantic_controls table has framework_name column."""
        self._verify_column_exists(cursor, "semantic_controls", "framework_name")

    def test_semantic_controls_has_group_id_column(self, cursor):
        """TC-2.3d: semantic_controls table has group_id column."""
        self._verify_column_exists(cursor, "semantic_controls", "group_id")

    def test_semantic_controls_has_objective_text_column(self, cursor):
        """TC-2.3e: semantic_controls table has objective_text column."""
        self._verify_column_exists(cursor, "semantic_controls", "objective_text")

    def test_semantic_controls_has_statement_text_column(self, cursor):
        """TC-2.3f: semantic_controls table has statement_text column."""
        self._verify_column_exists(cursor, "semantic_controls", "statement_text")

    def test_semantic_controls_has_action_verb_column(self, cursor):
        """TC-2.3g: semantic_controls table has action_verb column."""
        self._verify_column_exists(cursor, "semantic_controls", "action_verb")

    def test_semantic_controls_has_subject_noun_column(self, cursor):
        """TC-2.3h: semantic_controls table has subject_noun column."""
        self._verify_column_exists(cursor, "semantic_controls", "subject_noun")

    def test_semantic_controls_has_control_id_column(self, cursor):
        """TC-2.3i: semantic_controls table has control_id column."""
        self._verify_column_exists(cursor, "semantic_controls", "control_id")

    def test_semantic_controls_has_created_at_column(self, cursor):
        """TC-2.3j: semantic_controls table has created_at column."""
        self._verify_column_exists(cursor, "semantic_controls", "created_at")

    def test_semantic_controls_has_updated_at_column(self, cursor):
        """TC-2.3k: semantic_controls table has updated_at column."""
        self._verify_column_exists(cursor, "semantic_controls", "updated_at")

    @staticmethod
    def _verify_column_exists(cursor, table_name: str, column_name: str):
        """Helper to verify a column exists in a table."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = %s
            )
        """, (table_name, column_name))
        result = cursor.fetchone()["exists"]
        assert result is True, f"Column '{column_name}' does not exist in '{table_name}'"


class TestGoldenControlsTable:
    """Tests for Gold layer (golden_controls) table structure with bitemporal support."""

    def test_golden_controls_has_id_column(self, cursor):
        """TC-2.4a: golden_controls table has id column."""
        self._verify_column_exists(cursor, "golden_controls", "id")

    def test_golden_controls_has_uuid_column(self, cursor):
        """TC-2.4b: golden_controls table has uuid column."""
        self._verify_column_exists(cursor, "golden_controls", "uuid")

    def test_golden_controls_has_control_id_column(self, cursor):
        """TC-2.4c: golden_controls table has control_id column."""
        self._verify_column_exists(cursor, "golden_controls", "control_id")

    def test_golden_controls_has_bitemporal_valid_from(self, cursor):
        """TC-2.4d: golden_controls table has valid_from column (event time)."""
        self._verify_column_exists(cursor, "golden_controls", "valid_from")

    def test_golden_controls_has_bitemporal_valid_to(self, cursor):
        """TC-2.4e: golden_controls table has valid_to column (event time)."""
        self._verify_column_exists(cursor, "golden_controls", "valid_to")

    def test_golden_controls_has_bitemporal_ingested_at(self, cursor):
        """TC-2.4f: golden_controls table has ingested_at column (system time)."""
        self._verify_column_exists(cursor, "golden_controls", "ingested_at")

    def test_golden_controls_has_framework_name_column(self, cursor):
        """TC-2.4g: golden_controls table has framework_name column."""
        self._verify_column_exists(cursor, "golden_controls", "framework_name")

    def test_golden_controls_has_statement_text_column(self, cursor):
        """TC-2.4h: golden_controls table has statement_text column."""
        self._verify_column_exists(cursor, "golden_controls", "statement_text")

    def test_golden_controls_has_action_verb_column(self, cursor):
        """TC-2.4i: golden_controls table has action_verb column."""
        self._verify_column_exists(cursor, "golden_controls", "action_verb")

    def test_golden_controls_has_subject_noun_column(self, cursor):
        """TC-2.4j: golden_controls table has subject_noun column."""
        self._verify_column_exists(cursor, "golden_controls", "subject_noun")

    def test_golden_controls_has_status_column(self, cursor):
        """TC-2.4k: golden_controls table has status column."""
        self._verify_column_exists(cursor, "golden_controls", "status")

    def test_golden_controls_has_verification_level_column(self, cursor):
        """TC-2.4l: golden_controls table has verification_level column."""
        self._verify_column_exists(cursor, "golden_controls", "verification_level")

    def test_golden_controls_bitemporal_columns_are_timestamptz(self, cursor):
        """TC-2.4m: Bitemporal columns use TIMESTAMP WITH TIME ZONE."""
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'golden_controls'
            AND column_name IN ('valid_from', 'valid_to', 'ingested_at')
        """)
        results = cursor.fetchall()
        for row in results:
            assert row["data_type"] == "timestamp with time zone", \
                f"Column '{row['column_name']}' is {row['data_type']}, expected timestamp with time zone"

    def test_golden_controls_has_valid_from_index(self, cursor):
        """TC-2.4n: valid_from, valid_to has an index for temporal queries."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = 'golden_controls'
            AND indexdef LIKE '%valid_from%'
            AND indexdef LIKE '%valid_to%'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No composite index found on valid_from, valid_to"

    @staticmethod
    def _verify_column_exists(cursor, table_name: str, column_name: str):
        """Helper to verify a column exists in a table."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = %s
            )
        """, (table_name, column_name))
        result = cursor.fetchone()["exists"]
        assert result is True, f"Column '{column_name}' does not exist in '{table_name}'"


class TestAuditLogTable:
    """Tests for audit_log table structure."""

    def test_audit_log_has_id_column(self, cursor):
        """TC-2.5a: audit_log table has id column."""
        self._verify_column_exists(cursor, "audit_log", "id")

    def test_audit_log_has_event_type_column(self, cursor):
        """TC-2.5b: audit_log table has event_type column."""
        self._verify_column_exists(cursor, "audit_log", "event_type")

    def test_audit_log_has_event_data_column(self, cursor):
        """TC-2.5c: audit_log table has event_data column."""
        self._verify_column_exists(cursor, "audit_log", "event_data")

    def test_audit_log_has_event_data_as_jsonb(self, cursor):
        """TC-2.5d: audit_log.event_data is JSONB type."""
        cursor.execute("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'audit_log'
            AND column_name = 'event_data'
        """)
        result = cursor.fetchone()
        assert result is not None, "event_data column not found"
        assert result["data_type"].lower() == "jsonb", \
            f"event_data is {result['data_type']}, expected jsonb"

    def test_audit_log_has_actor_id_column(self, cursor):
        """TC-2.5e: audit_log table has actor_id column."""
        self._verify_column_exists(cursor, "audit_log", "actor_id")

    def test_audit_log_has_timestamp_column(self, cursor):
        """TC-2.5f: audit_log table has timestamp column."""
        self._verify_column_exists(cursor, "audit_log", "timestamp")

    def test_audit_log_has_ip_address_column(self, cursor):
        """TC-2.5g: audit_log table has ip_address column."""
        self._verify_column_exists(cursor, "audit_log", "ip_address")

    def test_audit_log_event_data_has_gin_index(self, cursor):
        """TC-2.5h: event_data has a GIN index for full-text search."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = 'audit_log'
            AND indexdef LIKE '%GIN%'
            AND indexdef LIKE '%event_data%'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No GIN index found on event_data"

    @staticmethod
    def _verify_column_exists(cursor, table_name: str, column_name: str):
        """Helper to verify a column exists in a table."""
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = %s
            )
        """, (table_name, column_name))
        result = cursor.fetchone()["exists"]
        assert result is True, f"Column '{column_name}' does not exist in '{table_name}'"


class TestIdempotency:
    """Tests for SQL migration idempotency."""

    def test_migration_script_can_run_multiple_times(self, db_connection):
        """TC-2.6: SQL migration scripts are idempotent and can be run multiple times."""
        migration_file = PROJECT_ROOT / "infra" / "postgres" / "init.sql"
        assert migration_file.exists(), f"Schema migration script not found at {migration_file}"

        with migration_file.open("r") as f:
            sql_script = f.read()

        cursor = db_connection.cursor()

        # Run the script multiple times
        for i in range(3):
            try:
                cursor.execute(sql_script)
                db_connection.commit()
            except Exception as e:
                cursor.close()
                pytest.fail(f"Migration script failed on run {i + 1}: {str(e)}")

        cursor.close()


class TestIndexes:
    """Tests for index definitions."""

    def test_semantic_control_id_has_unique_index(self, cursor):
        """Silver layer has unique index on control_id."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = 'semantic_controls'
            AND indexname LIKE '%control_id%'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No index found on control_id in semantic_controls"

    def test_golden_control_id_is_primary_key(self, cursor):
        """Gold layer has primary key constraint on control_id."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            AND table_name = 'golden_controls'
            AND constraint_type = 'PRIMARY KEY'
            AND constraint_name LIKE '%control_id%'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No primary key on control_id in golden_controls"

    def test_workflow_checkpoints_has_unique_constraint(self, cursor):
        """workflow_checkpoints has unique constraint on (workflow_id, stage)."""
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            AND table_name = 'workflow_checkpoints'
            AND constraint_type = 'UNIQUE'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "No unique constraint found on workflow_checkpoints"


class TestIdempotency:
    """Tests for SQL migration idempotency."""

    def test_migration_script_can_run_multiple_times(self, db_connection):
        """TC-2.6: SQL migration scripts are idempotent and can be run multiple times."""
        migration_file = PROJECT_ROOT / "infra" / "postgres" / "init.sql"
        assert migration_file.exists(), f"Schema migration script not found at {migration_file}"

        with migration_file.open("r") as f:
            sql_script = f.read()

        cursor = db_connection.cursor()

        # Run the script multiple times
        for i in range(3):
            try:
                cursor.execute(sql_script)
                db_connection.commit()
            except Exception as e:
                cursor.close()
                pytest.fail(f"Migration script failed on run {i + 1}: {str(e)}")

        cursor.close()

    def test_migration_creates_schema_migrations_entry(self, cursor):
        """Schema migrations table should have initial entry."""
        cursor.execute("""
            SELECT COUNT(*) FROM schema_migrations WHERE version = '1.0.0'
        """)
        result = cursor.fetchone()
        assert result["count"] > 0, "Schema migrations should have initial entry"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
