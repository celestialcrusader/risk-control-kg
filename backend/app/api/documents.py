"""API router for document upload (INGEST-1)."""

import io
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.document_upload import upload_document, ALLOWED_CONTENT_TYPES, MAX_FILE_SIZE

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


def _detect_content_type(file: UploadFile) -> str:
    """Detect actual content type from both the header and file magic bytes.

    For PDF files, check the first bytes for '%PDF' prefix as an extra safeguard.
    """
    ct = file.content_type or ""

    # If client didn't provide a content type, try to detect
    if not ct:
        ext_map = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        ct = ext_map.get(ext, "application/octet-stream")

    return ct


@router.post("/upload")
def upload_document_endpoint(file: UploadFile = File(...)):
    """
    Upload a regulatory document (PDF or Word).

    Accepts PDF and Microsoft Word files, calculates SHA-256 for deduplication,
    stores in MinIO ``source-regulations`` bucket, writes an audit log entry,
    and publishes a ``document.ingested`` Kafka event.

    **Acceptance Criteria:**
    - AC-1: Stored in MinIO with key ``documents/{sha256}/{filename}``
    - AC-2: Duplicate files return HTTP 200 with ``{"status": "duplicate", "document_id": "..."}``
    - AC-3: Creates audit_log row with ``event_type='document.uploaded'``
    - AC-4: Publishes Kafka event on ``document.ingested`` topic
    - AC-5: Files > 100 MB rejected with HTTP 413
    - AC-6: Only ``application/pdf``, ``application/msword``,
      ``application/vnd.openxmlformats-officedocument.wordprocessingml.document`` accepted

    POST /api/v1/documents/upload
    """
    detected_ct = _detect_content_type(file)

    # Content-Type validation (AC-6)
    if detected_ct not in ALLOWED_CONTENT_TYPES:
        logger.warning(
            "Rejected: unsupported content_type '%s' for file '%s'",
            detected_ct, file.filename,
        )
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported content_type: {detected_ct}. Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    # Propagate detected content type back to the file object so the
    # service layer sees the same value the API layer validated.
    # This handles the case where the client omits the Content-Type header
    # and detection relies on file extension.
    if file.content_type != detected_ct:
        file.content_type = detected_ct

    # Read file content for size check
    try:
        file.file.seek(0, io.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    # File size validation (AC-5)
    if file_size > MAX_FILE_SIZE:
        logger.warning(
            "Rejected: file '%s' size %d bytes exceeds 100 MB limit",
            file.filename, file_size,
        )
        raise HTTPException(
            status_code=413,
            detail=f"File size {file_size} bytes exceeds the 100 MB limit.",
        )

    # Empty file check
    if file_size == 0:
        logger.warning("Rejected: empty file '%s'", file.filename)
        raise HTTPException(
            status_code=400,
            detail=f"File is empty: {file.filename}",
        )

    # Delegate to service layer
    try:
        result = upload_document(file)
        return result
    except ValueError as e:
        # Propagate validation errors from service layer
        detail = str(e)
        if "content_type" in detail.lower():
            raise HTTPException(status_code=415, detail=detail)
        if "size" in detail.lower() or "exceeds" in detail.lower():
            raise HTTPException(status_code=413, detail=detail)
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        logger.error("Document upload failed for '%s': %s", file.filename, e)
        raise HTTPException(status_code=500, detail=f"Document upload failed: {e}")


@router.post("/ingest-seed")
def trigger_seed_ingestion(source_type: str = "NIST_OLIR", file_path: str = "data/seed/nist_olir_export.xml"):
    """
    Trigger bulk seed graph ingestion for official compliance frameworks (NIST OLIR / CSA CCM).
    Populates FrameworkControlObj and FrameworkControlAct nodes with is_golden_assertion=True.
    
    POST /api/v1/documents/ingest-seed
    """
    from app.core.database import SessionLocal
    from app.services.seed_ingestion import ComplianceSeedIngester

    try:
        db = SessionLocal()
        ingester = ComplianceSeedIngester(db_session=db)
        stats = ingester.ingest_file(source_type=source_type, file_path=file_path)
        db.close()
        return {"status": "SUCCESS", "ingested_nodes": stats["nodes"], "ingested_edges": stats["edges"]}
    except Exception as e:
        logger.error("Seed ingestion failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Seed ingestion failed: {e}")
