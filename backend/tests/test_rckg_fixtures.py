"""
TDD Tests for RCKG Test Infrastructure, Docker Compose, and Fixture Factories (RCKG-100).
"""

import os
import pytest
import yaml
from pathlib import Path
from app.models.rckg_nodes import (
    ObligationNode,
    ControlObjectiveNode,
    ControlActivityNode,
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    RiskNode,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_docker_compose_test_yml_exists_and_valid():
    """AC-1: Verify docker-compose.test.yml exists and configures isolated test ports."""
    docker_test_file = PROJECT_ROOT / "docker-compose.test.yml"
    assert docker_test_file.exists(), "docker-compose.test.yml does not exist"

    with open(docker_test_file, "r") as f:
        config = yaml.safe_load(f)

    services = config.get("services", {})
    assert "postgres_test" in services
    assert "memgraph_test" in services
    assert "elasticsearch_test" in services
    assert "qdrant_test" in services

    # Verify isolated ports mapping
    pg_ports = services["postgres_test"]["ports"]
    assert "5433:5432" in pg_ports

    mem_ports = services["memgraph_test"]["ports"]
    assert "7688:7687" in mem_ports

    es_ports = services["elasticsearch_test"]["ports"]
    assert "9201:9200" in es_ports

    qdrant_ports = services["qdrant_test"]["ports"]
    assert "6334:6333" in qdrant_ports


def test_makefile_test_env_targets():
    """AC-1 & AC-3: Verify Makefile contains test-env-up, test-env-down, and test targets."""
    makefile = PROJECT_ROOT / "Makefile"
    assert makefile.exists(), "Makefile does not exist"

    content = makefile.read_text()
    assert "test-env-up:" in content
    assert "test-env-down:" in content
    assert "test:" in content


def test_node_fixture_factories(
    sample_obligation,
    sample_control_objective,
    sample_control_activity,
    sample_framework_obj,
    sample_framework_act,
    sample_risk,
):
    """AC-2: Verify pytest node fixture factories generate valid 6 core node instances."""
    assert isinstance(sample_obligation, ObligationNode)
    assert sample_obligation.obligation_id.startswith("OBL-")

    assert isinstance(sample_control_objective, ControlObjectiveNode)
    assert sample_control_objective.objective_id.startswith("OBJ-")

    assert isinstance(sample_control_activity, ControlActivityNode)
    assert sample_control_activity.activity_id.startswith("ACT-")

    assert isinstance(sample_framework_obj, FrameworkControlObjectiveNode)
    assert sample_framework_obj.framework_obj_id.startswith("FCO-")

    assert isinstance(sample_framework_act, FrameworkControlActivityNode)
    assert sample_framework_act.framework_act_id.startswith("FCA-")

    assert isinstance(sample_risk, RiskNode)
    assert sample_risk.risk_id.startswith("RISK-")
