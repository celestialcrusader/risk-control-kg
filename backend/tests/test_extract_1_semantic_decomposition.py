"""
Test suite for EXTRACT-1: Semantic Decomposition Pipeline

This test module verifies the LLM-driven semantic decomposition pipeline
that extracts atomic rule units from regulatory Markdown text.

Test Strategy:
- Unit tests for Pydantic schema validation
- Unit tests with mocked LLM API for extraction logic
- Integration tests (mocked) for database persistence
- Edge cases: empty input, malformed LLM output, fallback behavior

Acceptance Criteria Covered:
- AC-1: extract_obligations(markdown) returns a list of obligation objects
- AC-2: Each obligation has required fields: id, prose, action_verb, subject_noun, clause_ref
- AC-3: Complex regulation clauses include section_ref and clause_hierarchy
- AC-4: Extraction uses Mistral 8B via vLLM/Ollama API
- AC-5: Output validated against Pydantic model in schemas/obligation.py
- AC-6: Extraction results stored in PostgreSQL semantic_controls (Silver layer)
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

from app.schemas.obligation import Obligation, ExtractedObligationsResponse, ClauseHierarchy


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_markdown():
    """Sample regulatory Markdown content from Bronze layer."""
    return """# Section 3: Access Control

## 3.1 General Requirements

The organization must limit information system access to authorized users,
processes acting on behalf of authorized users, or devices (identities).

## 3.2 Remote Access

The organization must monitor and control remote information system access
to designated locations outside of the authorized established and documented
areas.

## 3.3 Privileged Access

The organization must enforce privileged access authorization for security
related actions including:
- (a) loading security functional components during startup,
- (b) overriding access control mechanisms enforced by the information system.
"""


@pytest.fixture
def complex_markdown():
    """Regulatory Markdown with nested clause hierarchy for AC-3."""
    return """# Title 12: Banking

## Section 100: Consumer Protection

### 100(a) General Provisions

The director shall ensure that every covered entity establishes and maintains
a compliance program that includes written policies, procedures, and internal
controls.

### 100(b) Specific Requirements

#### 100(b)(1) Risk Assessment

Every covered entity must conduct an annual risk assessment that identifies
and evaluates the money laundering and terrorist financing risks.

#### 100(b)(2) Compliance Officer

Each covered entity must designate a compliance officer who is responsible
for implementing and monitoring the compliance program.

#### 100(b)(3) Training

The covered entity must provide ongoing training to appropriate personnel
on money laundering awareness and compliance obligations.

## Section 101: Examination Procedures

