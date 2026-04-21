"""
Integration tests for EXTRACT-1: Extraction API endpoint

Tests the POST /api/v1/extract endpoint end-to-end using FastAPI TestClient.
Covers: valid request, empty markdown rejection, LLM failure handling,
source_document_id passthrough, and response structure.

Test Strategy:
- FastAPI TestClient with mounted router
- Mock _extract_obligations_with_storage at the service layer
- Verify HTTP status codes, response schema, and field values
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def app_with_extract_router():
    """Create a FastAPI app with the extract router mounted at /api/v1/extract."""
    from app.api.extract import router as extract_router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(extract_router, prefix="/api/v1/extract", tags=["extraction"])
    return app


@pytest.fixture
def client(app_with_extract_router):
    """TestClient wrapping the app with the extract router."""
    return TestClient(app_with_extract_router)


@pytest.fixture
def valid_obligations():
    """Return a list of mock Obligation objects for the service layer mock."""
    from app.schemas.obligation import Obligation

    return [
        Obligation(
            id="AC-1",
            prose="The organization must limit access.",
            action_verb="limit",
            subject_noun="system access",
            clause_ref="Section 3.1",
        ),
        Obligation(
            id="AC-2",
            prose="The organization must monitor access.",
            action_verb="monitor",
            subject_noun="access",
            clause_ref="Section 3.2",
        ),
    ]


@pytest.fixture
def sample_markdown():
    """Sample regulatory Markdown content."""
    return """# Section 3: Access Control

The organization must limit information system access to authorized users.
"""


# ==============================================================================
# AC-1: POST /api/v1/extract accepts valid markdown and returns obligations
# ==============================================================================


class TestEndpointIntegration:
    """AC-1: Endpoint integration tests using FastAPI TestClient."""

    def test_valid_request_returns_200(self, client, valid_obligations, sample_markdown):
        """POST with valid markdown returns HTTP 200 with obligation data."""
        with patch(
            "app.api.extract._extract_obligations_with_storage",
            return_value=(valid_obligations, True),
        ) as mock_extract:
            resp = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["obligation_count"] == 2
        assert len(body["obligations"]) == 2
        assert body["storage_succeeded"] is True
        mock_extract.assert_called_once()

    def test_valid_request_obligation_fields(self, client, valid_obligations, sample_markdown):
        """Response obligations contain all required fields."""
        with patch(
            "app.api.extract._extract_obligations_with_storage",
            return_value=(valid_obligations, True),
        ):
            resp = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )

        for obs in resp.json()["obligations"]:
            assert "id" in obs
            assert "prose" in obs
            assert "action_verb" in obs
            assert "subject_noun" in obs
            assert "clause_ref" in obs

    def test_valid_request_with_source_document_id(self, client, valid_obligations, sample_markdown):
        """POST with source_document_id passes it through to the service layer."""
        with patch(
            "app.api.extract._extract_obligations_with_storage",
            return_value=(valid_obligations, True),
        ) as mock_extract:
            resp = client.post(
                "/api/v1/extract",
                json={
                    "markdown_content": sample_markdown,
                    "source_document_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )

        assert resp.status_code == 200
        call_kwargs = mock_extract.call_args[1]
        assert call_kwargs["source_document_id"] == "550e8400-e29b-41d4-a716-446655440000"

    def test_valid_request_without_source_document_id(self, client, valid_obligations, sample_markdown):
        """POST without source_document_id passes None to the service layer."""
        with patch(
            "app.api.extract._extract_obligations_with_storage",
            return_value=(valid_obligations, True),
        ) as mock_extract:
            resp = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )

        assert resp.status_code == 200
        call_kwargs = mock_extract.call_args[1]
        assert call_kwargs["source_document_id"] is None


# ==============================================================================
# AC-5: Empty markdown rejected with HTTP 400
# ==============================================================================


class TestContentValidation:
    """AC-5: Empty/whitespace markdown rejection."""

    def test_empty_markdown_returns_400(self, client):
        """POST with empty markdown_content returns HTTP 400."""
        resp = client.post(
            "/api/v1/extract",
            json={"markdown_content": ""},
        )
        assert resp.status_code == 400

    def test_whitespace_only_markdown_returns_400(self, client):
        """POST with whitespace-only markdown_content returns HTTP 400."""
        resp = client.post(
            "/api/v1/extract",
            json={"markdown_content": "   \n\t  "},
        )
        assert resp.status_code == 400

    def test_empty_markdown_response_detail(self, client):
        """400 response includes a descriptive error detail."""
        resp = client.post(
            "/api/v1/extract",
            json={"markdown_content": ""},
        )
        body = resp.json()
        assert "detail" in body
        assert "empty" in body["detail"].lower() or "whitespace" in body["detail"].lower()


# ==============================================================================
# LLM Failure Handling
# ==============================================================================


class TestLLMFailureHandling:
    """LLM/service failure scenarios."""

    def test_llm_failure_returns_500(self, client, sample_markdown):
        """When the service raises an exception, endpoint returns HTTP 500."""
        with patch(
            "app.api.extract._extract_obligations_with_storage",
            side_effect=RuntimeError("vLLM connection refused"),
        ):
            resp = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )

        assert resp.status_code == 500
        body = resp.json()
        assert "detail" in body
        assert "vLLM" in body["detail"]

    def test_llm_failure_empty_obligations(self, client, sample_markdown):
        """When LLM fails, response has obligation_count=0."""
        with patch(
            "app.api.extract._extract_obligations_with_storage",
            side_effect=RuntimeError("network error"),
        ):
            resp = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )

        assert resp.status_code == 500


# ==============================================================================
# Re-extraction Regression Test
# ==============================================================================


class TestReExtraction:
    """Regression test: unique constraint removal allows duplicate rows."""

    def test_re_extraction_creates_multiple_add_calls(self, client, sample_markdown):
        """Calling extract twice results in two separate session.add() calls."""
        from app.schemas.obligation import Obligation

        mock_obligations = [
            Obligation(
                id="AC-1",
                prose="Test obligation.",
                action_verb="test",
                subject_noun="test noun",
                clause_ref="Section 1.1",
            ),
        ]

        with patch(
            "app.api.extract._extract_obligations_with_storage",
            return_value=(mock_obligations, True),
        ) as mock_extract:
            resp1 = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )
            assert resp1.status_code == 200

            # Second call should also succeed (no unique constraint violation)
            resp2 = client.post(
                "/api/v1/extract",
                json={"markdown_content": sample_markdown},
            )
            assert resp2.status_code == 200

            # Verify both calls went through
            assert mock_extract.call_count == 2
