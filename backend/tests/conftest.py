"""
Pytest configuration and fixture factories for backend test suite (RCKG-100).
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add repository root and backend directory to sys.path so 'app' and 'backend.app' imports work
BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent
for path in [str(REPO_ROOT), str(BACKEND_ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from app.models import (
    Base,
    ObligationNode,
    ControlObjectiveNode,
    ControlActivityNode,
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    ControlObjectiveFrameworkMapping,
    RiskNode,
    GraphOutboxLog,
    GapNode,
    AuditLog,
)


from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def in_memory_db_engine():
    """Create in-memory SQLite database engine for testing model fixtures."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    target_tables = [
        ObligationNode.__table__,
        ControlObjectiveNode.__table__,
        ControlActivityNode.__table__,
        FrameworkControlObjectiveNode.__table__,
        FrameworkControlActivityNode.__table__,
        ControlObjectiveFrameworkMapping.__table__,
        RiskNode.__table__,
        GraphOutboxLog.__table__,
        GapNode.__table__,
        AuditLog.__table__,
    ]
    Base.metadata.create_all(engine, tables=target_tables)
    return engine


@pytest.fixture(scope="function")
def db_session(in_memory_db_engine):
    """Provide isolated transactional database session for each test function."""
    connection = in_memory_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# =============================================================================
# Node Fixture Factories (6 Core RCKG Node Types)
# =============================================================================

@pytest.fixture
def sample_obligation():
    """Fixture producing a sample ObligationNode instance."""
    return ObligationNode(
        id=uuid4(),
        obligation_id=f"OBL-{uuid4().hex[:8]}",
        framework_name="NIST SP 800-53",
        framework_version="Rev 5",
        statement_text="The organization manages information system accounts.",
        action_verb="manages",
        subject_noun="system accounts",
        section_reference="AC-2",
    )


@pytest.fixture
def sample_control_objective():
    """Fixture producing a sample ControlObjectiveNode instance."""
    return ControlObjectiveNode(
        id=uuid4(),
        objective_id=f"OBJ-{uuid4().hex[:8]}",
        policy_name="Access Control Policy",
        policy_version="v2.1",
        objective_name="Account Management Standard",
        objective_text="Ensure mandatory account lifecycle review and access control.",
        owner="SecOps Lead",
    )


@pytest.fixture
def sample_control_activity():
    """Fixture producing a sample ControlActivityNode instance."""
    return ControlActivityNode(
        id=uuid4(),
        activity_id=f"ACT-{uuid4().hex[:8]}",
        sop_name="User Provisioning SOP",
        sop_version="v1.0",
        activity_name="Quarterly Access Audit Procedure",
        activity_text="Automated script executes quarterly review of active LDAP accounts.",
        implementation_method="AUTOMATED_SCRIPT",
    )


@pytest.fixture
def sample_framework_obj():
    """Fixture producing a sample FrameworkControlObjectiveNode instance."""
    return FrameworkControlObjectiveNode(
        id=uuid4(),
        framework_obj_id=f"FCO-{uuid4().hex[:8]}",
        framework_name="NIST SP 800-53",
        framework_version="Rev 5",
        objective_name="AC-2 Account Management",
        objective_text="Control objective for managing information system accounts.",
    )


@pytest.fixture
def sample_framework_act():
    """Fixture producing a sample FrameworkControlActivityNode instance."""
    return FrameworkControlActivityNode(
        id=uuid4(),
        framework_act_id=f"FCA-{uuid4().hex[:8]}",
        framework_name="ISO/IEC 27001",
        framework_version="2022",
        activity_name="A.5.15 Access Control Implementation",
        activity_text="Rules to control physical and logical access to information.",
    )


@pytest.fixture
def sample_risk():
    """Fixture producing a sample RiskNode instance."""
    return RiskNode(
        id=uuid4(),
        risk_id=f"RISK-{uuid4().hex[:8]}",
        risk_name="Unauthorized Access Risk",
        description="Threat of unauthorized privilege escalation or stale account misuse.",
        category="OPERATIONAL_SECURITY",
        severity_level="HIGH",
    )
