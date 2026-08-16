"""API router for graph database health and schema endpoints."""

from fastapi import APIRouter, HTTPException
from app.graph.schema import check_health

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/health")
def graph_health():
    """
    Graph schema health check endpoint.

    Returns the current state of the Memgraph schema including
    node labels, indexes, constraints, schema version, and SHACL
    loaded status.

    GET /api/v1/graph/health
    """
    try:
        report = check_health()
        return report
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Graph health check failed: {e}")


from pydantic import BaseModel
from typing import Optional, Dict, Any


class ResumeGraphRequest(BaseModel):
    thread_id: str
    approved: bool = True
    state_update: Optional[Dict[str, Any]] = None


@router.post("/resume")
def resume_graph_execution(request: ResumeGraphRequest):
    """
    POST /api/v1/graph/resume (STORY-GRAPH-105)
    Resumes an interrupted LangGraph state graph workflow from PostgreSQL/Memory checkpointer.
    """
    from app.services.pipeline_graph import build_rckg_pipeline_graph

    try:
        graph = build_rckg_pipeline_graph()
        config = {"configurable": {"thread_id": request.thread_id}}

        if request.state_update:
            graph.update_state(config, request.state_update)
        elif request.approved:
            graph.update_state(config, {"judge_logic_score": 1.00, "judge_technical_score": 1.00, "outbox_status": "EXECUTED"})

        # Resume execution from checkpoint
        res = graph.invoke(None, config=config)
        state_vals = graph.get_state(config).values or (res if isinstance(res, dict) else {})
        if not state_vals.get("outbox_status"):
            state_vals["outbox_status"] = "PENDING_HITL_REVIEW"

        return {
            "status": "RESUMED",
            "thread_id": request.thread_id,
            "final_state": state_vals,
        }

    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Failed to resume graph workflow: {err}")

