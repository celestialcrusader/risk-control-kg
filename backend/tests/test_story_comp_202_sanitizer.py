"""
Unit and Integration tests for STORY-COMP-202: Catalog Sanitizer & Inactive/Withdrawn Control Filter.
"""
import pytest
from app.services.catalog_sanitizer import (
    is_active_control,
    filter_active_controls,
    WITHDRAWN_NIST_REV5_CONTROLS,
)


class MockControl:
    def __init__(self, framework_obj_id: str, objective_name: str, objective_text: str):
        self.framework_obj_id = framework_obj_id
        self.objective_name = objective_name
        self.objective_text = objective_text


def test_withdrawn_controls_list():
    """Verify known Rev 5 withdrawn controls are identified."""
    assert "NIST-RA-4" in WITHDRAWN_NIST_REV5_CONTROLS or "RA-4" in WITHDRAWN_NIST_REV5_CONTROLS
    assert "NIST-SA-12" in WITHDRAWN_NIST_REV5_CONTROLS or "SA-12" in WITHDRAWN_NIST_REV5_CONTROLS


def test_is_active_control_filters_blank_and_withdrawn():
    """Verify blank and withdrawn controls return False, while active controls return True."""
    # Active control
    active_ctrl = MockControl("NIST-AC-5", "Separation of Duties", "Define system access authorizations to support separation of duties...")
    assert is_active_control(active_ctrl) is True

    # Withdrawn control with blank text
    withdrawn_ctrl_1 = MockControl("NIST-RA-4", "Risk Assessment Update", "")
    assert is_active_control(withdrawn_ctrl_1) is False

    # Withdrawn control with asterisks / placeholder text
    withdrawn_ctrl_2 = MockControl("NIST-SA-12", "Supply Chain Protection", "**")
    assert is_active_control(withdrawn_ctrl_2) is False

    # Arbitrary empty text control
    blank_ctrl = MockControl("NIST-XX-99", "Unknown", "   ")
    assert is_active_control(blank_ctrl) is False


def test_filter_active_controls():
    """Verify filtering a mixed list leaves only valid, active controls."""
    controls = [
        MockControl("NIST-AC-1", "Access Control Policy", "Develop and document access control policy..."),
        MockControl("NIST-RA-4", "Risk Assessment Update", ""),
        MockControl("NIST-SA-12", "Supply Chain Protection", "**"),
        MockControl("NIST-IA-2", "Identification and Authentication", "The system uniquely identifies and authenticates organizational users..."),
    ]
    active = filter_active_controls(controls)
    assert len(active) == 2
    assert [c.framework_obj_id for c in active] == ["NIST-AC-1", "NIST-IA-2"]
