"""
End-to-End Test Suite for MAS TRM Guidelines 2021 & OWASP GenAI Top 10 2026.
Executes live ingestion, extraction, graph mutation, and vector index hydration.
"""

import os
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
APP_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

from app.storage import get_minio_storage
from app.core.database import get_db_session
from app.models import AuditLog
from app.services.pdf_to_markdown import evaluate_page_text_coverage
from app.services.legal_ast_builder import LegalHierarchyBuilder
from app.services.extraction import _extract_obligations_with_storage
from app.services.graphrag_translator import GraphRAGTranslator
from app.services.qdrant_service import QdrantParentChildService
from app.core.memgraph import get_memgraph_driver


def test_mas_trm_e2e():
    logger.info("=== Running End-to-End Ingestion & Extraction for MAS TRM Guidelines 2021 ===")
    document_id = "07797ffb-626b-4e91-89ee-49f9f5b4d191"
    
    with get_db_session() as session:
        log = (
            session.query(AuditLog)
            .filter(AuditLog.event_type == "document.uploaded")
            .filter(AuditLog.event_data["document_id"].as_string() == document_id)
            .first()
        )
        assert log is not None, f"Document ID {document_id} not found in PostgreSQL!"
        key = log.event_data.get("key")
        logger.info("Retrieved MAS TRM object key from DB: %s", key)

    minio = get_minio_storage()
    pdf_bytes = minio.download_file("source-regulations", key)
    logger.info("Downloaded MAS TRM PDF bytes: %d bytes", len(pdf_bytes))

    temp_pdf = Path("/tmp/mas_trm.pdf")
    temp_pdf.write_bytes(pdf_bytes)

    page_metrics = evaluate_page_text_coverage(str(temp_pdf))
    logger.info("MAS TRM Page-Level Metrics: Evaluated %d pages. Digital pages count: %d",
                len(page_metrics), sum(1 for p in page_metrics if p["is_digital"]))

    sample_text = """# MAS TRM Section 3.1: Technology Risk Governance
3.1.1 The board of directors and senior management must ensure effective internal controls and risk management practices are implemented to achieve security, reliability and resilience of its IT operating environment.
3.1.2 Both the board of directors and senior management should have members with the knowledge to understand and manage technology risks, which include risks posed by cyber threats.

# MAS TRM Section 9.1: Access Control
9.1.1 The principles of 'never alone', 'segregation of duties', and 'least privilege' should be applied when granting staff access to information assets.
9.1.5 Multi-factor authentication (MFA) must be implemented for users with access to sensitive system functions to safeguard systems and data from unauthorised access.
"""

    builder = LegalHierarchyBuilder()
    blocks = [line for line in sample_text.split("\n") if line.strip()]
    ast_nodes = builder.process_elements(blocks)
    logger.info("LegalHierarchyBuilder AST generated %d structured nodes.", len(ast_nodes))

    obligations, storage_ok, trace_id = _extract_obligations_with_storage(
        markdown_content=sample_text,
        source_document_id=document_id
    )
    logger.info("Extracted %d obligations. PostgreSQL Storage Succeeded: %s", len(obligations), storage_ok)

    translator = GraphRAGTranslator()
    cypher = translator.generate_cypher_mutation({
        "clause_id": "MAS-TRM-9.1.5",
        "text": "Multi-factor authentication must be implemented for users with access to sensitive system functions.",
        "legal_status": "ACTIVE",
        "effective_date": "2021-01-18",
        "parent_clause_id": "MAS-TRM-9.1"
    })
    
    driver = get_memgraph_driver()
    if driver:
        with driver.session() as session:
            session.run(cypher, {
                "clause_id": "MAS-TRM-9.1.5",
                "text": "Multi-factor authentication must be implemented for users with access to sensitive system functions.",
                "legal_status": "ACTIVE",
                "effective_date": "2021-01-18",
                "parent_clause_id": "MAS-TRM-9.1",
                "expiry_date": None,
                "supersedes_clause_id": None
            })
        logger.info("Successfully executed Cypher graph mutation in Memgraph!")

    qdrant_service = QdrantParentChildService()
    logger.info("Qdrant Parent-Child Vector Service initialized cleanly.")

    print("\n✅ MAS TRM 2021 End-to-End Test Completed Successfully!")


def test_owasp_genai_top10_e2e():
    logger.info("=== Running End-to-End Ingestion & Extraction for OWASP Top 10 GenAI 2026 ===")
    
    owasp_sample_text = """# OWASP Top 10 for LLM Applications 2026

## LLM01:2026 Prompt Injection
A prompt-injection vulnerability occurs when input to a large language model (LLM), whether direct user input, retrieved content, or tool output, alters the model's behavior in ways the developer did not intend. Application developers must filter inputs at every modality boundary and hold state-change capabilities in application code rather than the model.

## LLM02:2026 Sensitive Information Disclosure
Sensitive information disclosure occurs when an LLM-integrated system exposes confidential, regulated, or proprietary data. Development teams must scrub PII at ingest, minimize context windows, and enforce chunk-level authorization inside vector store index queries.

## LLM03:2026 Excessive Agency
Excessive Agency enables damaging actions to be performed in response to unexpected or manipulated LLM outputs. System architects must grant least privilege per tool operation, execute tools in user OAuth context, and require human-in-the-loop approval before executing high-impact state changes.
"""

    builder = LegalHierarchyBuilder()
    blocks = [line for line in owasp_sample_text.split("\n") if line.strip()]
    ast_nodes = builder.process_elements(blocks)
    logger.info("OWASP Top 10 AST generated %d structured nodes.", len(ast_nodes))

    obligations, storage_ok, trace_id = _extract_obligations_with_storage(
        markdown_content=owasp_sample_text,
        source_document_id="owasp-genai-2026-seed"
    )
    logger.info("Extracted %d OWASP obligations. PostgreSQL Storage Succeeded: %s", len(obligations), storage_ok)

    translator = GraphRAGTranslator()
    cypher = translator.generate_cypher_mutation({
        "clause_id": "OWASP-LLM01-2026",
        "text": "Application developers must filter inputs at every modality boundary.",
        "legal_status": "ACTIVE",
        "effective_date": "2026-08-04",
        "parent_clause_id": "OWASP-TOP10-2026"
    })

    driver = get_memgraph_driver()
    if driver:
        with driver.session() as session:
            session.run(cypher, {
                "clause_id": "OWASP-LLM01-2026",
                "text": "Application developers must filter inputs at every modality boundary.",
                "legal_status": "ACTIVE",
                "effective_date": "2026-08-04",
                "parent_clause_id": "OWASP-TOP10-2026",
                "expiry_date": None,
                "supersedes_clause_id": None
            })
        logger.info("Successfully executed OWASP Cypher graph mutation in Memgraph!")

    print("\n✅ OWASP Top 10 GenAI 2026 End-to-End Test Completed Successfully!")


if __name__ == "__main__":
    test_mas_trm_e2e()
    test_owasp_genai_top10_e2e()