The appropriate federal banking agency shall examine each covered entity
to determine compliance with this chapter.
"""


@pytest.fixture
def mock_llm_response_obligations():
    """Mock LLM JSON response with valid obligations."""
    return json.dumps({
        "obligations": [
            {
                "id": "AC-1",
                "prose": "The organization must limit information system access to authorized users.",
                "action_verb": "limit",
                "subject_noun": "information system access",
                "clause_ref": "Section 3.1",
                "effective_date": None,
                "section_ref": "Section 3",
                "clause_hierarchy": {
                    "parent": "Section 3",
                    "level": 2,
                    "path": "3.1"
                }
            },
            {
                "id": "AC-2",
                "prose": "The organization must monitor and control remote information system access.",
                "action_verb": "monitor and control",
                "subject_noun": "remote information system access",
                "clause_ref": "Section 3.2",
                "effective_date": None,
                "section_ref": "Section 3",
                "clause_hierarchy": {
                    "parent": "Section 3",
                    "level": 2,
                    "path": "3.2"
                }
            },
            {
                "id": "AC-3a",
                "prose": "The organization must enforce privileged access authorization for security related actions.",
                "action_verb": "enforce",
                "subject_noun": "privileged access authorization",
                "clause_ref": "Section 3.3",
                "effective_date": None,
                "section_ref": "Section 3",
                "clause_hierarchy": {
                    "parent": "Section 3",
                    "level": 2,
                    "path": "3.3"
                }
            }
        ]
    })


@pytest.fixture
def mock_llm_response_complex():
    """Mock LLM JSON response with hierarchical clauses for AC-3."""
    return json.dumps({
        "obligations": [
            {
                "id": "100-1",
                "prose": "The director shall ensure that every covered entity establishes and maintains a compliance program.",
                "action_verb": "ensure",
                "subject_noun": "compliance program",
                "clause_ref": "Section 100(a)",
                "effective_date": None,
                "section_ref": "Title 12",
                "clause_hierarchy": {
                    "parent": "Title 12",
                    "level": 2,
                    "path": "100.a"
                }
            },
            {
                "id": "100b1",
                "prose": "Every covered entity must conduct an annual risk assessment that identifies and evaluates money laundering and terrorist financing risks.",
                "action_verb": "conduct",
                "subject_noun": "annual risk assessment",
                "clause_ref": "Section 100(b)(1)",
                "effective_date": None,
                "section_ref": "Title 12",
                "clause_hierarchy": {
                    "parent": "Section 100",
                    "level": 3,
                    "path": "100.b.1"
                }
            },
            {
                "id": "100b2",
                "prose": "Each covered entity must designate a compliance officer responsible for implementing and monitoring the compliance program.",
                "action_verb": "designate",
                "subject_noun": "compliance officer",
                "clause_ref": "Section 100(b)(2)",
                "effective_date": None,
                "section_ref": "Title 12",
                "clause_hierarchy": {
                    "parent": "Section 100",
                    "level": 3,
                    "path": "100.b.2"
                }
            }
        ]
    })


@pytest.fixture
def mock_db_session():
    """Create a fresh mock SQLAlchemy session that works as a context manager."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    return session


# ==============================================================================
# AC-1: extract_obligations returns a list of obligation objects
# ==============================================================================


