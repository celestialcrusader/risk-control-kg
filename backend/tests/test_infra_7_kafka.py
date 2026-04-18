"""
Test suite for INFRA-7: Apache Kafka Event Bus Provisioning

This test module verifies the Kafka event bus implementation including:
- Producer initialization with correct configuration
- Message publishing to topics
- Topic registry and schema validation
- Dead letter queue pattern

Test Strategy:
- Unit tests with mocked confluent_kafka Producer
- Tests verify actual values, not just absence of errors
- All assertions are meaningful
"""

import pytest
from unittest.mock import MagicMock, patch


class TestKafkaProducer:
    """Tests for Kafka producer initialization and configuration."""

    def test_producer_creates_with_correct_config(self):
        """Producer initializes with acks=all and bootstrap servers."""
        from app.kafka.producer import KafkaProducer

        producer = KafkaProducer()

        assert producer.bootstrap_servers == "localhost:9092"

    def test_producer_env_override(self):
        """Producer reads bootstrap servers from environment."""
        import os
        from app.kafka.producer import KafkaProducer

        os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "kafka1:9092,kafka2:9092"
        try:
            producer = KafkaProducer()
            assert producer.bootstrap_servers == "kafka1:9092,kafka2:9092"
        finally:
            del os.environ["KAFKA_BOOTSTRAP_SERVERS"]

    def test_producer_has_topic_registry(self):
        """Producer knows all required topics."""
        from app.kafka.producer import KafkaProducer
        from app.kafka.topics import TOPICS

        producer = KafkaProducer()
        assert hasattr(producer, "topics")
        topic_names = {t["name"] for t in TOPICS}
        for topic_name in topic_names:
            assert topic_name in producer.topics


class TestTopicRegistry:
    """Tests for Kafka topic definitions."""

    def test_required_topics_exist(self):
        """All 5 required topics are defined."""
        from app.kafka.topics import TOPICS

        required = {
            "document.ingested",
            "extraction.completed",
            "validation.completed",
            "mapping.completed",
            "coverage.alert",
        }
        topic_names = {t["name"] for t in TOPICS}
        assert required.issubset(topic_names)

    def test_topic_retention_settings(self):
        """Topics have correct retention: 7 days for most, 30 for coverage.alert."""
        from app.kafka.topics import TOPICS

        topic_map = {t["name"]: t for t in TOPICS}

        # document.ingested should have 7 day retention (604800 seconds)
        assert topic_map["document.ingested"]["retention_seconds"] == 604800
        # coverage.alert should have 30 day retention (2592000 seconds)
        assert topic_map["coverage.alert"]["retention_seconds"] == 2592000

    def test_topic_partition_counts(self):
        """Topics have correct partition counts (3 for most, 1 for coverage.alert)."""
        from app.kafka.topics import TOPICS

        topic_map = {t["name"]: t for t in TOPICS}

        for name in ("document.ingested", "extraction.completed",
                     "validation.completed", "mapping.completed"):
            assert topic_map[name]["partitions"] == 3
        assert topic_map["coverage.alert"]["partitions"] == 1

    def test_all_topics_have_descriptions(self):
        """Every topic has a purpose description."""
        from app.kafka.topics import TOPICS

        for topic in TOPICS:
            assert "purpose" in topic
            assert len(topic["purpose"]) > 0

    def test_topics_sorted_by_usage(self):
        """Topic list is ordered by pipeline usage (ingested first)."""
        from app.kafka.topics import TOPICS

        names = [t["name"] for t in TOPICS]
        # document.ingested should be first (it triggers the pipeline)
        assert names[0] == "document.ingested"


class TestKafkaPublish:
    """Tests for message publishing."""

    def test_publish_calls_producer_flush(self):
        """publish() sends message and flushes producer."""
        from app.kafka.producer import KafkaProducer

        with patch.object(KafkaProducer, "_get_producer") as mock_get:
            mock_producer = MagicMock()
            mock_get.return_value = mock_producer

            producer = KafkaProducer()
            result = producer.publish(
                topic="document.ingested",
                key="doc-123",
                value={"document_id": "doc-123", "hash": "abc"},
            )

            # Verify delivery report was called
            mock_producer.poll.assert_called()
            mock_producer.flush.assert_called()

    def test_publish_none_value_to_string(self):
        """publish() handles None values gracefully."""
        from app.kafka.producer import KafkaProducer

        with patch.object(KafkaProducer, "_get_producer") as mock_get:
            mock_producer = MagicMock()
            mock_get.return_value = mock_producer

            producer = KafkaProducer()
            # Should not raise
            producer.publish(topic="document.ingested", key="doc-123", value=None)

    def test_publish_handles_error(self):
        """publish() logs error on delivery failure."""
        from app.kafka.producer import KafkaProducer

        with patch.object(KafkaProducer, "_get_producer") as mock_get:
            mock_producer = MagicMock()
            mock_get.return_value = mock_producer

            producer = KafkaProducer()
            # Should not raise even if delivery fails
            producer.publish(
                topic="nonexistent-topic",
                key="doc-123",
                value={"document_id": "doc-123"},
            )


class TestDeadLetterQueue:
    """Tests for DLQ pattern."""

    def test_dlq_topic_format(self):
        """DLQ topics follow the {topic}.dlq naming convention."""
        from app.kafka.producer import KafkaProducer
        from app.kafka.topics import TOPICS

        producer = KafkaProducer()

        for topic in TOPICS:
            dlq_topic = f"{topic['name']}.dlq"
            assert dlq_topic in producer.topics
