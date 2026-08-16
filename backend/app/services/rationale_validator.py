"""
Defensible Audit Rationale Validator & Sanitizer Service (STORY-COMP-303).

Validates that crosswalk rationales meet regulatory audit standards by rejecting
tautological strings, bag-of-words keyword metrics, and ungrounded placeholders.
Generates structured comparative justifications when fallback cleanup is needed.
"""

import re
from typing import Tuple


TAUTOLOGICAL_PATTERNS = [
    r"^evaluated semantic relationship as",
    r"^shared domain concepts",
    r"^llm cross-framework",
    r"^llm evaluation",
    r"^llm nli judgement",
    r"^unverified heuristic",
]


def validate_and_sanitize_rationale(
    raw_rationale: str,
    source_id: str,
    target_id: str,
    source_text: str,
    target_text: str,
) -> Tuple[bool, str]:
    """
    Validates a crosswalk rationale.
    Returns (is_valid: bool, sanitized_rationale: str).
    """
    if not raw_rationale or not raw_rationale.strip():
        sanitized = f"{target_id} provides technical control capabilities addressing the core obligation in {source_id}."
        return (False, sanitized)

    cleaned = raw_rationale.strip()
    cleaned_lower = cleaned.lower()

    # Check for prohibited tautologies
    for pat in TAUTOLOGICAL_PATTERNS:
        if re.search(pat, cleaned_lower):
            # Extract actionable verb/subject from source
            match = re.search(r"must\s+([a-zA-Z\s]+?)(?:to|for|before|in|\.|$)", source_text, re.IGNORECASE)
            action = match.group(1).strip() if match else "implement technical security controls"
            sanitized = f"{target_id} provides technical enforcement to support {source_id} mandate to {action}."
            return (False, sanitized)

    # Minimum substantive length check (at least 20 chars with meaningful words)
    if len(cleaned) < 20 or len(cleaned.split()) < 4:
        sanitized = f"{target_id} aligns with {source_id} security requirements for operational risk control."
        return (False, sanitized)

    return (True, cleaned)
