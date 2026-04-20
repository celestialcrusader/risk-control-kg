"""
Event publisher for the document ingestion pipeline.

Publishes status events to Kafka topics after each pipeline stage completes:
- document.ingested  (after upload)
- document.converted (after PDF-to-markdown conversion)
- document.chunked   (after chunking)
- document.bronzed   (after Bronze layer storage)

Includes retry with exponential backoff and DLQ fallback.

Usage:
    publisher = PipelineEventPublisher(producer=kafka_producer)
    result = publisher.run_pipeline(doc_id="doc-1", ...)
"""

import json
import logging
import time
from typing import Any, Optional

from app.kafka.producer import KafkaProducer

logger = logging.getLogger(__name__)


# ==============================================================================
# Individual event publish functions
# ==============================================================================


def publish_ingested_event(
    producer: KafkaProducer,
    doc_id: str,
    hash: str,
    source_path: str,
    uploaded_at: str,
) -> dict:
    """
    Publish a document.ingested event.

    Args:
        producer: KafkaProducer instance.
        doc_id: Document identifier.
        hash: Content hash of the uploaded document.
        source_path: Filesystem path of the original upload.
        uploaded_at: ISO-8601 timestamp of upload.

    Returns:
        Dict with topic and status.
    """
    payload = {
        "doc_id": doc_id,
        "hash": hash,
        "source_path": source_path,
        "uploaded_at": uploaded_at,
        "pipeline_stage": "ingested",
    }

    producer.publish(
        topic="document.ingested",
        key=doc_id,
        value=payload,
    )
    return {"topic": "document.ingested", "status": "published"}


def publish_converted_event(
    producer: KafkaProducer,
    doc_id: str,
    chunks: int,
    md5_hash: str,
    conversion_time_ms: int,
) -> dict:
    """
    Publish a document.converted event.

    Args:
        producer: KafkaProducer instance.
        doc_id: Document identifier.
        chunks: Number of chunks produced.
        md5_hash: MD5 hash of converted content.
        conversion_time_ms: Conversion duration in milliseconds.

    Returns:
        Dict with topic and status.
    """
    payload = {
        "doc_id": doc_id,
        "chunks": chunks,
        "md5_hash": md5_hash,
        "conversion_time_ms": conversion_time_ms,
        "pipeline_stage": "converted",
    }

    producer.publish(
        topic="document.converted",
        key=doc_id,
        value=payload,
    )
    return {"topic": "document.converted", "status": "published"}


def publish_chunked_event(
    producer: KafkaProducer,
    doc_id: str,
    chunk_count: int,
    manifest_uri: str,
) -> dict:
    """
    Publish a document.chunked event.

    Args:
        producer: KafkaProducer instance.
        doc_id: Document identifier.
        chunk_count: Total number of chunks produced.
        manifest_uri: MinIO URI of the chunk manifest file.

    Returns:
        Dict with topic and status.
    """
    payload = {
        "doc_id": doc_id,
        "chunk_count": chunk_count,
        "manifest_uri": manifest_uri,
        "pipeline_stage": "chunked",
    }

    producer.publish(
        topic="document.chunked",
        key=doc_id,
        value=payload,
    )
    return {"topic": "document.chunked", "status": "published"}


def publish_bronzed_event(
    producer: KafkaProducer,
    doc_id: str,
    bronze_uri: str,
    checksum: str,
) -> dict:
    """
    Publish a document.bronzed event.

    Args:
        producer: KafkaProducer instance.
        doc_id: Document identifier.
        bronze_uri: MinIO URI of the Bronze layer data.
        checksum: SHA-256 checksum of stored data.

    Returns:
        Dict with topic and status.
    """
    payload = {
        "doc_id": doc_id,
        "bronze_uri": bronze_uri,
        "checksum": checksum,
        "pipeline_stage": "bronzed",
    }

    producer.publish(
        topic="document.bronzed",
        key=doc_id,
        value=payload,
    )
    return {"topic": "document.bronzed", "status": "published"}


# ==============================================================================
# Retry and DLQ helpers
# ==============================================================================


def publish_to_dlq(
    producer: KafkaProducer,
    original_topic: str,
    key: Optional[str],
    value: Any,
    error_message: str,
) -> dict:
    """
    Publish a message to the DLQ topic with error information.

    Args:
        producer: KafkaProducer instance.
        original_topic: The original topic that failed.
        key: Message key for partitioning.
        value: Original message payload.
        error_message: Description of the failure.

    Returns:
        Dict with DLQ topic and status.
    """
    dlq_topic = f"{original_topic}.dlq"

    if value is not None and not isinstance(value, bytes):
        payload_dict = dict(value) if isinstance(value, dict) else {}
    else:
        payload_dict = {}

    # Derive pipeline_stage from topic name for tracing
    stage = original_topic.split(".")[-1] if "." in original_topic else original_topic
    if "pipeline_stage" not in payload_dict:
        payload_dict["pipeline_stage"] = stage

    payload_dict["error"] = error_message
    payload_dict["original_topic"] = original_topic

    producer.publish(
        topic=dlq_topic,
        key=key,
        value=payload_dict,
    )
    return {"topic": dlq_topic, "status": "dlq"}


