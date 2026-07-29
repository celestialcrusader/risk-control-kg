"""
Extraction event publisher for EXTRACT-5.

Publishes Kafka events after extraction pipeline stages complete:
- extraction.completed  (after successful extraction)
- extraction.failed     (after failed extraction)

Uses fire-and-forget semantics: Kafka failures never break the extraction.

Uses the existing KafkaProducer from INFRA-7.
"""

import json
import logging
import time
from typing import Any, List, Optional

from app.kafka.producer import KafkaProducer

logger = logging.getLogger(__name__)


def publish_extraction_completed_event(
    producer: KafkaProducer,
    document_id: str,
    obligation_count: int,
    extraction_id: str,
    source_document_id: Optional[str] = None,
    model_used: str = "",
    processing_time_ms: int = 0,
    chunk_count: int = 0,
    obligation_ids: Optional[List[str]] = None,
) -> dict:
    """
    Publish an extraction.completed event.

    Args:
        producer: KafkaProducer instance.
        document_id: Document identifier (used as message key).
        source_document_id: UUID of the source document, if available.
        obligation_count: Number of obligations extracted.
        extraction_id: Unique identifier for this extraction run.
        model_used: Model name used for extraction (e.g., Mistral-8B).
        processing_time_ms: Total extraction duration in milliseconds.
        chunk_count: Number of chunks processed.
        obligation_ids: Optional list of obligation IDs for downstream consumers.

    Returns:
        Dict with topic and status.
    """
    payload: dict[str, Any] = {
        "event_type": "extraction.completed",
        "document_id": document_id,
        "source_document_id": source_document_id,
        "obligation_count": obligation_count,
        "extraction_id": extraction_id,
        "model_used": model_used,
        "processing_time_ms": processing_time_ms,
        "chunk_count": chunk_count,
        "obligation_ids": obligation_ids or [],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    producer.publish(
        topic="extraction.completed",
        key=document_id,
        value=payload,
    )
    return {"topic": "extraction.completed", "status": "published"}


def publish_extraction_failed_event(
    producer: KafkaProducer,
    document_id: str,
    extraction_id: str,
    error_reason: str,
    source_document_id: Optional[str] = None,
    model_used: str = "",
    processing_time_ms: int = 0,
) -> dict:
    """
    Publish an extraction.failed event.

    Args:
        producer: KafkaProducer instance.
        document_id: Document identifier (used as message key).
        source_document_id: UUID of the source document, if available.
        extraction_id: Unique identifier for the failed extraction run.
        error_reason: Description of why extraction failed.
        model_used: Model name that was being used.
        processing_time_ms: Duration before failure in milliseconds.

    Returns:
        Dict with topic and status.
    """
    payload: dict[str, Any] = {
        "event_type": "extraction.failed",
        "document_id": document_id,
        "source_document_id": source_document_id,
        "extraction_id": extraction_id,
        "error_reason": error_reason,
        "model_used": model_used,
        "processing_time_ms": processing_time_ms,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    producer.publish(
        topic="extraction.failed",
        key=document_id,
        value=payload,
    )
    return {"topic": "extraction.failed", "status": "published"}


class ExtractionEventPublisher:
    """
    Publishes extraction-related Kafka events with fire-and-forget semantics.

    Kafka failures are silently logged and never propagate to the caller,
    ensuring extraction remains resilient even when Kafka is unavailable.
    """

    def __init__(
        self,
        producer: Optional[KafkaProducer] = None,
    ) -> None:
        self.producer = producer or KafkaProducer()

    def on_extraction_completed(
        self,
        document_id: str,
        obligation_count: int,
        extraction_id: str,
        model_used: str = "",
        processing_time_ms: int = 0,
        chunk_count: int = 0,
        source_document_id: Optional[str] = None,
        obligation_ids: Optional[List[str]] = None,
    ) -> dict:
        """
        Publish an extraction.completed event (fire-and-forget).

        Never raises — if publishing fails, logs and returns error status.
        """
        try:
            return publish_extraction_completed_event(
                producer=self.producer,
                document_id=document_id,
                source_document_id=source_document_id,
                obligation_count=obligation_count,
                extraction_id=extraction_id,
                model_used=model_used,
                processing_time_ms=processing_time_ms,
                chunk_count=chunk_count,
                obligation_ids=obligation_ids,
            )
        except Exception as e:
            logger.error(
                "Failed to publish extraction.completed for doc %s: %s",
                document_id,
                e,
            )
            return {"topic": "extraction.completed", "status": "failed", "error": str(e)}

    def on_extraction_failed(
        self,
        document_id: str,
        extraction_id: str,
        error_reason: str,
        model_used: str = "",
        processing_time_ms: int = 0,
        source_document_id: Optional[str] = None,
    ) -> dict:
        """
        Publish an extraction.failed event (fire-and-forget).

        Never raises — if publishing fails, logs and returns error status.
        """
        try:
            return publish_extraction_failed_event(
                producer=self.producer,
                document_id=document_id,
                source_document_id=source_document_id,
                extraction_id=extraction_id,
                error_reason=error_reason,
                model_used=model_used,
                processing_time_ms=processing_time_ms,
            )
        except Exception as e:
            logger.error(
                "Failed to publish extraction.failed for doc %s: %s",
                document_id,
                e,
            )
            return {
                "topic": "extraction.failed",
                "status": "failed",
                "error": str(e),
            }