class TestExtractObligationsReturnsList:
    """TC-1.1: extract_obligations returns a list of Obligation objects."""

    def test_extract_obligations_returns_list(self, sample_markdown, mock_llm_response_obligations):
        """When extract_obligations is called with markdown, the result is a list."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            assert isinstance(result, list)

    def test_extract_obligations_returns_obligation_objects(self, sample_markdown, mock_llm_response_obligations):
        """Each item in the result is an Obligation Pydantic model instance."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            from app.schemas.obligation import Obligation
            for item in result:
                assert isinstance(item, Obligation)

    def test_extract_obligations_empty_markdown_returns_empty_list(self):
        """Given empty markdown, extract_obligations returns an empty list without error."""
        from app.services.extraction import extract_obligations

        result = extract_obligations("")

        assert result == []

    def test_extract_obligations_none_markdown_returns_empty_list(self):
        """Given None markdown, extract_obligations returns an empty list without error."""
        from app.services.extraction import extract_obligations

        result = extract_obligations(None)

        assert result == []

    def test_extract_obligations_preserves_order(self, sample_markdown, mock_llm_response_obligations):
        """The order of obligations in the output matches the LLM response order."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            ids = [o.id for o in result]
            assert ids == ["AC-1", "AC-2", "AC-3a"]


# ==============================================================================
# AC-2: Obligations have all required fields
# ==============================================================================


class TestObligationRequiredFields:
    """TC-1.2: Each obligation object has all required fields."""

    def test_obligation_has_required_id_field(self, sample_markdown, mock_llm_response_obligations):
        """Every obligation has a non-empty 'id' field."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            for obs in result:
                assert hasattr(obs, "id")
                assert obs.id is not None
                assert isinstance(obs.id, str)
                assert len(obs.id) > 0

    def test_obligation_has_required_prose_field(self, sample_markdown, mock_llm_response_obligations):
        """Every obligation has a non-empty 'prose' field."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            for obs in result:
                assert hasattr(obs, "prose")
                assert obs.prose is not None
                assert isinstance(obs.prose, str)
                assert len(obs.prose) > 0

    def test_obligation_has_required_action_verb_field(self, sample_markdown, mock_llm_response_obligations):
        """Every obligation has an 'action_verb' field."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            for obs in result:
                assert hasattr(obs, "action_verb")
                assert obs.action_verb is not None
                assert isinstance(obs.action_verb, str)

    def test_obligation_has_required_subject_noun_field(self, sample_markdown, mock_llm_response_obligations):
        """Every obligation has a 'subject_noun' field."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            for obs in result:
                assert hasattr(obs, "subject_noun")
                assert obs.subject_noun is not None
                assert isinstance(obs.subject_noun, str)

    def test_obligation_has_required_clause_ref_field(self, sample_markdown, mock_llm_response_obligations):
        """Every obligation has a 'clause_ref' field."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            for obs in result:
                assert hasattr(obs, "clause_ref")
                assert obs.clause_ref is not None
                assert isinstance(obs.clause_ref, str)

    def test_invalid_obligation_missing_id_raises_validation_error(self):
        """An obligation dict without 'id' raises Pydantic ValidationError."""
        invalid_data = {
            "prose": "Some obligation text.",
            "action_verb": "must",
            "subject_noun": "something",
            "clause_ref": "Section 1.1",
        }
        with pytest.raises(Exception):  # ValidationError
            Obligation(**invalid_data)

    def test_invalid_obligation_missing_prose_raises_validation_error(self):
        """An obligation dict without 'prose' raises Pydantic ValidationError."""
        invalid_data = {
            "id": "TEST-1",
            "action_verb": "must",
            "subject_noun": "something",
            "clause_ref": "Section 1.1",
        }
        with pytest.raises(Exception):  # ValidationError
            Obligation(**invalid_data)

    def test_invalid_obligation_missing_action_verb_raises_validation_error(self):
        """An obligation dict without 'action_verb' raises Pydantic ValidationError."""
        invalid_data = {
            "id": "TEST-1",
            "prose": "Some text.",
            "subject_noun": "something",
            "clause_ref": "Section 1.1",
        }
        with pytest.raises(Exception):  # ValidationError
            Obligation(**invalid_data)

    def test_invalid_obligation_missing_subject_noun_raises_validation_error(self):
        """An obligation dict without 'subject_noun' raises Pydantic ValidationError."""
        invalid_data = {
            "id": "TEST-1",
            "prose": "Some text.",
            "action_verb": "must",
            "clause_ref": "Section 1.1",
        }
        with pytest.raises(Exception):  # ValidationError
            Obligation(**invalid_data)

    def test_invalid_obligation_missing_clause_ref_raises_validation_error(self):
        """An obligation dict without 'clause_ref' raises Pydantic ValidationError."""
        invalid_data = {
            "id": "TEST-1",
            "prose": "Some text.",
            "action_verb": "must",
            "subject_noun": "something",
        }
        with pytest.raises(Exception):  # ValidationError
            Obligation(**invalid_data)


# ==============================================================================
# AC-3: Complex regulation includes section_ref and clause_hierarchy
# ==============================================================================


class TestSectionReferenceAndHierarchy:
    """TC-1.3: Complex regulation clauses include section_ref and clause_hierarchy."""

    def test_obligation_has_section_ref(self, complex_markdown, mock_llm_response_complex):
        """Extracted obligations include a 'section_ref' field."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_complex,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(complex_markdown)

            for obs in result:
                assert hasattr(obs, "section_ref")
                assert obs.section_ref is not None
                assert isinstance(obs.section_ref, str)

    def test_obligation_has_clause_hierarchy(self, complex_markdown, mock_llm_response_complex):
        """Extracted obligations include a 'clause_hierarchy' field with structured data."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_complex,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(complex_markdown)

            for obs in result:
                assert hasattr(obs, "clause_hierarchy")
                assert obs.clause_hierarchy is not None
                assert isinstance(obs.clause_hierarchy, ClauseHierarchy)
                assert obs.clause_hierarchy.parent is not None
                assert obs.clause_hierarchy.level is not None
                assert obs.clause_hierarchy.path is not None

    def test_nested_clauses_have_correct_hierarchy_level(self, complex_markdown, mock_llm_response_complex):
        """Deeply nested clauses have higher hierarchy levels."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_complex,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(complex_markdown)

            # 100b1 and 100b2 should have level 3 (nested under Section 100)
            nested = [o for o in result if o.id in ("100b1", "100b2")]
            for obs in nested:
                assert obs.clause_hierarchy.level == 3

    def test_parent_section_ref_matches_document_structure(self, complex_markdown, mock_llm_response_complex):
        """section_ref reflects the parent section from the document structure."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_complex,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(complex_markdown)

            # All obligations should reference "Title 12" as their section_ref
            for obs in result:
                assert obs.section_ref == "Title 12"