def publish_with_retry(
    producer: KafkaProducer,
    topic: str,
    key: Optional[str],
    value: Any,
    base_delay: float = 1.0,
    max_retries: int = 3,
) -> dict:
    """
    Publish a message with exponential backoff retry.

    Retries up to max_retries times with delays of base_delay,
    base_delay*2, base_delay*4, etc. If all retries fail,
    routes the message to the DLQ.

    Args:
        producer: KafkaProducer instance.
        topic: Target Kafka topic.
        key: Message key for partitioning.
        value: Message payload.
        base_delay: Initial delay in seconds (doubles each retry).
        max_retries: Maximum number of retry attempts.

    Returns:
        Dict with topic and status ("published" or "dlq").
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            producer.publish(topic=topic, key=key, value=value)
            return {"topic": topic, "status": "published"}
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.error(
                    "Publish to '%s' failed (attempt %d/%d): %s. "
                    "Retrying in %.1fs...",
                    topic,
                    attempt + 1,
                    max_retries,
                    e,
                    delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "Publish to '%s' failed after %d retries: %s. "
                    "Routing to DLQ.",
                    topic,
                    max_retries,
                    e,
                )

    # All retries exhausted -- send to DLQ
    dlq_result = publish_to_dlq(
        producer=producer,
        original_topic=topic,
        key=key,
        value=value,
        error_message=str(last_error) if last_error else "unknown error",
    )
    return dlq_result


# ==============================================================================
# PipelineEventPublisher coordinator
# ==============================================================================


class PipelineEventPublisher:
    """
    Coordinates event publishing across all pipeline stages.

    Wraps a KafkaProducer and provides methods to publish each stage event
    with configurable retry behavior.
    """

    def __init__(
        self,
        producer: Optional[KafkaProducer] = None,
        base_delay: float = 1.0,
        max_retries: int = 3,
    ) -> None:
        self.producer = producer or KafkaProducer()
        self.base_delay = base_delay
        self.max_retries = max_retries

    def publish_ingested(
        self,
        doc_id: str,
        hash: str,
        source_path: str,
        uploaded_at: str,
    ) -> dict:
        """Publish the ingested event with retry logic."""
        return publish_with_retry(
            producer=self.producer,
            topic="document.ingested",
            key=doc_id,
            value={
                "doc_id": doc_id,
                "hash": hash,
                "source_path": source_path,
                "uploaded_at": uploaded_at,
                "pipeline_stage": "ingested",
            },
            base_delay=self.base_delay,
            max_retries=self.max_retries,
        )

    def publish_converted(
        self,
        doc_id: str,
        chunks: int,
        md5_hash: str,
        conversion_time_ms: int,
    ) -> dict:
        """Publish the converted event with retry logic."""
        return publish_with_retry(
            producer=self.producer,
            topic="document.converted",
            key=doc_id,
            value={
                "doc_id": doc_id,
                "chunks": chunks,
                "md5_hash": md5_hash,
                "conversion_time_ms": conversion_time_ms,
                "pipeline_stage": "converted",
            },
            base_delay=self.base_delay,
            max_retries=self.max_retries,
        )

    def publish_chunked(
        self,
        doc_id: str,
        chunk_count: int,
        manifest_uri: str,
    ) -> dict:
        """Publish the chunked event with retry logic."""
        return publish_with_retry(
            producer=self.producer,
            topic="document.chunked",
            key=doc_id,
            value={
                "doc_id": doc_id,
                "chunk_count": chunk_count,
                "manifest_uri": manifest_uri,
                "pipeline_stage": "chunked",
            },
            base_delay=self.base_delay,
            max_retries=self.max_retries,
        )

    def publish_bronzed(
        self,
        doc_id: str,
        bronze_uri: str,
        checksum: str,
    ) -> dict:
        """Publish the bronzed event with retry logic."""
        return publish_with_retry(
            producer=self.producer,
            topic="document.bronzed",
            key=doc_id,
            value={
                "doc_id": doc_id,
                "bronze_uri": bronze_uri,
                "checksum": checksum,
                "pipeline_stage": "bronzed",
            },
            base_delay=self.base_delay,
            max_retries=self.max_retries,
        )

    def run_pipeline(
        self,
        doc_id: str,
        hash: str,
        source_path: str,
        uploaded_at: str,
        chunks: int,
        md5_hash: str,
        conversion_time_ms: int,
        chunk_count: int,
        manifest_uri: str,
        bronze_uri: str,
        checksum: str,
    ) -> dict:
        """
        Run all four pipeline stages in sequence.

        Args:
            doc_id: Document identifier.
            hash: Content hash of the uploaded document.
            source_path: Filesystem path of the original upload.
            uploaded_at: ISO-8601 timestamp of upload.
            chunks: Number of chunks produced.
            md5_hash: MD5 hash of converted content.
            conversion_time_ms: Conversion duration in ms.
            chunk_count: Total number of chunks.
            manifest_uri: MinIO URI of chunk manifest.
            bronze_uri: MinIO URI of Bronze layer data.
            checksum: SHA-256 checksum of stored data.

        Returns:
            Dict with results list and total stage count.
        """
        results = [
            self.publish_ingested(doc_id, hash, source_path, uploaded_at),
            self.publish_converted(doc_id, chunks, md5_hash, conversion_time_ms),
            self.publish_chunked(doc_id, chunk_count, manifest_uri),
            self.publish_bronzed(doc_id, bronze_uri, checksum),
        ]

        return {
            "doc_id": doc_id,
            "results": results,
            "total_stages": len(results),
        }
