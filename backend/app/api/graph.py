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
