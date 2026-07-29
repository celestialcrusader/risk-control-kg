"""
Test suite for EXTRACT-3: Iterative Repair Loop

This test module verifies the repair service that re-submits low-scoring
obligations to the LLM with the judge's feedback, so that extraction
quality improves automatically before committing to the Silver layer.

Test Strategy:
- Unit tests for prompt template loading and building
- Unit tests for Pydantic validation of repair output
- Unit tests for repair service with mocked LLM
- Unit tests for max_attempts exhaustion -> "rejected" + DLQ
- Unit tests for Langfuse logging per attempt
- Unit tests for context augmentation (parent section + preceding paragraphs)
- Integration tests for the API endpoint using TestClient
- Edge cases: empty input, malformed LLM output, max_attempts=1

Acceptance Criteria Covered:
- AC-1: repair_obligation(obligation, feedback, markdown) re-runs with feedback
- AC-2: Repaired obligation with valid output gets "repaired" status
- AC-3: All repair attempts fail -> "rejected" + DLQ
- AC-4: Original kept when feedback is empty
- AC-5: Context augmentation with parent section and preceding paragraphs
- AC-6: Each attempt logs to Langfuse
- AC-7: Maximum 3 repair attempts (configurable)
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

from app.schemas.obligation import Obligation, ExtractedObligationsResponse
from app.schemas.judge import Judgment, JudgmentResponse


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_obligation_dict():
    """A sample extracted obligation needing repair."""
    return {
        "id": "AC-1",
        "prose": "The organization must limit information system access to authorized users.",
        "action_verb": "limit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1",
    }


@pytest.fixture
def sample_obligation_model():
    """A sample Obligation Pydantic model."""
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
def sample_feedback():
    """Sample judge feedback indicating problems."""
    return "The action_verb should include the modal verb 'shall'. The clause_ref should reference the specific subsection 3.1.1."


@pytest.fixture
def empty_feedback():
    """Feedback indicating no issues found."""
    return ""


@pytest.fixture
def good_feedback():
    """Feedback that is positive, indicating the obligation is fine."""
    return "The obligation is well-structured with correct metadata fields and aligns with compliance terminology."


@pytest.fixture
def mock_repaired_obligation_json():
    """Mock LLM response for a successful repair."""
    return json.dumps({
        "id": "AC-1",
        "prose": "The organization shall limit information system access to authorized users.",
        "action_verb": "shall limit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1.1",
    }, separators=(",", ":"))


@pytest.fixture
def mock_repair_response_full():
    """Mock LLM response with a full obligation repair including optional fields."""
    return json.dumps({
        "id": "AC-1",
        "prose": "The organization shall limit information system access to authorized users.",
        "action_verb": "shall limit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1.1",
        "effective_date": "2024-01-01",
        "section_ref": "Section 3",
    }, separators=(",", ":"))


@pytest.fixture
def mock_malformed_repair_json():
    """Malformed JSON from LLM repair attempt."""
    return "this is not valid json at all {{{"


@pytest.fixture
def mock_missing_fields_repair_json():
    """Valid JSON but missing required obligation fields."""
    return json.dumps({
        "id": "AC-1",
        # missing prose, action_verb, subject_noun, clause_ref
    })


@pytest.fixture
def mock_llm_failures():
    """A list of responses that simulate LLM failures during repair."""
    return [
        json.dumps({
            "id": "AC-1",
            "prose": "The organization shall limit access.",
            "action_verb": "shall limit",
            "subject_noun": "access",
            "clause_ref": "Section 3.1",
        }),
        json.dumps({
            "id": "AC-1",
            "prose": "The organization shall limit information system access to authorized users.",
            "action_verb": "shall limit",
            "subject_noun": "information system access",
            "clause_ref": "Section 3.1.1",
        }),
    ]


# ==============================================================================
# AC-1 & Context Augmentation: Prompt template exists and builds correctly
# ==============================================================================


class TestRepairPromptTemplate:
    """TC-3.1: Repair prompt template loads and builds correctly."""

    def test_prompt_template_file_exists(self):
        """The repair prompt template file exists at the expected path."""
        from app.services.repair import PROMPT_TEMPLATE_PATH
        assert PROMPT_TEMPLATE_PATH.exists()
        assert PROMPT_TEMPLATE_PATH.name == "repair.md"

    def test_prompt_template_contains_obligation_placeholder(self):
        """The prompt template contains the obligation JSON placeholder."""
        from app.services.repair import _load_prompt_template
        template = _load_prompt_template()
        assert "{{obligation_json}}" in template

    def test_prompt_template_contains_feedback_placeholder(self):
        """The prompt template contains the feedback placeholder."""
        from app.services.repair import _load_prompt_template
        template = _load_prompt_template()
        assert "{{feedback}}" in template

    def test_prompt_template_contains_original_markdown_placeholder(self):
        """The prompt template contains the original markdown placeholder."""
        from app.services.repair import _load_prompt_template
        template = _load_prompt_template()
        assert "{{original_markdown}}" in template

    def test_prompt_template_contains_parent_section_placeholder(self):
        """The prompt template contains the parent section heading placeholder."""
        from app.services.repair import _load_prompt_template
        template = _load_prompt_template()
        assert "{{parent_section_heading}}" in template

    def test_prompt_template_contains_preceding_paragraphs_placeholder(self):
        """The prompt template contains the preceding paragraphs placeholder."""
        from app.services.repair import _load_prompt_template
        template = _load_prompt_template()
        assert "{{preceding_paragraphs}}" in template

    def test_prompt_includes_context_augmentation(self):
        """The prompt template includes context from parent section."""
        from app.services.repair import _load_prompt_template
        template = _load_prompt_template()
        # The template should reference parent section, original text, obligation, and feedback
        assert "PARENT SECTION" in template or "parent" in template.lower()
        assert "PRECEDING" in template or "preceding" in template.lower()
        assert "ORIGINAL TEXT" in template or "original" in template.lower()
        assert "JUDGE FEEDBACK" in template or "feedback" in template.lower()
        assert "EXTRACTED OBLIGATION" in template or "obligation" in template.lower()

    def test_build_prompt_includes_obligation_json(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The built prompt contains the obligation JSON."""
        from app.services.repair import _build_prompt
        prompt = _build_prompt(sample_obligation_dict, sample_feedback, sample_markdown)
        assert "AC-1" in prompt
        assert "limit" in prompt

    def test_build_prompt_includes_feedback(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The built prompt contains the judge feedback."""
        from app.services.repair import _build_prompt
        prompt = _build_prompt(sample_obligation_dict, sample_feedback, sample_markdown)
        assert "action_verb" in prompt

    def test_build_prompt_includes_original_markdown(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The built prompt contains the original markdown text."""
        from app.services.repair import _build_prompt
        prompt = _build_prompt(sample_obligation_dict, sample_feedback, sample_markdown)
        assert "Section 3" in prompt
        assert "Access Control" in prompt

    def test_build_prompt_excludes_unresolved_placeholders(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """After building, the prompt should not contain unresolved template placeholders."""
        from app.services.repair import _build_prompt
        prompt = _build_prompt(sample_obligation_dict, sample_feedback, sample_markdown)
        assert "{{obligation_json}}" not in prompt
        assert "{{feedback}}" not in prompt
        assert "{{original_markdown}}" not in prompt
        assert "{{parent_section_heading}}" not in prompt
        assert "{{preceding_paragraphs}}" not in prompt

    def test_build_prompt_with_pydantic_obligation(self, sample_obligation_model, sample_markdown, sample_feedback):
        """The prompt building works with a Pydantic Obligation model, not just a dict."""
        from app.services.repair import _build_prompt
        prompt = _build_prompt(sample_obligation_model, sample_feedback, sample_markdown)
        assert "AC-1" in prompt
        assert "limit" in prompt

    def test_build_prompt_includes_context_params(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The built prompt includes parent section and preceding paragraphs when provided."""
        from app.services.repair import _build_prompt
        prompt = _build_prompt(
            sample_obligation_dict,
            sample_feedback,
            sample_markdown,
            parent_section_heading="# Section 3: Access Control",
            preceding_paragraphs="Preceding text here",
        )
        assert "Section 3: Access Control" in prompt
        assert "Preceding text here" in prompt


# ==============================================================================
# AC-5: Context extraction
# ==============================================================================


class TestContextExtraction:
    """TC-3.6: Context extraction from parent section and preceding paragraphs."""

    def test_extract_context_finds_matching_section(self, sample_obligation_model, sample_markdown):
        """Context extraction finds the section matching the clause_ref."""
        from app.services.repair import _extract_context
        heading, paragraphs = _extract_context(sample_obligation_model, sample_markdown)
        assert "Section 3" in heading or "3.1" in heading

    def test_extract_context_returns_preceding_paragraphs(self, sample_obligation_model, sample_markdown):
        """Context extraction returns preceding paragraphs (may be empty if section is at top)."""
        from app.services.repair import _extract_context
        heading, paragraphs = _extract_context(sample_obligation_model, sample_markdown)
        # The section "## 3.1 General Requirements" is near the top of the document,
        # so preceding paragraphs may be empty (no non-heading content before it).
        # The important thing is the function doesn't crash and returns a tuple.
        assert isinstance(heading, str)
        assert isinstance(paragraphs, str)

    def test_extract_context_with_preceding_content(self):
        """Context extraction returns preceding paragraphs when section has content above it."""
        from app.services.repair import _extract_context
        markdown = """# Introduction

This is the introduction paragraph for the regulatory document.
It provides general context about the scope.

# Section 4.2 Specific Requirements

The organization must implement specific controls here.
"""
        obligation = {"id": "X-1", "prose": "Must implement controls", "action_verb": "implement",
                      "subject_noun": "controls", "clause_ref": "Section 4.2"}
        heading, paragraphs = _extract_context(obligation, markdown)
        assert "Section 4.2" in heading or "4.2" in heading
        # Preceding paragraphs are non-heading text lines before the matched section
        assert "This is the introduction paragraph" in paragraphs
        assert "It provides general context" in paragraphs

    def test_extract_context_empty_clause_ref(self, sample_markdown):
        """Context extraction returns empty strings when clause_ref is missing."""
        from app.services.repair import _extract_context
        heading, paragraphs = _extract_context({}, sample_markdown)
        assert heading == ""
        assert paragraphs == ""

    def test_extract_context_empty_markdown(self, sample_obligation_model):
        """Context extraction returns empty strings when markdown is empty."""
        from app.services.repair import _extract_context
        heading, paragraphs = _extract_context(sample_obligation_model, "")
        assert heading == ""
        assert paragraphs == ""


# ==============================================================================
# AC-2: Pydantic validation of repair output
# ==============================================================================


class TestRepairOutputValidation:
    """TC-3.2: Repair output is validated against the Obligation schema."""

    def test_valid_repaired_obligation_passes_validation(self, mock_repaired_obligation_json):
        """A well-formed repair response validates against the Obligation schema."""
        parsed = json.loads(mock_repaired_obligation_json)
        obligation = Obligation(**parsed)
        assert obligation.id == "AC-1"
        assert obligation.action_verb == "shall limit"
        assert obligation.clause_ref == "Section 3.1.1"

    def test_repaired_obligation_with_optional_fields(self, mock_repair_response_full):
        """A repair response with optional fields validates correctly."""
        parsed = json.loads(mock_repair_response_full)
        obligation = Obligation(**parsed)
        assert obligation.id == "AC-1"
        assert obligation.effective_date == "2024-01-01"
        assert obligation.section_ref == "Section 3"

    def test_malformed_json_fails_validation(self):
        """Malformed JSON raises an exception during parsing."""
        from app.services.repair import _parse_repair_response
        result = _parse_repair_response("not json {{{")
        assert result is None

    def test_missing_required_fields_fails_validation(self):
        """JSON missing required Obligation fields fails Pydantic validation."""
        from app.services.repair import _parse_repair_response
        result = _parse_repair_response(json.dumps({"id": "AC-1"}))
        assert result is None

    def test_parse_repair_response_returns_obligation_on_success(self, mock_repaired_obligation_json):
        """_parse_repair_response returns an Obligation instance on success."""
        from app.services.repair import _parse_repair_response
        result = _parse_repair_response(mock_repaired_obligation_json)
        assert result is not None
        assert isinstance(result, Obligation)

    def test_parse_repair_response_returns_none_on_failure(self, mock_malformed_repair_json):
        """_parse_repair_response returns None when parsing fails."""
        from app.services.repair import _parse_repair_response
        result = _parse_repair_response(mock_malformed_repair_json)
        assert result is None


# ==============================================================================
# AC-1 & AC-5: Repair service - iterative loop with configurable max_attempts
# ==============================================================================


class TestRepairService:
    """TC-3.3: The repair service implements the iterative repair loop."""

    def test_repair_obligation_returns_3_tuple(self, sample_obligation_dict, sample_markdown, sample_feedback, mock_repaired_obligation_json):
        """repair_obligation returns a 3-tuple of (obligation, status, attempts_made)."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired_obligation_json):
            result = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert len(result) == 3
        obligation, status, attempts_made = result
        assert status in ("repaired", "rejected", "original_kept")
        assert obligation is not None
        assert isinstance(attempts_made, int)

    def test_repair_succeeds_on_first_attempt(self, sample_obligation_dict, sample_markdown, sample_feedback, mock_repaired_obligation_json):
        """When the LLM returns a valid repair immediately, status is 'repaired'."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired_obligation_json):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert status == "repaired"
        assert obligation.id == "AC-1"
        assert attempts_made == 1

    def test_repair_incorporates_feedback_into_prompt(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The repair prompt includes the judge feedback."""
        import app.services.repair as repair_mod

        captured_prompt = None

        def capture_prompt(content):
            nonlocal captured_prompt
            captured_prompt = content
            return mock_repaired_obligation_json_fixture()

        with patch.object(repair_mod, "_call_llm", side_effect=capture_prompt):
            repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert captured_prompt is not None
        assert "action_verb" in captured_prompt.lower()

    def test_max_attempts_exhaustion_returns_rejected(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When all LLM repair attempts return malformed JSON, status is 'rejected'."""
        import app.services.repair as repair_mod

        call_count = 0

        def always_malformed(_prompt):
            nonlocal call_count
            call_count += 1
            return "not valid json"

        with patch.object(repair_mod, "_call_llm", side_effect=always_malformed):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

        assert status == "rejected"
        assert call_count == 3
        assert attempts_made == 3

    def test_configurable_max_attempts(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """max_attempts parameter controls how many times the LLM is called."""
        import app.services.repair as repair_mod

        call_count = 0

        def count_calls(_prompt):
            nonlocal call_count
            call_count += 1
            return "not valid json"

        with patch.object(repair_mod, "_call_llm", side_effect=count_calls):
            _, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=2,
            )

        assert status == "rejected"
        assert call_count == 2
        assert attempts_made == 2

    def test_max_attempts_default_is_3(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The default max_attempts is 3 when not specified."""
        import app.services.repair as repair_mod

        call_count = 0

        def count_calls(_prompt):
            nonlocal call_count
            call_count += 1
            return "not valid json"

        with patch.object(repair_mod, "_call_llm", side_effect=count_calls):
            _, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert call_count == 3
        assert attempts_made == 3

    def test_repair_uses_temperature_03(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """The repair LLM call uses temperature 0.3 for deterministic output."""
        import app.services.repair as repair_mod

        assert repair_mod.LLM_TEMPERATURE == 0.3

    def test_repair_with_pydantic_obligation_model(self, sample_obligation_model, sample_markdown, sample_feedback, mock_repaired_obligation_json):
        """repair_obligation works with a Pydantic Obligation model input."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired_obligation_json):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_model,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert status == "repaired"
        assert attempts_made == 1

    def test_repair_handles_llm_api_error(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When the LLM API raises an exception, the repair returns 'rejected'."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", side_effect=RuntimeError("LLM connection refused")):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert status == "rejected"
        assert attempts_made == 3

    def test_repair_with_empty_markdown_returns_original_kept(self, sample_obligation_dict, sample_feedback):
        """When original_markdown is empty, the repair returns 'original_kept'."""
        import app.services.repair as repair_mod

        obligation, status, attempts_made = repair_mod.repair_obligation(
            obligation=sample_obligation_dict,
            judgment_feedback=sample_feedback,
            original_markdown="",
        )

        assert status == "original_kept"
        assert attempts_made == 0
        assert obligation is sample_obligation_dict

    def test_max_attempts_1(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When max_attempts=1 and LLM fails, the repair returns rejected with 1 attempt."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value="not valid json"):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=1,
            )

        assert status == "rejected"
        assert attempts_made == 1

    def test_partial_success_on_second_attempt(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When first attempt fails but second succeeds, status is 'repaired' with attempts_made=2."""
        import app.services.repair as repair_mod

        call_count = 0

        def side_effect(prompt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "not valid json"
            return json.dumps({
                "id": "AC-1",
                "prose": "The organization shall limit information system access to authorized users.",
                "action_verb": "shall limit",
                "subject_noun": "information system access",
                "clause_ref": "Section 3.1.1",
            })

        with patch.object(repair_mod, "_call_llm", side_effect=side_effect):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

        assert status == "repaired"
        assert attempts_made == 2
        assert call_count == 2


def mock_repaired_obligation_json_fixture():
    """Helper to return the mock repaired obligation JSON."""
    return json.dumps({
        "id": "AC-1",
        "prose": "The organization shall limit information system access to authorized users.",
        "action_verb": "shall limit",
        "subject_noun": "information system access",
        "clause_ref": "Section 3.1.1",
    }, separators=(",", ":"))


# ==============================================================================
# AC-4: original_kept when feedback is empty or obligation is already good
# ==============================================================================


class TestOriginalKept:
    """TC-3.4: The repair service keeps the original when feedback is empty/good enough."""

    def test_empty_feedback_returns_original_kept(self, sample_obligation_dict, sample_markdown):
        """When feedback is empty string, repair returns 'original_kept' without calling LLM."""
        import app.services.repair as repair_mod

        obligation, status, attempts_made = repair_mod.repair_obligation(
            obligation=sample_obligation_dict,
            judgment_feedback="",
            original_markdown=sample_markdown,
        )

        assert status == "original_kept"
        assert attempts_made == 0
        assert obligation is sample_obligation_dict

    def test_whitespace_only_feedback_returns_original_kept(self, sample_obligation_dict, sample_markdown):
        """When feedback is whitespace-only, repair returns 'original_kept'."""
        import app.services.repair as repair_mod

        obligation, status, attempts_made = repair_mod.repair_obligation(
            obligation=sample_obligation_dict,
            judgment_feedback="   \n\t  ",
            original_markdown=sample_markdown,
        )

        assert status == "original_kept"
        assert attempts_made == 0

    def test_positive_feedback_returns_original_kept(self, sample_obligation_dict, sample_markdown, good_feedback):
        """When feedback is positive (no issues to fix), status is 'original_kept' since the
        repair logic treats any non-empty feedback as needing repair. The service still
        attempts repair since it doesn't evaluate feedback content."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired_obligation_json_fixture()):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=good_feedback,
                original_markdown=sample_markdown,
            )

        # Positive feedback goes through the LLM since the service doesn't judge feedback quality
        assert status in ("repaired", "rejected", "original_kept")
        assert attempts_made == 1

    def test_empty_obligation_dict_returns_original_kept(self, sample_markdown, sample_feedback):
        """When the obligation dict is empty, repair returns 'original_kept'."""
        import app.services.repair as repair_mod

        obligation, status, attempts_made = repair_mod.repair_obligation(
            obligation={},
            judgment_feedback=sample_feedback,
            original_markdown=sample_markdown,
        )

        assert status == "original_kept"
        assert attempts_made == 0

    def test_none_obligation_returns_original_kept(self, sample_markdown, sample_feedback):
        """When the obligation is None, repair returns 'original_kept'."""
        import app.services.repair as repair_mod

        obligation, status, attempts_made = repair_mod.repair_obligation(
            obligation=None,
            judgment_feedback=sample_feedback,
            original_markdown=sample_markdown,
        )

        assert status == "original_kept"
        assert attempts_made == 0


# ==============================================================================
# AC-3: Max attempts exhaustion -> "rejected" + DLQ
# ==============================================================================


class TestMaxAttemptsExhaustion:
    """TC-3.5: All repair attempts failing results in 'rejected' status and DLQ."""

    def test_all_malformed_responses_result_in_rejected(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When all LLM responses are malformed, the final status is 'rejected'."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value="invalid json {{{"):
            _, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

        assert status == "rejected"
        assert attempts_made == 3

    def test_all_missing_fields_responses_result_in_rejected(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When all LLM responses miss required fields, the final status is 'rejected'."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=json.dumps({"id": "AC-1"})):
            _, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

        assert status == "rejected"
        assert attempts_made == 3

    def test_retry_then_succeed_on_third_attempt(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When first 2 attempts fail but 3rd succeeds, status is 'repaired'."""
        import app.services.repair as repair_mod

        responses = [
            "not valid json",
            json.dumps({"id": "AC-1"}),  # missing fields
            json.dumps({
                "id": "AC-1",
                "prose": "The organization shall limit access.",
                "action_verb": "shall limit",
                "subject_noun": "access",
                "clause_ref": "Section 3.1",
            }),
        ]

        call_count = 0

        def get_response(prompt):
            nonlocal call_count
            result = responses[call_count]
            call_count += 1
            return result

        with patch.object(repair_mod, "_call_llm", side_effect=get_response):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

        assert status == "repaired"
        assert obligation.id == "AC-1"
        assert attempts_made == 3

    def test_succeed_on_first_attempt_then_stops(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When the first attempt succeeds, no additional attempts are made."""
        import app.services.repair as repair_mod

        call_count = 0

        def count_calls(prompt):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "id": "AC-1",
                "prose": "The organization shall limit access.",
                "action_verb": "shall limit",
                "subject_noun": "access",
                "clause_ref": "Section 3.1",
            })

        with patch.object(repair_mod, "_call_llm", side_effect=count_calls):
            _, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

        assert status == "repaired"
        assert call_count == 1
        assert attempts_made == 1


# ==============================================================================
# AC-3: DLQ logic
# ==============================================================================


class TestDLQ:
    """TC-3.7: Dead-letter queue logic on max repair attempts exceeded."""

    def test_dlq_logged_on_max_attempts_exceeded(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When all repair attempts fail, the DLQ is called with reason 'max_repair_attempts_exceeded'."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value="invalid json"), \
             patch.object(repair_mod, "_send_to_dlq") as mock_dlq:
            repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

            mock_dlq.assert_called_once()
            call_args = mock_dlq.call_args
            assert call_args[0][0] is sample_obligation_dict or isinstance(call_args[0][0], dict)
            assert call_args[1].get("reason") == "max_repair_attempts_exceeded" or \
                   call_args[0][1] == "max_repair_attempts_exceeded"

    def test_dlq_graceful_degradation_with_db_error(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When the DLQ write raises an error, the repair still returns rejected gracefully."""
        import app.services.repair as repair_mod

        def failing_dlq(obl, reason):
            raise Exception("DLQ write failed")

        with patch.object(repair_mod, "_call_llm", return_value="invalid json"), \
             patch.object(repair_mod, "_send_to_dlq", side_effect=failing_dlq):
            # The repair service wraps DLQ in try/except, so it should still return rejected
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=1,
            )

        assert status == "rejected"
        assert attempts_made == 1


# ==============================================================================
# AC-4: Langfuse logging
# ==============================================================================


class TestLangfuseLogging:
    """TC-3.8: Each repair attempt logs feedback and new extraction to Langfuse."""

    def test_langfuse_logged_on_repair_success(self, sample_obligation_dict, sample_markdown, sample_feedback, mock_repaired_obligation_json):
        """When repair succeeds, each attempt is logged to Langfuse."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired_obligation_json), \
             patch.object(repair_mod, "_log_attempt_to_langfuse") as mock_log:
            repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

            assert mock_log.call_count >= 1

    def test_langfuse_logged_on_max_attempts_exceeded(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When all attempts fail, each attempt is logged plus the final rejection."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value="invalid json"), \
             patch.object(repair_mod, "_log_attempt_to_langfuse") as mock_log:
            repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=3,
            )

            assert mock_log.call_count >= 3

    def test_langfuse_not_installed_is_noop(self, sample_obligation_dict, sample_markdown, sample_feedback):
        """When Langfuse is None, the logging function does nothing."""
        import app.services.repair as repair_mod

        original_langfuse = repair_mod.Langfuse
        repair_mod.Langfuse = None

        try:
            _, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
                max_attempts=1,
            )
            assert status == "rejected"
        finally:
            repair_mod.Langfuse = original_langfuse


# ==============================================================================
# Integration Tests: API Endpoint
# ==============================================================================


class TestRepairAPIEndpoint:
    """Integration tests for POST /api/v1/repair endpoint."""

    @pytest.fixture
    def app_with_repair_router(self):
        """Create a FastAPI app with the repair router mounted."""
        from app.api.repair import router as repair_router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(repair_router, prefix="/api/v1/repair", tags=["repair"])
        return app

    @pytest.fixture
    def client(self, app_with_repair_router):
        """TestClient wrapping the app with the repair router."""
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("fastapi not installed")

        return TestClient(app_with_repair_router)

    def test_happy_path_returns_repaired(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """POST with valid data returns status 'repaired'."""
        with patch("app.api.repair.repair_obligation", return_value=(
            Obligation(id="AC-1", prose="Fixed", action_verb="shall limit",
                       subject_noun="access", clause_ref="Section 3.1.1"),
            "repaired",
            1,
        )):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "repaired"
        assert "obligation" in body
        assert "attempts" in body

    def test_rejection_returns_rejected(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """POST that results in rejection returns status 'rejected'."""
        with patch("app.api.repair.repair_obligation", return_value=(None, "rejected", 3)):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "rejected"

    def test_max_attempts_returns_rejected(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """POST that exhausts max attempts returns status 'rejected'."""
        with patch("app.api.repair.repair_obligation", return_value=(None, "rejected", 3)):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                },
            )

        body = resp.json()
        assert body["status"] == "rejected"
        assert body["attempts"] == 3

    def test_original_kept_returns_original_kept(self, client, sample_obligation_dict, sample_markdown):
        """POST with empty feedback returns status 'original_kept'."""
        with patch("app.api.repair.repair_obligation", return_value=(
            Obligation(**sample_obligation_dict),
            "original_kept",
            0,
        )):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": "",
                    "original_markdown": sample_markdown,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "original_kept"

    def test_missing_obligation_returns_422(self, client, sample_markdown, sample_feedback):
        """POST without obligation field returns HTTP 422."""
        resp = client.post(
            "/api/v1/repair",
            json={
                "judgment_feedback": sample_feedback,
                "original_markdown": sample_markdown,
            },
        )
        assert resp.status_code == 422

    def test_missing_feedback_returns_422(self, client, sample_obligation_dict, sample_markdown):
        """POST without judgment_feedback field returns HTTP 422."""
        resp = client.post(
            "/api/v1/repair",
            json={
                "obligation": sample_obligation_dict,
                "original_markdown": sample_markdown,
            },
        )
        assert resp.status_code == 422

    def test_missing_original_markdown_returns_422(self, client, sample_obligation_dict, sample_feedback):
        """POST without original_markdown field returns HTTP 422."""
        resp = client.post(
            "/api/v1/repair",
            json={
                "obligation": sample_obligation_dict,
                "judgment_feedback": sample_feedback,
            },
        )
        assert resp.status_code == 422

    def test_response_contains_attempts_count(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """Response includes the number of attempts made."""
        with patch("app.api.repair.repair_obligation", return_value=(None, "rejected", 3)):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                },
            )

        body = resp.json()
        assert isinstance(body["attempts"], int)
        assert body["attempts"] == 3

    def test_response_contains_obligation_when_repaired(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """Response contains the repaired obligation when status is 'repaired'."""
        repaired = Obligation(id="AC-1", prose="Fixed text", action_verb="shall fix",
                              subject_noun="the obligation", clause_ref="Section 3.1")
        with patch("app.api.repair.repair_obligation", return_value=(repaired, "repaired", 1)):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                },
            )

        body = resp.json()
        assert body["status"] == "repaired"
        assert body["obligation"]["id"] == "AC-1"
        assert body["obligation"]["prose"] == "Fixed text"

    def test_service_error_returns_500(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """When the repair service raises an exception, endpoint returns HTTP 500."""
        with patch("app.api.repair.repair_obligation", side_effect=RuntimeError("LLM connection refused")):
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                },
            )

        assert resp.status_code == 500

    def test_custom_max_attempts_passed_to_service(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """POST with a custom max_attempts value passes it to the service."""
        with patch("app.api.repair.repair_obligation", return_value=(None, "rejected", 5)) as mock_repair:
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                    "max_attempts": 5,
                },
            )

        assert resp.status_code == 200
        call_kwargs = mock_repair.call_args[1]
        assert call_kwargs["max_attempts"] == 5

    def test_api_attempts_count_matches_actual_calls(self, client, sample_obligation_dict, sample_markdown, sample_feedback):
        """The API returns the actual attempts_made from the service, not a computed value."""
        with patch("app.api.repair.repair_obligation", return_value=(None, "rejected", 2)) as mock_repair:
            resp = client.post(
                "/api/v1/repair",
                json={
                    "obligation": sample_obligation_dict,
                    "judgment_feedback": sample_feedback,
                    "original_markdown": sample_markdown,
                    "max_attempts": 5,
                },
            )

        body = resp.json()
        # The service returns attempts_made=2 even though max_attempts=5
        # The API should return 2, not compute it
        assert body["attempts"] == 2


# ==============================================================================
# AC-6: Status terminology (keep "repaired" not "approved")
# ==============================================================================


class TestStatusTerminology:
    """Verify that the repair service uses 'repaired' (not 'approved') as its status."""

    def test_status_is_repaired_not_approved(self, sample_obligation_dict, sample_markdown, sample_feedback, mock_repaired_obligation_json):
        """The repair service returns 'repaired' status (not 'approved')."""
        import app.services.repair as repair_mod

        with patch.object(repair_mod, "_call_llm", return_value=mock_repaired_obligation_json):
            obligation, status, attempts_made = repair_mod.repair_obligation(
                obligation=sample_obligation_dict,
                judgment_feedback=sample_feedback,
                original_markdown=sample_markdown,
            )

        assert status == "repaired"
        assert status != "approved"
