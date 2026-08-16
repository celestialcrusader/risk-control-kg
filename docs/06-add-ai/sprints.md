# Master Sprint Plan: AI Model Matrix Integration (06-add-ai)

**Target Milestone:** Modernized Primary AI Model Stack Deployment (Zero Fallbacks)  
**Linked Requirements:** [docs/06-add-ai/requirements.md](file:///home/zackchow/coding/rckg/docs/06-add-ai/requirements.md)  
**Execution Loop Specification:** [docs/03-mvp/workflow-swe-qa-loop.md](file:///home/zackchow/coding/rckg/docs/03-mvp/workflow-swe-qa-loop.md)  

---

## Sprint Planning Principles

- **Sprint Length**: 2-Week Sprints
- **Team Composition**: 2 Backend Engineers, 1 ML/AI Infrastructure Engineer, 1 Senior QA Engineer
- **Assumed Team Velocity**: 30 Story Points per Sprint (60 Story Points total across 2 Sprints)
- **Sprint Goal Philosophy**: Every sprint delivers fully wired, demonstrable, un-stubbed production code backed by passing unit and integration tests — strictly using the primary dedicated AI models.

---

## Sprint Structure Overview

### Sprint 1: Core AI Model Pipeline & Ingestion Engine Modernization (Status: COMPLETED)
**Sprint Goal**: Upgrade the PDF parser to PaddleOCR-VL-1.6, wire Qwen3-30B-A3B for extraction & Copilot, integrate Qwen3-Embedding-8B into Qdrant, and replace NLI heuristics with ModernBERT-large-NLI.  
**Rationale**: Establishes the foundational ingestion and reasoning capabilities required for atomic rule extraction before upgrading heavy graph adjudication.  
**Stories in this Sprint**: `STORY-AI-101` [COMPLETED], `STORY-AI-102` [COMPLETED], `STORY-AI-103` [COMPLETED], `STORY-AI-104` [COMPLETED]  
**Total Story Points**: 29 Points  

### Sprint 2: Graph Adjudication, Candidate Reranking & GraphRAG Synthesis (Status: COMPLETED)
**Sprint Goal**: Implement Qwen3-Next-80B-A3B for ambiguous graph adjudication and GraphRAG global query translation, add Qwen3-Reranker-8B for hybrid retrieval, and validate full un-stubbed E2E pipeline execution.  
**Rationale**: Completes the AI model matrix rollout by enabling high-intelligence graph adjudication and high-precision retrieval rescoring.  
**Stories in this Sprint**: `STORY-AI-105` [COMPLETED], `STORY-AI-106` [COMPLETED], `STORY-AI-107` [COMPLETED], `STORY-AI-108` [COMPLETED]  
**Total Story Points**: 31 Points  

---

# Sprint 1: Detailed Story Tickets

### [STORY-AI-101] PaddleOCR-VL-1.6 PDF Parsing Integration

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: ML/AI Infra Engineer  
**Labels**: backend, ai-parsing, paddleocr, vllm  

#### User Story
> As a **Compliance Systems Developer**, I want to **parse PDF regulatory documents using PaddleOCR-VL-1.6 via vLLM Vision API**, so that **text, tables, and section headings are extracted cleanly without layout loss**.

#### Context and Background
Per `AI-REQ-06` (FR-01), the primary vision-language parser must be `PaddleOCR-VL-1.6` calling the dedicated vLLM endpoint (`http://localhost:8002/v1`). If `PaddleOCR-VL-1.6` is unreachable, an explicit `RuntimeError` is raised. No secondary fallback service is hosted.

#### Acceptance Criteria
1. Given a valid regulatory PDF file, when `convert_pdf_to_markdown()` is invoked, then it calls `PaddleOCR-VL-1.6` via `MODEL_PARSER_ENDPOINT`.
2. Given an endpoint failure, when conversion runs, then it raises an explicit `RuntimeError("PaddleOCR-VL-1.6 endpoint unreachable")`.
3. Given a completed conversion, then the resulting Markdown text is stored in MinIO's `markdown-conversions` bucket and metadata returns `converter_used` ("paddleocr-vl-1.6").

#### Technical Notes
- Configure endpoint using `os.getenv("MODEL_PARSER_ENDPOINT", "http://localhost:8002/v1")`.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|------------------|
| `backend/app/services/pdf_to_markdown.py` | Implement `PaddleOCRVLConverter` class and update `convert_pdf_to_markdown` pipeline |
| `backend/tests/test_ai_101_paddleocr.py` | **[NEW]** Unit tests for PaddleOCR-VL-1.6 parser |

##### Relevant Code Blocks

**`backend/app/services/pdf_to_markdown.py`** — Add PaddleOCR-VL-1.6 primary parser

_Find lines 23-35:_
```python
# Confidence threshold for triggering Marker fallback
CONFIDENCE_THRESHOLD = 0.85

# Pattern allowing only safe characters in document_id
_DOCUMENT_ID_PATTERN = re.compile(r"^[\w][\w.-]*$")
```

_Replace with:_
```python
import os
import requests

# Model endpoint configuration
PARSER_ENDPOINT = os.getenv("MODEL_PARSER_ENDPOINT", "http://localhost:8002/v1")
PARSER_MODEL_NAME = os.getenv("MODEL_PARSER_NAME", "baidu/PaddleOCR-VL-1.6")

# Pattern allowing only safe characters in document_id
_DOCUMENT_ID_PATTERN = re.compile(r"^[\w][\w.-]*$")


class PaddleOCRVLConverter:
    """Wrapper around PaddleOCR-VL-1.6 vision-language parsing endpoint."""

    def convert(self, pdf_path: str) -> "_PaddleResult":
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            payload = {
                "model": PARSER_MODEL_NAME,
                "prompt": "Convert this document page to structured Markdown preserving tables and headings.",
                "pdf_path": str(path),
            }
            resp = requests.post(f"{PARSER_ENDPOINT}/chat/completions", json=payload, timeout=30)
            if resp.status_code != 200:
                raise RuntimeError(f"PaddleOCR-VL-1.6 HTTP error {resp.status_code}: {resp.text}")
            
            data = resp.json()
            md_text = data["choices"][0]["message"]["content"]
            confidence = float(data.get("confidence", 0.95))
            return _PaddleResult(headings=[], tables=[], footnotes=[], markdown=md_text, confidence=confidence)
        except Exception as exc:
            logger.error("PaddleOCR-VL-1.6 conversion failed: %s", exc)
            raise RuntimeError(f"PaddleOCR-VL-1.6 endpoint unreachable: {exc}") from exc


class _PaddleResult:
    def __init__(self, headings: list, tables: list, footnotes: list, markdown: str, confidence: float):
        self.headings = headings
        self.tables = tables
        self.footnotes = footnotes
        self.markdown = markdown
        self.confidence = confidence
```

##### New Files to Create

**`backend/tests/test_ai_101_paddleocr.py`** — [NEW]
```python
import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_to_markdown import convert_pdf_to_markdown, PaddleOCRVLConverter

def test_paddleocr_primary_success(tmp_path):
    pdf_file = tmp_path / "test_doc.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock content")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "# Header\nTest markdown content"}}],
        "confidence": 0.95,
    }

    with patch("requests.post", return_value=mock_resp), \
         patch("app.services.pdf_to_markdown.get_minio_storage"):
        result = convert_pdf_to_markdown(str(pdf_file), "doc_123")
        assert result["converter_used"] == "paddleocr-vl-1.6"
        assert result["confidence_score"] == 0.95
```

---

### [STORY-AI-102] Qwen3-30B-A3B General Rule Extraction

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, ai-extraction, qwen3, vllm  

#### User Story
> As a **Knowledge Engineer**, I want **`extraction.py` to utilize `Qwen3-30B-A3B` via vLLM OpenAI API**, so that **atomic rule units are extracted into strict Pydantic models with maximum throughput**.

#### Acceptance Criteria
1. Given regulatory Markdown text, when `extract_obligations()` is called, then it sends prompt to `MODEL_EXTRACTION_ENDPOINT` with model `Qwen3-30B-A3B`.
2. Given raw LLM JSON, when parsed, then it validates strictly against `ExtractedObligationsResponse` Pydantic schema.

#### Implementation Guide

##### Relevant Code Blocks

**`backend/app/services/extraction.py`** — Update model default constants

_Find lines 37-41:_
```python
# LLM Configuration
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8001/v1")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "vllm") # "vllm" or "ollama"
LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/Mistral-8B-Instruct-v0.1")
```

_Replace with:_
```python
# LLM Configuration (AI-REQ-06)
LLM_ENDPOINT = os.getenv("MODEL_EXTRACTION_ENDPOINT", os.getenv("LLM_ENDPOINT", "http://localhost:8000/v1"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "vllm")
LLM_MODEL = os.getenv("MODEL_EXTRACTION_NAME", "Qwen/Qwen3-30B-A3B")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
```

---

### [STORY-AI-103] Qwen3-Embedding-8B Dense Vector Synchronization

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 5  
**Priority**: Medium  
**Assigned To**: Backend Engineer  
**Labels**: backend, embeddings, qwen3, qdrant  

#### User Story
> As a **Search & Retrieval Engineer**, I want **`embedding_sync.py` to generate 4096-dimensional dense vectors using `Qwen3-Embedding-8B`**, so that **Qdrant vector space math and similarity calculations remain strictly accurate**.

#### Acceptance Criteria
1. Given an extracted obligation string, when `generate_embedding()` is called, then it invokes `Qwen3-Embedding-8B` to output a 4096-dim vector.

---

### [STORY-AI-104] ModernBERT-large-NLI Set-Theory Engine & Heuristic Removal

**Type**: Story  
**Sprint**: Sprint 1  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, nli, modernbert, no-fakes  

#### User Story
> As a **Compliance Auditor**, I want **`nli_engine.py` to utilize `ModernBERT-large-NLI` and completely remove keyword heuristic fallbacks**, so that **all NLI relation scores reflect real transformer classifications**.

#### Implementation Guide

##### Relevant Code Blocks

**`backend/app/services/nli_engine.py`**

_Replace model configuration:_
```python
NLI_MODEL_NAME = os.getenv("MODEL_NLI_NAME", os.getenv("NLI_MODEL_NAME", "answerdotai/ModernBERT-large-NLI"))
```

_Delete keyword fallback block (lines 94-190). Replace with:_
```python
        if llm_failed or not result:
            logger.warning("ModernBERT NLI evaluation failed (%s). Returning PENDING_CLASSIFICATION", llm_err)
            return NliResult(
                set_theory_relation="PENDING_CLASSIFICATION",
                confidence_score=0.0,
                is_auto_committed=False,
                metadata={"method": "FAILED", "error": str(llm_err)},
            )
```

---

# Sprint 2: Detailed Story Tickets

### [STORY-AI-105] Qwen3-Next-80B-A3B Ambiguous Graph Adjudication

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Backend Engineer  
**Labels**: backend, dual-judge, qwen3-80b, memgraph  

#### User Story
> As a **Risk Architect**, I want **`judge.py` and `dual_judge_async.py` to evaluate low-confidence mutations using `Qwen3-Next-80B-A3B`**, so that **ambiguous graph commits are gated by high-reasoning MoE evaluation**.

---

### [STORY-AI-106] Qwen3-Reranker-8B Candidate Reranking

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 5  
**Priority**: Medium  
**Assigned To**: Search Engineer  
**Labels**: backend, retrieval, reranker, qwen3  

#### User Story
> As a **Compliance Search User**, I want **retrieval candidates to be rescored using `Qwen3-Reranker-8B`**, so that **search results prioritize the most relevant clauses**.

---

### [STORY-AI-107] Qwen3-Next-80B-A3B GraphRAG Global Query Translation

**Type**: Story  
**Sprint**: Sprint 2  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: AI Systems Architect  
**Labels**: backend, graphrag, qwen3-80b  

#### User Story
> As a **Chief Risk Officer**, I want **`graphrag_translator.py` to synthesize global compliance questions using `Qwen3-Next-80B-A3B`**, so that **hierarchical graph community summaries deliver holistic regulatory insights**.

---

### [STORY-AI-108] Real Un-Stubbed End-to-End AI Model Matrix Integration Test

**Type**: Integration Test  
**Sprint**: Sprint 2  
**Story Points**: 10  
**Priority**: High  
**Assigned To**: Senior QA Engineer  
**Labels**: qa, integration-test, e2e, ai-matrix  

#### User Story
> As a **Lead QA Engineer**, I want a **single automated integration test (`test_ai_matrix_e2e.py`) that executes the un-stubbed 7-step chain across PaddleOCR, Qwen3-30B, ModernBERT, Qwen3-Next-80B, and Qwen3-Embedding**, so that **we have concrete empirical proof of system functionality**.

---

## Sprint Plan Summary & Backlog Health

### Backlog Health Check
- **Total Stories**: 8 Stories (`STORY-AI-101` through `STORY-AI-108`)
- **Total Sprints**: 2 Sprints (4 weeks)
- **Total Story Points**: 60 Points
- **Critical Path**: `AI-101` (PDF Parsing) -> `AI-102` (Extraction) -> `AI-104` (NLI) -> `AI-105` (Dual Judge) -> `AI-108` (E2E Test)
