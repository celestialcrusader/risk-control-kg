"""
Memgraph schema initialization module for INFRA-9.

Provides functions to:
- Initialize graph schema (labels, constraints, indexes) from Cypher scripts
- Load SHACL shape definitions into Memgraph
- Check schema health and version status
- Track schema version for idempotent migrations

Usage:
    from app.graph.schema import init_schema, check_health
    init_schema()
    health = check_health()
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project root and paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GRAPH_SCRIPT_PATH = PROJECT_ROOT / "app" / "graph" / "init_schema.cypher"
SHAPES_DIR = PROJECT_ROOT / "app" / "shapes"

# Memgraph connection settings
MEMGRAPH_HOST = os.getenv("MEMGRAPH_HOST", "localhost")
MEMGRAPH_PORT = int(os.getenv("MEMGRAPH_PORT", "7687"))


def _get_memgraph_connection():
    """
    Establish a connection to Memgraph via Bolt protocol.

    Returns:
        A Memgraph database connection object.

    Raises:
        ImportError: If no memgraph client library is installed.
        ConnectionError: If Memgraph is unreachable.
    """
    try:
        import py2neo
        graph = py2neo.Graph(f"bolt://{MEMGRAPH_HOST}:{MEMGRAPH_PORT}")
        return graph
    except ImportError:
        # Fallback: try mgclient (Memgraph Python driver)
        try:
            import mgclient
            conn = mgclient.connect(host=MEMGRAPH_HOST, port=MEMGRAPH_PORT)
            return conn
        except ImportError:
            raise ImportError(
                "No Memgraph client library found. Install one of: "
                "py2neo, mgclient. Set MEMGRAPH_HOST/MEMGRAPH_PORT env vars."
            )


def _execute_cypher(conn, cypher_text: str) -> List[Any]:
    """
    Execute a block of Cypher statements against Memgraph.

    Args:
        conn: Memgraph connection object.
        cypher_text: Raw Cypher text with multiple statements.

    Returns:
        List of results from each statement.
    """
    results = []
    statements = [
        s.strip() for s in cypher_text.split(";") if s.strip() and not s.strip().startswith("--")
    ]

    for statement in statements:
        if not statement:
            continue
        result = conn.execute(statement)
        results.append(result)

    return results


def _load_shacl_shapes(conn, shapes_dir: Path) -> List[str]:
    """
    Load SHACL shape definitions from TTL files into Memgraph.

    Args:
        conn: Memgraph connection object.
        shapes_dir: Path to directory containing .ttl shape files.

    Returns:
        List of loaded shape file names.
    """
    loaded = []
    if not shapes_dir.exists():
        return loaded

    for ttl_file in sorted(shapes_dir.glob("*.ttl")):
        shape_name = ttl_file.name
        try:
            cypher = f"CALL shacl.load_shapes_from_file('{ttl_file}');"
            conn.execute(cypher)
            loaded.append(shape_name)
        except Exception:
            # Continue loading remaining shapes even if one fails
            continue

    return loaded


def init_schema(cypher_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Initialize the Memgraph schema: labels, constraints, indexes, and SHACL shapes.

    This function is idempotent -- all CREATE statements use IF NOT EXISTS,
    so running this multiple times has no side effects.

    Args:
        cypher_path: Optional path to the Cypher initialization script.
                     Defaults to the standard location.

    Returns:
        Dictionary with initialization summary:
        - labels: number of node labels defined
        - constraints: number of unique constraints
        - indexes: number of secondary indexes
        - shacl_loaded: number of SHACL shape files loaded
        - version: schema version string
        - applied_at: ISO timestamp of application
    """
    script_path = cypher_path or GRAPH_SCRIPT_PATH

    if not script_path.exists():
        raise FileNotFoundError(f"Cypher script not found: {script_path}")

    conn = _get_memgraph_connection()

    try:
        # Execute the main Cypher script (labels, constraints, indexes, version)
        cypher_text = script_path.read_text()
        _execute_cypher(conn, cypher_text)

        # Load SHACL shapes
        shacl_loaded = _load_shacl_shapes(conn, SHAPES_DIR)

        # Record schema version
        version = "INFRA-9"
        applied_at = datetime.now(timezone.utc).isoformat()

        # Read actual counts from the database
        labels = 0
        constraints = 0
        indexes = 0
        try:
            labels = len(list(conn.execute("SHOW LABELS INFO")))
        except Exception:
            pass
        try:
            constraints = len(list(conn.execute("SHOW CONSTRAINTS INFO")))
        except Exception:
            pass
        try:
            indexes = len(list(conn.execute("SHOW INDEXES INFO")))
        except Exception:
            pass

        return {
            "labels": labels,
            "constraints": constraints,
            "indexes": indexes,
            "shacl_loaded": shacl_loaded,
            "shacl_count": len(shacl_loaded),
            "version": version,
            "applied_at": applied_at,
            "status": "success",
        }

    finally:
        if hasattr(conn, "close"):
            conn.close()


def check_health() -> Dict[str, Any]:
    """
    Check the current state of the Memgraph schema.

    Returns:
        Health report dictionary with keys:
        - schema_version: the schema version string
        - labels: number of node labels
        - indexes: number of secondary indexes
        - constraints: number of unique constraints
        - shacl_loaded: boolean indicating SHACL shapes are loaded
        - status: "healthy", "degraded", or "unknown"
    """
    report: Dict[str, Any] = {
        "schema_version": "unknown",
        "labels": 0,
        "indexes": 0,
        "constraints": 0,
        "shacl_loaded": False,
        "status": "unknown",
    }

    conn = _get_memgraph_connection()

    try:
        # Schema version
        try:
            result = conn.execute(
                'MATCH (s:MemgraphSchemaVersion) RETURN s.version AS version LIMIT 1'
            )
            row = list(result)
            if row:
                report["schema_version"] = str(row[0][0])
        except Exception:
            pass

        # Labels count
        try:
            result = conn.execute("SHOW LABELS INFO")
            labels = [row for row in result]
            report["labels"] = len(labels)
        except Exception:
            pass

        # Indexes count
        try:
            result = conn.execute("SHOW INDEXES INFO")
            indexes = [row for row in result]
            report["indexes"] = len(indexes)
        except Exception:
            pass

        # Constraints count
        try:
            result = conn.execute("SHOW CONSTRAINTS INFO")
            constraints = [row for row in result]
            report["constraints"] = len(constraints)
        except Exception:
            pass

        # SHACL loaded status
        try:
            result = conn.execute("CALL shacl.get_loaded_shapes() YIELD name")
            shapes = list(result)
            report["shacl_loaded"] = len(shapes) > 0
        except Exception:
            pass

        # Determine overall status
        if report["labels"] > 0 and report["schema_version"] != "unknown":
            report["status"] = "healthy"
        elif report["schema_version"] != "unknown":
            report["status"] = "degraded"

    finally:
        if hasattr(conn, "close"):
            conn.close()

    return report
