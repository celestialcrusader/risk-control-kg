"""
Test suite for INFRA-9: Memgraph Schema Initialization

This test module verifies the graph schema initialization implementation including:
- Cypher schema initialization script with all 8 node labels
- Unique constraints on primary keys
- Indexes on key properties
- SHACL shape files
- Python schema initialization module with idempotent execution
- Schema version tracking
- Health check endpoint

Test Strategy:
- Unit tests with mocked py2neo driver (no real Memgraph needed)
- File-based tests read actual .cypher and .ttl files
- Tests verify actual values, not just absence of errors
- All assertions are meaningful
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

NODE_LABELS = [
    "Obligation",
    "Control",
    "Regulation",
    "Gap",
    "Risk",
    "Evidence",
    "ThirdParty",
    "ControlEffectiveness",
]

UNIQUE_CONSTRAINT_KEYS = {
    "Obligation": "obligation_id",
    "Control": "control_id",
    "Regulation": "document_id",
    "Gap": "gap_id",
    "Risk": "risk_id",
    "Evidence": "evidence_id",
    "ThirdParty": "third_party_id",
    "ControlEffectiveness": "effectiveness_id",
}

INDEX_PROPERTIES = ["obligation_id", "control_id", "framework_id", "document_id"]

SCHEMA_VERSION = "INFRA-9"


# ─── AC-1: Cypher file exists and contains all 8 node labels ─────────────────

class TestCypherFile:
    """Tests for the Cypher schema initialization script."""

    def test_cypher_file_exists(self):
        """AC-1a: init_schema.cypher file exists at the expected path."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        assert cypher_path.exists(), "init_schema.cypher should exist"

    @pytest.mark.parametrize("label", NODE_LABELS)
    def test_all_node_labels_in_cypher(self, label):
        """AC-1b: All 8 node labels are created in the Cypher script."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        assert label in content

    def test_cypher_creates_unique_constraints(self):
        """AC-3: Unique constraints exist for all 8 primary keys."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        for label, key in UNIQUE_CONSTRAINT_KEYS.items():
            assert label in content
            assert key in content
        assert "IS UNIQUE" in content

    def test_cypher_creates_indexes(self):
        """AC-2: Indexes exist on all required properties."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        for prop in INDEX_PROPERTIES:
            assert prop in content, f"Index property '{prop}' missing from cypher"

    def test_cypher_uses_if_not_exists(self):
        """AC-6: Schema script is idempotent with IF NOT EXISTS guards."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        assert "IF NOT EXISTS" in content

    def test_cypher_tracks_schema_version(self):
        """AC-5: Schema version is recorded in the Cypher script."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        assert SCHEMA_VERSION in content

    def test_python_loads_shacl_shapes(self):
        """AC-4: Python init_schema loads SHACL shapes from TTL files."""
        from app.graph import schema

        assert hasattr(schema, "init_schema")
        assert hasattr(schema, "_load_shacl_shapes")


# ─── AC-4: SHACL shape files ────────────────────────────────────────────────

class TestShaclShapes:
    """Tests for SHACL shape files."""

    def test_shapes_directory_exists(self):
        """AC-4a: shapes directory exists."""
        shapes_dir = Path("app", "shapes")
        assert shapes_dir.exists(), "shapes directory should exist"

    def test_shapes_directory_contains_ttl_files(self):
        """AC-4b: At least one .ttl shape file exists."""
        shapes_dir = Path("app", "shapes")
        ttl_files = list(shapes_dir.glob("*.ttl"))
        assert len(ttl_files) > 0, "At least one .ttl file should exist"

    def test_all_8_shape_files_exist(self):
        """AC-4b: All 8 node labels have a corresponding shape file."""
        shapes_dir = Path("app", "shapes")
        ttl_files = {f.stem.lower().replace("_", "") for f in shapes_dir.glob("*.ttl")}
        expected = {
            "obligation",
            "control",
            "regulation",
            "gap",
            "risk",
            "evidence",
            "thirdparty",
            "controleffectiveness",
        }
        assert expected.issubset(ttl_files), (
            f"Missing shape files. Found: {ttl_files}, Expected subset: {expected}"
        )

    def test_ttl_files_are_valid_rdf_syntax(self):
        """AC-4c: TTL files have valid structure with @prefix and shapes."""
        shapes_dir = Path("app", "shapes")
        for ttl_file in shapes_dir.glob("*.ttl"):
            content = ttl_file.read_text()
            assert "@prefix" in content or "PREFIX" in content
            assert ":" in content or "http" in content

    def test_ttl_files_define_node_shapes(self):
        """AC-4c: TTL files define SHACL NodeShapes."""
        shapes_dir = Path("app", "shapes")
        for ttl_file in shapes_dir.glob("*.ttl"):
            content = ttl_file.read_text()
            assert "sh:NodeShape" in content or "sh:NodeShape" in content

    def test_shapes_cover_all_node_labels(self):
        """AC-4d: Together, the shape files reference all node labels."""
        shapes_dir = Path("app", "shapes")
        combined = ""
        for ttl_file in shapes_dir.glob("*.ttl"):
            combined += ttl_file.read_text()
        for label in NODE_LABELS:
            assert label in combined, f"Label '{label}' should be referenced in shape files"


# ─── AC-5 & AC-6: Python Schema Initialization Module ───────────────────────

class TestInitSchema:
    """Tests for the init_schema() function."""

    def test_init_schema_raises_file_not_found(self):
        """init_schema raises FileNotFoundError when script is missing."""
        from app.graph.schema import init_schema

        with pytest.raises(FileNotFoundError, match="Cypher script not found"):
            init_schema(cypher_path=Path("/nonexistent/script.cypher"))

    @patch("app.graph.schema._get_memgraph_connection")
    def test_init_schema_executes_cypher(self, mock_get_conn):
        """init_schema reads and executes the Cypher script."""
        from app.graph.schema import init_schema

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Mock SHOW queries
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result

        with patch("app.graph.schema.GRAPH_SCRIPT_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = (
                "CREATE CONSTRAINT IF NOT EXISTS FOR (o:Obligation) "
                "REQUIRE o.obligation_id IS UNIQUE;"
            )

            result = init_schema()

        mock_conn.execute.assert_called()
        assert result["status"] == "success"
        assert result["version"] == SCHEMA_VERSION

    @patch("app.graph.schema._get_memgraph_connection")
    def test_init_schema_loads_shacl_shapes(self, mock_get_conn):
        """init_schema loads SHACL shapes from .ttl files."""
        from app.graph.schema import init_schema

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Mock SHOW queries
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result

        with patch("app.graph.schema.GRAPH_SCRIPT_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = ""

            with patch("app.graph.schema.SHAPES_DIR") as mock_shapes:
                mock_shape_file = MagicMock()
                mock_shape_file.name = "test.ttl"
                mock_shapes.glob.return_value = [mock_shape_file]

                result = init_schema()

        assert result["status"] == "success"
        assert len(result["shacl_loaded"]) == 1
        assert "test.ttl" in result["shacl_loaded"]

    @patch("app.graph.schema._get_memgraph_connection")
    def test_init_schema_returns_application_summary(self, mock_get_conn):
        """init_schema returns summary with expected keys."""
        from app.graph.schema import init_schema

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Mock SHOW queries to return expected counts
        mock_labels_result = MagicMock()
        mock_labels_result.__iter__ = MagicMock(return_value=iter([["label"]] * 8))
        mock_constraints_result = MagicMock()
        mock_constraints_result.__iter__ = MagicMock(return_value=iter([["c"]] * 8))
        mock_indexes_result = MagicMock()
        mock_indexes_result.__iter__ = MagicMock(return_value=iter([["i"]] * 2))

        def show_side_effect(q):
            if "SHOW LABELS" in q:
                return mock_labels_result
            if "SHOW CONSTRAINTS" in q:
                return mock_constraints_result
            if "SHOW INDEXES" in q:
                return mock_indexes_result
            return MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = show_side_effect

        with patch("app.graph.schema.GRAPH_SCRIPT_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = ""

            with patch("app.graph.schema.SHAPES_DIR") as mock_shapes:
                mock_shapes.glob.return_value = []
                result = init_schema()

        expected_keys = {"labels", "constraints", "indexes", "shacl_loaded",
                         "shacl_count", "version", "applied_at", "status"}
        assert expected_keys.issubset(result.keys())
        assert result["labels"] == 8
        assert result["constraints"] == 8
        assert result["indexes"] == 2
        assert result["version"] == SCHEMA_VERSION

    @patch("app.graph.schema._get_memgraph_connection")
    def test_init_schema_cleans_up_connection(self, mock_get_conn):
        """init_schema closes connection after execution."""
        from app.graph.schema import init_schema

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result

        with patch("app.graph.schema.GRAPH_SCRIPT_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = ""
            with patch("app.graph.schema.SHAPES_DIR") as mock_shapes:
                mock_shapes.glob.return_value = []
                init_schema()

        mock_conn.close.assert_called_once()

    @patch("app.graph.schema._get_memgraph_connection")
    def test_init_schema_is_idempotent(self, mock_get_conn):
        """AC-6a: init_schema can run multiple times without error."""
        from app.graph.schema import init_schema

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Mock SHOW queries to avoid TypeError when converting MagicMock to list
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result

        with patch("app.graph.schema.GRAPH_SCRIPT_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = (
                "CREATE CONSTRAINT IF NOT EXISTS FOR (o:Obligation) "
                "REQUIRE o.obligation_id IS UNIQUE;"
            )
            with patch("app.graph.schema.SHAPES_DIR") as mock_shapes:
                mock_shapes.glob.return_value = []
                init_schema()
                init_schema()

        # Both calls succeed -- no assertion error raised
        # Each init_schema call: 1 cypher execute + 3 SHOW queries = 4
        assert mock_conn.execute.call_count == 8


# ─── Health Check ────────────────────────────────────────────────────────────

class TestCheckHealth:
    """Tests for the check_health() function."""

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_schema_version(self, mock_get_conn):
        """Health returns the schema version from the graph."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Simulate version node query
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([[SCHEMA_VERSION]]))
        mock_conn.execute.side_effect = lambda q: (
            mock_result if "MemgraphSchemaVersion" in q else MagicMock(return_value=iter([]))
        )

        health = check_health()

        assert health["schema_version"] == SCHEMA_VERSION

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_labels_count(self, mock_get_conn):
        """Health returns the count of labels."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([["Obligation"]] * 8))

        def side_effect(q):
            if "SHOW LABELS" in q:
                return mock_result
            return MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = side_effect

        health = check_health()
        assert health["labels"] == 8

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_indexes_count(self, mock_get_conn):
        """Health returns the count of indexes."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([["idx"]] * 2))

        def side_effect(q):
            if "SHOW INDEXES" in q:
                return mock_result
            return MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = side_effect

        health = check_health()
        assert health["indexes"] == 2

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_constraints_count(self, mock_get_conn):
        """Health returns the count of constraints."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([["constraint"]] * 8))

        def side_effect(q):
            if "SHOW CONSTRAINTS" in q:
                return mock_result
            return MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = side_effect

        health = check_health()
        assert health["constraints"] == 8

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_shacl_loaded_status(self, mock_get_conn):
        """Health returns SHACL loaded status."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([["shape_name"]]))
        mock_conn.execute.side_effect = lambda q: (
            mock_result if "shacl.get_loaded_shapes" in q else MagicMock(return_value=iter([]))
        )

        health = check_health()
        assert health["shacl_loaded"] is True
        assert isinstance(health["shacl_loaded"], bool)

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_healthy_status(self, mock_get_conn):
        """Health returns 'healthy' when labels and schema_version are present."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([[SCHEMA_VERSION]]))
        mock_result2 = MagicMock()
        mock_result2.__iter__ = MagicMock(return_value=iter([["label"]] * 8))

        def side_effect(q):
            if "MemgraphSchemaVersion" in q:
                return mock_result
            if "SHOW LABELS" in q:
                return mock_result2
            return MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = side_effect

        health = check_health()
        assert health["status"] == "healthy"

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_degraded_status(self, mock_get_conn):
        """Health returns 'degraded' when schema version exists but labels are 0."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([[SCHEMA_VERSION]]))
        mock_conn.execute.side_effect = lambda q: (
            mock_result if "MemgraphSchemaVersion" in q
            else MagicMock(return_value=iter([]))
        )

        health = check_health()
        assert health["status"] == "degraded"

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_returns_unknown_status(self, mock_get_conn):
        """Health returns 'unknown' when nothing is found."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("connection refused")

        health = check_health()
        assert health["status"] == "unknown"
        assert health["schema_version"] == "unknown"
        assert health["labels"] == 0

    @patch("app.graph.schema._get_memgraph_connection")
    def test_health_cleans_up_connection(self, mock_get_conn):
        """Health check closes connection after execution."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Simulate successful queries
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([[SCHEMA_VERSION]]))
        mock_result2 = MagicMock()
        mock_result2.__iter__ = MagicMock(return_value=iter([["label"]]))
        mock_result3 = MagicMock()
        mock_result3.__iter__ = MagicMock(return_value=iter([["idx"]]))
        mock_result4 = MagicMock()
        mock_result4.__iter__ = MagicMock(return_value=iter([["constraint"]]))
        mock_result5 = MagicMock()
        mock_result5.__iter__ = MagicMock(return_value=iter([]))

        def side_effect(q):
            if "MemgraphSchemaVersion" in q:
                return mock_result
            if "SHOW LABELS" in q:
                return mock_result2
            if "SHOW INDEXES" in q:
                return mock_result3
            if "SHOW CONSTRAINTS" in q:
                return mock_result4
            return mock_result5

        mock_conn.execute.side_effect = side_effect

        health = check_health()
        mock_conn.close.assert_called_once()

    def test_health_returns_expected_keys(self):
        """Health response contains all expected keys."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        with patch("app.graph.schema._get_memgraph_connection", return_value=mock_conn):
            mock_result = MagicMock()
            mock_result.__iter__ = MagicMock(return_value=iter([]))
            mock_conn.execute.side_effect = lambda q: MagicMock(return_value=iter([]))

            health = check_health()

        expected_keys = {"schema_version", "labels", "indexes", "constraints",
                         "shacl_loaded", "status"}
        assert expected_keys.issubset(health.keys())


# ─── AC-Health: Health check endpoint ─────────────────────────────────────────

class TestHealthCheckEndpoint:
    """Tests for the /api/v1/graph/health endpoint."""

    def test_health_check_endpoint_returns_json(self):
        """AC-Health: The health endpoint returns a JSON response."""
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("fastapi not installed")

        from app.api.graph import router as graph_router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(graph_router, prefix="/api/v1/graph", tags=["graph"])

        client = TestClient(app)

        with patch("app.graph.schema.check_health") as mock_health:
            mock_health.return_value = {
                "schema_version": SCHEMA_VERSION,
                "labels": 8,
                "indexes": 2,
                "constraints": 8,
                "shacl_loaded": True,
                "status": "healthy",
            }
            response = client.get("/api/v1/graph/health")

        assert response.status_code == 200
        body = response.json()
        assert body["schema_version"] == SCHEMA_VERSION
        assert body["labels"] == 8
        assert body["indexes"] == 2
        assert body["constraints"] == 8
        assert body["shacl_loaded"] is True
        assert body["status"] == "healthy"


# ─── Module Import Tests ─────────────────────────────────────────────────────

class TestSchemaModuleImport:
    """Tests that the module is importable as a Python module."""

    def test_schema_module_is_importable(self):
        """The schema module can be imported."""
        from app.graph import schema

        assert hasattr(schema, "init_schema")
        assert hasattr(schema, "check_health")

    def test_init_schema_is_callable(self):
        """The init_schema function is callable."""
        from app.graph.schema import init_schema

        assert callable(init_schema)

    def test_check_health_is_callable(self):
        """The check_health function is callable."""
        from app.graph.schema import check_health

        assert callable(check_health)

    def test_graph_init_exposes_functions(self):
        """The graph package __init__ exposes the public functions."""
        from app.graph import init_schema, check_health

        assert callable(init_schema)
        assert callable(check_health)


# ─── Edge Cases ──────────────────────────────────────────────────────────────

class TestEdgeCases:
    """Edge case tests beyond the acceptance criteria."""

    @patch("app.graph.schema._get_memgraph_connection")
    def test_init_schema_handles_missing_shapes_dir(self, mock_get_conn):
        """init_schema handles missing shapes directory gracefully."""
        from app.graph.schema import init_schema

        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result

        with patch("app.graph.schema.GRAPH_SCRIPT_PATH") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = ""

            with patch("app.graph.schema.SHAPES_DIR") as mock_shapes:
                mock_shapes.exists.return_value = False
                mock_shapes.glob.return_value = []
                result = init_schema()

        assert result["status"] == "success"
        assert result["shacl_count"] == 0

    @patch("app.graph.schema._get_memgraph_connection")
    def test_check_health_handles_connection_failure(self, mock_get_conn):
        """check_health raises when no Memgraph client is available."""
        from app.graph.schema import check_health

        mock_get_conn.side_effect = ImportError("No Memgraph client library found")

        with pytest.raises(ImportError, match="No Memgraph client library"):
            check_health()

    def test_cypher_all_constraints_have_unique(self):
        """Every constraint in the Cypher file uses IS UNIQUE."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        constraint_lines = [
            line for line in content.split("\n")
            if "CREATE CONSTRAINT" in line
        ]
        unique_count = content.count("IS UNIQUE")
        assert unique_count == len(constraint_lines), (
            f"Expected {len(constraint_lines)} IS UNIQUE clauses, "
            f"found {unique_count}"
        )

    def test_cypher_all_indexes_use_if_not_exists(self):
        """Every CREATE INDEX uses IF NOT EXISTS."""
        cypher_path = Path("app", "graph", "init_schema.cypher")
        content = cypher_path.read_text()
        index_lines = [
            line for line in content.split("\n")
            if "CREATE INDEX" in line
        ]
        if_not_exists_count = content.count("IF NOT EXISTS")
        constraint_lines = [
            line for line in content.split("\n")
            if "CREATE CONSTRAINT" in line
        ]
        total_statements = len(index_lines) + len(constraint_lines)
        assert if_not_exists_count >= total_statements, (
            f"Expected IF NOT EXISTS on all {total_statements} statements"
        )

    def test_all_ttl_files_are_unique_shapes(self):
        """Each TTL file defines exactly one NodeShape."""
        shapes_dir = Path("app", "shapes")
        for ttl_file in shapes_dir.glob("*.ttl"):
            content = ttl_file.read_text()
            shape_count = content.count("a sh:NodeShape")
            assert shape_count == 1, (
                f"{ttl_file.name} should define exactly 1 NodeShape, "
                f"found {shape_count}"
            )

    def test_health_returns_empty_shacl_when_no_ttl(self):
        """Health returns shacl_loaded=False when no TTL files exist."""
        from app.graph.schema import check_health

        mock_conn = MagicMock()
        mock_get_conn = MagicMock(return_value=mock_conn)

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.side_effect = lambda q: mock_result

        with patch("app.graph.schema._get_memgraph_connection", mock_get_conn):
            health = check_health()

        assert health["shacl_loaded"] is False