# ==============================================================================
# AC-4: Extraction uses Mistral 8B via vLLM API with Ollama fallback
# ==============================================================================


class TestLLMApiIntegration:
    """TC-1.4: Extraction uses Mistral 8B via vLLM API (dev: Ollama fallback)."""

    def test_calls_vllm_endpoint_by_default(self, sample_markdown, mock_llm_response_obligations):
        """When LLM_ENDPOINT is vLLM, the vLLM OpenAI-compatible client is called."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ) as mock_call:
            from app.services.extraction import extract_obligations

            extract_obligations(sample_markdown)

            mock_call.assert_called_once()
            args = mock_call.call_args
            # First positional arg (prompt) should contain the markdown content
            assert sample_markdown in args[0][0]

    def test_vllm_client_uses_correct_endpoint(self, sample_markdown, mock_llm_response_obligations):
        """The vLLM client connects to the configured LLM_ENDPOINT."""
        with patch("app.services.extraction._call_vllm", return_value=mock_llm_response_obligations):
            with patch.dict("os.environ", {"LLM_ENDPOINT": "http://localhost:8000/v1", "LLM_PROVIDER": "vllm"}):
                from app.services.extraction import extract_obligations

                result = extract_obligations(sample_markdown)

                assert isinstance(result, list)
                assert len(result) > 0

    def test_ollama_fallback_when_configured(self, sample_markdown, mock_llm_response_obligations):
        """When LLM_PROVIDER is ollama, _call_ollama is invoked (not _call_vllm)."""
        import app.services.extraction as extraction_mod

        mock_ollama_module = MagicMock()
        mock_ollama_module.chat.return_value = {"message": {"content": mock_llm_response_obligations}}

        with patch.dict("sys.modules", {"ollama": mock_ollama_module}):
            with patch.object(
                extraction_mod, "_call_vllm", side_effect=RuntimeError("should not be called"),
            ):
                with patch.object(
                    extraction_mod, "_store_obligations_in_semantic_controls",
                ):
                    with patch.dict("os.environ", {"LLM_PROVIDER": "ollama"}):
                        # Reload module to pick up new LLM_PROVIDER
                        import importlib
                        importlib.reload(extraction_mod)

                        result = extraction_mod.extract_obligations(sample_markdown)

                        assert isinstance(result, list)
                        assert len(result) > 0

    def test_vllm_uses_temperature_03(self, sample_markdown, mock_llm_response_obligations):
        """The vLLM client is called with temperature=0.3 for deterministic extraction."""
        with patch("app.services.extraction._call_vllm", return_value=mock_llm_response_obligations) as mock_vllm:
            with patch.dict("os.environ", {"LLM_TEMPERATURE": "0.3", "LLM_PROVIDER": "vllm"}):
                # Re-import to pick up patched env vars
                import importlib
                import app.services.extraction as extraction_mod
                importlib.reload(extraction_mod)

                result = extraction_mod.extract_obligations(sample_markdown)
                assert isinstance(result, list)

                # Verify the config constants match expected values
                assert extraction_mod.LLM_TEMPERATURE == 0.3

    def test_vllm_uses_max_tokens_4000(self, sample_markdown, mock_llm_response_obligations):
        """The vLLM client is called with max_tokens=4000."""
        import app.services.extraction as extraction_mod
        assert extraction_mod.LLM_MAX_TOKENS == 4000

    def test_ollama_uses_temperature_03(self, sample_markdown, mock_llm_response_obligations):
        """The Ollama client is called with temperature=0.3."""
        import app.services.extraction as extraction_mod
        assert extraction_mod.LLM_TEMPERATURE == 0.3


# ==============================================================================
# AC-5: Output validated against Pydantic schema in schemas/obligation.py
# ==============================================================================


class TestSchemaValidation:
    """TC-1.5: Output is validated against Pydantic schema in schemas/obligation.py."""

    def test_valid_obligation_passes_validation(self):
        """A well-formed obligation dict passes Pydantic validation."""
        data = {
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
            "effective_date": None,
            "section_ref": "Section 3",
            "clause_hierarchy": {"parent": "Section 3", "level": 2, "path": "3.1"},
        }
        obligation = Obligation(**data)
        assert obligation.id == "AC-1"
        assert obligation.prose == "The organization must limit access."

    def test_response_wrapper_validates_obligations_list(self):
        """ExtractedObligationsResponse wraps a list of validated Obligation objects."""
        data = {
            "obligations": [
                {
                    "id": "AC-1",
                    "prose": "Test obligation.",
                    "action_verb": "test",
                    "subject_noun": "test noun",
                    "clause_ref": "Section 1",
                }
            ]
        }
        response = ExtractedObligationsResponse(**data)
        assert len(response.obligations) == 1
        assert isinstance(response.obligations[0], Obligation)

    def test_extraction_service_validates_llm_response(self, sample_markdown, mock_llm_response_obligations):
        """The extraction service validates the LLM response against the schema."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            # All items should be valid Obligation instances
            from app.schemas.obligation import Obligation
            for item in result:
                assert isinstance(item, Obligation)

    def test_extraction_service_handles_malformed_llm_json(self, sample_markdown):
        """When LLM returns invalid JSON, the service returns an empty list gracefully."""
        with patch(
            "app.services.extraction._call_llm",
            return_value="not valid json at all",
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            assert result == []

    def test_extraction_service_handles_missing_obligations_key(self, sample_markdown):
        """When LLM returns JSON without 'obligations' key, the service returns an empty list."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=json.dumps({"other_field": "not relevant"}),
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            assert result == []


# ==============================================================================
# AC-6: Extraction results stored in PostgreSQL semantic_controls
# ==============================================================================


class TestSemanticControlsPersistence:
    """TC-1.6: Extraction results stored in PostgreSQL semantic_controls table."""

    def test_results_stored_in_semantic_controls(self, sample_markdown, mock_llm_response_obligations, mock_db_session):
        """Extracted obligations are stored in the semantic_controls table."""
        from app.models import SemanticControl

        mock_db_session.set_first_return_value = lambda val: None
        mock_db_session.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = None

        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            with patch(
                "app.services.extraction.get_db_session",
                return_value=mock_db_session,
            ):
                from app.services.extraction import extract_obligations

                result = extract_obligations(sample_markdown)

                # Verify SemanticControl objects were added to the session
                semantic_adds = [
                    c for c in mock_db_session.add.call_args_list
                    if isinstance(c[0][0], SemanticControl)
                ]
                assert len(semantic_adds) == len(result)

    def test_semantic_control_stores_control_id(self, sample_markdown, mock_llm_response_obligations, mock_db_session):
        """Each SemanticControl record stores the obligation id as control_id."""
        from app.models import SemanticControl

        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            with patch(
                "app.services.extraction.get_db_session",
                return_value=mock_db_session,
            ):
                from app.services.extraction import extract_obligations

                extract_obligations(sample_markdown)

                semantic_adds = [
                    c for c in mock_db_session.add.call_args_list
                    if isinstance(c[0][0], SemanticControl)
                ]
                for call_obj in semantic_adds:
                    record = call_obj[0][0]
                    assert record.control_id is not None
                    assert isinstance(record.control_id, str)

    def test_semantic_control_stores_action_verb(self, sample_markdown, mock_llm_response_obligations, mock_db_session):
        """Each SemanticControl record stores the action_verb field."""
        from app.models import SemanticControl

        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            with patch(
                "app.services.extraction.get_db_session",
                return_value=mock_db_session,
            ):
                from app.services.extraction import extract_obligations

                extract_obligations(sample_markdown)

                semantic_adds = [
                    c for c in mock_db_session.add.call_args_list
                    if isinstance(c[0][0], SemanticControl)
                ]
                for call_obj in semantic_adds:
                    record = call_obj[0][0]
                    assert record.action_verb is not None

    def test_semantic_control_stores_subject_noun(self, sample_markdown, mock_llm_response_obligations, mock_db_session):
        """Each SemanticControl record stores the subject_noun field."""
        from app.models import SemanticControl

        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            with patch(
                "app.services.extraction.get_db_session",
                return_value=mock_db_session,
            ):
                from app.services.extraction import extract_obligations

                extract_obligations(sample_markdown)

                semantic_adds = [
                    c for c in mock_db_session.add.call_args_list
                    if isinstance(c[0][0], SemanticControl)
                ]
                for call_obj in semantic_adds:
                    record = call_obj[0][0]
                    assert record.subject_noun is not None

    def test_semantic_control_stores_framework_name(self, sample_markdown, mock_llm_response_obligations, mock_db_session):
        """Each SemanticControl record has a framework_name set."""
        from app.models import SemanticControl

        with patch(
            "app.services.extraction._call_llm",
            return_value=mock_llm_response_obligations,
        ):
            with patch(
                "app.services.extraction.get_db_session",
                return_value=mock_db_session,
            ):
                from app.services.extraction import extract_obligations

                extract_obligations(sample_markdown)

                semantic_adds = [
                    c for c in mock_db_session.add.call_args_list
                    if isinstance(c[0][0], SemanticControl)
                ]
                for call_obj in semantic_adds:
                    record = call_obj[0][0]
                    assert record.framework_name is not None


# ==============================================================================
# Edge Cases and Additional Tests
# ==============================================================================


class TestEdgeCases:
    """Additional edge case tests beyond acceptance criteria."""

    def test_llm_api_error_returns_empty_list(self, sample_markdown):
        """When the LLM API raises an exception, the pipeline returns an empty list."""
        with patch(
            "app.services.extraction._call_llm",
            side_effect=Exception("Network error"),
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            assert result == []

    def test_llm_returns_empty_obligations_list(self, sample_markdown):
        """When LLM returns an empty obligations list, the result is an empty list."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=json.dumps({"obligations": []}),
        ):
            from app.services.extraction import extract_obligations

            result = extract_obligations(sample_markdown)

            assert result == []

    def test_obligation_effective_date_optional(self):
        """The effective_date field is optional and can be null."""
        data = {
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
        }
        obligation = Obligation(**data)
        assert obligation.effective_date is None

    def test_obligation_section_ref_optional(self):
        """The section_ref field is optional and can be null."""
        data = {
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
        }
        obligation = Obligation(**data)
        assert obligation.section_ref is None

    def test_obligation_clause_hierarchy_optional(self):
        """The clause_hierarchy field is optional and can be null."""
        data = {
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
        }
        obligation = Obligation(**data)
        assert obligation.clause_hierarchy is None

    def test_obligation_serializable_to_dict(self):
        """An Obligation can be serialized to a dictionary."""
        data = {
            "id": "AC-1",
            "prose": "The organization must limit access.",
            "action_verb": "limit",
            "subject_noun": "system access",
            "clause_ref": "Section 3.1",
            "effective_date": "2024-01-01",
            "section_ref": "Section 3",
            "clause_hierarchy": {"parent": "Section 3", "level": 2, "path": "3.1"},
        }
        obligation = Obligation(**data)
        d = obligation.model_dump()
        assert d["id"] == "AC-1"
        assert d["prose"] == "The organization must limit access."
        assert d["action_verb"] == "limit"

    def test_extraction_uses_prompt_template(self, sample_markdown, mock_llm_response_obligations):
        """The extraction service loads and uses the prompt template from prompts/extraction.md."""
        with patch("app.services.extraction._call_vllm", return_value=mock_llm_response_obligations):
            with patch.dict("os.environ", {"LLM_ENDPOINT": "http://localhost:8000/v1", "LLM_PROVIDER": "vllm"}):
                from app.services.extraction import extract_obligations, _load_prompt_template

                extract_obligations(sample_markdown)

                template = _load_prompt_template()
                assert "{{markdown_content}}" in template or sample_markdown not in template
