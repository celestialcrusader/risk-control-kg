import sys
from pathlib import Path

# Add backend directory and app directory to sys.path
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
for path in [str(APP_DIR), str(BACKEND_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    documents,
    extract,
    graph,
    judge,
    repair,
    semantic,
    gaps,
    controls,
)

app = FastAPI(
    title="Pure RCKG Engine API",
    description="Risk Control Knowledge Graph (RCKG) - Phase 1 Cold-Start & Phase 2 Graphiti Maintenance Engine",
    version="1.0.0",
)

# Enable CORS for frontend/CLI testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
app.include_router(extract.router, prefix="/api/v1/extract", tags=["Extract & Bootstrap"])
app.include_router(documents.router, prefix="/api/v1", tags=["Document Upload"])

from app.api.v1 import crosswalk_router, governance_router

app.include_router(graph.router, prefix="/api/v1", tags=["Graph Visualizer & Queries"])
app.include_router(judge.router, prefix="/api/v1", tags=["Dual-Judge Audit"])
app.include_router(repair.router, prefix="/api/v1", tags=["Graph Repair"])
app.include_router(semantic.router, prefix="/api/v1", tags=["Semantic Search"])
app.include_router(controls.router, prefix="/api/v1", tags=["Control Mappings"])
app.include_router(crosswalk_router.router, prefix="/api/v1", tags=["Canonical Crosswalk API"])
app.include_router(governance_router.router, prefix="/api/v1", tags=["Governance & Gap Analytics"])

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount Static Files for Thin Human Governance UI
STATIC_DIR = APP_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/ui", include_in_schema=False)
@app.get("/", include_in_schema=False)
def serve_ui():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Pure RCKG Governance Engine API is running. Access /docs for Swagger UI."}


import socket
from urllib.parse import urlparse
from app.core.observability import logger


@app.on_event("startup")
def init_database_tables():
    """Ensure all SQLAlchemy metadata tables (audit_log, documents, etc.) exist."""
    try:
        from app.core.database import engine
        from app.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("SQLAlchemy database tables initialized successfully.")
    except Exception as err:
        logger.error("Failed to initialize database tables: %s", err)

    # Initialize Memgraph driver & indexes
    try:
        from app.core.memgraph import get_memgraph_driver
        get_memgraph_driver()
    except Exception as err:
        logger.warning("Memgraph startup initialization warning: %s", err)

    # Initialize MinIO storage buckets
    try:
        from app.storage import get_minio_storage
        get_minio_storage()
    except Exception as err:
        logger.warning("MinIO storage bucket startup initialization warning: %s", err)



@app.on_event("startup")
def validate_llm_endpoint_locality():

    """REMED-104: Validate LLM_ENDPOINT resolves to RFC 1918 private or loopback IP range."""
    from app.services.extraction import LLM_ENDPOINT
    try:
        parsed = urlparse(LLM_ENDPOINT if "://" in LLM_ENDPOINT else f"http://{LLM_ENDPOINT}")
        hostname = parsed.hostname or "localhost"
        ip = socket.gethostbyname(hostname)
        is_private = (
            ip.startswith("127.") or
            ip.startswith("10.") or
            ip.startswith("192.168.") or
            (ip.startswith("172.") and 16 <= int(ip.split(".")[1]) <= 31)
        )
        if not is_private:
            logger.warning(
                "SECURITY WARNING: LLM_ENDPOINT (%s) resolves to public IP %s — compliance data may cross network boundary!",
                LLM_ENDPOINT, ip,
            )
        else:
            logger.info("LLM_ENDPOINT verified private/local IP: %s (%s)", ip, LLM_ENDPOINT)
    except Exception as err:
        logger.error("Failed to resolve LLM_ENDPOINT hostname locality: %s", err)


@app.get("/")
def root():
    return {
        "engine": "Pure RCKG Engine",
        "version": "v1.0.0",
        "status": "HEALTHY",
        "docs_url": "/docs",
    }


@app.get("/api/v1/health")
def health_check():
    """GET /api/v1/health - System Dependency Health Check Endpoint (CFIX-304)."""
    from app.core.health import get_system_health
    return get_system_health()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
