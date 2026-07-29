"""
Tests for EXTRACT-5: Extraction Kafka Event.

Covers:
- AC1: Successful extraction publishes to extraction.completed topic
- AC2: Event includes extraction metadata (model, processing time, chunk count)
- AC3: Failed extraction publishes to extraction.failed topic with error reason
- AC4: Fire-and-forget — Kafka unavailability doesn't break extraction
- AC5: Integration with existing KafkaProducer and PipelinePublisher patterns
"""

import json
import time
from unittest.mock import MagicMock, patch, call

import pytest

from app.kafka.producer import KafkaProducer, _NullProducer
from app.services.extraction_event import (
    ExtractionEventPublisher,
    publish_extraction_completed_event,
    publish_extraction_failed_event,
)
from app.services.extraction import extract_obligations


# ==============================================================================
# Fixtures
# ==============================================================================


class MockProducer:
    """Lightweight mock of KafkaProducer that records publishes without network calls."""

    def __init__(self):
        self.published = []

    def publish(self, topic, key=None, value=None, headers=None):
        self.published.append({
            "topic": topic,
            "key": key,
            "value": value,
            "headers": headers,
        })

    def reset(self):
        self.published.clear()


@pytest.fixture
def mock_producer():
    return MockProducer()


@pytest.fixture
def event_publisher(mock_producer):
    return ExtractionEventPublisher(producer=mock_producer)


# ==============================================================================
# AC-1: On successful extraction, publish to extraction.completed topic
# ==============================================================================


