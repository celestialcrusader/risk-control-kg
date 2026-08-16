"""
Document Storage & Audit Log Cleanup Script.

Clears uploaded documents from MinIO source-regulations bucket
and resets the audit_logs database table.
"""

import os
import sys
import logging
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup_documents")


def cleanup_all_uploaded_documents():
    from backend.app.storage import get_minio_storage
    from backend.app.core.database import get_db_session
    from backend.app.models import AuditLog

    # 1. Clean MinIO storage
    try:
        minio = get_minio_storage()
        files = minio.list_files("source-regulations")
        for key in files:
            minio.delete_file("source-regulations", key)
            logger.info("Deleted object from MinIO: %s", key)
    except Exception as e:
        logger.warning("MinIO cleanup warning: %s", e)

    # 2. Clean AuditLog table entries for document.uploaded
    try:
        with get_db_session() as session:
            num_deleted = session.query(AuditLog).filter(
                AuditLog.event_type.in_(["document.uploaded", "document.ingested"])
            ).delete(synchronize_session=False)
            session.commit()
            logger.info("Deleted %d document audit log entries from database.", num_deleted)
    except Exception as e:
        logger.warning("Database audit log cleanup warning: %s", e)

    logger.info("==================================================")
    logger.info("DOCUMENT CLEANUP COMPLETE!")
    logger.info("==================================================")


if __name__ == "__main__":
    cleanup_all_uploaded_documents()
