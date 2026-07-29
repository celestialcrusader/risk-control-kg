"""
Unit Tests for Pure RCKG Graph Entity Nodes and Set-Theory Linkages

Validates CRUD operations, dictionary serialization, set-theory enum values,
and foreign key relationship mappings defined in backend/app/models/rckg_nodes.py.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import (
    Base,
    SetTheoryRelation,
    GapSeverity,
    GapState,
    MappingStatus,
    ObligationNode,
    ControlObjectiveNode,
    ControlActivityNode,
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    RiskNode,
    GapNode,
    ShortCircuitAuditLog,
    RiskControlObjectiveMapping,

    ObligationControlObjectiveMapping,
    ControlObjectiveActivityMapping,
    ControlObjectiveFrameworkMapping,
    ControlActivityFrameworkMapping,
)


@pytest.fixture(scope="module")
def engine():
    """Create in-memory SQLite engine for testing ORM models."""
    engine = create_engine("sqlite:///:memory:")
    target_tables = [
        ObligationNode.__table__,
        ControlObjectiveNode.__table__,
        ControlActivityNode.__table__,
        FrameworkControlObjectiveNode.__table__,
        FrameworkControlActivityNode.__table__,
        RiskNode.__table__,
        GapNode.__table__,
        ShortCircuitAuditLog.__table__,
        RiskControlObjectiveMapping.__table__,

        ObligationControlObjectiveMapping.__table__,
        ControlObjectiveActivityMapping.__table__,
        ControlObjectiveFrameworkMapping.__table__,
        ControlActivityFrameworkMapping.__table__,
    ]
    Base.metadata.create_all(engine, tables=target_tables)
    return engine



@pytest.fixture
def db_session(engine):
    """Provide transactional database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def test_set_theory_enums():
    """Test SetTheoryRelation enum values match mathematical definitions."""
    assert SetTheoryRelation.EQUIVALENT_TO.value == "EQUIVALENT_TO"
    assert SetTheoryRelation.SUPERSET_OF.value == "SUPERSET_OF"
    assert SetTheoryRelation.SUBSET_OF.value == "SUBSET_OF"
    assert SetTheoryRelation.INTERSECTS_WITH.value == "INTERSECTS_WITH"
    assert SetTheoryRelation.NO_RELATIONSHIP.value == "NO_RELATIONSHIP"


def test_obligation_node_creation(db_session):
    """Test creating and querying an ObligationNode."""
    obligation = ObligationNode(
        obligation_id="EU-AI-ACT-ART-10.1",
        framework_name="EU AI Act",
        framework_version="2024",
        statement_text="High-risk AI systems shall be developed using high quality training datasets.",
        action_verb="develop",
        subject_noun="training dataset",
        section_reference="Article 10, Paragraph 1"
    )
    db_session.add(obligation)
    db_session.commit()

    saved = db_session.query(ObligationNode).filter_by(obligation_id="EU-AI-ACT-ART-10.1").first()
    assert saved is not None
    assert saved.framework_name == "EU AI Act"
    assert saved.action_verb == "develop"
    
    d = saved.to_dict()
    assert d["obligation_id"] == "EU-AI-ACT-ART-10.1"
    assert d["framework_name"] == "EU AI Act"


def test_control_objective_node_creation(db_session):
    """Test creating and querying a ControlObjectiveNode."""
    obj = ControlObjectiveNode(
        objective_id="POL-SEC-01-OBJ-3",
        policy_name="Information Security Policy",
        policy_version="v2.1",
        objective_name="Data Quality & Integrity Governance",
        objective_text="All training data used in enterprise AI models must undergo validation and bias scanning.",
        owner="Data Governance Board"
    )
    db_session.add(obj)
    db_session.commit()

    saved = db_session.query(ControlObjectiveNode).filter_by(objective_id="POL-SEC-01-OBJ-3").first()
    assert saved is not None
    assert saved.policy_name == "Information Security Policy"
    assert saved.owner == "Data Governance Board"


def test_control_activity_node_creation(db_session):
    """Test creating and querying a ControlActivityNode."""
    act = ControlActivityNode(
        activity_id="SOP-SEC-04-ACT-12",
        sop_name="User Access Provisioning SOP",
        sop_version="v1.0",
        activity_name="Automated Access Review Script",
        activity_text="Execute daily cron job script to revoke dormant user privileges after 30 days of inactivity.",
        implementation_method="AUTOMATED"
    )
    db_session.add(act)
    db_session.commit()

    saved = db_session.query(ControlActivityNode).filter_by(activity_id="SOP-SEC-04-ACT-12").first()
    assert saved is not None
    assert saved.implementation_method == "AUTOMATED"


def test_framework_nodes_creation(db_session):
    """Test creating FrameworkControlObjectiveNode and FrameworkControlActivityNode."""
    fw_obj = FrameworkControlObjectiveNode(
        framework_obj_id="NIST-AI-RMF-GOVERN-1.1",
        framework_name="NIST AI RMF",
        framework_version="1.0",
        objective_name="Governance Policies & Legal Compliance",
        objective_text="Legal and regulatory requirements regarding AI systems are understood and documented."
    )
    fw_act = FrameworkControlActivityNode(
        framework_act_id="NIST-SP800-53-AC-2(1)",
        framework_name="NIST SP 800-53",
        framework_version="Rev 5",
        activity_name="Automated Account Management",
        activity_text="The organization employs automated mechanisms to support the management of information system accounts."
    )
    db_session.add_all([fw_obj, fw_act])
    db_session.commit()

    saved_obj = db_session.query(FrameworkControlObjectiveNode).filter_by(framework_obj_id="NIST-AI-RMF-GOVERN-1.1").first()
    saved_act = db_session.query(FrameworkControlActivityNode).filter_by(framework_act_id="NIST-SP800-53-AC-2(1)").first()
    assert saved_obj is not None
    assert saved_act is not None


