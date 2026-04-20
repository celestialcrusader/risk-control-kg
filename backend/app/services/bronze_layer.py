"""
Bronze Layer Storage Service

Persists raw chunked document data in the Bronze layer (MinIO) and records
staging control entries for audit trail purposes.

Follows the three-layer vault pattern (TRD Section 8) where Bronze stores
immutable, append-only copies of raw ingested data.
"""

import hashlib
import json
import re
from typing import List, Dict, Any

from app.storage import get_minio_storage
from app.core.database import get_db_session
from app.models import StagingControl, AuditLog


# Sanitize doc_id against path traversal (same regex as INGEST-2)
_DOC_ID_PATTERN = re.compile(r"^[\w][\w.-]*$")

BRONZE_BUCKET = "bronze-layer"
BRONZE_PREFIX = "bronze"


def _validate_doc_id(doc_id: str) -> str:
    """
    Validate and sanitize the document ID.

    Args:
        doc_id: The document identifier to validate.

    Returns:
        The validated doc_id.

    Raises:
        ValueError: If doc_id is None, empty, or contains invalid characters.
    """
    if not doc_id:
        raise ValueError("doc_id is required")
    if not isinstance(doc_id, str):
        raise ValueError("doc_id must be a string")
    if not _DOC_ID_PATTERN.match(doc_id):
        raise ValueError(f"doc_id contains invalid characters: {doc_id!r}")
    return doc_id


def _compute_checksum(chunk_data: dict) -> str:
    """
    Compute SHA-256 checksum of a chunk's JSON representation.

    Args:
        chunk_data: The chunk dictionary to hash.

    Returns:
        Hex digest of the SHA-256 hash.
    """
    raw = json.dumps(chunk_data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def store_in_bronze(
    doc_id: str,
    chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Store chunked document data in the Bronze layer.

    Persists each chunk as JSON in MinIO and creates staging_control
    records for audit trail.

    Args:
        doc_id: The document identifier (sanitized against path traversal).
        chunks: List of chunk dictionaries with keys like
                chunk_index, heading_path, text, table_ref, doc_id.

    Returns:
        List of stored chunk metadata dicts.

    Raises:
        ValueError: If doc_id is invalid or chunks is not a list.
    """
    _validate_doc_id(doc_id)

    if not isinstance(chunks, list):
        raise ValueError("chunks must be a list")

    stored = []
    staging_created = False

    for chunk in chunks:
        chunk_index = chunk.get("chunk_index", 0)
        chunk_key = f"{BRONZE_PREFIX}/{doc_id}/{chunk_index}.json"

        # Persist to MinIO
        minio = get_minio_storage()
        chunk_json = json.dumps(chunk, sort_keys=True).encode("utf-8")
        minio.upload_data(
            bucket=BRONZE_BUCKET,
            key=chunk_key,
            data=chunk_json,
            content_type="application/json",
        )

        # Record in database via staging_controls + audit log
        checksum = _compute_checksum(chunk)

        with get_db_session() as session:
            # Create StagingControl once per document (AC-3: dedup)
            if not staging_created:
                existing = (
                    session.query(StagingControl)
                    .filter_by(canonical_id=doc_id)
                    .first()
                )
                if existing is None:
                    staging = StagingControl(
                        canonical_id=doc_id,
                        raw_file_content=chunk,
                    )
                    session.add(staging)
                    staging_created = True
                else:
                    # Already exists — this is the duplicate path
                    staging_created = True

            # Always write audit log for this chunk
            audit = AuditLog(
                event_type="bronze.store",
                event_data={
                    "doc_id": doc_id,
                    "chunk_index": chunk_index,
                    "checksum": checksum,
                    "minio_key": chunk_key,
                },
            )
            session.add(audit)

        stored.append({
            "doc_id": doc_id,
            "chunk_index": chunk_index,
            "minio_key": chunk_key,
            "checksum": checksum,
        })

    return stored
