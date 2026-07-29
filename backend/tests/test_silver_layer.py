"""
Test suite for EXTRACT-4: Silver Layer Storage

This test module verifies the Silver layer storage pipeline:
- SemanticControl model fields (bronze_record_id, status, version)
- Silver layer service functions (write, batch write, query, versioning)
- API endpoint POST /api/v1/semantic

Test Strategy:
- Unit tests for model fields using SQLAlchemy session mocking
- Unit tests for service layer with MagicMock sessions
- Integration tests for the API endpoint using FastAPI TestClient
- Edge cases: missing obligation, DB errors, version increment, batch ops

Acceptance Criteria Covered:
- AC-1: write_silver_record(obligation) inserts a row into semantic_controls
- AC-2: Silver record has all facet fields: framework_name, group_id,
  objective_text, statement_text, action_verb, subject_noun
- AC-3: status is set to pending_validation on creation
- AC-4: bronze_record_id FK is set correctly when provided
- AC-5: Version auto-increments on new versions of an obligation
- AC-6: SQLAlchemy model in models/__init__.py with proper definitions
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Ensure app module is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from fastapi.testclient import TestClient
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_obligation_dict():
    """A sample extracted obligation as a dictionary."""
    return {
        "id": "AC-1",
        "prose": "The organization must limit information system access to authorized users.",
        "action_verb": "limit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1",
    }


@pytest.fixture
def sample_obligation():
    """A sample Obligation Pydantic model instance."""
    from app.schemas.obligation import Obligation
    return Obligation(
        id="AC-1",
        prose="The organization must limit information system access to authorized users.",
        action_verb="limit",
        subject_noun="information system access",
        clause_ref="Section 3.1",
    )


@pytest.fixture
def sample_obligation_2():
    """A second sample Obligation for batch tests."""
    from app.schemas.obligation import Obligation
    return Obligation(
        id="AC-2",
        prose="The organization must monitor all access attempts.",
        action_verb="monitor",
        subject_noun="access attempts",
        clause_ref="Section 3.2",
    )


@pytest.fixture
def obligations_list(sample_obligation, sample_obligation_2):
    """List of two obligations for batch tests."""
    return [sample_obligation, sample_obligation_2]


@pytest.fixture
def mock_db_session():
    """Create a fresh mock SQLAlchemy session that works as a context manager."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.query = MagicMock(return_value=MagicMock())
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    return session


@pytest.fixture
def bronze_record_id():
    """A UUID string representing a bronze layer record."""
    return "550e8400-e29b-41d4-a716-446655440001"


# ==============================================================================
# Model Field Tests
# ==============================================================================


class TestModelFields:
    """Test that SemanticControl model has the required new fields."""

    def test_semantic_control_has_bronze_record_id_column(self):
        """TC-4.1: SemanticControl has a bronze_record_id column (FK to staging_controls)."""
        from app.models import SemanticControl

        assert hasattr(SemanticControl, "bronze_record_id"), \
            "SemanticControl must have a bronze_record_id column"

    def test_semantic_control_has_status_column(self):
        """TC-4.2: SemanticControl has a status column."""
        from app.models import SemanticControl

        assert hasattr(SemanticControl, "status"), \
            "SemanticControl must have a status column"

    def test_semantic_control_has_version_column(self):
        """TC-4.3: SemanticControl has a version column."""
        from app.models import SemanticControl

        assert hasattr(SemanticControl, "version"), \
            "SemanticControl must have a version column"

    def test_status_default_is_pending_validation(self):
        """TC-4.4: Status defaults to pending_validation when creating a SemanticControl."""
        from app.models import SemanticControl
        from uuid import uuid4

        record = SemanticControl(
            uuid=uuid4(),
            framework_name="test",
            control_id="TEST-1",
        )
        assert record.status == "pending_validation"

    def test_version_default_is_one(self):
        """TC-4.5: Version defaults to 1 when creating a SemanticControl."""
        from app.models import SemanticControl
        from uuid import uuid4

        record = SemanticControl(
            uuid=uuid4(),
            framework_name="test",
            control_id="TEST-1",
        )
        assert record.version == 1

    def test_bronze_record_id_nullable(self):
        """TC-4.6: bronze_record_id can be None (not required)."""
        from app.models import SemanticControl
        from uuid import uuid4

        record = SemanticControl(
            uuid=uuid4(),
            framework_name="test",
            control_id="TEST-1",
            bronze_record_id=None,
        )
        assert record.bronze_record_id is None

    def test_version_can_be_set_explicitly(self):
        """TC-4.7: Version can be set explicitly (not just default)."""
        from app.models import SemanticControl
        from uuid import uuid4

        record = SemanticControl(
            uuid=uuid4(),
            framework_name="test",
            control_id="TEST-1",
            version=3,
        )
        assert record.version == 3

    def test_status_can_be_set_explicitly(self):
        """TC-4.8: Status can be set explicitly to other values."""
        from app.models import SemanticControl
        from uuid import uuid4

        record = SemanticControl(
            uuid=uuid4(),
            framework_name="test",
            control_id="TEST-1",
            status="approved",
        )
        assert record.status == "approved"


