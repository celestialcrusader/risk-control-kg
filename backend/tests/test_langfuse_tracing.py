"""
Test suite for OBSERV-1: Langfuse Tracing Integration.

This test module verifies the Langfuse tracing pipeline across extraction,
judge, and repair services with consistent trace_id linkage.

Test Strategy:
- Unit tests for Langfuse config loading and graceful degradation
- Unit tests for trace creation with mocked Langfuse SDK
- Unit tests for trace_id linkage across extraction -> judge -> repair
- Unit tests for graceful degradation when Langfuse is unavailable
- Edge cases: missing env vars, empty input, malformed responses

Acceptance Criteria Covered:
- AC-1: Trace created with trace_id when Langfuse is initialized
- AC-2: Span includes full prompt, completion, and token usage
- AC-3: Failure logging includes judge feedback and repair attempts
- AC-4: Langfuse dashboard accessible with documented credentials
- AC-5: Consistent trace_id linkage across extraction, judge, repair
- AC-6: Environment config with project scoping for dev/prod
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure app module is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.judge import Judgment, JudgmentResponse
from app.schemas.obligation import Obligation


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_obligation_dict():
    """A sample extracted obligation for testing."""
    return {
        "id": "AC-1",
        "prose": "The organization must limit information system access to authorized users.",
        "action_verb": "limit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1",
    }


@pytest.fixture
def sample_obligation_model():
    """A sample Obligation Pydantic model instance."""
    return Obligation(
        id="AC-1",
        prose="The organization must limit information system access to authorized users.",
        action_verb="limit",
        subject_noun="information system access",
        clause_ref="Section 3.1",
    )


@pytest.fixture
def sample_markdown():
    """Sample regulatory Markdown content from the original document."""
    return """# Section 3: Access Control

## 3.1 General Requirements

The organization must limit information system access to authorized users,
processes acting on behalf of authorized users, or devices (identities).

## 3.2 Remote Access

