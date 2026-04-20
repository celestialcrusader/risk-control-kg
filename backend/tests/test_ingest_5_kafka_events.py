"""
Test suite for INGEST-5: Kafka Event Publishing

This test module verifies the document ingestion pipeline event publishing
including:
- Four event types: ingested, converted, chunked, bronzed
- Each event has the correct payload fields
- Retry with exponential backoff when broker unavailable
- DLQ delivery when all retries exhausted
- PipelineEventPublisher coordinator

Test Strategy:
- Unit tests with mocked KafkaProducer
- All assertions are meaningful
- AAA pattern (Arrange, Act, Assert)

Acceptance Criteria Covered:
- AC-1: document.ingested event with {doc_id, hash, source_path, uploaded_at}
- AC-2: document.converted event with {doc_id, chunks, md5_hash, conversion_time_ms}
- AC-3: document.chunked event with {doc_id, chunk_count, manifest_uri}
- AC-4: document.bronzed event with {doc_id, bronze_uri, checksum}
- AC-5: Retry with exponential backoff (base 1s, max 3 retries)
- AC-6: DLQ delivery when retries exhausted
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timezone

import pytest

# Ensure app module is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_kafka_producer():
    """Create a mock KafkaProducer that records publish calls."""
    mock = MagicMock()
    mock.publish = MagicMock(return_value=None)
    return mock


@pytest.fixture
def sample_doc_id():
    """A sample document ID for tests."""
    return "doc-test-001"


@pytest.fixture
def sample_uploaded_at():
    """A sample uploaded_at timestamp."""
    return datetime(2026, 4, 20, 10, 30, 0, tzinfo=timezone.utc)


# ==============================================================================
# AC-1: document.ingested event
# ==============================================================================


class TestDocumentIngestedEvent:
    """TC-5.1: publish_ingested_event publishes to document.ingested topic."""

    def test_publish_ingested_event_calls_kafka_publish(
        self, mock_kafka_producer
    ):
        """publish_ingested_event() calls KafkaProducer.publish on the correct topic."""
        from app.services.event_publisher import publish_ingested_event

        doc_id = "doc-ingest-1"
        file_hash = "sha256:abc123"
        source_path = "/data/uploads/report.pdf"
        uploaded_at = "2026-04-20T10:30:00+00:00"

        publish_ingested_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            hash=file_hash,
            source_path=source_path,
            uploaded_at=uploaded_at,
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.ingested"

    def test_publish_ingested_event_includes_required_fields(
        self, mock_kafka_producer
    ):
        """The event payload contains doc_id, hash, source_path, uploaded_at."""
        from app.services.event_publisher import publish_ingested_event

        doc_id = "doc-ingest-2"
        file_hash = "sha256:def456"
        source_path = "/data/uploads/manual.pdf"
        uploaded_at = "2026-04-20T11:00:00+00:00"

        publish_ingested_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            hash=file_hash,
            source_path=source_path,
            uploaded_at=uploaded_at,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]

        # The value is serialized to JSON bytes by KafkaProducer.publish
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["doc_id"] == doc_id
        assert payload["hash"] == file_hash
        assert payload["source_path"] == source_path
        assert payload["uploaded_at"] == uploaded_at

    def test_publish_ingested_event_includes_pipeline_stage(
        self, mock_kafka_producer
    ):
        """The event includes a pipeline_stage field set to 'ingested'."""
        from app.services.event_publisher import publish_ingested_event

        publish_ingested_event(
            producer=mock_kafka_producer,
            doc_id="doc-stage-test",
            hash="sha256:stage",
            source_path="/data/uploads/test.pdf",
            uploaded_at="2026-04-20T10:00:00+00:00",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["pipeline_stage"] == "ingested"

    def test_publish_ingested_event_uses_doc_id_as_key(
        self, mock_kafka_producer
    ):
        """The Kafka message key is the doc_id for partitioning."""
        from app.services.event_publisher import publish_ingested_event

        doc_id = "doc-key-test-42"

        publish_ingested_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            hash="sha256:keytest",
            source_path="/data/uploads/test.pdf",
            uploaded_at="2026-04-20T10:00:00+00:00",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.ingested"
        assert call_kwargs["key"] == doc_id


# ==============================================================================
# AC-2: document.converted event
# ==============================================================================


class TestDocumentConvertedEvent:
    """TC-5.2: publish_converted_event publishes to document.converted topic."""

    def test_publish_converted_event_calls_kafka_publish(
        self, mock_kafka_producer
    ):
        """publish_converted_event() calls KafkaProducer.publish on correct topic."""
        from app.services.event_publisher import publish_converted_event

        doc_id = "doc-convert-1"
        chunk_count = 15
        md5_hash = "md5:abc123def456"
        conversion_time_ms = 2350

        publish_converted_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            chunks=chunk_count,
            md5_hash=md5_hash,
            conversion_time_ms=conversion_time_ms,
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.converted"

    def test_publish_converted_event_includes_required_fields(
        self, mock_kafka_producer
    ):
        """The event payload contains doc_id, chunks, md5_hash, conversion_time_ms."""
        from app.services.event_publisher import publish_converted_event

        doc_id = "doc-convert-2"
        chunk_count = 20
        md5_hash = "md5:def789"
        conversion_time_ms = 3100

        publish_converted_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            chunks=chunk_count,
            md5_hash=md5_hash,
            conversion_time_ms=conversion_time_ms,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["doc_id"] == doc_id
        assert payload["chunks"] == chunk_count
        assert payload["md5_hash"] == md5_hash
        assert payload["conversion_time_ms"] == conversion_time_ms

    def test_publish_converted_event_includes_pipeline_stage(
        self, mock_kafka_producer
    ):
        """The event includes pipeline_stage set to 'converted'."""
        from app.services.event_publisher import publish_converted_event

        publish_converted_event(
            producer=mock_kafka_producer,
            doc_id="doc-stage-conv",
            chunks=5,
            md5_hash="md5:stagetest",
            conversion_time_ms=1000,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["pipeline_stage"] == "converted"

    def test_publish_converted_event_uses_doc_id_as_key(
        self, mock_kafka_producer
    ):
        """The Kafka message key is the doc_id."""
        from app.services.event_publisher import publish_converted_event

        doc_id = "doc-key-convert-99"

        publish_converted_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            chunks=10,
            md5_hash="md5:keytest",
            conversion_time_ms=2000,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.converted"
        assert call_kwargs["key"] == doc_id


# ==============================================================================
# AC-3: document.chunked event
# ==============================================================================


class TestDocumentChunkedEvent:
    """TC-5.3: publish_chunked_event publishes to document.chunked topic."""

    def test_publish_chunked_event_calls_kafka_publish(
        self, mock_kafka_producer
    ):
        """publish_chunked_event() calls KafkaProducer.publish on correct topic."""
        from app.services.event_publisher import publish_chunked_event

        doc_id = "doc-chunk-1"
        chunk_count = 25
        manifest_uri = "minio://chunks/manifests/doc-chunk-1.json"

        publish_chunked_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            chunk_count=chunk_count,
            manifest_uri=manifest_uri,
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.chunked"

    def test_publish_chunked_event_includes_required_fields(
        self, mock_kafka_producer
    ):
        """The event payload contains doc_id, chunk_count, manifest_uri."""
        from app.services.event_publisher import publish_chunked_event

        doc_id = "doc-chunk-2"
        chunk_count = 30
        manifest_uri = "minio://chunks/manifests/doc-chunk-2.json"

        publish_chunked_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            chunk_count=chunk_count,
            manifest_uri=manifest_uri,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["doc_id"] == doc_id
        assert payload["chunk_count"] == chunk_count
        assert payload["manifest_uri"] == manifest_uri

    def test_publish_chunked_event_includes_pipeline_stage(
        self, mock_kafka_producer
    ):
        """The event includes pipeline_stage set to 'chunked'."""
        from app.services.event_publisher import publish_chunked_event

        publish_chunked_event(
            producer=mock_kafka_producer,
            doc_id="doc-stage-chunk",
            chunk_count=10,
            manifest_uri="minio://chunks/manifests/test.json",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["pipeline_stage"] == "chunked"

    def test_publish_chunked_event_uses_doc_id_as_key(
        self, mock_kafka_producer
    ):
        """The Kafka message key is the doc_id."""
        from app.services.event_publisher import publish_chunked_event

        doc_id = "doc-key-chunk-55"

        publish_chunked_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            chunk_count=12,
            manifest_uri="minio://chunks/manifests/55.json",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.chunked"
        assert call_kwargs["key"] == doc_id


# ==============================================================================
# AC-4: document.bronzed event
# ==============================================================================


class TestDocumentBronzedEvent:
    """TC-5.4: publish_bronzed_event publishes to document.bronzed topic."""

    def test_publish_bronzed_event_calls_kafka_publish(
        self, mock_kafka_producer
    ):
        """publish_bronzed_event() calls KafkaProducer.publish on correct topic."""
        from app.services.event_publisher import publish_bronzed_event

        doc_id = "doc-bronze-1"
        bronze_uri = "minio://bronze-layer/doc-bronze-1/chunks.json"
        checksum = "sha256:bronze_checksum_abc123"

        publish_bronzed_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            bronze_uri=bronze_uri,
            checksum=checksum,
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.bronzed"

    def test_publish_bronzed_event_includes_required_fields(
        self, mock_kafka_producer
    ):
        """The event payload contains doc_id, bronze_uri, checksum."""
        from app.services.event_publisher import publish_bronzed_event

        doc_id = "doc-bronze-2"
        bronze_uri = "minio://bronze-layer/doc-bronze-2/data.json"
        checksum = "sha256:bronze_checksum_def456"

        publish_bronzed_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            bronze_uri=bronze_uri,
            checksum=checksum,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["doc_id"] == doc_id
        assert payload["bronze_uri"] == bronze_uri
        assert payload["checksum"] == checksum

    def test_publish_bronzed_event_includes_pipeline_stage(
        self, mock_kafka_producer
    ):
        """The event includes pipeline_stage set to 'bronzed'."""
        from app.services.event_publisher import publish_bronzed_event

        publish_bronzed_event(
            producer=mock_kafka_producer,
            doc_id="doc-stage-bronze",
            bronze_uri="minio://bronze-layer/test.json",
            checksum="sha256:stagetest",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["pipeline_stage"] == "bronzed"

    def test_publish_bronzed_event_uses_doc_id_as_key(
        self, mock_kafka_producer
    ):
        """The Kafka message key is the doc_id."""
        from app.services.event_publisher import publish_bronzed_event

        doc_id = "doc-key-bronze-77"

        publish_bronzed_event(
            producer=mock_kafka_producer,
            doc_id=doc_id,
            bronze_uri="minio://bronze-layer/77.json",
            checksum="sha256:keytest",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.bronzed"
        assert call_kwargs["key"] == doc_id


# ==============================================================================
# AC-5: Retry with exponential backoff
# ==============================================================================


class TestRetryWithExponentialBackoff:
    """TC-5.5: Retry with exponential backoff when broker unavailable."""

    def test_retry_attempts_exponential_backoff_delays(
        self, mock_kafka_producer
    ):
        """Retries are attempted with 1s, 2s, 4s delays (base 1s exponential)."""
        from app.services.event_publisher import publish_with_retry

        # Simulate broker failure on first 3 attempts, success on 4th
        mock_kafka_producer.publish.side_effect = [
            ConnectionRefusedError("broker unavailable"),
            ConnectionRefusedError("broker unavailable"),
            ConnectionRefusedError("broker unavailable"),
            None,  # 4th attempt succeeds (1 initial + 3 retries)
        ]

        with patch("time.sleep") as mock_sleep:
            publish_with_retry(
                producer=mock_kafka_producer,
                topic="document.ingested",
                key="doc-retry-test",
                value={"doc_id": "doc-retry-test"},
                base_delay=1.0,
                max_retries=3,
            )

        # Should have been called 4 times total (1 initial + 3 retries)
        assert mock_kafka_producer.publish.call_count == 4

        # Verify sleep delays: 1s, 2s, 4s
        sleep_calls = [c[0][0] for c in mock_sleep.call_args_list]
        assert sleep_calls == [1.0, 2.0, 4.0]

    def test_retry_succeeds_after_retries(self, mock_kafka_producer):
        """publish_with_retry returns success after eventual success."""
        from app.services.event_publisher import publish_with_retry

        mock_kafka_producer.publish.side_effect = [
            ConnectionRefusedError("broker unavailable"),
            None,  # Succeeds on 2nd attempt
        ]

        result = publish_with_retry(
            producer=mock_kafka_producer,
            topic="document.ingested",
            key="doc-retry-success",
            value={"doc_id": "doc-retry-success"},
            base_delay=1.0,
            max_retries=3,
        )

        assert result == {"topic": "document.ingested", "status": "published"}
        assert mock_kafka_producer.publish.call_count == 2

    def test_retry_returns_dlq_when_all_retries_exhausted(
        self, mock_kafka_producer
    ):
        """When all retries fail, result indicates dlq routing."""
        from app.services.event_publisher import publish_with_retry

        mock_kafka_producer.publish.side_effect = ConnectionRefusedError(
            "broker unavailable"
        )

        with patch("time.sleep"):
            with patch(
                "app.services.event_publisher.publish_to_dlq"
            ) as mock_dlq:
                mock_dlq.return_value = {"topic": "document.ingested.dlq", "status": "dlq"}

                result = publish_with_retry(
                    producer=mock_kafka_producer,
                    topic="document.ingested",
                    key="doc-dlq-test",
                    value={"doc_id": "doc-dlq-test"},
                    base_delay=1.0,
                    max_retries=3,
                )

                assert result["status"] == "dlq"
                assert result["topic"] == "document.ingested.dlq"
                mock_dlq.assert_called_once()

    def test_retry_logs_each_failure(self, mock_kafka_producer):
        """Each retry attempt is logged."""
        import logging
        from app.services.event_publisher import publish_with_retry

        mock_kafka_producer.publish.side_effect = ConnectionRefusedError(
            "broker unavailable"
        )

        with patch("time.sleep"):
            with patch("app.services.event_publisher.logger") as mock_logger:
                with patch("app.services.event_publisher.publish_to_dlq"):
                    publish_with_retry(
                        producer=mock_kafka_producer,
                        topic="document.ingested",
                        key="doc-log-test",
                        value={"doc_id": "doc-log-test"},
                        base_delay=1.0,
                        max_retries=3,
                    )

                # Should have logged error for each failed attempt
                error_calls = [
                    c for c in mock_logger.error.call_args_list
                    if "Retry" in str(c) or "failed" in str(c).lower()
                ]
                # At least some log messages for failures
                assert len(mock_logger.error.call_args_list) >= 3

    def test_retry_zero_max_retries_no_retry(self, mock_kafka_producer):
        """With max_retries=0, only one attempt is made."""
        from app.services.event_publisher import publish_with_retry

        mock_kafka_producer.publish.side_effect = ConnectionRefusedError(
            "broker unavailable"
        )

        with patch("app.services.event_publisher.publish_to_dlq") as mock_dlq:
            mock_dlq.return_value = {"topic": "test.dlq", "status": "dlq"}

            with patch("time.sleep"):
                publish_with_retry(
                    producer=mock_kafka_producer,
                    topic="test.topic",
                    key="doc-no-retry",
                    value={"doc_id": "doc-no-retry"},
                    base_delay=1.0,
                    max_retries=0,
                )

            # Should have been called exactly once
            assert mock_kafka_producer.publish.call_count == 1


# ==============================================================================
# AC-6: DLQ delivery
# ==============================================================================


class TestDeadLetterQueue:
    """TC-5.6: DLQ delivery when all retries exhausted."""

    def test_publish_to_dlq_uses_topic_dlq_suffix(self, mock_kafka_producer):
        """DLQ messages are sent to {topic}.dlq."""
        from app.services.event_publisher import publish_to_dlq

        publish_to_dlq(
            producer=mock_kafka_producer,
            original_topic="document.ingested",
            key="doc-dlq-1",
            value={"doc_id": "doc-dlq-1"},
            error_message="broker unavailable",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.ingested.dlq"

    def test_publish_to_dlq_includes_error_info(self, mock_kafka_producer):
        """DLQ message includes the original error information."""
        from app.services.event_publisher import publish_to_dlq

        error_msg = "ConnectionRefusedError: broker unavailable"

        publish_to_dlq(
            producer=mock_kafka_producer,
            original_topic="document.converted",
            key="doc-dlq-2",
            value={"doc_id": "doc-dlq-2"},
            error_message=error_msg,
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert "error" in payload
        assert payload["error"] == error_msg
        assert payload["original_topic"] == "document.converted"

    def test_publish_to_dlq_includes_original_payload(self, mock_kafka_producer):
        """DLQ message preserves the original payload."""
        from app.services.event_publisher import publish_to_dlq

        original_value = {"doc_id": "doc-dlq-3", "chunks": 10}

        publish_to_dlq(
            producer=mock_kafka_producer,
            original_topic="document.chunked",
            key="doc-dlq-3",
            value=original_value,
            error_message="timeout",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert payload["doc_id"] == "doc-dlq-3"
        assert payload["chunks"] == 10

    def test_publish_to_dlq_includes_pipeline_stage(self, mock_kafka_producer):
        """DLQ message includes pipeline_stage for tracing."""
        from app.services.event_publisher import publish_to_dlq

        publish_to_dlq(
            producer=mock_kafka_producer,
            original_topic="document.bronzed",
            key="doc-dlq-4",
            value={"doc_id": "doc-dlq-4"},
            error_message="error",
        )

        call_kwargs = mock_kafka_producer.publish.call_args[1]
        value = call_kwargs["value"]
        if isinstance(value, bytes):
            payload = json.loads(value)
        else:
            payload = value

        assert "pipeline_stage" in payload

    def test_full_retry_then_dlq_flow(self, mock_kafka_producer):
        """Full flow: retries exhausted, then DLQ receives message with error."""
        from app.services.event_publisher import publish_with_retry

        mock_kafka_producer.publish.side_effect = ConnectionRefusedError(
            "broker down"
        )

        with patch("time.sleep"):
            with patch(
                "app.services.event_publisher.publish_to_dlq"
            ) as mock_dlq:
                mock_dlq.return_value = {
                    "topic": "document.ingested.dlq",
                    "status": "dlq",
                }

                result = publish_with_retry(
                    producer=mock_kafka_producer,
                    topic="document.ingested",
                    key="doc-full-flow",
                    value={"doc_id": "doc-full-flow"},
                    base_delay=1.0,
                    max_retries=3,
                )

                assert result["status"] == "dlq"
                assert result["topic"] == "document.ingested.dlq"
                # Verify DLQ was called with original payload and error
                dlq_call = mock_dlq.call_args[1]
                assert dlq_call["original_topic"] == "document.ingested"
                assert dlq_call["value"] == {"doc_id": "doc-full-flow"}
                assert "broker down" in dlq_call["error_message"]


# ==============================================================================
# PipelineEventPublisher coordinator
# ==============================================================================


class TestPipelineEventPublisher:
    """Tests for the PipelineEventPublisher class that coordinates all events."""

    def test_publisher_init_with_kafka_producer(self, mock_kafka_producer):
        """PipelineEventPublisher initializes with a KafkaProducer."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)
        assert publisher.producer is mock_kafka_producer

    def test_publish_ingested_via_publisher(self, mock_kafka_producer):
        """Publisher.publish_ingested publishes the ingested event."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)

        publisher.publish_ingested(
            doc_id="doc-pub-1",
            hash="sha256:pubtest",
            source_path="/data/uploads/test.pdf",
            uploaded_at="2026-04-20T10:00:00+00:00",
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.ingested"

    def test_publish_converted_via_publisher(self, mock_kafka_producer):
        """Publisher.publish_converted publishes the converted event."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)

        publisher.publish_converted(
            doc_id="doc-pub-2",
            chunks=15,
            md5_hash="md5:pubtest",
            conversion_time_ms=2500,
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.converted"

    def test_publish_chunked_via_publisher(self, mock_kafka_producer):
        """Publisher.publish_chunked publishes the chunked event."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)

        publisher.publish_chunked(
            doc_id="doc-pub-3",
            chunk_count=20,
            manifest_uri="minio://manifests/3.json",
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.chunked"

    def test_publish_bronzed_via_publisher(self, mock_kafka_producer):
        """Publisher.publish_bronzed publishes the bronzed event."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)

        publisher.publish_bronzed(
            doc_id="doc-pub-4",
            bronze_uri="minio://bronze/4.json",
            checksum="sha256:pubtest",
        )

        mock_kafka_producer.publish.assert_called_once()
        call_kwargs = mock_kafka_producer.publish.call_args[1]
        assert call_kwargs["topic"] == "document.bronzed"

    def test_run_pipeline_publishes_all_four_events(
        self, mock_kafka_producer
    ):
        """run_pipeline() publishes all four events in sequence."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)

        result = publisher.run_pipeline(
            doc_id="doc-pipeline-1",
            hash="sha256:piptest",
            source_path="/data/uploads/pipeline.pdf",
            uploaded_at="2026-04-20T10:00:00+00:00",
            chunks=25,
            md5_hash="md5:piptest",
            conversion_time_ms=5000,
            chunk_count=30,
            manifest_uri="minio://manifests/pipeline.json",
            bronze_uri="minio://bronze/pipeline.json",
            checksum="sha256:piptest",
        )

        assert mock_kafka_producer.publish.call_count == 4

        # Verify all topics were used
        published_topics = [
            c[1]["topic"] for c in mock_kafka_producer.publish.call_args_list
        ]
        assert "document.ingested" in published_topics
        assert "document.converted" in published_topics
        assert "document.chunked" in published_topics
        assert "document.bronzed" in published_topics

        # Verify order
        assert published_topics == [
            "document.ingested",
            "document.converted",
            "document.chunked",
            "document.bronzed",
        ]

        # Verify result
        assert "results" in result
        assert len(result["results"]) == 4
        for r in result["results"]:
            assert r["status"] == "published"

    def test_run_pipeline_handles_dlq_gracefully(
        self, mock_kafka_producer
    ):
        """run_pipeline() continues if one stage goes to DLQ."""
        from app.services.event_publisher import PipelineEventPublisher

        topic_call_counts: dict[str, int] = {}

        def side_effect(*args, **kwargs):
            topic = kwargs.get("topic", args[0] if args else "")
            topic_call_counts[topic] = topic_call_counts.get(topic, 0) + 1
            # 'document.converted' fails all 4 attempts (1 initial + 3 retries)
            if topic == "document.converted" and topic_call_counts[topic] <= 4:
                raise ConnectionRefusedError("broker down")
            return None

        mock_kafka_producer.publish.side_effect = side_effect

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)

        result = publisher.run_pipeline(
            doc_id="doc-pipeline-dlq",
            hash="sha256:dlqtest",
            source_path="/data/uploads/dlq.pdf",
            uploaded_at="2026-04-20T10:00:00+00:00",
            chunks=10,
            md5_hash="md5:dlqtest",
            conversion_time_ms=1000,
            chunk_count=15,
            manifest_uri="minio://manifests/dlq.json",
            bronze_uri="minio://bronze/dlq.json",
            checksum="sha256:dlqtest",
        )

        assert len(result["results"]) == 4
        # At least one result should indicate dlq
        statuses = [r["status"] for r in result["results"]]
        assert "dlq" in statuses

    def test_publisher_default_backoff_config(self, mock_kafka_producer):
        """PipelineEventPublisher defaults to base_delay=1.0 and max_retries=3."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(producer=mock_kafka_producer)
        assert publisher.base_delay == 1.0
        assert publisher.max_retries == 3

    def test_publisher_custom_backoff_config(self, mock_kafka_producer):
        """PipelineEventPublisher accepts custom backoff parameters."""
        from app.services.event_publisher import PipelineEventPublisher

        publisher = PipelineEventPublisher(
            producer=mock_kafka_producer,
            base_delay=2.0,
            max_retries=5,
        )
        assert publisher.base_delay == 2.0
        assert publisher.max_retries == 5