# ==============================================================================
# Version Auto-Increment Tests
# ==============================================================================


class TestVersionAutoIncrement:
    """Test that version auto-increments via before_insert event."""

    def test_version_increments_on_insert(self, mock_db_session):
        """TC-4.9: When version_obligation is called, the new version has version=N+1."""
        from app.models import SemanticControl
        from app.services.silver_layer import version_obligation
        from uuid import uuid4

        existing_uuid = uuid4()
        existing = SemanticControl(
            uuid=existing_uuid,
            framework_name="de-jure",
            control_id="AC-1",
            objective_text="Original text",
            statement_text="Original text",
            action_verb="limit",
            subject_noun="access",
            version=1,
        )
        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = existing

        from app.schemas.obligation import Obligation
        new_obligation = Obligation(
            id="AC-1",
            prose="Updated text for the obligation.",
            action_verb="limit",
            subject_noun="system access",
            clause_ref="Section 3.1",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = version_obligation("AC-1", new_obligation, mock_db_session)

        assert result is not None
        # The newly created record should have been added to the session
        # The service should have set version = existing.version + 1 = 2
        add_calls = [c for c in mock_db_session.add.call_args_list]
        assert len(add_calls) > 0
        new_record = add_calls[-1][0][0]
        assert new_record.version == 2

    def test_version_increments_correctly_from_version_2(self, mock_db_session):
        """TC-4.10: Version increments correctly when starting from version > 1."""
        from app.models import SemanticControl
        from app.services.silver_layer import version_obligation
        from uuid import uuid4

        existing_uuid = uuid4()
        existing = SemanticControl(
            uuid=existing_uuid,
            framework_name="de-jure",
            control_id="AC-1",
            objective_text="V2 text",
            statement_text="V2 text",
            action_verb="monitor",
            subject_noun="access",
            version=2,
        )
        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = existing

        from app.schemas.obligation import Obligation
        new_obligation = Obligation(
            id="AC-1",
            prose="V3 text",
            action_verb="monitor",
            subject_noun="access",
            clause_ref="Section 3.1",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = version_obligation("AC-1", new_obligation, mock_db_session)

        add_calls = [c for c in mock_db_session.add.call_args_list]
        new_record = add_calls[-1][0][0]
        assert new_record.version == 3


# ==============================================================================
# Service Layer: write_silver_record
# ==============================================================================


class TestWriteSilverRecord:
    """Test write_silver_record service function."""

    def test_write_silver_record_inserts_row(self, mock_db_session, sample_obligation):
        """TC-4.11: write_silver_record calls session.add with a SemanticControl."""
        from app.services.silver_layer import write_silver_record

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        assert result is not None
        assert mock_db_session.add.called

    def test_write_silver_record_sets_framework_name(self, mock_db_session, sample_obligation):
        """TC-4.12: write_silver_record sets framework_name='de-jure'."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        # Check the SemanticControl that was created
        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        assert len(semantic_adds) == 1
        record = semantic_adds[0][0][0]
        assert record.framework_name == "de-jure"

    def test_write_silver_record_maps_control_id(self, mock_db_session, sample_obligation):
        """TC-4.13: write_silver_record maps obligation.id to control_id."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        assert len(semantic_adds) == 1
        record = semantic_adds[0][0][0]
        assert record.control_id == "AC-1"

    def test_write_silver_record_maps_objective_text(self, mock_db_session, sample_obligation):
        """TC-4.14: write_silver_record maps obligation.prose to objective_text."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        assert len(semantic_adds) == 1
        record = semantic_adds[0][0][0]
        assert record.objective_text == "The organization must limit information system access to authorized users."

    def test_write_silver_record_maps_statement_text(self, mock_db_session, sample_obligation):
        """TC-4.15: write_silver_record maps obligation.prose to statement_text."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.statement_text == record.objective_text

    def test_write_silver_record_maps_action_verb(self, mock_db_session, sample_obligation):
        """TC-4.16: write_silver_record maps obligation.action_verb."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.action_verb == "limit"

    def test_write_silver_record_maps_subject_noun(self, mock_db_session, sample_obligation):
        """TC-4.17: write_silver_record maps obligation.subject_noun."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.subject_noun == "information system access"

    def test_write_silver_record_sets_status_pending_validation(self, mock_db_session, sample_obligation):
        """TC-4.18: write_silver_record sets status='pending_validation'."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.status == "pending_validation"

    def test_write_silver_record_sets_version_one(self, mock_db_session, sample_obligation):
        """TC-4.19: write_silver_record sets version=1 for new records."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.version == 1

    def test_write_silver_record_sets_bronze_record_id_fk(self, mock_db_session, sample_obligation, bronze_record_id):
        """TC-4.20: write_silver_record sets bronze_record_id FK when provided."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(
                sample_obligation,
                mock_db_session,
                bronze_record_id=bronze_record_id,
            )

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.bronze_record_id is not None

    def test_write_silver_record_skips_bronze_record_id_when_none(self, mock_db_session, sample_obligation):
        """TC-4.21: write_silver_record does not set bronze_record_id when not provided."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        record = semantic_adds[0][0][0]
        assert record.bronze_record_id is None

    def test_write_silver_record_returns_semantic_control(self, mock_db_session, sample_obligation):
        """TC-4.22: write_silver_record returns the created SemanticControl object."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(sample_obligation, mock_db_session)

        assert isinstance(result, SemanticControl)

    def test_write_silver_record_calls_commit(self, mock_db_session, sample_obligation):
        """TC-4.23: write_silver_record calls session.commit()."""
        from app.services.silver_layer import write_silver_record

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            write_silver_record(sample_obligation, mock_db_session)

        assert mock_db_session.commit.called


# ==============================================================================
# Service Layer: write_batch_silver_records
# ==============================================================================


class TestWriteBatchSilverRecords:
    """Test write_batch_silver_records service function."""

    def test_write_batch_inserts_multiple_rows(self, mock_db_session, obligations_list):
        """TC-4.24: write_batch_silver_records inserts one row per obligation."""
        from app.services.silver_layer import write_batch_silver_records
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_batch_silver_records(obligations_list, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        assert len(semantic_adds) == 2

    def test_write_batch_all_records_have_framework_name(self, mock_db_session, obligations_list):
        """TC-4.25: All batch records have framework_name='de-jure'."""
        from app.services.silver_layer import write_batch_silver_records
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_batch_silver_records(obligations_list, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        for call_obj in semantic_adds:
            assert call_obj[0][0].framework_name == "de-jure"

    def test_write_batch_all_records_have_status(self, mock_db_session, obligations_list):
        """TC-4.26: All batch records have status='pending_validation'."""
        from app.services.silver_layer import write_batch_silver_records
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_batch_silver_records(obligations_list, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        for call_obj in semantic_adds:
            assert call_obj[0][0].status == "pending_validation"

    def test_write_batch_empty_list_does_nothing(self, mock_db_session):
        """TC-4.27: write_batch_silver_records with empty list does not call add."""
        from app.services.silver_layer import write_batch_silver_records

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_batch_silver_records([], mock_db_session)

        assert result == []
        # add should not be called for empty list
        mock_db_session.add.assert_not_called()

    def test_write_batch_returns_list_of_semantic_controls(self, mock_db_session, obligations_list):
        """TC-4.28: write_batch_silver_records returns a list of SemanticControl objects."""
        from app.services.silver_layer import write_batch_silver_records
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_batch_silver_records(obligations_list, mock_db_session)

        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert isinstance(item, SemanticControl)

    def test_write_batch_sets_bronze_record_id_for_all(self, mock_db_session, obligations_list, bronze_record_id):
        """TC-4.29: write_batch_silver_records sets bronze_record_id on all records."""
        from app.services.silver_layer import write_batch_silver_records
        from app.models import SemanticControl

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_batch_silver_records(
                obligations_list, mock_db_session,
                bronze_record_id=bronze_record_id,
            )

        add_calls = mock_db_session.add.call_args_list
        semantic_adds = [
            c for c in add_calls if isinstance(c[0][0], SemanticControl)
        ]
        for call_obj in semantic_adds:
            assert call_obj[0][0].bronze_record_id is not None


# ==============================================================================
# Service Layer: get_semantic_control
# ==============================================================================


class TestGetSemanticControl:
    """Test get_semantic_control service function."""

    def test_get_semantic_control_returns_record(self, mock_db_session):
        """TC-4.30: get_semantic_control returns a SemanticControl when found."""
        from app.models import SemanticControl
        from app.services.silver_layer import get_semantic_control
        from uuid import uuid4

        expected = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            objective_text="Test obligation.",
            status="pending_validation",
            version=1,
        )
        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = expected

        result = get_semantic_control("AC-1", mock_db_session)

        assert result is not None
        assert result.control_id == "AC-1"

    def test_get_semantic_control_returns_none_when_not_found(self, mock_db_session):
        """TC-4.31: get_semantic_control returns None when no record matches."""
        from app.services.silver_layer import get_semantic_control

        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = None

        result = get_semantic_control("NONEXISTENT", mock_db_session)

        assert result is None

    def test_get_semantic_control_queries_by_control_id(self, mock_db_session):
        """TC-4.32: get_semantic_control queries using the control_id parameter."""
        from app.services.silver_layer import get_semantic_control

        mock_db_session.query.return_value.filter.return_value.filter.return_value.first.return_value = None

        get_semantic_control("AC-42", mock_db_session)

        # Verify filter was called with control_id
        mock_db_session.query.assert_called()


# ==============================================================================
# Service Layer: version_obligation
# ==============================================================================


class TestVersionObligation:
    """Test version_obligation service function."""

    def test_version_obligation_creates_new_record(self, mock_db_session):
        """TC-4.33: version_obligation creates a new SemanticControl row."""
        from app.models import SemanticControl
        from app.services.silver_layer import version_obligation
        from uuid import uuid4

        existing = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            objective_text="V1 text",
            statement_text="V1 text",
            action_verb="limit",
            subject_noun="access",
            version=1,
        )
        mock_db_session.query.return_value.filter.return_value.filter.return_value.first.return_value = existing

        from app.schemas.obligation import Obligation
        new_obligation = Obligation(
            id="AC-1",
            prose="V2 text",
            action_verb="limit",
            subject_noun="access",
            clause_ref="Section 3.1",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = version_obligation("AC-1", new_obligation, mock_db_session)

        assert result is not None

    def test_version_obligation_returns_none_when_existing_not_found(self, mock_db_session):
        """TC-4.34: version_obligation returns None when no existing record is found."""
        from app.services.silver_layer import version_obligation

        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = None

        from app.schemas.obligation import Obligation
        new_obligation = Obligation(
            id="AC-1",
            prose="V2 text",
            action_verb="limit",
            subject_noun="access",
            clause_ref="Section 3.1",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = version_obligation("AC-1", new_obligation, mock_db_session)

        assert result is None

    def test_version_obligation_sets_new_objective_text(self, mock_db_session):
        """TC-4.35: version_obligation sets the new obligation's prose as objective_text."""
        from app.models import SemanticControl
        from app.services.silver_layer import version_obligation
        from uuid import uuid4

        existing = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            objective_text="Old text",
            statement_text="Old text",
            action_verb="limit",
            subject_noun="access",
            version=1,
        )
        mock_db_session.query.return_value.filter.return_value.filter.return_value.first.return_value = existing

        from app.schemas.obligation import Obligation
        new_obligation = Obligation(
            id="AC-1",
            prose="Brand new objective text.",
            action_verb="monitor",
            subject_noun="events",
            clause_ref="Section 4.0",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = version_obligation("AC-1", new_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        new_record = add_calls[-1][0][0]
        assert new_record.objective_text == "Brand new objective text."

    def test_version_obligation_carries_bronze_record_id(self, mock_db_session):
        """TC-4.36: version_obligation copies bronze_record_id from the existing record."""
        from app.models import SemanticControl
        from app.services.silver_layer import version_obligation
        from uuid import uuid4

        existing_uuid = uuid4()
        existing = SemanticControl(
            uuid=existing_uuid,
            framework_name="de-jure",
            control_id="AC-1",
            objective_text="V1",
            statement_text="V1",
            action_verb="limit",
            subject_noun="access",
            version=1,
            bronze_record_id=uuid4(),
        )
        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = existing

        from app.schemas.obligation import Obligation
        new_obligation = Obligation(
            id="AC-1",
            prose="V2",
            action_verb="limit",
            subject_noun="access",
            clause_ref="Section 3.1",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = version_obligation("AC-1", new_obligation, mock_db_session)

        add_calls = mock_db_session.add.call_args_list
        new_record = add_calls[-1][0][0]
        assert new_record.bronze_record_id is not None
        assert new_record.bronze_record_id == existing.bronze_record_id


# ==============================================================================
# API Endpoint Tests
# ==============================================================================


class TestSemanticAPIEndpoint:
    """Tests for POST /api/v1/semantic endpoint."""

    @pytest.fixture
    def app_with_semantic_router(self):
        """Create a FastAPI app with the semantic router mounted."""
        if not HAS_FASTAPI:
            pytest.skip("fastapi not installed")
        from app.api.semantic import router as semantic_router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(semantic_router, prefix="/api/v1/semantic", tags=["semantic"])
        return app

    @pytest.fixture
    def client(self, app_with_semantic_router):
        """TestClient wrapping the app with the semantic router."""
        if not HAS_FASTAPI:
            pytest.skip("fastapi not installed")
        return TestClient(app_with_semantic_router)

    def test_endpoint_returns_200_on_success(self, client, sample_obligation_dict):
        """TC-4.37: POST /api/v1/semantic returns HTTP 200 on successful write."""
        from uuid import uuid4
        from app.models import SemanticControl

        mock_record = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            status="pending_validation",
            version=1,
        )

        with patch(
            "app.api.semantic.write_silver_record",
            return_value=mock_record,
        ):
            resp = client.post(
                "/api/v1/semantic",
                json={
                    "obligation": sample_obligation_dict,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert "id" in body
        assert body["status"] == "pending_validation"
        assert body["version"] == 1

    def test_endpoint_includes_bronze_record_id_in_response(self, client, sample_obligation_dict, bronze_record_id):
        """TC-4.38: Response includes bronze_record_id when provided."""
        from uuid import uuid4
        from app.models import SemanticControl

        mock_record = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            status="pending_validation",
            version=1,
            bronze_record_id=uuid4(),
        )

        with patch(
            "app.api.semantic.write_silver_record",
            return_value=mock_record,
        ):
            resp = client.post(
                "/api/v1/semantic",
                json={
                    "obligation": sample_obligation_dict,
                    "bronze_record_id": bronze_record_id,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert "bronze_record_id" in body

    def test_endpoint_rejects_missing_obligation(self, client):
        """TC-4.39: POST without obligation field returns HTTP 422."""
        resp = client.post(
            "/api/v1/semantic",
            json={},
        )
        assert resp.status_code == 422

    def test_endpoint_rejects_empty_obligation(self, client):
        """TC-4.40: POST with empty obligation object returns HTTP 422."""
        resp = client.post(
            "/api/v1/semantic",
            json={"obligation": {}},
        )
        assert resp.status_code == 422

    def test_endpoint_handles_service_error(self, client, sample_obligation_dict):
        """TC-4.41: Service errors return HTTP 500."""
        with patch(
            "app.api.semantic.write_silver_record",
            side_effect=RuntimeError("database connection refused"),
        ):
            resp = client.post(
                "/api/v1/semantic",
                json={"obligation": sample_obligation_dict},
            )

        assert resp.status_code == 500
        body = resp.json()
        assert "detail" in body

    def test_endpoint_passes_bronze_record_id_to_service(self, client, sample_obligation_dict, bronze_record_id):
        """TC-4.42: bronze_record_id is passed through to the service layer."""
        from uuid import uuid4
        from app.models import SemanticControl

        mock_record = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            status="pending_validation",
            version=1,
        )

        with patch(
            "app.api.semantic.write_silver_record",
            return_value=mock_record,
        ) as mock_service:
            resp = client.post(
                "/api/v1/semantic",
                json={
                    "obligation": sample_obligation_dict,
                    "bronze_record_id": bronze_record_id,
                },
            )

        assert resp.status_code == 200
        call_kwargs = mock_service.call_args[1]
        # The API endpoint converts the string to a UUID object
        from uuid import UUID
        passed_id = call_kwargs["bronze_record_id"]
        if isinstance(passed_id, UUID):
            passed_id = str(passed_id)
        assert passed_id == bronze_record_id

    def test_endpoint_optional_bronze_record_id(self, client, sample_obligation_dict):
        """TC-4.43: bronze_record_id is optional - omission should not cause error."""
        from uuid import uuid4
        from app.models import SemanticControl

        mock_record = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            status="pending_validation",
            version=1,
            bronze_record_id=None,
        )

        with patch(
            "app.api.semantic.write_silver_record",
            return_value=mock_record,
        ) as mock_service:
            resp = client.post(
                "/api/v1/semantic",
                json={"obligation": sample_obligation_dict},
            )

        assert resp.status_code == 200
        call_kwargs = mock_service.call_args[1]
        assert call_kwargs.get("bronze_record_id") is None

    def test_endpoint_response_serialization(self, client, sample_obligation_dict):
        """TC-4.44: Response is a valid JSON with serializable fields."""
        from uuid import uuid4
        from app.models import SemanticControl

        mock_record = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="AC-1",
            status="pending_validation",
            version=1,
        )

        with patch(
            "app.api.semantic.write_silver_record",
            return_value=mock_record,
        ):
            resp = client.post(
                "/api/v1/semantic",
                json={"obligation": sample_obligation_dict},
            )

        body = resp.json()
        # Verify the response is a flat dict with string keys
        assert isinstance(body, dict)
        assert isinstance(body["id"], str)
        assert isinstance(body["status"], str)
        assert isinstance(body["version"], int)


# ==============================================================================
# Edge Cases
# ==============================================================================


class TestEdgeCases:
    """Edge case tests beyond acceptance criteria."""

    def test_write_silver_record_with_special_characters_in_prose(self, mock_db_session):
        """Edge case: prose with special characters is stored correctly."""
        from app.services.silver_layer import write_silver_record
        from app.models import SemanticControl
        from app.schemas.obligation import Obligation

        special_obligation = Obligation(
            id="SPECIAL-1",
            prose="The organization must \"limit\" access & ensure compliance with §12.3.",
            action_verb="limit",
            subject_noun="access",
            clause_ref="Section 12.3",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(special_obligation, mock_db_session)

        assert result is not None
        add_calls = mock_db_session.add.call_args_list
        record = add_calls[-1][0][0]
        assert record.objective_text == special_obligation.prose

    def test_version_obligation_with_no_query_result_returns_none(self, mock_db_session):
        """Edge case: version_obligation when query returns None."""
        from app.services.silver_layer import version_obligation

        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = None

        from app.schemas.obligation import Obligation
        result = version_obligation(
            "NONEXISTENT",
            Obligation(
                id="NONEXISTENT",
                prose="New text",
                action_verb="test",
                subject_noun="noun",
                clause_ref="Section 1",
            ),
            mock_db_session,
        )
        assert result is None

    def test_get_semantic_control_handles_db_error(self, mock_db_session):
        """Edge case: get_semantic_control re-raises DB errors."""
        from app.services.silver_layer import get_semantic_control

        mock_db_session.query.side_effect = RuntimeError("connection timeout")

        with pytest.raises(RuntimeError, match="connection timeout"):
            get_semantic_control("AC-1", mock_db_session)

    def test_write_silver_record_handles_db_error(self, mock_db_session, sample_obligation):
        """Edge case: write_silver_record re-raises DB errors."""
        from app.services.silver_layer import write_silver_record

        mock_db_session.add.side_effect = RuntimeError("disk full")

        with pytest.raises(RuntimeError, match="disk full"):
            write_silver_record(sample_obligation, mock_db_session)

    def test_empty_obligation_id_is_stored(self, mock_db_session):
        """Edge case: obligation with empty string id."""
        from app.services.silver_layer import write_silver_record
        from app.schemas.obligation import Obligation

        empty_id_obligation = Obligation(
            id="",
            prose="Test obligation.",
            action_verb="test",
            subject_noun="test noun",
            clause_ref="Section 1",
        )

        with patch(
            "app.services.silver_layer.get_db_session",
            return_value=mock_db_session,
        ):
            result = write_silver_record(empty_id_obligation, mock_db_session)

        # Should still create a record even with empty ID (validation is at Pydantic level)
        assert result is not None

    def test_to_dict_includes_new_fields(self):
        """Edge case: SemanticControl.to_dict() includes status, version, bronze_record_id."""
        from app.models import SemanticControl
        from uuid import uuid4

        record = SemanticControl(
            uuid=uuid4(),
            framework_name="de-jure",
            control_id="TEST-1",
            status="pending_validation",
            version=2,
            bronze_record_id=uuid4(),
        )
        d = record.to_dict()

        assert "status" in d
        assert "version" in d
        assert "bronze_record_id" in d
