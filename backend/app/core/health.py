"""
System Dependency Health Check Module (CFIX-304).

Verifies connectivity for PostgreSQL, Memgraph, and LLM inference service.
"""

import os
import time
import requests
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.database import ping_database
from app.core.memgraph import get_memgraph_driver


def check_llm_connectivity(timeout: float = 2.0) -> bool:
    """Check if LLM inference endpoint is reachable."""
    llm_url = os.getenv("MODEL_EXTRACTION_ENDPOINT", os.getenv("LLM_API_BASE", "http://localhost:8000/v1"))

    try:
        # Quick ping / GET models or health endpoint
        base_host = llm_url.split("/v1")[0]
        res = requests.get(base_host, timeout=timeout)
        return res.status_code in [200, 404, 405]
    except Exception:
        return False


def get_system_health() -> Dict[str, Any]:
    """Perform health checks across PostgreSQL, Memgraph, and LLM inference engine."""
    pg_ok = ping_database()

    memgraph_ok = False
    try:
        driver = get_memgraph_driver()
        if driver is not None:
            driver.verify_connectivity()
            memgraph_ok = True
    except Exception:
        memgraph_ok = False

    llm_ok = check_llm_connectivity(timeout=1.5)

    if pg_ok and memgraph_ok and llm_ok:
        overall_status = "HEALTHY"
    elif pg_ok and memgraph_ok and not llm_ok:
        overall_status = "DEGRADED"
    else:
        overall_status = "UNHEALTHY"

    return {
        "status": overall_status,
        "postgresql": "connected" if pg_ok else "unreachable",
        "memgraph": "connected" if memgraph_ok else "unreachable",
        "llm_endpoint": "connected" if llm_ok else "unreachable",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
