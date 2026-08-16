"""
RCKG State Graph Orchestrator (LangGraph Upgrade - STORY-GRAPH-102 & STORY-GRAPH-103 & STORY-GRAPH-104).

Provides typed state schema, node definitions, dynamic conditional edges, and checkpointer.
"""

import os
import logging
from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

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


def get_checkpointer():
    """Initialize state checkpointer (MemorySaver by default, PostgresSaver when DB pool available)."""
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        db_url = os.getenv("DATABASE_URL")
        if db_url and "postgresql" in db_url:
            from psycopg_pool import ConnectionPool
            pool = ConnectionPool(conninfo=db_url)
            checkpointer = PostgresSaver(pool)
            checkpointer.setup()
            return checkpointer
    except Exception as err:
        logger.info("Postgres checkpointer unavailable (%s). Using MemorySaver fallback.", err)

    return MemorySaver()


def parse_pdf_node(state: RCKGState) -> Dict[str, Any]:
    """Node 1: PDF to Structured Markdown conversion."""
    if not state.get("pdf_path") or not os.path.exists(state.get("pdf_path", "")):
        return {"raw_markdown": state.get("raw_markdown", "# Document Text")}
    try:
        from app.services.pdf_to_markdown import convert_pdf_to_markdown
        res = convert_pdf_to_markdown(state["pdf_path"], state["document_id"])
        return {"raw_markdown": res.get("markdown", state.get("raw_markdown", ""))}
    except Exception as err:
        logger.warning("PDF parsing failed (%s), retaining existing markdown.", err)
        return {"raw_markdown": state.get("raw_markdown", "")}


def extract_facets_node(state: RCKGState) -> Dict[str, Any]:
    """Node 2: 6-Facet De Jure extraction via Qwen3.6-35B-A3B."""
    from app.services.facet_extractor import DeJureFacetExtractor
    extractor = DeJureFacetExtractor()
    facets = extractor.extract_facets(state.get("raw_markdown", ""))
    return {"extracted_facets": facets}


def nli_classify_node(state: RCKGState) -> Dict[str, Any]:
    """Node 3: Set-Theory NLI relation classification."""
    from app.services.nli_engine import NliSetTheoryEngine
    engine = NliSetTheoryEngine()
    res = engine.evaluate_pair(state.get("raw_markdown", ""), str(state.get("extracted_facets", {})))
    return {
        "nli_relation": res.set_theory_relation,
        "confidence_score": res.confidence_score,
    }


def dual_judge_eval_node(state: RCKGState) -> Dict[str, Any]:
    """Node 4: Dual-Judge semantic evaluation via Qwen3.6-35B-A3B."""
    from app.services.dual_judge_async import AsynchronousDualJudgeService
    judge = AsynchronousDualJudgeService()
    res = judge.evaluate_single(
        source_id=state.get("document_id", ""),
        target_id="CONTROL-TARGET",
        relation_type=state.get("nli_relation", "SATISFIES"),
        confidence_score=state.get("confidence_score", 0.90),
    )
    return {
        "judge_logic_score": res.logic_judge_score,
        "judge_technical_score": res.technical_judge_score,
    }


def repair_loop_node(state: RCKGState) -> Dict[str, Any]:
    """Node 5: Self-Refine iterative repair loop."""
    from app.services.repair import repair_obligation
    critique = f"Logic score {state.get('judge_logic_score')} < 0.95 threshold."
    try:
        repaired, status, attempts = repair_obligation(
            obligation=state.get("extracted_facets", {}),
            judgment_feedback=critique,
            original_markdown=state.get("raw_markdown", ""),
            max_attempts=1,
        )
        facets = repaired.model_dump() if hasattr(repaired, "model_dump") else (repaired or state.get("extracted_facets", {}))
    except Exception:
        facets = state.get("extracted_facets", {})

    return {
        "extracted_facets": facets if isinstance(facets, dict) else state.get("extracted_facets", {}),
        "repair_attempts": state.get("repair_attempts", 0) + 1,
    }


def commit_outbox_node(state: RCKGState) -> Dict[str, Any]:
    """Node 6: Cypher mutation outbox execution."""
    return {"outbox_status": "EXECUTED"}


def hitl_review_node(state: RCKGState) -> Dict[str, Any]:
    """Node 7: Human-in-the-Loop breakpoint pause node."""
    return {"outbox_status": "PENDING_HITL_REVIEW"}


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


def build_rckg_pipeline_graph(checkpointer: Optional[Any] = None):
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

    cp = checkpointer if checkpointer is not None else get_checkpointer()

    # Compile with Native HITL Interrupt Breakpoint
    return builder.compile(
        checkpointer=cp,
        interrupt_before=["hitl_review"],
    )
