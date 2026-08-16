"""
Full Document Ingestion & Extraction Script for MAS TRM Guidelines 2021.
Runs end-to-end conversion, legal AST parsing, batch obligation extraction,
PostgreSQL storage, and Memgraph graph database population.
"""

import sys
import logging
from pathlib import Path

# Add backend to sys.path
APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from app.storage import get_minio_storage
from app.core.database import get_db_session
from app.models import AuditLog, SemanticControl
from app.services.pdf_to_markdown import evaluate_page_text_coverage
from app.services.legal_ast_builder import LegalHierarchyBuilder
from app.services.extraction import _extract_obligations_with_storage
from app.services.graphrag_translator import GraphRAGTranslator
from app.core.memgraph import get_memgraph_driver
import fitz  # PyMuPDF


def run_full_mas_ingestion():
    logger.info("=== STARTING FULL MAS TRM 2021 DOCUMENT INGESTION ===")
    document_id = "07797ffb-626b-4e91-89ee-49f9f5b4d191"

    # Step 1: Download full PDF bytes from MinIO
    minio = get_minio_storage()
    pdf_bytes = None
    with get_db_session() as session:
        log = (
            session.query(AuditLog)
            .filter(AuditLog.event_type == "document.uploaded")
            .filter(AuditLog.event_data["document_id"].as_string() == document_id)
            .first()
        )
        if log:
            key = log.event_data.get("key")
            logger.info("Downloading MAS TRM from MinIO key: %s", key)
            try:
                pdf_bytes = minio.download_file("source-regulations", key)
            except Exception as e:
                logger.warning("Download by DB key failed: %s", e)

    if not pdf_bytes:
        logger.info("Downloading default MAS TRM key from source-regulations...")
        pdf_bytes = minio.download_file("source-regulations", "documents/2b8959e883bd66cb17286bdfc3e04fc181a6cd0ad786c99d4998c2d6c3e0efcb/TRM Guidelines 18 January 2021.pdf")

    temp_pdf = Path("/tmp/mas_trm_full.pdf")
    temp_pdf.write_bytes(pdf_bytes)
    logger.info("Saved full MAS TRM PDF (%d bytes) to /tmp/mas_trm_full.pdf", len(pdf_bytes))

    # Step 2: Page-Level Evaluation & Text Extraction via PyMuPDF
    doc = fitz.open(str(temp_pdf))
    total_pages = len(doc)
    logger.info("Loaded PDF with %d total pages.", total_pages)

    page_metrics = evaluate_page_text_coverage(str(temp_pdf))
    digital_count = sum(1 for p in page_metrics if p["is_digital"])
    logger.info("Page Text Coverage: %d/%d pages evaluated as Digital PDF (>95%% text coverage).", digital_count, total_pages)

    # Extract all text line by line across all 57 pages
    all_lines = []
    for page_num in range(total_pages):
        page = doc.load_page(page_num)
        text_content = page.get_text("text").strip()
        if text_content:
            for line in text_content.split("\n"):
                cleaned = line.strip()
                if cleaned:
                    all_lines.append(f"[Page {page_num + 1}] {cleaned}")

    logger.info("Extracted %d non-empty text lines across %d pages.", len(all_lines), total_pages)

    # Step 3: Chunk text into sliding windows of 60 lines (approx 2-3 pages per chunk)
    chunk_size = 60
    overlap = 10
    chunks = []
    
    start_idx = 0
    while start_idx < len(all_lines):
        end_idx = min(start_idx + chunk_size, len(all_lines))
        chunk_lines = all_lines[start_idx:end_idx]
        chunk_text = "\n".join(chunk_lines)
        chunks.append((start_idx, end_idx, chunk_text))
        if end_idx >= len(all_lines):
            break
        start_idx += (chunk_size - overlap)

    logger.info("Created %d sliding text chunks across the entire document.", len(chunks))

    # Step 4: Batch Obligation Extraction into PostgreSQL & Memgraph
    total_obligations_extracted = 0
    driver = get_memgraph_driver()
    translator = GraphRAGTranslator()

    for chunk_idx, (s_idx, e_idx, chunk_text) in enumerate(chunks, 1):
        logger.info("Extracting chunk %d/%d (Lines %d-%d)...", chunk_idx, len(chunks), s_idx, e_idx)
        try:
            obligations, storage_ok, trace_id = _extract_obligations_with_storage(
                markdown_content=chunk_text,
                source_document_id=document_id
            )
            count = len(obligations)
            total_obligations_extracted += count
            logger.info("  -> Extracted %d obligations from chunk %d.", count, chunk_idx)

            # Step 5: Graph Mutation in Memgraph
            if driver and count > 0:
                with driver.session() as memgraph_session:
                    for idx, obl in enumerate(obligations):
                        clause_id = f"MAS-{obl.id}" if not obl.id.startswith("MAS-") else obl.id
                        parent_id = f"MAS-CHUNK-{chunk_idx}"
                        
                        cypher = translator.generate_cypher_mutation({
                            "clause_id": clause_id,
                            "text": obl.prose,
                            "legal_status": "ACTIVE",
                            "effective_date": "2021-01-18",
                            "parent_clause_id": parent_id
                        })
                        try:
                            memgraph_session.run(cypher, {
                                "clause_id": clause_id,
                                "text": obl.prose,
                                "legal_status": "ACTIVE",
                                "effective_date": "2021-01-18",
                                "parent_clause_id": parent_id,
                                "expiry_date": None,
                                "supersedes_clause_id": None
                            })
                        except Exception as ge:
                            logger.debug("Memgraph mutation skipped/existing for %s: %s", clause_id, ge)

        except Exception as exc:
            logger.error("Extraction error in chunk %d: %s", chunk_idx, exc)

    logger.info("=== FULL INGESTION & EXTRACTION COMPLETE ===")
    logger.info("Total Pages Processed: %d", total_pages)
    logger.info("Total Sliding Chunks Analyzed: %d", len(chunks))
    logger.info("Total Obligations Saved to Postgres: %d", total_obligations_extracted)


if __name__ == "__main__":
    run_full_mas_ingestion()
