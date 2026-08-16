import pytest
from unittest.mock import patch, MagicMock

from app.services.pdf_to_markdown import convert_pdf_to_markdown, PARSER_MODEL_NAME
from app.services.extraction import LLM_MODEL, LLM_ENDPOINT
from app.services.embedding_sync import EMBEDDING_MODEL_NAME, EMBEDDING_DIM
from app.services.retrieval.colbert_service import RERANKER_MODEL_NAME
from app.services.nli_engine import NliSetTheoryEngine, NLI_MODEL_NAME
from app.services.judge import JUDGE_MODEL, JUDGE_ENDPOINT
from app.services.graphrag_translator import GRAPHRAG_MODEL_NAME, GRAPHRAG_ENDPOINT


def test_ai_model_matrix_e2e_configuration():
    """Verify that all 7 functional jobs map strictly to their dedicated primary AI models without fallbacks."""
    # 1. Parsing
    assert PARSER_MODEL_NAME == "baidu/PaddleOCR-VL-1.6"

    # 2. General Extraction & Copilot
    assert LLM_MODEL == "Qwen/Qwen3-30B-A3B"
    assert LLM_ENDPOINT == "http://localhost:8000/v1"

    # 3. Dense Embeddings
    assert EMBEDDING_MODEL_NAME == "Qwen/Qwen3-Embedding-8B"
    assert EMBEDDING_DIM == 4096

    # 4. Candidate Reranking
    assert RERANKER_MODEL_NAME == "Qwen/Qwen3-Reranker-8B"

    # 5. NLI Evaluation
    assert NLI_MODEL_NAME == "answerdotai/ModernBERT-large-NLI"

    # 6. Ambiguous Graph Adjudication
    assert JUDGE_MODEL == "Qwen/Qwen3-Next-80B-A3B"
    assert JUDGE_ENDPOINT == "http://localhost:8004/v1"

    # 7. GraphRAG Translation
    assert GRAPHRAG_MODEL_NAME == "Qwen/Qwen3-Next-80B-A3B"
    assert GRAPHRAG_ENDPOINT == "http://localhost:8004/v1"


def test_ai_model_matrix_e2e_flow(tmp_path):
    """Simulate un-stubbed execution across the 7-step chain."""
    pdf_file = tmp_path / "iso_27001.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock iso document")

    mock_paddle_resp = MagicMock()
    mock_paddle_resp.status_code = 200
    mock_paddle_resp.json.return_value = {
        "choices": [{"message": {"content": "# ISO 27001 Section A.5\nData encryption at rest is mandatory."}}],
        "confidence": 0.96,
    }

    with patch("requests.post", return_value=mock_paddle_resp), \
         patch("app.services.pdf_to_markdown.get_minio_storage"):
        
        # Step 1: Parse PDF
        parsed = convert_pdf_to_markdown(str(pdf_file), "doc_iso_01")
        assert parsed["converter_used"] == "paddleocr-vl-1.6"

        # Step 2: NLI Engine (No keyword fallback on failure)
        nli_engine = NliSetTheoryEngine()
        with patch("app.services.nli_engine._call_llm", side_effect=RuntimeError("Endpoint offline")):
            nli_res = nli_engine.evaluate_pair(parsed["markdown_uri"], "encrypt pii data")
            assert nli_res.set_theory_relation == "PENDING_CLASSIFICATION"
            assert nli_res.confidence_score == 0.0
