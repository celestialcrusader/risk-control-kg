"""
Kafka producer for RCKG event-driven pipeline.

Provides:
- KafkaProducer: Wraps confluent-kafka Producer with topic registry
- Topic creation via `/infra/kafka/create-topics.sh`
"""

import json
import logging
import os
import time
from typing import Any, Optional

from app.kafka.topics import TOPICS

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Kafka producer with topic registry and DLQ support."""

    def __init__(self, bootstrap_servers: Optional[str] = None) -> None:
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        # Build topic set including DLQ variants
        self.topics: dict[str, dict[str, Any]] = {t["name"]: t for t in TOPICS}
        for topic in TOPICS:
            dlq_name = f"{topic['name']}.dlq"
            self.topics[dlq_name] = {
                "name": dlq_name,
                "retention_seconds": topic["retention_seconds"],
                "partitions": 1,
                "purpose": f"Dead letter queue for {topic['name']}",
            }
        self._producer = None

    def _get_producer(self):
        """Lazily initialize the confluent-kafka Producer."""
        if self._producer is None:
            try:
                from confluent_kafka import Producer as _Producer

                self._producer = _Producer(
                    {
                        "bootstrap.servers": self.bootstrap_servers,
                        "acks": "all",
                        "retries": 3,
                        "enable.idempotence": True,
                    }
                )
            except ImportError:
                logger.warning(
                    "confluent-kafka not installed; Kafka publishing will be skipped"
                )
                self._producer = _NullProducer()
        return self._producer

    def publish(
        self,
        topic: str,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        headers: Optional[list] = None,
    ) -> None:
        """
        Publish a message to a Kafka topic.

        Args:
            topic: Topic name (must be in registry or DLQ variant).
            key: Message key for partitioning.
            value: Message payload (serialized to JSON).
            headers: Optional message headers.
        """
        producer = self._get_producer()

        # Serialize value to JSON bytes
        if value is not None and not isinstance(value, bytes):
            value = json.dumps(value).encode("utf-8")

        try:
            producer.produce(
                topic=topic,
                key=key.encode() if key else None,
                value=value,
                headers=headers,
                on_delivery=self._delivery_report,
            )
            producer.poll(0)
        except Exception as e:
            logger.error("Failed to publish to topic '%s': %s", topic, e)
        finally:
            producer.flush()

    @staticmethod
    def _delivery_report(err, msg) -> None:
        """Delivery callback for async produce."""
        if err is not None:
            logger.error("Kafka delivery error for %s: %s", msg.topic(), err)
        else:
            logger.debug(
                "Message delivered to %s [%s] at offset %s",
                msg.topic(),
                msg.partition(),
                msg.offset(),
            )


class _NullProducer:
    """No-op producer used when confluent-kafka is not installed."""

    def produce(self, topic, key=None, value=None, headers=None, on_delivery=None):
        pass

    def poll(self, timeout):
        pass

    def flush(self, timeout):
        pass