def test_risk_and_gap_nodes_creation(db_session):
    """Test creating RiskNode and GapNode."""
    risk = RiskNode(
        risk_id="RSK-SEC-042",
        risk_name="Unsanitized Training Data Bias Risk",
        description="Risk of AI model output bias due to unvalidated training dataset inputs.",
        category="AI_BIAS",
        severity_level="HIGH"
    )
    gap = GapNode(
        gap_id="GAP-2026-001",
        target_entity_type="Obligation",
        target_entity_id=uuid4(),
        set_theory_relation=SetTheoryRelation.SUBSET_OF,
        severity=GapSeverity.HIGH,
        state=GapState.NEW,
        due_date=datetime.utcnow() + timedelta(days=30),
        reviewer_id="auditor_alex"
    )
    db_session.add_all([risk, gap])
    db_session.commit()

    saved_risk = db_session.query(RiskNode).filter_by(risk_id="RSK-SEC-042").first()
    saved_gap = db_session.query(GapNode).filter_by(gap_id="GAP-2026-001").first()
    assert saved_risk is not None
    assert saved_gap is not None
    assert saved_gap.set_theory_relation == SetTheoryRelation.SUBSET_OF


def test_all_5_linkage_mappings(db_session):
    """Test creating mappings for all 5 explicit graph linkages with set-theory classifications."""
    # Create base entity nodes
    risk = RiskNode(risk_id="RSK-1", risk_name="Risk 1", description="Test risk")
    ob = ObligationNode(obligation_id="OB-1", framework_name="FW", statement_text="Obligation text")
    obj = ControlObjectiveNode(objective_id="OBJ-1", policy_name="POL", objective_name="Obj Name", objective_text="Obj text")
    act = ControlActivityNode(activity_id="ACT-1", sop_name="SOP", activity_name="Act Name", activity_text="Act text")
    fw_obj = FrameworkControlObjectiveNode(framework_obj_id="FW-OBJ-1", framework_name="NIST", objective_name="FW Obj", objective_text="FW Obj text")
    fw_act = FrameworkControlActivityNode(framework_act_id="FW-ACT-1", framework_name="NIST", activity_name="FW Act", activity_text="FW Act text")

    db_session.add_all([risk, ob, obj, act, fw_obj, fw_act])
    db_session.commit()

    # Linkage 1: Risk <-> Control Objective (MITIGATES)
    m1 = RiskControlObjectiveMapping(
        risk_id=risk.id,
        control_objective_id=obj.id,
        set_theory_relation=SetTheoryRelation.SUPERSET_OF,
        confidence_score="0.95",
        logic_judge_score="0.98",
        technical_judge_score="0.92",
        rationale="Control objective fully covers the risk vector."
    )

    # Linkage 2: Obligation <-> Control Objective (SATISFIES)
    m2 = ObligationControlObjectiveMapping(
        obligation_id=ob.id,
        control_objective_id=obj.id,
        set_theory_relation=SetTheoryRelation.EQUIVALENT_TO,
        confidence_score="0.99",
        logic_judge_score="1.00",
        technical_judge_score="0.98",
        rationale="1:1 semantic identity match."
    )

    # Linkage 3: Control Objective <-> Control Activity (OPERATIONALIZED_BY)
    m3 = ControlObjectiveActivityMapping(
        control_objective_id=obj.id,
        control_activity_id=act.id,
        set_theory_relation=SetTheoryRelation.SUPERSET_OF,
        confidence_score="0.91",
        rationale="Activity operationalizes objective completely."
    )

    # Linkage 4: Control Objective <-> Framework Control Objective (CROSSWALKS_TO_OBJ)
    m4 = ControlObjectiveFrameworkMapping(
        control_objective_id=obj.id,
        framework_objective_id=fw_obj.id,
        set_theory_relation=SetTheoryRelation.EQUIVALENT_TO,
        confidence_score="0.94",
        rationale="Direct crosswalk match to NIST AI RMF."
    )

    # Linkage 5: Control Activity <-> Framework Control Activity (CROSSWALKS_TO_ACT)
    m5 = ControlActivityFrameworkMapping(
        control_activity_id=act.id,
        framework_activity_id=fw_act.id,
        set_theory_relation=SetTheoryRelation.SUBSET_OF,
        confidence_score="0.85",
        rationale="SOP satisfies a subset of the NIST activity requirement."
    )

    db_session.add_all([m1, m2, m3, m4, m5])
    db_session.commit()

    # Query back & verify
    assert db_session.query(RiskControlObjectiveMapping).count() == 1
    assert db_session.query(ObligationControlObjectiveMapping).count() == 1
    assert db_session.query(ControlObjectiveActivityMapping).count() == 1
    assert db_session.query(ControlObjectiveFrameworkMapping).count() == 1
    assert db_session.query(ControlActivityFrameworkMapping).count() == 1

    saved_m2 = db_session.query(ObligationControlObjectiveMapping).first()
    assert saved_m2.set_theory_relation == SetTheoryRelation.EQUIVALENT_TO
    assert saved_m2.confidence_score == "0.99"
