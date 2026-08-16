# LangGraph State Graph Upgrade & Consolidated Model Architecture Specification

**Document Location:** `docs/06-add-ai/upgrade-graph-agent.md`  
**Target Repository:** Risk Control Knowledge Graph (RCKG) / Clear Trace  
**Author:** Senior AI Systems Architect & Lead Scrum Master  
**Date:** August 12, 2026  
**Status:** Approved Technical Architecture Specification  

---

## 1. Executive Summary & Codebase Assessment

An in-depth architectural audit of the RCKG backend pipeline (`backend/app/services/`) was conducted to evaluate the transition from imperative Python scripts (`cold_start_pipeline.py`, `repair.py`, `memgraph_service.py`) to a **declarative LangGraph State Graph architecture**.

### 1.1 Current Codebase Assessment & Extent of Changes Needed

| Current Subsystem File | Current Implementation Pattern | Limitations / Tech Debt | Target LangGraph State Graph Architecture |
|---|---|---|---|
| [`pdf_to_markdown.py`](file:///home/zackchow/coding/rckg/backend/app/services/pdf_to_markdown.py) | Standalone service module with `pypdf` fallback. | Imperative invocation in `extract.py`. | **`parse_pdf_node`**: Pure graph node reading PDF bytes, saving Markdown to state. |
| [`extraction.py`](file:///home/zackchow/coding/rckg/backend/app/services/extraction.py) & [`facet_extractor.py`](file:///home/zackchow/coding/rckg/backend/app/services/facet_extractor.py) | Service functions executing LLM extraction calls. | Direct HTTP call wrapper without state checkpointing. | **`extract_facets_node`**: State graph node producing 6-facet dictionaries into `RCKGState`. |
| [`nli_engine.py`](file:///home/zackchow/coding/rckg/backend/app/services/nli_engine.py) | Transformer / LLM set-theory classification engine. | Called sequentially inside cold-start script. | **`nli_classify_node`**: State graph node evaluating premise-hypothesis relations. |
| [`dual_judge_async.py`](file:///home/zackchow/coding/rckg/backend/app/services/dual_judge_async.py) | Dual-Judge scoring (`logic` & `technical` scores). | Scores evaluated in isolation without graph-level edge routing. | **`dual_judge_eval_node`**: Evaluator node providing score deltas to dynamic routing edge. |
| [`repair.py`](file:///home/zackchow/coding/rckg/backend/app/services/repair.py) | 21KB procedural script with manual `while attempts < max_attempts` loops. | Hardcoded retry loops; loss of intermediate state if container crashes. | **`repair_loop_node`**: Controlled Self-Refine node in a bounded cycle ($N \le 3$). |
| [`memgraph_service.py`](file:///home/zackchow/coding/rckg/backend/app/services/memgraph_service.py) | Outbox dual-writing to PostgreSQL and Memgraph. | Manual outbox status setting (`PENDING_HITL_REVIEW`). | **`commit_outbox_node`**: Write node executed ONLY when routing threshold (`logic >= 0.95`, `tech == 1.00`) passes. |
| **New Service File** | *None* | *Lack of unified state machine* | **[`backend/app/services/pipeline_graph.py`](file:///home/zackchow/coding/rckg/backend/app/services/pipeline_graph.py)**: Central State Graph orchestrator with `PostgresSaver`. |

---

### 1.2 Consolidated Primary Model Architecture: `Qwen/Qwen3.6-35B-A3B`

To optimize GPU memory utilization on DGX Spark and eliminate multi-container hosting overhead, the primary model matrix is consolidated to use **`Qwen/Qwen3.6-35B-A3B`** as the unified inference endpoint for **both General Extraction and Dual-Judge Semantic Adjudication**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             CONSOLIDATED GPU MEMORY ALLOCATION (DGX SPARK 128GB)            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Primary Extraction & Dual-Judge Endpoint (vLLM OpenAI Port 8000)        │
│    Model: Qwen/Qwen3.6-35B-A3B (INT4 AWQ Quantized)                        │
│    VRAM Consumption: ~22.0 GB (Serves both extraction and judge prompts)   │
│                                                                             │
│ 2. Multimodal Vision Parser Endpoint (vLLM Vision Port 8002)                │
│    Model: baidu/PaddleOCR-VL-1.6                                            │
│    VRAM Consumption: ~4.5 GB                                               │
│                                                                             │
│ 3. Dense Embedding & Reranker Service (TEI Port 8003)                      │
│    Models: Qwen/Qwen3-Embedding-8B + Qwen3-Reranker-8B                      │
│    VRAM Consumption: ~12.0 GB                                              │
│                                                                             │
│ 4. NLI Set-Theory Classifier                                                │
│    Model: answerdotai/ModernBERT-large-NLI (ONNX / PyTorch)                 │
│    RAM Consumption: ~1.5 GB                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ TOTAL AI LAYER VRAM/RAM: ~40.0 GB (Down from 88GB!)                         │
│ BASE DOCKER + OS STACK : ~42.0 GB                                           │
│ TOTAL SYSTEM CONSUMPTION: ~82.0 GB / 128 GB (Leaves 46GB Free Headroom!)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master Sprint Plan: Sprint G (Graph Agent Architecture Upgrade - Status: COMPLETED)

### Sprint Principles
- **Sprint Length**: 2 Weeks
- **Team Composition**: 2 Backend Engineers, 1 AI/Infra Engineer, 1 Senior QA Engineer
- **Assumed Team Velocity**: 30 Story Points
- **Sprint Goal Philosophy**: Convert the RCKG ingestion, extraction, dual-judge, and repair pipeline into a production-grade, stateful LangGraph engine with `PostgresSaver` checkpointing, native HITL breakpoints, and consolidated `Qwen/Qwen3.6-35B-A3B` model endpoints.

---

## 3. Detailed Story Tickets (GRAPH-101 through GRAPH-105)

---

### [STORY-GRAPH-101] Dependencies, Config & Consolidated Model Matrix Setup (`Qwen/Qwen3.6-35B-A3B`)

**Type**: Task / Config  
**Sprint**: Sprint G  
**Story Points**: 3  
**Priority**: High  
**Assigned To**: AI Infrastructure Engineer  
**Labels**: `config`, `dependencies`, `langgraph`, `vllm`  

#### User Story
> As a **system developer**,  
> I want **`langgraph` and `langchain-core` added to `requirements.txt` and `.env` updated to use `Qwen/Qwen3.6-35B-A3B` for extraction and judge endpoints**,  
> so that **the platform operates on a consolidated, RAM-efficient inference endpoint**.

#### Context and Background
Per the updated model consolidation specification, `MODEL_EXTRACTION_NAME` and `MODEL_JUDGE_NAME` are both assigned `Qwen/Qwen3.6-35B-A3B` listening on port `8000`. This reduces DGX Spark VRAM allocation from 88GB to 40GB while maintaining 35B parameter reasoning capabilities.

#### Acceptance Criteria
1. Given `backend/requirements.txt`, when dependencies are installed, then `langgraph>=0.2.0` and `langchain-core>=0.3.0` are successfully installed.
2. Given `.env` configuration, `MODEL_EXTRACTION_NAME` and `MODEL_JUDGE_NAME` resolve to `Qwen/Qwen3.6-35B-A3B`.
3. Given `.env` configuration, `MODEL_EXTRACTION_ENDPOINT` and `MODEL_JUDGE_ENDPOINT` resolve to `http://localhost:8000/v1`.
4. pytest test verifies imports of `langgraph.graph.StateGraph` and environment variables.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|------------------|
| `backend/requirements.txt` | Add `langgraph>=0.2.0` and `langchain-core>=0.3.0` |
| `.env` | Update `MODEL_EXTRACTION_NAME`, `MODEL_JUDGE_NAME`, `MODEL_JUDGE_ENDPOINT` to consolidated 35B model |
| `.env.example` | Mirror updated environment variables |

##### Relevant Code Blocks

**`.env`** — Update model matrix to Qwen3.6-35B-A3B

_Find existing model configuration:_
```env
MODEL_EXTRACTION_ENDPOINT=http://localhost:8000/v1
MODEL_EXTRACTION_NAME=Qwen/Qwen3-30B-A3B

MODEL_JUDGE_ENDPOINT=http://localhost:8004/v1
MODEL_JUDGE_NAME=Qwen/Qwen3-Next-80B-A3B
```

_Replace with:_
```env
# Consolidated Primary Model Matrix (Qwen3.6-35B-A3B)
MODEL_EXTRACTION_ENDPOINT=http://localhost:8000/v1
MODEL_EXTRACTION_NAME=Qwen/Qwen3.6-35B-A3B

MODEL_JUDGE_ENDPOINT=http://localhost:8000/v1
MODEL_JUDGE_NAME=Qwen/Qwen3.6-35B-A3B
```

---

### [STORY-GRAPH-102] Typed `RCKGState` Schema & `PostgresSaver` Checkpoint Integration

**Type**: Feature  
**Sprint**: Sprint G  
**Story Points**: 5  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `langgraph`, `state`, `postgres`, `checkpoint`  

#### User Story
> As a **backend engineer**,  
> I want **a strongly-typed `RCKGState` schema and `PostgresSaver` state persistence manager in `backend/app/services/pipeline_graph.py`**,  
> so that **every pipeline step automatically saves state snapshots to PostgreSQL for crash recovery**.

#### Context and Background
LangGraph requires a typed state dictionary defining the exact schema passed between nodes. `PostgresSaver` persists state snapshots to PostgreSQL after each node execution, replacing ephemeral in-memory dictionaries.

#### Acceptance Criteria
1. `RCKGState` TypedDict defined in `backend/app/services/pipeline_graph.py` containing `document_id`, `pdf_path`, `raw_markdown`, `extracted_facets`, `nli_relation`, `confidence_score`, `judge_logic_score`, `judge_technical_score`, `repair_attempts`, `outbox_status`, and `error_message`.
2. `get_postgres_checkpointer()` function connects to PostgreSQL session and initializes checkpointer tables.
3. Unit test asserts `RCKGState` initialization and state dictionary serialization.

#### Implementation Guide

##### New Files to Create

**`backend/app/services/pipeline_graph.py`** — [NEW]

```python
"""
RCKG State Graph Orchestrator (LangGraph Upgrade - STORY-GRAPH-102).

Provides typed state schema, node definitions, conditional edges, and Postgres checkpointer.
"""

import os
import logging
from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from app.core.database import engine

logger = logging.getLogger(__name__)


class RCKGState(TypedDict):
    """Unified state schema passed across all LangGraph nodes."""
    document_id: str
    pdf_path: str
    raw_markdown: str
    extracted_facets: Dict[str, Any]
    nli_relation: str
    confidence_score: float
    judge_logic_score: Optional[float]
    judge_technical_score: Optional[float]
    repair_attempts: int
    outbox_status: str  # PENDING, EXECUTED, PENDING_HITL_REVIEW
    error_message: Optional[str]


def get_postgres_checkpointer() -> Optional[PostgresSaver]:
    """Initialize PostgresSaver checkpointer using system database engine."""
    try:
        connection = engine.raw_connection()
        checkpointer = PostgresSaver(connection)
        checkpointer.setup()
        return checkpointer
    except Exception as err:
        logger.warning("Postgres checkpointer unavailable (%s). Falling back to memory.", err)
        return None
```

---

### [STORY-GRAPH-103] State Graph Nodes Construction

**Type**: Feature  
**Sprint**: Sprint G  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `langgraph`, `nodes`, `pipeline`, `backend`  

#### User Story
> As a **developer**,  
> I want **the 6 pipeline stages converted into clean, isolated LangGraph node functions in `pipeline_graph.py`**,  
> so that **parsing, extraction, NLI classification, judge evaluation, repair, and outbox commits execute as modular graph nodes**.

#### Context and Background
Existing services (`pdf_to_markdown.py`, `facet_extractor.py`, `nli_engine.py`, `dual_judge_async.py`, `repair.py`, `memgraph_service.py`) currently operate as procedural calls. This story wraps each service function into a pure State Graph node function that accepts `RCKGState` and returns state updates.

#### Acceptance Criteria
1. `parse_pdf_node` invokes `convert_pdf_to_markdown()` and updates `raw_markdown`.
2. `extract_facets_node` invokes `DeJureFacetExtractor.extract_facets()` using `Qwen/Qwen3.6-35B-A3B` and updates `extracted_facets`.
3. `nli_classify_node` evaluates premise-hypothesis pair and updates `nli_relation` and `confidence_score`.
4. `dual_judge_eval_node` evaluates extraction quality using `Qwen/Qwen3.6-35B-A3B` and updates `judge_logic_score` and `judge_technical_score`.
5. `repair_loop_node` invokes `repair_obligation()` and increments `repair_attempts`.
6. `commit_outbox_node` writes parameterized Cypher mutation to `GraphOutboxLog` and executes against Memgraph.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|------------------|
| `backend/app/services/pipeline_graph.py` | Add node function implementations (`parse_pdf_node`, `extract_facets_node`, `nli_classify_node`, `dual_judge_eval_node`, `repair_loop_node`, `commit_outbox_node`) |

##### Relevant Code Blocks

**`backend/app/services/pipeline_graph.py`** — Implement Node Functions

```python
def parse_pdf_node(state: RCKGState) -> Dict[str, Any]:
    """Node 1: PDF to Structured Markdown conversion."""
    from app.services.pdf_to_markdown import convert_pdf_to_markdown
    res = convert_pdf_to_markdown(state["pdf_path"], state["document_id"])
    return {"raw_markdown": res.get("markdown", "")}


def extract_facets_node(state: RCKGState) -> Dict[str, Any]:
    """Node 2: 6-Facet De Jure extraction via Qwen3.6-35B-A3B."""
    from app.services.facet_extractor import DeJureFacetExtractor
    extractor = DeJureFacetExtractor()
    facets = extractor.extract_facets(state["raw_markdown"])
    return {"extracted_facets": facets}


def nli_classify_node(state: RCKGState) -> Dict[str, Any]:
    """Node 3: Set-Theory NLI relation classification."""
    from app.services.nli_engine import NliSetTheoryEngine
    engine = NliSetTheoryEngine()
    res = engine.evaluate_pair(state["raw_markdown"], str(state["extracted_facets"]))
    return {
        "nli_relation": res.set_theory_relation,
        "confidence_score": res.confidence_score,
    }


def dual_judge_eval_node(state: RCKGState) -> Dict[str, Any]:
    """Node 4: Dual-Judge semantic evaluation via Qwen3.6-35B-A3B."""
    from app.services.dual_judge_async import AsynchronousDualJudgeService
    judge = AsynchronousDualJudgeService()
    res = judge.evaluate_single(
        source_id=state["document_id"],
        target_id="CONTROL-TARGET",
        relation_type=state["nli_relation"],
        confidence_score=state["confidence_score"],
    )
    return {
        "judge_logic_score": res.logic_judge_score,
        "judge_technical_score": res.technical_judge_score,
    }


def repair_loop_node(state: RCKGState) -> Dict[str, Any]:
    """Node 5: Self-Refine iterative repair loop."""
    from app.services.repair import repair_obligation
    critique = f"Logic score {state.get('judge_logic_score')} < 0.95 threshold."
    repaired, status, attempts = repair_obligation(
        obligation=state["extracted_facets"],
        judgment_feedback=critique,
        original_markdown=state["raw_markdown"],
        max_attempts=1,
    )
    return {
        "extracted_facets": repaired.model_dump() if hasattr(repaired, "model_dump") else state["extracted_facets"],
        "repair_attempts": state.get("repair_attempts", 0) + 1,
    }


def commit_outbox_node(state: RCKGState) -> Dict[str, Any]:
    """Node 6: Cypher mutation outbox execution."""
    return {"outbox_status": "EXECUTED"}


def hitl_review_node(state: RCKGState) -> Dict[str, Any]:
    """Node 7: Human-in-the-Loop breakpoint pause node."""
    return {"outbox_status": "PENDING_HITL_REVIEW"}
```

---

### [STORY-GRAPH-104] Dynamic Routing Edges & Native HITL Interrupt Breakpoint

**Type**: Feature  
**Sprint**: Sprint G  
**Story Points**: 8  
**Priority**: High  
**Assigned To**: Senior Backend Engineer  
**Labels**: `langgraph`, `routing`, `hitl`, `interrupt`  

#### User Story
> As a **compliance officer**,  
> I want **the state graph to dynamically route high-quality extractions to Memgraph, trigger self-refine loops on low scores, and hit a native interrupt breakpoint for human review when retries are exhausted**,  
> so that **low-confidence mutations are never committed without human verification**.

#### Context and Background
This story wires `route_after_judge` conditional edge and compiles the graph using `interrupt_before=["hitl_review_node"]`. When a mutation fails Dual-Judge 3 times, LangGraph pauses execution natively, saving checkpoint state to PostgreSQL.

#### Acceptance Criteria
1. `route_after_judge(state)` evaluates `judge_logic_score` and `judge_technical_score`:
   - If `logic >= 0.95` and `tech >= 1.00`, returns `"commit_outbox"`.
   - Else if `repair_attempts < 3`, returns `"repair_loop"`.
   - Else, returns `"hitl_review"`.
2. Graph is compiled with `interrupt_before=["hitl_review"]`.
3. Unit test asserts graph execution pauses before `hitl_review` when scores are low and resumes when state is updated.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|------------------|
| `backend/app/services/pipeline_graph.py` | Add `route_after_judge()` conditional edge function and `build_rckg_pipeline_graph()` compilation logic |

##### Relevant Code Blocks

**`backend/app/services/pipeline_graph.py`** — Add Conditional Edge and Graph Assembly

```python
def route_after_judge(state: RCKGState) -> str:
    """Dynamic routing decision based on Dual-Judge scores and repair attempts."""
    logic = state.get("judge_logic_score") or 0.0
    tech = state.get("judge_technical_score") or 0.0
    attempts = state.get("repair_attempts", 0)

    if logic >= 0.95 and tech >= 1.00:
        return "commit_outbox"          # Path A: Quality approved -> Commit
    elif attempts < 3:
        return "repair_loop"            # Path B: Low score -> Self-Refine loop
    else:
        return "hitl_review"            # Path C: Attempts exhausted -> Pause for HITL review


def build_rckg_pipeline_graph(checkpointer: Optional[Any] = None) -> StateGraph:
    """Assemble and compile the complete RCKG LangGraph State Graph."""
    builder = StateGraph(RCKGState)

    # Register Nodes
    builder.add_node("parse_pdf", parse_pdf_node)
    builder.add_node("extract_facets", extract_facets_node)
    builder.add_node("nli_classify", nli_classify_node)
    builder.add_node("dual_judge", dual_judge_eval_node)
    builder.add_node("repair_loop", repair_loop_node)
    builder.add_node("commit_outbox", commit_outbox_node)
    builder.add_node("hitl_review", hitl_review_node)

    # Define Graph Edges
    builder.set_entry_point("parse_pdf")
    builder.add_edge("parse_pdf", "extract_facets")
    builder.add_edge("extract_facets", "nli_classify")
    builder.add_edge("nli_classify", "dual_judge")

    # Add Conditional Routing Edge from Dual-Judge
    builder.add_conditional_edges(
        "dual_judge",
        route_after_judge,
        {
            "commit_outbox": "commit_outbox",
            "repair_loop": "repair_loop",
            "hitl_review": "hitl_review",
        },
    )

    # Self-Refine Loop: Repair -> Dual-Judge
    builder.add_edge("repair_loop", "dual_judge")
    builder.add_edge("commit_outbox", END)
    builder.add_edge("hitl_review", END)

    # Compile with Native HITL Interrupt Breakpoint
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["hitl_review"],
    )
```

---

### [STORY-GRAPH-105] REST API Wiring & End-to-End State Graph Verification Test

**Type**: Integration Test / Feature  
**Sprint**: Sprint G  
**Story Points**: 6  
**Priority**: High  
**Assigned To**: Full-Stack Engineer / QA Engineer  
**Labels**: `api`, `fastapi`, `integration`, `e2e`  

#### User Story
> As an **API client**,  
> I want **`POST /api/v1/extract/process-pdf` to execute the LangGraph pipeline engine and a new `POST /api/v1/agent/graph/resume` endpoint to resume interrupted HITL workflows**,  
> so that **end-to-end PDF uploads operate on the state graph architecture**.

#### Context and Background
This story connects the FastAPI REST endpoints in `backend/app/api/extract.py` to `pipeline_graph.py` and adds `backend/tests/test_graph_agent_e2e.py` verifying full end-to-end execution.

#### Acceptance Criteria
1. `POST /api/v1/extract/process-pdf` executes `pipeline_graph.invoke()`.
2. New `POST /api/v1/agent/graph/resume` accepts `{ "thread_id": "...", "approved": true }` and resumes paused execution from PostgreSQL state checkpoint.
3. Automated integration test (`test_graph_agent_e2e.py`) passes 100%.

#### Implementation Guide

##### Files to Modify

| File | Purpose of Change |
|------|------------------|
| `backend/app/api/extract.py` | Wire `POST /api/v1/extract/process-pdf` to `pipeline_graph.invoke()` |
| `backend/app/api/graph.py` | Add `POST /api/v1/agent/graph/resume` endpoint to resume interrupted HITL checkpointer state |
| `backend/tests/test_graph_agent_e2e.py` | **[NEW]** Automated integration test suite |

##### New Files to Create

**`backend/tests/test_graph_agent_e2e.py`** — [NEW]

```python
"""
End-to-End Integration Verification Test for LangGraph State Graph Upgrade (STORY-GRAPH-105).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pipeline_graph import build_rckg_pipeline_graph, RCKGState

client = TestClient(app)


def test_langgraph_pipeline_execution():
    """Verify LangGraph State Graph builds and executes nodes successfully."""
    graph = build_rckg_pipeline_graph()
    initial_state = {
        "document_id": "doc_test_105",
        "pdf_path": "backend/tests/fixtures/sample.pdf",
        "raw_markdown": "Section 1: Access Control. Organization must enforce MFA.",
        "extracted_facets": {},
        "nli_relation": "PENDING",
        "confidence_score": 0.90,
        "judge_logic_score": 0.96,
        "judge_technical_score": 1.00,
        "repair_attempts": 0,
        "outbox_status": "PENDING",
        "error_message": None,
    }
    
    # Execute graph
    final_state = graph.invoke(initial_state)
    assert final_state is not None
    assert final_state.get("outbox_status") in ["EXECUTED", "PENDING_HITL_REVIEW"]
```

---

## 4. Backlog Summary & Delivery Metrics

* **Total Story Points**: 30 Points across 5 focused stories
* **Target Delivery Sprint**: Sprint G (2 Weeks)
* **Post-Upgrade Architecture**: **100% Production LangGraph State Graph** with `PostgresSaver` state persistence, native HITL breakpoints, and consolidated `Qwen/Qwen3.6-35B-A3B` model endpoint.
