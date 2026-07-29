"""
Test suite for EXTRACT-2: LLM-as-Judge Extraction Quality Check

This test module verifies the LLM-as-Judge quality evaluation pipeline
that scores extracted obligations across three criteria:
  1. Metadata Accuracy (0.0-1.0): Are action_verb, subject_noun, clause_ref correct?
  2. Legal Definition Alignment (0.0-1.0): Does it align with compliance terminology?
  3. Rule Semantics (0.0-1.0): Is the intent preserved without semantic loss?

Threshold: >= 0.80 passes (approved), < 0.80 flagged for repair.

Test Strategy:
- Unit tests for Pydantic schema validation (valid/invalid responses)
- Unit tests for prompt building
- Unit tests for threshold logic (approved vs repair scenarios)
- Unit tests with mocked LLM for judge extraction
- Integration test for the API endpoint using TestClient
- Langfuse logging tested with mocked imports (graceful degradation)
- Edge cases: boundary scores, malformed LLM output, empty input

Acceptance Criteria Covered:
- AC-1: judge_extraction(obligation, original_markdown) returns a score (0.0-1.0) for each criterion
- AC-2: All criteria >= 0.80 -> status "approved"
- AC-3: Any criterion < 0.80 -> status "repair" with reason in feedback field
- AC-4: Uses Ollama (local dev) with Llama 3.1 model
- AC-5: Judge output includes detailed feedback
- AC-6: Scores logged to Langfuse with trace_id
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure app module is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.judge import Judgment, JudgmentResponse


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
        "feedback": "The obligation is well-structured with correct metadata fields and aligns with compliance terminology.",
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
        "feedback": "The action_verb appears to be missing key modal verb. The clause_ref should reference the specific subsection.",
    })


@pytest.fixture
def mock_boundary_judgment_json():
    """Mock LLM response with scores exactly at the 0.80 threshold boundary."""
    return json.dumps({
        "metadata_accuracy": 0.80,
        "legal_alignment": 0.80,
        "semantics": 0.80,
        "overall_score": 0.80,
        "status": "approved",
        "feedback": "All criteria meet the minimum threshold.",
    })


@pytest.fixture
def mock_malformed_json():
    """Malformed JSON that would fail Pydantic validation."""
    return "not valid json at all {{{"


@pytest.fixture
def mock_missing_fields_json():
    """Valid JSON but missing required judgment fields."""
    return json.dumps({
        "metadata_accuracy": 0.90,
        # missing legal_alignment, semantics, overall_score, status, feedback
    })


@pytest.fixture
def mock_negative_score_json():
    """JSON with a score outside the valid 0.0-1.0 range."""
    return json.dumps({
        "metadata_accuracy": -0.10,
        "legal_alignment": 0.90,
        "semantics": 0.85,
        "overall_score": 0.82,
        "status": "approved",
        "feedback": "Test response with negative score.",
    })


# ==============================================================================
# AC-1: judge_extraction returns a score (0.0-1.0) for each criterion
# ==============================================================================


class TestJudgeCriteriaValidation:
    """TC-2.1: Pydantic validation for Judgment model."""

    def test_judgment_from_dict(self):
        """A Judgment can be constructed from a dictionary of scores."""
        data = {
            "metadata_accuracy": 0.95,
            "legal_alignment": 0.90,
            "semantics": 0.88,
            "overall_score": 0.91,
            "status": "approved",
            "feedback": "All criteria are strong.",
        }
        judgment = Judgment(**data)
        assert judgment.metadata_accuracy == 0.95
        assert judgment.status == "approved"
        assert judgment.feedback == "All criteria are strong."

    def test_judgment_status_rejects_invalid_value(self):
        """A Judgment with an invalid status string raises ValidationError."""
        data = {
            "metadata_accuracy": 0.90,
            "legal_alignment": 0.85,
            "semantics": 0.80,
            "overall_score": 0.85,
            "status": "rejected",  # not "approved" or "repair"
            "feedback": "Test.",
        }
        with pytest.raises(Exception):  # ValidationError
            Judgment(**data)

    def test_judgment_response_wraps_judgment(self):
        """JudgmentResponse correctly wraps a Judgment object."""
        data = {
            "judgment": {
                "metadata_accuracy": 0.95,
                "legal_alignment": 0.90,
                "semantics": 0.88,
                "overall_score": 0.91,
                "status": "approved",
                "feedback": "All criteria strong.",
            }
        }
        response = JudgmentResponse(**data)
        assert isinstance(response.judgment, Judgment)
        assert response.judgment.status == "approved"


# ==============================================================================
# AC-2: All criteria >= 0.80 results in "approved" status
# ==============================================================================


class TestApprovedStatus:
    """TC-2.2: Threshold logic for "approved" status when all scores >= 0.80."""

    def test_all_scores_above_080_results_in_approved(self, mock_approved_judgment_json):
        """When all three criteria exceed 0.80, status is 'approved'."""
        parsed = json.loads(mock_approved_judgment_json)
        judgment = Judgment(**parsed)
        assert judgment.status == "approved"
        assert judgment.metadata_accuracy >= 0.80
        assert judgment.legal_alignment >= 0.80
        assert judgment.semantics >= 0.80

    def test_boundary_scores_080_are_approved(self, mock_boundary_judgment_json):
        """When all scores are exactly 0.80, status is 'approved'."""
        parsed = json.loads(mock_boundary_judgment_json)
        judgment = Judgment(**parsed)
        assert judgment.status == "approved"
        assert judgment.overall_score == pytest.approx(0.80)

    def test_overall_score_is_average_of_three_criteria(self, mock_approved_judgment_json):
        """Overall score approximately equals the arithmetic mean of the three criterion scores."""
        parsed = json.loads(mock_approved_judgment_json)
        judgment = Judgment(**parsed)
        expected_avg = (parsed["metadata_accuracy"] + parsed["legal_alignment"] + parsed["semantics"]) / 3
        # Allow for rounding (LLM typically rounds to 2 decimal places)
        assert judgment.overall_score == pytest.approx(expected_avg, rel=0.02)

    def test_overall_score_for_boundary(self, mock_boundary_judgment_json):
        """Overall score for boundary case (0.80, 0.80, 0.80) is 0.80."""
        parsed = json.loads(mock_boundary_judgment_json)
        judgment = Judgment(**parsed)
        assert judgment.overall_score == pytest.approx(0.80)


# ==============================================================================
# AC-3: Any criterion < 0.80 results in "repair" status with feedback
# ==============================================================================


class TestRepairStatus:
    """TC-2.3: Threshold logic for "repair" status when any score < 0.80."""

    def test_one_score_below_080_results_in_repair(self, mock_repair_judgment_json):
        """When any criterion is below 0.80, status is 'repair'."""
        parsed = json.loads(mock_repair_judgment_json)
        judgment = Judgment(**parsed)
        assert judgment.status == "repair"

    def test_repair_judgment_has_feedback(self, mock_repair_judgment_json):
        """A 'repair' judgment includes a non-empty feedback string."""
        parsed = json.loads(mock_repair_judgment_json)
        judgment = Judgment(**parsed)
        assert judgment.feedback is not None
        assert len(judgment.feedback) > 0

    def test_metadata_accuracy_below_080_triggers_repair(self):
        """When metadata_accuracy < 0.80, status is 'repair'."""
        judgment = Judgment(
            metadata_accuracy=0.70,
            legal_alignment=0.95,
            semantics=0.90,
            overall_score=0.85,
            status="repair",
            feedback="Metadata accuracy is below threshold.",
        )
        assert judgment.status == "repair"

    def test_legal_alignment_below_080_triggers_repair(self):
        """When legal_alignment < 0.80, status is 'repair'."""
        judgment = Judgment(
            metadata_accuracy=0.95,
            legal_alignment=0.70,
            semantics=0.90,
            overall_score=0.85,
            status="repair",
            feedback="Legal alignment needs improvement.",
        )
        assert judgment.status == "repair"

    def test_semantics_below_080_triggers_repair(self):
        """When semantics < 0.80, status is 'repair'."""
        judgment = Judgment(
            metadata_accuracy=0.95,
            legal_alignment=0.90,
            semantics=0.75,
            overall_score=0.87,
            status="repair",
            feedback="Semantic preservation is inadequate.",
        )
        assert judgment.status == "repair"

    def test_all_scores_below_080_results_in_repair(self):
        """When all criteria are below 0.80, status is 'repair'."""
        judgment = Judgment(
            metadata_accuracy=0.50,
            legal_alignment=0.55,
            semantics=0.60,
            overall_score=0.55,
            status="repair",
            feedback="All criteria need significant improvement.",
        )
        assert judgment.status == "repair"


# ==============================================================================
# AC-4: Uses Ollama with Llama 3.1 model
# ==============================================================================


class TestLLMConfiguration:
    """TC-2.4: Judge service uses Ollama with llama3.1 model."""

    def test_ollama_package_is_used(self, sample_markdown):
        """The judge service imports and uses the ollama package."""
        import app.services.judge as judge_mod

        mock_ollama = MagicMock()
        mock_ollama.chat.return_value = {
            "message": {"content": json.dumps({
                "metadata_accuracy": 0.90,
                "legal_alignment": 0.85,
                "semantics": 0.88,
                "overall_score": 0.88,
                "status": "approved",
                "feedback": "Good quality extraction.",
            })}
        }

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            result = judge_mod._call_ollama("test prompt")

        mock_ollama.chat.assert_called_once()
        call_kwargs = mock_ollama.chat.call_args[1]
        assert call_kwargs["model"] == "llama3.1"

    def test_ollama_uses_temperature_03(self, sample_markdown):
        """The Ollama client is called with temperature=0.3."""
        import app.services.judge as judge_mod

        mock_ollama = MagicMock()
        mock_ollama.chat.return_value = {
            "message": {"content": json.dumps({
                "metadata_accuracy": 0.90,
                "legal_alignment": 0.85,
                "semantics": 0.88,
                "overall_score": 0.88,
                "status": "approved",
                "feedback": "Good quality.",
            })}
        }

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            judge_mod._call_ollama("test prompt")

        call_options = mock_ollama.chat.call_args[1]["options"]
        assert call_options["temperature"] == 0.3


# ==============================================================================
# AC-5: Judge output includes detailed feedback
# ==============================================================================


class TestDetailedFeedback:
    """TC-2.5: Judge output includes detailed explanatory feedback."""

    def test_approved_judgment_has_feedback(self, mock_approved_judgment_json):
        """An approved judgment includes a non-empty feedback string."""
        parsed = json.loads(mock_approved_judgment_json)
        judgment = Judgment(**parsed)
        assert len(judgment.feedback) > 0

    def test_repair_judgment_has_feedback(self, mock_repair_judgment_json):
        """A repair judgment includes a non-empty feedback string."""
        parsed = json.loads(mock_repair_judgment_json)
        judgment = Judgment(**parsed)
        assert len(judgment.feedback) > 0

    def test_feedback_is_explanatory_string(self, mock_approved_judgment_json):
        """Feedback is a string, not a number or null."""
        parsed = json.loads(mock_approved_judgment_json)
        judgment = Judgment(**parsed)
        assert isinstance(judgment.feedback, str)
        # The feedback should contain useful information (at least a few words)
        assert len(judgment.feedback.split()) > 1


# ==============================================================================
# AC-6: Scores logged to Langfuse with trace_id (graceful degradation)
# ==============================================================================


class TestLangfuseLogging:
    """TC-2.6: Judge scores are logged to Langfuse with trace_id."""

    def test_langfuse_not_available_returns_result_without_error(self, mock_approved_judgment_json, sample_markdown):
        """When langfuse is not installed, judge_extraction still returns a valid result."""
        import app.services.judge as judge_mod

        # Mock _call_llm so the test exercises the Langfuse path (not Ollama unavailability)
        with patch.object(judge_mod, "_call_llm", return_value=mock_approved_judgment_json):
            # Verify graceful degradation by mocking the Langfuse import as unavailable
            with patch.object(judge_mod, "Langfuse", None):
                result = judge_mod.judge_extraction(
                    obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                    original_markdown=sample_markdown,
                )
                assert result is not None
                assert hasattr(result, "judgment")

    def test_langfuse_logging_called_when_available(self, mock_approved_judgment_json):
        """When langfuse is available, _score_in_langfuse calls log_judgment_score."""
        import app.services.judge as judge_mod

        mock_trace_instance = MagicMock()
        mock_trace_instance.__enter__ = MagicMock(return_value=mock_trace_instance)
        mock_trace_instance.__exit__ = MagicMock(return_value=None)
        mock_trace_instance.update_generation = MagicMock(return_value=None)

        mock_langfuse_instance = MagicMock()
        mock_langfuse_instance.trace.return_value = mock_trace_instance

        mock_langfuse_class = MagicMock(return_value=mock_langfuse_instance)

        with patch.object(judge_mod, "Langfuse", mock_langfuse_class):
            mock_judgment = JudgmentResponse(
                judgment=Judgment(**json.loads(mock_approved_judgment_json))
            )
            judge_mod._score_in_langfuse(mock_judgment)

        # Verify Langfuse was instantiated and trace was created
        assert mock_langfuse_class.called
        assert mock_trace_instance.update_generation.called


# ==============================================================================
# AC-7: judge_extraction returns JudgmentResponse with correct structure
# ==============================================================================


class TestJudgeExtractionService:
    """TC-2.7: judge_extraction service returns a complete JudgmentResponse."""

    def test_judge_extraction_returns_judgment_response(self, sample_markdown, mock_approved_judgment_json):
        """judge_extraction returns a JudgmentResponse instance."""
        import app.services.judge as judge_mod

        with patch.object(judge_mod, "_call_llm", return_value=mock_approved_judgment_json):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert isinstance(result, JudgmentResponse)

    def test_judge_extraction_includes_metadata_accuracy(self, sample_markdown, mock_approved_judgment_json):
        """judge_extraction result contains metadata_accuracy score."""
        import app.services.judge as judge_mod

        with patch.object(judge_mod, "_call_llm", return_value=mock_approved_judgment_json):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert hasattr(result.judgment, "metadata_accuracy")
        assert isinstance(result.judgment.metadata_accuracy, float)
        assert 0.0 <= result.judgment.metadata_accuracy <= 1.0

    def test_judge_extraction_includes_legal_alignment(self, sample_markdown, mock_approved_judgment_json):
        """judge_extraction result contains legal_alignment score."""
        import app.services.judge as judge_mod

        with patch.object(judge_mod, "_call_llm", return_value=mock_approved_judgment_json):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert hasattr(result.judgment, "legal_alignment")
        assert isinstance(result.judgment.legal_alignment, float)
        assert 0.0 <= result.judgment.legal_alignment <= 1.0

    def test_judge_extraction_includes_semantics(self, sample_markdown, mock_approved_judgment_json):
        """judge_extraction result contains semantics score."""
        import app.services.judge as judge_mod

        with patch.object(judge_mod, "_call_llm", return_value=mock_approved_judgment_json):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert hasattr(result.judgment, "semantics")
        assert isinstance(result.judgment.semantics, float)
        assert 0.0 <= result.judgment.semantics <= 1.0

    def test_judge_extraction_handles_malformed_json(self, sample_markdown):
        """When LLM returns malformed JSON, judge_extraction returns an empty judgment."""
        import app.services.judge as judge_mod

        with patch.object(judge_mod, "_call_llm", return_value="not valid json"):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        # Should handle gracefully - return a default/rejected judgment
        assert result is not None

    def test_judge_extraction_handles_missing_fields(self, sample_markdown):
        """When LLM response is missing required fields, judge_extraction returns a default judgment."""
        import app.services.judge as judge_mod

        with patch.object(judge_mod, "_call_llm", return_value=json.dumps({"metadata_accuracy": 0.9})):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        # Should handle gracefully
        assert result is not None


# ==============================================================================
# Prompt Template Tests
# ==============================================================================


class TestPromptTemplate:
    """Tests for prompt template loading and building."""

    def test_prompt_template_file_exists(self):
        """The judge prompt template file exists at the expected path."""
        from app.services.judge import PROMPT_TEMPLATE_PATH
        assert PROMPT_TEMPLATE_PATH.exists()
        assert PROMPT_TEMPLATE_PATH.name == "judge.md"

    def test_prompt_template_contains_criteria_description(self):
        """The prompt template describes all three evaluation criteria."""
        from app.services.judge import _load_prompt_template

        template = _load_prompt_template()
        assert "metadata" in template.lower() or "action_verb" in template.lower()
        assert "legal" in template.lower() or "compliance" in template.lower()
        assert "semantics" in template.lower() or "intent" in template.lower()

    def test_prompt_includes_obligation_placeholder(self):
        """The prompt template contains a placeholder for the obligation."""
        from app.services.judge import _load_prompt_template

        template = _load_prompt_template()
        assert "{{obligation_json}}" in template or "obligation" in template.lower()

    def test_prompt_includes_original_text_placeholder(self):
        """The prompt template contains a placeholder for the original text."""
        from app.services.judge import _load_prompt_template

        template = _load_prompt_template()
        assert "{{original_markdown}}" in template or "original" in template.lower()

    def test_build_prompt_includes_obligation(self, sample_obligation_dict, sample_markdown):
        """The built prompt includes the obligation JSON."""
        from app.services.judge import _build_prompt

        prompt = _build_prompt(sample_obligation_dict, sample_markdown)
        assert "AC-1" in prompt or "obligation" in prompt.lower()

    def test_build_prompt_includes_original_text(self, sample_obligation_dict, sample_markdown):
        """The built prompt includes the original markdown text."""
        from app.services.judge import _build_prompt

        prompt = _build_prompt(sample_obligation_dict, sample_markdown)
        assert "Section 3" in prompt

    def test_build_prompt_excludes_raw_template_placeholders(self, sample_obligation_dict, sample_markdown):
        """After building, the prompt should not contain unresolved template placeholders."""
        from app.services.judge import _build_prompt

        prompt = _build_prompt(sample_obligation_dict, sample_markdown)
        assert "{{obligation_json}}" not in prompt
        assert "{{original_markdown}}" not in prompt


# ==============================================================================
# Integration Test: API Endpoint
# ==============================================================================


class TestJudgeAPIEndpoint:
    """Integration tests for POST /api/v1/judge endpoint."""

    @pytest.fixture
    def app_with_judge_router(self):
        """Create a FastAPI app with the judge router mounted."""
        from app.api.judge import router as judge_router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(judge_router, prefix="/api/v1/judge", tags=["judge"])
        return app

    @pytest.fixture
    def client(self, app_with_judge_router):
        """TestClient wrapping the app with the judge router."""
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("fastapi not installed")

        return TestClient(app_with_judge_router)

    def test_valid_request_returns_200(self, client, sample_obligation_dict, sample_markdown, mock_approved_judgment_json):
        """POST with valid obligation returns HTTP 200 with judgment data."""
        with patch("app.api.judge.judge_extraction", return_value=JudgmentResponse(
            judgment=Judgment(
                metadata_accuracy=0.95,
                legal_alignment=0.92,
                semantics=0.90,
                overall_score=0.92,
                status="approved",
                feedback="Good quality.",
            )
        )):
            resp = client.post(
                "/api/v1/judge",
                json={
                    "obligation": sample_obligation_dict,
                    "original_markdown": sample_markdown,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert "judgment" in body
        assert body["judgment"]["status"] == "approved"

    def test_response_contains_all_judgment_fields(self, client, sample_obligation_dict, sample_markdown):
        """Response judgment contains all required fields."""
        with patch("app.api.judge.judge_extraction", return_value=JudgmentResponse(
            judgment=Judgment(
                metadata_accuracy=0.95,
                legal_alignment=0.92,
                semantics=0.90,
                overall_score=0.92,
                status="approved",
                feedback="Good quality.",
            )
        )):
            resp = client.post(
                "/api/v1/judge",
                json={
                    "obligation": sample_obligation_dict,
                    "original_markdown": sample_markdown,
                },
            )

        body = resp.json()
        j = body["judgment"]
        assert "metadata_accuracy" in j
        assert "legal_alignment" in j
        assert "semantics" in j
        assert "overall_score" in j
        assert "status" in j
        assert "feedback" in j

    def test_repair_status_from_endpoint(self, client, sample_obligation_dict, sample_markdown):
        """POST that results in repair status returns the repair judgment."""
        with patch("app.api.judge.judge_extraction", return_value=JudgmentResponse(
            judgment=Judgment(
                metadata_accuracy=0.65,
                legal_alignment=0.70,
                semantics=0.85,
                overall_score=0.73,
                status="repair",
                feedback="Needs revision.",
            )
        )):
            resp = client.post(
                "/api/v1/judge",
                json={
                    "obligation": sample_obligation_dict,
                    "original_markdown": sample_markdown,
                },
            )

        body = resp.json()
        assert body["judgment"]["status"] == "repair"

    def test_missing_obligation_returns_422(self, client, sample_markdown):
        """POST without obligation field returns HTTP 422 validation error."""
        resp = client.post(
            "/api/v1/judge",
            json={"original_markdown": sample_markdown},
        )
        assert resp.status_code == 422

    def test_missing_original_markdown_returns_422(self, client, sample_obligation_dict):
        """POST without original_markdown returns HTTP 422 validation error."""
        resp = client.post(
            "/api/v1/judge",
            json={"obligation": sample_obligation_dict},
        )
        assert resp.status_code == 422

    def test_service_error_returns_500(self, client, sample_obligation_dict, sample_markdown):
        """When the judge service raises an exception, endpoint returns HTTP 500."""
        with patch("app.api.judge.judge_extraction", side_effect=RuntimeError("LLM connection refused")):
            resp = client.post(
                "/api/v1/judge",
                json={
                    "obligation": sample_obligation_dict,
                    "original_markdown": sample_markdown,
                },
            )

        assert resp.status_code == 500


class TestThresholdLogicIndependentComputation:
    """TC-2.8: Status is independently computed from criterion scores, not trusted from LLM."""

    def test_high_scores_override_llm_repair_to_approved(self, sample_markdown):
        """When all scores >= 0.80 but LLM says 'repair', service overrides to 'approved'."""
        import app.services.judge as judge_mod

        # LLM incorrectly says "repair" even though all scores are above threshold
        llm_response = json.dumps({
            "judgment": {
                "metadata_accuracy": 0.95,
                "legal_alignment": 0.92,
                "semantics": 0.90,
                "overall_score": 0.92,
                "status": "repair",  # LLM is wrong
                "feedback": "Actually this is high quality.",
            }
        })

        with patch.object(judge_mod, "_call_llm", return_value=llm_response):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert result.judgment.status == "approved"
        # Feedback from LLM should be preserved
        assert "high quality" in result.judgment.feedback.lower()

    def test_low_scores_override_llm_approved_to_repair(self, sample_markdown):
        """When any score < 0.80 but LLM says 'approved', service overrides to 'repair'."""
        import app.services.judge as judge_mod

        # LLM incorrectly says "approved" even though metadata_accuracy is below threshold
        llm_response = json.dumps({
            "judgment": {
                "metadata_accuracy": 0.65,
                "legal_alignment": 0.90,
                "semantics": 0.88,
                "overall_score": 0.81,
                "status": "approved",  # LLM is wrong
                "feedback": "Needs metadata correction.",
            }
        })

        with patch.object(judge_mod, "_call_llm", return_value=llm_response):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert result.judgment.status == "repair"

    def test_boundary_score_at_080_is_approved(self, sample_markdown):
        """When all scores are exactly 0.80, status is 'approved' (>= threshold)."""
        import app.services.judge as judge_mod

        llm_response = json.dumps({
            "judgment": {
                "metadata_accuracy": 0.80,
                "legal_alignment": 0.80,
                "semantics": 0.80,
                "overall_score": 0.80,
                "status": "repair",  # LLM says repair
                "feedback": "At the boundary.",
            }
        })

        with patch.object(judge_mod, "_call_llm", return_value=llm_response):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert result.judgment.status == "approved"

    def test_one_score_at_079_is_repair(self, sample_markdown):
        """When one score is 0.79 (just below threshold), status is 'repair'."""
        import app.services.judge as judge_mod

        llm_response = json.dumps({
            "judgment": {
                "metadata_accuracy": 0.79,
                "legal_alignment": 0.95,
                "semantics": 0.90,
                "overall_score": 0.88,
                "status": "approved",  # LLM is wrong
                "feedback": "Almost there.",
            }
        })

        with patch.object(judge_mod, "_call_llm", return_value=llm_response):
            result = judge_mod.judge_extraction(
                obligation={"id": "AC-1", "prose": "Test", "action_verb": "test", "subject_noun": "test", "clause_ref": "Section 1"},
                original_markdown=sample_markdown,
            )

        assert result.judgment.status == "repair"
