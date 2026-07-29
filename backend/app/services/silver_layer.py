"""
Silver Layer Storage service for EXTRACT-4.

Handles writing, querying, and versioning of SemanticControl records
in the PostgreSQL semantic_controls table.

Functions:
- write_silver_record: Insert a single obligation as a SemanticControl row
- write_batch_silver_records: Insert multiple obligations in one transaction
- get_semantic_control: Query a SemanticControl by control_id
- version_obligation: Create a new version of an existing control
"""

import logging
from typing import List, Optional

from app.models import SemanticControl
from app.schemas.obligation import Obligation
from app.core.database import get_db_session

logger = logging.getLogger(__name__)


def write_silver_record(
    obligation: Obligation,
    session,
    bronze_record_id=None,
) -> SemanticControl:
    """
    Write a single validated obligation to the Silver layer.

    Maps Obligation fields to SemanticControl columns:
    - control_id <- obligation.id
    - objective_text <- obligation.prose
    - statement_text <- obligation.prose
    - action_verb <- obligation.action_verb
    - subject_noun <- obligation.subject_noun

    Args:
        obligation: Validated Obligation Pydantic model instance.
        session: SQLAlchemy session (caller's responsibility).
        bronze_record_id: Optional UUID string linking to Bronze layer.

    Returns:
        The created SemanticControl object.
    """
    record = SemanticControl(
        framework_name="de-jure",
        control_id=obligation.id,
        objective_text=obligation.prose,
        statement_text=obligation.prose,
        action_verb=obligation.action_verb,
        subject_noun=obligation.subject_noun,
        bronze_record_id=bronze_record_id,
    )
    session.add(record)
    session.commit()
    logger.info("Wrote silver record for control_id=%s (v%d)", record.control_id, record.version)
    return record


def write_batch_silver_records(
    obligations: List[Obligation],
    session,
    bronze_record_id=None,
) -> List[SemanticControl]:
    """
    Write multiple obligations to the Silver layer in one transaction.

    Args:
        obligations: List of validated Obligation instances.
        session: SQLAlchemy session (caller's responsibility).
        bronze_record_id: Optional UUID string linking to Bronze layer.

    Returns:
        List of created SemanticControl objects.
    """
    records = []
    for obligation in obligations:
        record = SemanticControl(
            framework_name="de-jure",
            control_id=obligation.id,
            objective_text=obligation.prose,
            statement_text=obligation.prose,
            action_verb=obligation.action_verb,
            subject_noun=obligation.subject_noun,
            bronze_record_id=bronze_record_id,
        )
        session.add(record)
        records.append(record)

    if records:
        session.commit()

    logger.info(
        "Wrote %d silver records",
        len(records),
    )
    return records


def get_semantic_control(control_id: str, session) -> Optional[SemanticControl]:
    """
    Query a SemanticControl by its control_id.

    Args:
        control_id: The control identifier to look up.
        session: SQLAlchemy session (caller's responsibility).

    Returns:
        The SemanticControl record, or None if not found.
    """
    result = (
        session.query(SemanticControl)
        .filter(SemanticControl.control_id == control_id)
        .filter(SemanticControl.status != "superseded")
        .order_by(SemanticControl.version.desc())
        .first()
    )
    return result


def version_obligation(
    control_id: str,
    obligation: Obligation,
    session,
) -> Optional[SemanticControl]:
    """
    Create a new version of an existing semantic control record.

    Finds the latest version of the control, copies its bronze_record_id,
    and inserts a new row with version incremented by 1.

    Args:
        control_id: The control identifier to version.
        obligation: The new Obligation data for the new version.
        session: SQLAlchemy session (caller's responsibility).

    Returns:
        The new SemanticControl record, or None if no existing record found.
    """
    existing = get_semantic_control(control_id, session)
    if existing is None:
        logger.warning("No existing semantic control found for control_id=%s", control_id)
        return None

    new_record = SemanticControl(
        framework_name=existing.framework_name,
        control_id=existing.control_id,
        objective_text=obligation.prose,
        statement_text=obligation.prose,
        action_verb=obligation.action_verb,
        subject_noun=obligation.subject_noun,
        bronze_record_id=existing.bronze_record_id,
        version=existing.version + 1,
    )
    session.add(new_record)
    session.commit()
    logger.info(
        "Versioned control_id=%s to version=%d",
        control_id,
        new_record.version,
    )
    return new_record