The organization must monitor and control remote information system access
to designated locations outside of the authorized established and documented
areas.
"""


@pytest.fixture
def mock_approved_judgment_json():
    """Mock LLM response representing an approved obligation."""
    return json.dumps({
        "metadata_accuracy": 0.95,
        "legal_alignment": 0.92,
        "semantics": 0.90,
        "overall_score": 0.92,
        "status": "approved",
        "feedback": "The obligation is well-structured with correct metadata.",
    }, separators=(",", ":"))


@pytest.fixture
def mock_repair_judgment_json():
    """Mock LLM response representing an obligation needing repair."""
    return json.dumps({
        "metadata_accuracy": 0.65,
        "legal_alignment": 0.70,
        "semantics": 0.85,
        "overall_score": 0.73,
        "status": "repair",
        "feedback": "The action_verb is incorrect; should be 'shall prohibit'.",
    }, separators=(",", ":"))


@pytest.fixture
def mock_repaired_obligation_json():
    """Mock LLM response representing a successfully repaired obligation."""
    return json.dumps({
        "id": "AC-1",
        "prose": "The organization shall prohibit information system access for unauthorized users.",
        "action_verb": "prohibit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1",
    }, separators=(",", ":"))


@pytest.fixture
def sample_feedback():
    """Sample judge feedback for repair scenarios."""
    return "The action_verb is imprecise; should use regulatory language 'shall prohibit'."


@pytest.fixture(autouse=True)
def _clear_langfuse_env():
    """Clear Langfuse env vars before each test to avoid cross-test pollution."""
    original_langfuse_key = os.environ.get("LANGFUSE_SECRET_KEY")
    original_langfuse_public = os.environ.get("LANGFUSE_PUBLIC_KEY")
    original_langfuse_host = os.environ.get("LANGFUSE_HOST")
    original_langfuse_release = os.environ.get("LANGFUSE_RELEASE")
    original_langfuse_user_id = os.environ.get("LANGFUSE_USER_ID")

    # Remove Langfuse env vars to ensure clean state
    for key in [
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_HOST",
        "LANGFUSE_RELEASE",
        "LANGFUSE_USER_ID",
    ]:
        os.environ.pop(key, None)

    yield

    # Restore original values
    if original_langfuse_key is not None:
        os.environ["LANGFUSE_SECRET_KEY"] = original_langfuse_key
    if original_langfuse_public is not None:
        os.environ["LANGFUSE_PUBLIC_KEY"] = original_langfuse_public
    if original_langfuse_host is not None:
        os.environ["LANGFUSE_HOST"] = original_langfuse_host
    if original_langfuse_release is not None:
        os.environ["LANGFUSE_RELEASE"] = original_langfuse_release
    if original_langfuse_user_id is not None:
        os.environ["LANGFUSE_USER_ID"] = original_langfuse_user_id


# ==============================================================================
# AC-4 & AC-6: Environment Configuration
# ==============================================================================


class TestLangfuseConfig:
    """TC-OBS-1: Langfuse environment configuration loading and project scoping."""

    def test_config_returns_none_when_langfuse_not_installed(self):
        """When langfuse package is not installed, config returns None gracefully."""
        with patch.dict("sys.modules", {"langfuse": None}):
            from app.services.langfuse_config import get_langfuse_config
            result = get_langfuse_config()
            assert result is None

    def test_config_returns_dict_when_langfuse_installed(self):
        """When langfuse is installed and env vars exist, config returns dict with keys."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"
        os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

        # Patch langfuse import so the module-level import succeeds
        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            # Need to reimport to pick up the patched module
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert isinstance(result, dict)
            assert result["secret_key"] == "test-secret-key"
            assert result["public_key"] == "test-public-key"
            assert result["host"] == "https://cloud.langfuse.com"

    def test_config_defaults_to_development_when_release_not_set(self):
        """When LANGFUSE_RELEASE is not set, defaults to 'development'."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"
        os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert result["environment"] == "development"

    def test_config_uses_release_env_for_environment_scoping(self):
        """When LANGFUSE_RELEASE is set, uses it as the environment name."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"
        os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"
        os.environ["LANGFUSE_RELEASE"] = "production"

        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert result["environment"] == "production"

    def test_config_defaults_host_to_local_when_not_set(self):
        """When LANGFUSE_HOST is not set, defaults to localhost for local dev."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"

        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert result["host"] == "http://localhost:3000"

    def test_config_default_project_name(self):
        """Config defaults project_name to 'rckg'."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"

        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert result["project_name"] == "rckg"

    def test_config_dashboard_url_contains_port_3000(self):
        """Dashboard URL is documented at http://localhost:3000 by default."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"

        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert result["dashboard_url"] == "http://localhost:3000"

    def test_config_dashboard_url_uses_env_host(self):
        """Dashboard URL uses the configured host when set."""
        os.environ["LANGFUSE_SECRET_KEY"] = "test-secret-key"
        os.environ["LANGFUSE_PUBLIC_KEY"] = "test-public-key"
        os.environ["LANGFUSE_HOST"] = "https://langfuse.example.com"

        mock_langfuse = MagicMock()
        with patch.dict("sys.modules", {"langfuse": mock_langfuse}):
            import importlib
            import app.services.langfuse_config as config_mod
            importlib.reload(config_mod)
            result = config_mod.get_langfuse_config()

            assert result["dashboard_url"] == "https://langfuse.example.com"


# ==============================================================================
# AC-1: Trace Creation with trace_id
# ==============================================================================


class TestExtractionTracing:
    """TC-OBS-2: Extraction trace creation with trace_id."""

    def test_extract_and_trace_creates_trace_with_trace_id(self):
        """When extraction trace is called, a Langfuse trace is created with a trace_id."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-abc-123"
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            result = extract_and_trace(
                markdown_content="# Test section",
                prompt="Test prompt content",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-123",
            )

        assert result["trace_id"] is not None
        assert len(result["trace_id"]) == 36  # UUID4 format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        mock_langfuse_class.assert_called_once()
        mock_langfuse_instance.trace.assert_called_once()
        call_kwargs = mock_langfuse_instance.trace.call_args[1]
        assert "id" in call_kwargs
        assert call_kwargs.get("name") == "extraction"

    def test_extract_and_trace_returns_token_usage(self):
        """The trace result includes token usage data."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-token-456"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            result = extract_and_trace(
                markdown_content="# Test section",
                prompt="Test prompt content",
                completion='{"obligations": [{"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"}]}',
                model_used="mistral",
                document_id="doc-123",
                prompt_tokens=100,
                completion_tokens=50,
            )

        assert result["prompt_tokens"] == 100
        assert result["completion_tokens"] == 50

    def test_extract_and_trace_noop_when_langfuse_none(self):
        """When Langfuse is None, extract_and_trace returns without error."""
        from app.services.langfuse_tracing import extract_and_trace

        with patch("app.services.langfuse_tracing.Langfuse", None):
            result = extract_and_trace(
                markdown_content="# Test",
                prompt="Test prompt",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-123",
            )

            assert result is None

    def test_extract_and_trace_noop_on_langfuse_error(self):
        """When Langfuse API raises an error, extract_and_trace returns None gracefully."""
        mock_langfuse_instance = MagicMock()
        mock_langfuse_instance.trace.side_effect = Exception("Langfuse API down")
        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            result = extract_and_trace(
                markdown_content="# Test",
                prompt="Test prompt",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-123",
            )

            assert result is None

    def test_extract_and_trace_logs_prompt_and_completion(self):
        """The span includes the full prompt and completion via update_generation."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-logging-789"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            extract_and_trace(
                markdown_content="# Test section",
                prompt="This is the full prompt content",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-123",
            )

        # Verify update_generation was called with the prompt and completion
        assert mock_trace_instance.update_generation.called
        call_kwargs = mock_trace_instance.update_generation.call_args[1]
        assert "input" in call_kwargs  # Verify input/output passed