class TestAC1ExtractionCompletedEvent:
    """AC-1: extraction.completed event is published on successful extraction."""

    def test_publishes_to_extration_completed_topic(self, mock_producer, event_publisher):
        """Event goes to the extraction.completed topic."""
        result = event_publisher.on_extraction_completed(
            document_id="doc-001",
            obligation_count=5,
            extraction_id="ext-001",
        )
        assert result["topic"] == "extraction.completed"
        assert result["status"] == "published"
        assert len(mock_producer.published) == 1
        assert mock_producer.published[0]["topic"] == "extraction.completed"

    def test_message_key_is_document_id(self, mock_producer, event_publisher):
        """Message key is set to document_id for partitioning."""
        event_publisher.on_extraction_completed(
            document_id="doc-002",
            obligation_count=3,
            extraction_id="ext-002",
        )
        assert mock_producer.published[0]["key"] == "doc-002"

    def test_event_payload_has_required_fields(self, mock_producer, event_publisher):
        """Payload contains all required fields: document_id, obligation_count, extraction_id."""
        event_publisher.on_extraction_completed(
            document_id="doc-003",
            obligation_count=7,
            extraction_id="ext-003",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["document_id"] == "doc-003"
        assert payload["obligation_count"] == 7
        assert payload["extraction_id"] == "ext-003"
        assert payload["event_type"] == "extraction.completed"

    def test_event_includes_obligation_ids(self, mock_producer, event_publisher):
        """Event includes the list of obligation IDs for downstream consumers."""
        event_publisher.on_extraction_completed(
            document_id="doc-004",
            obligation_count=3,
            extraction_id="ext-004",
            obligation_ids=["obl-A", "obl-B", "obl-C"],
        )
        payload = mock_producer.published[0]["value"]
        assert payload["obligation_ids"] == ["obl-A", "obl-B", "obl-C"]

    def test_event_includes_source_document_id(self, mock_producer, event_publisher):
        """Event includes source_document_id when provided."""
        event_publisher.on_extraction_completed(
            document_id="doc-005",
            obligation_count=2,
            extraction_id="ext-005",
            source_document_id="src-doc-uuid",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["source_document_id"] == "src-doc-uuid"


# ==============================================================================
# AC-2: Event includes extraction metadata (model, processing time, chunk count)
# ==============================================================================


class TestAC2ExtractionMetadata:
    """AC-2: Event includes model_used, processing_time_ms, chunk_count."""

    def test_includes_model_used(self, mock_producer, event_publisher):
        """Event includes which model was used for extraction."""
        event_publisher.on_extraction_completed(
            document_id="doc-010",
            obligation_count=4,
            extraction_id="ext-010",
            model_used="mistralai/Mistral-8B-Instruct-v0.1",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["model_used"] == "mistralai/Mistral-8B-Instruct-v0.1"

    def test_includes_processing_time_ms(self, mock_producer, event_publisher):
        """Event includes processing duration in milliseconds."""
        event_publisher.on_extraction_completed(
            document_id="doc-011",
            obligation_count=4,
            extraction_id="ext-011",
            processing_time_ms=1250,
        )
        payload = mock_producer.published[0]["value"]
        assert payload["processing_time_ms"] == 1250

    def test_includes_chunk_count(self, mock_producer, event_publisher):
        """Event includes chunk count processed."""
        event_publisher.on_extraction_completed(
            document_id="doc-012",
            obligation_count=4,
            extraction_id="ext-012",
            chunk_count=42,
        )
        payload = mock_producer.published[0]["value"]
        assert payload["chunk_count"] == 42

    def test_includes_timestamp(self, mock_producer, event_publisher):
        """Event includes a UTC timestamp."""
        event_publisher.on_extraction_completed(
            document_id="doc-013",
            obligation_count=1,
            extraction_id="ext-013",
        )
        payload = mock_producer.published[0]["value"]
        assert "timestamp" in payload
        assert payload["timestamp"].endswith("Z")

    def test_all_metadata_fields_present_together(self, mock_producer, event_publisher):
        """All metadata fields present in a single publish call."""
        event_publisher.on_extraction_completed(
            document_id="doc-014",
            obligation_count=10,
            extraction_id="ext-014",
            model_used="mistral-8b",
            processing_time_ms=2500,
            chunk_count=25,
            obligation_ids=["o1", "o2"],
            source_document_id="src-001",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["model_used"] == "mistral-8b"
        assert payload["processing_time_ms"] == 2500
        assert payload["chunk_count"] == 25
        assert payload["obligation_ids"] == ["o1", "o2"]
        assert payload["source_document_id"] == "src-001"
        assert payload["obligation_count"] == 10
        assert payload["event_type"] == "extraction.completed"


# ==============================================================================
# AC-3: Failed extraction publishes to extraction.failed topic with error reason
# ==============================================================================


class TestAC3ExtractionFailedEvent:
    """AC-3: Failed extraction publishes to extraction.failed with error reason."""

    def test_publishes_to_extration_failed_topic(self, mock_producer, event_publisher):
        """Event goes to the extraction.failed topic."""
        result = event_publisher.on_extraction_failed(
            document_id="doc-020",
            extraction_id="ext-fail-001",
            error_reason="LLM API unreachable",
        )
        assert result["topic"] == "extraction.failed"
        assert result["status"] == "published"
        assert len(mock_producer.published) == 1
        assert mock_producer.published[0]["topic"] == "extraction.failed"

    def test_includes_error_reason(self, mock_producer, event_publisher):
        """Event payload contains the error reason."""
        event_publisher.on_extraction_failed(
            document_id="doc-021",
            extraction_id="ext-fail-002",
            error_reason="Token limit exceeded",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["error_reason"] == "Token limit exceeded"

    def test_event_has_event_type_failed(self, mock_producer, event_publisher):
        """Event type is extraction.failed."""
        event_publisher.on_extraction_failed(
            document_id="doc-022",
            extraction_id="ext-fail-003",
            error_reason="Connection timeout",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["event_type"] == "extraction.failed"

    def test_includes_model_used_on_failure(self, mock_producer, event_publisher):
        """Failed event includes which model was being used."""
        event_publisher.on_extraction_failed(
            document_id="doc-023",
            extraction_id="ext-fail-004",
            error_reason="GPU OOM",
            model_used="qwen3.6-35b",
        )
        payload = mock_producer.published[0]["value"]
        assert payload["model_used"] == "qwen3.6-35b"

    def test_includes_processing_time_on_failure(self, mock_producer, event_publisher):
        """Failed event includes processing time before failure."""
        event_publisher.on_extraction_failed(
            document_id="doc-024",
            extraction_id="ext-fail-005",
            error_reason="LLM returned null",
            processing_time_ms=300,
        )
        payload = mock_producer.published[0]["value"]
        assert payload["processing_time_ms"] == 300

    def test_message_key_is_document_id_on_failure(self, mock_producer, event_publisher):
        """Message key is set to document_id for failed events too."""
        event_publisher.on_extraction_failed(
            document_id="doc-025",
            extraction_id="ext-fail-006",
            error_reason="network error",
        )
        assert mock_producer.published[0]["key"] == "doc-025"


# ==============================================================================
# AC-4: Fire-and-forget — Kafka unavailability doesn't break extraction
# ==============================================================================


class TestAC4GracefulDegradation:
    """AC-4: Kafka failures are silent — extraction never breaks."""

    def test_publisher_does_not_raise_on_kafka_failure(self, event_publisher):
        """on_extraction_completed never raises, even if Kafka is down."""
        # Use a producer that always raises
        failing_producer = MagicMock()
        failing_producer.publish = MagicMock(side_effect=ConnectionError("Kafka unreachable"))
        event_publisher_with_failing = ExtractionEventPublisher(producer=failing_producer)

        # Should NOT raise
        result = event_publisher_with_failing.on_extraction_completed(
            document_id="doc-030",
            obligation_count=3,
            extraction_id="ext-030",
        )
        assert result["status"] == "failed"
        assert "error" in result

    def test_failed_publish_does_not_break_extraction_flow(self, event_publisher):
        """Calling on_extraction_completed then on_extraction_failed still works if first fails."""
        failing_producer = MagicMock()
        failing_producer.publish = MagicMock(side_effect=TimeoutError("Timeout"))
        failing_publisher = ExtractionEventPublisher(producer=failing_producer)

        # First call fails
        result1 = failing_publisher.on_extraction_completed(
            document_id="doc-031",
            obligation_count=0,
            extraction_id="ext-031",
        )
        assert result1["status"] == "failed"

        # Second call also fails cleanly — no cascading errors
        result2 = failing_publisher.on_extraction_failed(
            document_id="doc-031",
            extraction_id="ext-031",
            error_reason="recovery attempt",
        )
        assert result2["status"] == "failed"

    def test_null_producer_publishes_without_error(self):
        """When confluent-kafka is not installed, _NullProducer handles publishes silently."""
        real_producer = KafkaProducer.__new__(KafkaProducer)
        real_producer._producer = _NullProducer()
        real_producer.topics = {}
        publisher = ExtractionEventPublisher(producer=real_producer)

        # Should not raise
        result = publisher.on_extraction_completed(
            document_id="doc-032",
            obligation_count=1,
            extraction_id="ext-032",
        )
        # _NullProducer.publish() does nothing, but our wrapper expects publish to return
        # The actual _NullProducer is called via publish_extraction_completed_event
        # which calls producer.publish() — _NullProducer.publish() returns None
        # The function returns {"topic": ..., "status": "published"} regardless
        assert result["topic"] == "extraction.completed"

    def test_publisher_with_no_producer_creates_default(self):
        """ExtractionEventPublisher with no producer creates a default KafkaProducer."""
        with patch("app.services.extraction_event.KafkaProducer") as MockKP:
            publisher = ExtractionEventPublisher()
            MockKP.assert_called_once()
            assert publisher.producer is not None


# ==============================================================================
# AC-5: Integration with existing KafkaProducer and PipelinePublisher patterns
# ==============================================================================


class TestAC5IntegrationWithExistingInfrastructure:
    """AC-5: Uses existing KafkaProducer, follows PipelinePublisher pattern."""

    def test_uses_existing_kafka_producer_publish_method(self, mock_producer):
        """The function calls KafkaProducer.publish() with correct args."""
        publish_extraction_completed_event(
            producer=mock_producer,
            document_id="doc-040",
            obligation_count=5,
            extraction_id="ext-040",
            source_document_id="src-040",
            model_used="mistral-8b",
            processing_time_ms=100,
            chunk_count=10,
        )
        published_call = mock_producer.published[0]
        assert published_call["topic"] == "extraction.completed"
        assert published_call["key"] == "doc-040"
        assert isinstance(published_call["value"], dict)

    def test_follows_same_pattern_as_pipeline_event_publisher(self, mock_producer):
        """The publish functions return the same structure as PipelinePublisher methods."""
        result = publish_extraction_completed_event(
            producer=mock_producer,
            document_id="doc-041",
            obligation_count=3,
            extraction_id="ext-041",
        )
        # PipelinePublisher returns {"topic": ..., "status": ...}
        assert "topic" in result
        assert "status" in result
        assert result["topic"] == "extraction.completed"
        assert result["status"] == "published"

    def test_topic_is_in_kafka_topic_registry(self):
        """extraction.completed and extraction.failed exist in the TOPICS registry (from INFRA-7)."""
        from app.kafka.topics import TOPICS
        topic_names = [t["name"] for t in TOPICS]
        assert "extraction.completed" in topic_names
        assert "extraction.failed" in topic_names

    def test_failed_topic_follows_same_publish_pattern(self, mock_producer):
        """publish_extraction_failed_event follows the same pattern as publish_* functions."""
        result = publish_extraction_failed_event(
            producer=mock_producer,
            document_id="doc-042",
            extraction_id="ext-042",
            error_reason="test failure",
        )
        assert "topic" in result
        assert "status" in result
        assert result["topic"] == "extraction.failed"
        assert result["status"] == "published"

    def test_event_publisher_delegates_to_kafka_producer(self, mock_producer, event_publisher):
        """ExtractionEventPublisher delegates publish calls to the KafkaProducer."""
        event_publisher.on_extraction_completed(
            document_id="doc-043",
            obligation_count=1,
            extraction_id="ext-043",
        )
        assert len(mock_producer.published) == 1

    def test_event_publisher_default_constructor_creates_producer(self):
        """Default constructor creates a KafkaProducer instance."""
        with patch("app.services.extraction_event.KafkaProducer") as MockKP:
            publisher = ExtractionEventPublisher()
            MockKP.assert_called_once_with()
            assert publisher.producer is not None


# ==============================================================================
# Integration test: Full extraction flow with event publishing
# ==============================================================================


class TestExtractionIntegration:
    """Integration: extract_obligations with event publisher (mocked LLM)."""

    def test_extract_obligations_publishes_completed_event(
        self, mock_producer, event_publisher
    ):
        """
        When extract_obligations succeeds with obligations,
        it publishes extraction.completed via the event_publisher.
        """
        with patch(
            "app.services.extraction._call_llm",
            return_value=json.dumps({
                "obligations": [
                    {
                        "id": "OBL-1",
                        "prose": "The system must authenticate users.",
                        "action_verb": "authenticate",
                        "subject_noun": "user access",
                        "clause_ref": "Section 1.1",
                    },
                ]
            }),
        ), patch(
            "app.services.extraction._store_obligations_in_semantic_controls",
            return_value=True,
        ):
            result = extract_obligations(
                markdown_content="# The system must authenticate users.",
                source_document_id="doc-src-001",
                event_publisher=event_publisher,
            )
            assert len(result) == 1
            assert result[0].id == "OBL-1"

        # Verify event was published
        assert len(mock_producer.published) == 1
        payload = mock_producer.published[0]["value"]
        assert payload["event_type"] == "extraction.completed"
        assert payload["document_id"] == "doc-src-001"
        assert payload["obligation_count"] == 1
        assert payload["obligation_ids"] == ["OBL-1"]
        assert payload["source_document_id"] == "doc-src-001"

    def test_extract_obligations_publishes_failed_event_on_no_obligations(
        self, mock_producer, event_publisher
    ):
        """
        When extract_obligations returns zero obligations,
        it publishes extraction.failed with error reason.
        """
        with patch(
            "app.services.extraction._call_llm",
            return_value=json.dumps({"obligations": []}),
        ), patch(
            "app.services.extraction._store_obligations_in_semantic_controls",
            return_value=True,
        ):
            result = extract_obligations(
                markdown_content="# Some text.",
                source_document_id="doc-src-002",
                event_publisher=event_publisher,
            )
            assert result == []

        # Verify failed event was published
        assert len(mock_producer.published) == 1
        payload = mock_producer.published[0]["value"]
        assert payload["event_type"] == "extraction.failed"
        assert payload["error_reason"] == "No obligations extracted or validation failed"

    def test_extract_obligations_no_publisher_skips_events(self):
        """When no event_publisher provided, no events are published (backward compatible)."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=json.dumps({
                "obligations": [
                    {
                        "id": "OBL-2",
                        "prose": "The system must encrypt data.",
                        "action_verb": "encrypt",
                        "subject_noun": "data at rest",
                        "clause_ref": "Section 2.0",
                    },
                ]
            }),
        ), patch(
            "app.services.extraction._store_obligations_in_semantic_controls",
            return_value=True,
        ):
            result = extract_obligations(
                markdown_content="# Encrypt data.",
            )
            assert len(result) == 1

    def test_extract_obligations_empty_content(self):
        """Empty content returns empty obligations without publishing events."""
        result = extract_obligations(
            markdown_content="",
        )
        assert result == []

    def test_extract_obligations_with_no_obligations_no_publisher(self):
        """No obligations + no publisher = no errors, just empty list."""
        with patch(
            "app.services.extraction._call_llm",
            return_value=json.dumps({"obligations": []}),
        ), patch(
            "app.services.extraction._store_obligations_in_semantic_controls",
            return_value=True,
        ):
            result = extract_obligations(
                markdown_content="# Empty obligations.",
            )
            assert result == []
