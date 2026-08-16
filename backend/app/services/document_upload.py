"""
Document upload service for RCKG.

Provides business logic for document ingestion:
- SHA-256 hash calculation for deduplication
- MinIO storage with content-type validation
- Audit log creation
- Kafka event publishing on document.ingested topic
- File size enforcement (max 100 MB)
"""

import hashlib
import io
import logging
import uuid
from typing import Any, Optional

from app.core.database import get_db_session
from app.kafka.producer import KafkaProducer
from app.models import AuditLog
from app.storage import get_minio_storage

logger = logging.getLogger(__name__)

# Allowed MIME types
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Maximum file size: 100 MB (strictly enforced -- files > this limit rejected)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def calculate_sha256(file_obj: io.BytesIO) -> str:
    """Calculate SHA-256 hash of file contents.

    Args:
        file_obj: Seekable BytesIO object with file content.

    Returns:
        Hex digest string (64 characters).
    """
    file_obj.seek(0)
    return hashlib.sha256(file_obj.read()).hexdigest()


def get_kafka_producer() -> KafkaProducer:
    """Get or create a KafkaProducer instance."""
    return KafkaProducer()


def upload_document(
    file_obj: Any,
    requestor_id: Optional[str] = None,
) -> dict:
    """
    Process a document upload: validate, hash, store, audit, and publish event.

    Args:
        file_obj: FastAPI UploadFile-like object with .filename, .file, .content_type.
        requestor_id: Optional identifier for the actor performing the upload.

    Returns:
        Dict with 'status', 'document_id', 'hash', and optionally 'key'.
    """
    filename = getattr(file_obj, "filename", "unknown")
    content_type = getattr(file_obj, "content_type", "")
    file_stream = file_obj.file

    # --- Content-Type validation (AC-6) ---
    if content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(
            "Rejected upload: unsupported content_type '%s' for file '%s'",
            content_type, filename,
        )
        raise ValueError(
            f"Unsupported content_type: {content_type}. "
            f"Allowed types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
        )

    # Read file contents
    file_stream.seek(0)
    content = file_stream.read()
    file_size = len(content)

    # --- File size validation (AC-5) ---
    if file_size > MAX_FILE_SIZE:
        logger.warning(
            "Rejected upload: file '%s' exceeds 100 MB limit (%d bytes)",
            filename, file_size,
        )
        raise ValueError(
            f"File size {file_size} bytes exceeds the 100 MB limit."
        )

    # --- Empty file check ---
    if file_size == 0:
        logger.warning("Rejected upload: empty file '%s'", filename)
        raise ValueError(f"File is empty: {filename}")

    # --- SHA-256 hash calculation ---
    hash_hex = hashlib.sha256(content).hexdigest()
    key = f"documents/{hash_hex}/{filename}"

    minio = get_minio_storage()
    bucket = "source-regulations"

    # --- Duplicate detection (AC-2) ---
    if minio.file_exists(bucket, key):
        # File already exists -- return existing document info
        with get_db_session() as session:
            existing = (
                session.query(AuditLog)
                .filter(AuditLog.event_type == "document.uploaded")
                .filter(AuditLog.event_data["hash"].as_string() == hash_hex)
                .order_by(AuditLog.timestamp.desc())
                .first()
            )
            if existing:
                document_id = str(existing.id)
            else:
                document_id = str(uuid.uuid4())
                # Still log the duplicate attempt
                audit_entry = AuditLog(
                    event_type="document.uploaded",
                    event_data={
                        "hash": hash_hex,
                        "filename": filename,
                        "document_id": document_id,
                        "key": key,
                        "status": "duplicate",
                        "file_size": file_size,
                        "requestor_id": requestor_id,
                    },
                    actor_id=requestor_id,
                )
                session.add(audit_entry)

        logger.info("Duplicate detected: hash=%s file=%s", hash_hex, filename)
        return {
            "status": "duplicate",
            "document_id": document_id,
            "hash": hash_hex,
            "key": key,
        }

    # --- Upload to MinIO ---
    file_stream.seek(0)
    minio.upload_file(
        bucket=bucket,
        key=key,
        file_obj=io.BytesIO(content),
        content_type=content_type,
    )

    # --- Create audit log (AC-3) ---
    document_id = str(uuid.uuid4())

    # --- Format Classification Inspection (RCKG-201) ---
    from app.services.format_classifier import UpstreamFormatClassifier
    classifier = UpstreamFormatClassifier()
    classification = classifier.classify(content, filename=filename)

    with get_db_session() as session:
        audit_entry = AuditLog(
            event_type="document.uploaded",
            event_data={
                "hash": hash_hex,
                "filename": filename,
                "document_id": document_id,
                "key": key,
                "file_size": file_size,
                "content_type": content_type,
                "detected_format": classification.format.value,
                "recommended_parser": classification.recommended_parser,
                "requestor_id": requestor_id,
            },
            actor_id=requestor_id,
        )
        session.add(audit_entry)

    # --- Publish Kafka event (AC-4) ---
    try:
        producer = get_kafka_producer()
        producer.publish(
            topic="document.ingested",
            key=document_id,
            value={
                "document_id": document_id,
                "hash": hash_hex,
                "source_path": key,
                "filename": filename,
                "content_type": content_type,
                "file_size": file_size,
                "requestor_id": requestor_id,
            },
        )
        logger.info(
            "Kafka event published for document %s on topic document.ingested",
            document_id,
        )
    except Exception as e:
        # Kafka failure does not block upload (resilience)
        logger.error("Kafka publish failed for document %s: %s", document_id, e)

    logger.info("Document uploaded successfully: id=%s hash=%s", document_id, hash_hex)

    return {
        "status": "uploaded",
        "document_id": document_id,
        "hash": hash_hex,
        "key": key,
    }
