"""
Catalog Sanitizer & Inactive/Withdrawn Control Filter (STORY-COMP-202).

Prevents withdrawn or blank framework controls (e.g. NIST SP 800-53 Rev 5 withdrawn controls)
from entering candidate retrieval indexes or being matched against empty text.
"""
from typing import List, Any, Set

# Formal NIST SP 800-53 Rev 5 Withdrawn Controls (folded into other controls or carved out)
WITHDRAWN_NIST_REV5_CONTROLS: Set[str] = {
    # Access Control (AC)
    "AC-13", "NIST-AC-13", "AC-15", "NIST-AC-15",
    # Audit & Accountability (AU)
    "AU-13", "NIST-AU-13", "AU-15", "NIST-AU-15",
    # Identification & Authentication (IA)
    "IA-10", "NIST-IA-10",
    # Risk Assessment (RA)
    "RA-4", "NIST-RA-4",  # Folded into RA-3 (Risk Assessment)
    # System & Services Acquisition (SA)
    "SA-12", "NIST-SA-12",  # Withdrawn and moved to SR (Supply Chain Risk Management) family
    "SA-13", "NIST-SA-13", "SA-14", "NIST-SA-14",
    # System & Communications Protection (SC)
    "SC-9", "NIST-SC-9", "SC-14", "NIST-SC-14",
    # System & Information Integrity (SI)
    "SI-9", "NIST-SI-9", "SI-13", "NIST-SI-13", "SI-14", "NIST-SI-14", "SI-15", "NIST-SI-15",
    # Program Management (PM)
    "PM-17", "NIST-PM-17", "PM-18", "NIST-PM-18",
}


def is_active_control(control: Any) -> bool:
    """
    Validates if a framework control is active and has sufficient normative text.
    Returns False if control is known to be withdrawn or has blank/placeholder text.
    """
    ctrl_id = getattr(control, "framework_obj_id", "") or ""
    # 1. Check if ID in known withdrawn list
    if ctrl_id in WITHDRAWN_NIST_REV5_CONTROLS:
        return False
    # Also check without prefix if prefixed
    bare_id = ctrl_id.replace("NIST-", "").strip()
    if bare_id in WITHDRAWN_NIST_REV5_CONTROLS:
        return False

    # 2. Check for empty, whitespace, or placeholder text
    raw_text = (getattr(control, "objective_text", "") or "").strip()
    if len(raw_text) < 15:
        return False
    # Check if text is only asterisks or punctuation placeholders
    if set(raw_text).issubset({"*", "-", " ", "_", ".", ":"}):
        return False

    return True


def filter_active_controls(controls: List[Any]) -> List[Any]:
    """Filters a list of controls to only those that are active and have valid normative text."""
    return [c for c in controls if is_active_control(c)]