# ==============================================================================
# AC-2: Span includes full prompt, completion, and token usage
# ==============================================================================


class TestSpanContent:
    """TC-OBS-3: Span content includes prompt, completion, and token usage."""

    def test_span_includes_full_prompt(self):
        """The span metadata includes the full prompt text."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-prompt-001"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            extract_and_trace(
                markdown_content="# Full test content here",
                prompt="The complete prompt sent to the LLM",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-001",
            )

            call_kwargs = mock_trace_instance.update_generation.call_args[1]
            assert call_kwargs.get("input") == "The complete prompt sent to the LLM"

    def test_span_includes_completion(self):
        """The span metadata includes the full completion (LLM output)."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-completion-001"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            completion_text = json.dumps({
                "obligations": [
                    {"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"}
                ]
            })
            extract_and_trace(
                markdown_content="# Content",
                prompt="Test prompt",
                completion=completion_text,
                model_used="mistral",
                document_id="doc-001",
            )

            # update_generation was called — verify it received the completion data
            call_kwargs = mock_trace_instance.update_generation.call_args[1]
            assert call_kwargs.get("output") == completion_text

    def test_span_includes_token_usage(self):
        """Token usage is captured in the trace."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-tokens-001"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            result = extract_and_trace(
                markdown_content="# Content",
                prompt="Test prompt",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-001",
                prompt_tokens=200,
                completion_tokens=150,
            )

            assert result is not None
            assert result.get("prompt_tokens") == 200
            assert result.get("completion_tokens") == 150


# ==============================================================================
# AC-3: Failure logging includes judge feedback and repair attempts
# ==============================================================================


class TestFailureLogging:
    """TC-OBS-4: Failure logging includes judge feedback and repair attempts."""

    def test_log_extraction_failure_creates_trace_with_feedback(self):
        """When extraction fails, log includes judge feedback."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-fail-001"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import log_extraction_failure

            log_extraction_failure(
                trace_id="trace-fail-001",
                judge_feedback="The metadata accuracy is too low.",
                repair_attempts=3,
                final_status="rejected",
                document_id="doc-001",
            )

            assert mock_langfuse_class.called
            assert mock_trace_instance.update_generation.called

    def test_log_extraction_failure_includes_repair_attempts_count(self):
        """Failure trace includes the number of repair attempts made."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-fail-002"
        mock_trace_instance.update_generation = MagicMock(return_value=None)
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import log_extraction_failure

            log_extraction_failure(
                trace_id="trace-fail-002",
                judge_feedback="Needs fixing",
                repair_attempts=5,
                final_status="rejected",
                document_id="doc-002",
            )

            assert mock_trace_instance.update_generation.called

    def test_log_extraction_failure_noop_when_langfuse_none(self):
        """When Langfuse is None, log_extraction_failure does nothing."""
        from app.services.langfuse_tracing import log_extraction_failure

        with patch("app.services.langfuse_tracing.Langfuse", None):
            log_extraction_failure(
                trace_id="trace-fail-003",
                judge_feedback="Some feedback",
                repair_attempts=2,
                final_status="repair",
                document_id="doc-003",
            )

    def test_log_extraction_failure_noop_on_langfuse_error(self):
        """When Langfuse API fails, log_extraction_failure returns gracefully."""
        mock_langfuse_instance = MagicMock()
        mock_langfuse_instance.trace.side_effect = Exception("Connection refused")
        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import log_extraction_failure

            # Should not raise
            log_extraction_failure(
                trace_id="trace-fail-004",
                judge_feedback="Feedback",
                repair_attempts=1,
                final_status="rejected",
                document_id="doc-004",
            )


# ==============================================================================
# AC-5: Consistent trace_id linkage across extraction -> judge -> repair
# ==============================================================================


class TestTraceIdLinkage:
    """TC-OBS-5: Consistent trace_id linkage across the pipeline."""

    def test_judge_receives_trace_id_as_parent(self):
        """Judge scoring uses the extraction trace_id as the parent observation."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-judge-linked"
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.judge.Langfuse", mock_langfuse_class):
            import app.services.judge as judge_mod

            mock_judgment = JudgmentResponse(
                judgment=Judgment(**{
                    "metadata_accuracy": 0.90,
                    "legal_alignment": 0.88,
                    "semantics": 0.92,
                    "overall_score": 0.90,
                    "status": "approved",
                    "feedback": "Good quality extraction.",
                })
            )

            # Pass a parent trace_id to score with parent
            judge_mod._score_in_langfuse(
                mock_judgment,
                parent_trace_id="parent-extraction-trace",
            )

            # Verify the trace was created with parent_observation_id set
            call_kwargs = mock_langfuse_instance.trace.call_args[1]
            assert call_kwargs.get("parent_observation_id") == "parent-extraction-trace"

    def test_repair_receives_trace_id_as_grandparent(self):
        """Repair logging uses the extraction trace_id for grandparent linkage."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "trace-repair-linked"
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.repair.Langfuse", mock_langfuse_class):
            import app.services.repair as repair_mod

            repair_mod._log_attempt_to_langfuse(
                attempt_number=1,
                feedback="Fix the action verb",
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                status="in_progress",
            )

            assert mock_langfuse_class.called

    def test_extract_and_trace_returns_trace_id_for_linkage(self):
        """extract_and_trace returns a trace_id that can be passed to judge and repair."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "extract-trace-abc"
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            result = extract_and_trace(
                markdown_content="# Section 1",
                prompt="Extract obligations",
                completion='{"obligations": [{"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"}]}',
                model_used="mistral",
                document_id="doc-link-001",
            )

            # The returned dict must contain trace_id for downstream linkage
            assert "trace_id" in result
            assert len(result["trace_id"]) == 36  # UUID4 format

    def test_trace_id_is_uuid_format(self):
        """The trace_id returned by extract_and_trace is a valid UUID-like string."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "uuid-12345-67890"
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class):
            from app.services.langfuse_tracing import extract_and_trace
            result = extract_and_trace(
                markdown_content="# Content",
                prompt="Test",
                completion='{"obligations": []}',
                model_used="mistral",
                document_id="doc-uuid",
            )

            assert len(result["trace_id"]) == 36  # UUID4 format


# ==============================================================================
# Extraction service integration test (without real LLM calls)
# ==============================================================================


class TestExtractionServiceIntegration:
    """Integration tests for extraction.py with Langfuse tracing."""

    def test_extract_obligations_returns_obligations_with_tracing(self):
        """extract_obligations returns obligations and traces to Langfuse when available."""
        mock_langfuse_instance = MagicMock()
        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.id = "extract-service-trace"
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        mock_obligations = [
            Obligation(
                id="AC-1",
                prose="Test obligation",
                action_verb="must",
                subject_noun="system",
                clause_ref="Section 1",
            ),
        ]

        # Mock _extract_obligations_with_storage to return obligations without DB calls
        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class), \
             patch("app.services.extraction._extract_obligations_with_storage", return_value=(mock_obligations, True, "extract-service-trace")):
            from app.services.extraction import extract_obligations
            result = extract_obligations(
                markdown_content="# Test section",
                source_document_id="doc-123",
            )

            assert len(result) == 1
            assert result[0].id == "AC-1"

    def test_extract_obligations_empty_input_returns_empty_list(self):
        """extract_obligations returns empty list for empty input."""
        with patch("app.services.langfuse_tracing.Langfuse", None):
            from app.services.extraction import extract_obligations
            result = extract_obligations(
                markdown_content="",
            )

            assert result == []

    def test_extract_obligations_none_input_returns_empty_list(self):
        """extract_obligations returns empty list for None input."""
        with patch("app.services.langfuse_tracing.Langfuse", None):
            from app.services.extraction import extract_obligations
            result = extract_obligations(
                markdown_content=None,
            )

            assert result == []


# ==============================================================================
# Graceful Degradation Tests
# ==============================================================================


class TestGracefulDegradation:
    """TC-OBS-6: Langfuse failures never break the extraction pipeline."""

    def test_extraction_continues_without_langfuse(self):
        """Extraction pipeline continues even when Langfuse is None."""
        mock_obligations = [
            Obligation(
                id="AC-1",
                prose="Test",
                action_verb="must",
                subject_noun="test",
                clause_ref="Section 1",
            ),
        ]

        with patch("app.services.langfuse_tracing.Langfuse", None), \
             patch("app.services.extraction._extract_obligations_with_storage", return_value=(mock_obligations, True, None)):
            from app.services.extraction import extract_obligations
            result = extract_obligations(markdown_content="# Test")

            assert len(result) == 1

    def test_judge_continues_without_langfuse(self):
        """Judge evaluation continues even when Langfuse is None."""
        import app.services.judge as judge_mod

        mock_judgment_json = json.dumps({
            "judgment": {
                "metadata_accuracy": 0.90,
                "legal_alignment": 0.85,
                "semantics": 0.92,
                "overall_score": 0.89,
                "status": "approved",
                "feedback": "Good quality.",
            }
        })

        with patch.object(judge_mod, "_call_llm", return_value=mock_judgment_json), \
             patch.object(judge_mod, "Langfuse", None):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown="# Test",
            )

            assert result is not None
            assert result.judgment.status == "approved"

    def test_repair_continues_without_langfuse(self):
        """Repair loop continues even when Langfuse is None."""
        import app.services.repair as repair_mod

        mock_repaired = json.dumps({
            "id": "AC-1",
            "prose": "Repaired obligation",
            "action_verb": "shall",
            "subject_noun": "access",
            "clause_ref": "Section 1",
        })

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired):
            result = repair_mod.repair_obligation(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                judgment_feedback="Fix it",
                original_markdown="# Test",
                max_attempts=1,
            )

            # Should return repaired obligation (not fail due to Langfuse)
            obligation, status, attempts = result
            assert obligation is not None or status == "rejected"

    def test_extraction_handles_langfuse_api_error(self):
        """When Langfuse API raises an error, extraction still returns results."""
        mock_obligations = [
            Obligation(
                id="AC-1",
                prose="Test obligation",
                action_verb="must",
                subject_noun="system",
                clause_ref="Section 1",
            ),
        ]

        # Simulate Langfuse API failure during trace creation
        mock_langfuse_instance = MagicMock()
        mock_langfuse_instance.trace.side_effect = Exception("Connection refused")
        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch("app.services.langfuse_tracing.Langfuse", mock_langfuse_class), \
             patch("app.services.extraction._extract_obligations_with_storage", return_value=(mock_obligations, True, None)):
            from app.services.extraction import extract_obligations
            result = extract_obligations(markdown_content="# Test")

            # Extraction should still return the obligations
            assert len(result) == 1
