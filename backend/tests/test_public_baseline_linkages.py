"""
Unit & Integration Tests for Direct Public Baseline Linkages (STORY-FOUNDATION-104).
"""

import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.rckg_nodes import (
    ObligationNode,
    FrameworkControlObjectiveNode,
    RiskNode,
    SetTheoryRelation,
    MappingStatus,
    ObligationFrameworkMapping,
    RiskFrameworkMapping,
    FrameworkCrosswalkMapping,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session for testing ORM mappings."""
    engine = create_engine("sqlite:///:memory:")
    target_tables = [
        ObligationNode.__table__,
        FrameworkControlObjectiveNode.__table__,
        RiskNode.__table__,
        ObligationFrameworkMapping.__table__,
        RiskFrameworkMapping.__table__,
        FrameworkCrosswalkMapping.__table__,
    ]
    Base.metadata.create_all(engine, tables=target_tables)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()



def test_obligation_framework_mapping_creation(db_session):
    """Verify direct Obligation <---> Framework Control Objective mapping without ControlObjective."""
    obl = ObligationNode(
        id=uuid4(),
        obligation_id="MAS-5.1.1",
        framework_name="MAS TRM",
        framework_version="2021",
        statement_text="The Financial Institution must implement multi-factor authentication.",
        action_verb="implement",
        subject_noun="Financial Institution",
    )
    fco = FrameworkControlObjectiveNode(
        id=uuid4(),
        framework_obj_id="NIST-AC-2",
        framework_name="NIST SP 800-53",
        framework_version="Rev 5",
        objective_name="Account Management",
        objective_text="Organization manages information system accounts.",
    )
    db_session.add(obl)
    db_session.add(fco)
    db_session.commit()

    mapping = ObligationFrameworkMapping(
        id=uuid4(),
        obligation_id=obl.id,
        framework_objective_id=fco.id,
        set_theory_relation=SetTheoryRelation.EQUIVALENT_TO,
        confidence_score="0.95",
        status=MappingStatus.HUMAN_ATTESTED,
        is_golden_assertion="TRUE",
    )
    db_session.add(mapping)
    db_session.commit()

    saved = db_session.query(ObligationFrameworkMapping).filter_by(obligation_id=obl.id).first()
    assert saved is not None
    assert saved.framework_objective_id == fco.id
    assert saved.set_theory_relation == SetTheoryRelation.EQUIVALENT_TO
    assert saved.is_golden_assertion == "TRUE"


def test_risk_framework_mapping_creation(db_session):
    """Verify direct Risk <---> Framework Control Objective mapping (MITIGATES)."""
    risk = RiskNode(
        id=uuid4(),
        risk_id="RISK-01.01",
        risk_name="Model Inversion Attack",
        description="Adversaries query model endpoints to reconstruct sensitive training data.",
        category="TECHNICAL",
        severity_level="HIGH",
    )
    fco = FrameworkControlObjectiveNode(
        id=uuid4(),
        framework_obj_id="NIST-SI-10",
        framework_name="NIST SP 800-53",
        framework_version="Rev 5",
        objective_name="Information Input Validation",
        objective_text="Organization checks character strings for validity.",
    )
    db_session.add(risk)
    db_session.add(fco)
    db_session.commit()

    risk_map = RiskFrameworkMapping(
        id=uuid4(),
        risk_id=risk.id,
        framework_objective_id=fco.id,
        confidence_score="0.88",
    )
    db_session.add(risk_map)
    db_session.commit()

    saved_risk_map = db_session.query(RiskFrameworkMapping).filter_by(risk_id=risk.id).first()
    assert saved_risk_map is not None
    assert saved_risk_map.framework_objective_id == fco.id


def test_framework_crosswalk_mapping_creation(db_session):
    """Verify direct Framework <---> Framework crosswalk (e.g. CSA CCM <-> NIST)."""
    fco_source = FrameworkControlObjectiveNode(
        id=uuid4(),
        framework_obj_id="CCM-IAM-01",
        framework_name="CSA CCM",
        framework_version="v4",
        objective_name="Identity and Access Management Policy",
        objective_text="Policies and procedures shall be established for identity and access management.",
    )
    fco_target = FrameworkControlObjectiveNode(
        id=uuid4(),
        framework_obj_id="NIST-AC-1",
        framework_name="NIST SP 800-53",
        framework_version="Rev 5",
        objective_name="Policy and Procedures",
        objective_text="Organization develops access control policy.",
    )
    db_session.add(fco_source)
    db_session.add(fco_target)
    db_session.commit()

    crosswalk = FrameworkCrosswalkMapping(
        id=uuid4(),
        source_framework_obj_id=fco_source.id,
        target_framework_obj_id=fco_target.id,
        set_theory_relation=SetTheoryRelation.EQUIVALENT_TO,
        confidence_score="1.00",
        status=MappingStatus.HUMAN_ATTESTED,
    )
    db_session.add(crosswalk)
    db_session.commit()

    saved_cw = db_session.query(FrameworkCrosswalkMapping).filter_by(source_framework_obj_id=fco_source.id).first()
    assert saved_cw is not None
    assert saved_cw.target_framework_obj_id == fco_target.id
