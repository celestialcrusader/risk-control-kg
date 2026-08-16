"""
3-Tier Multi-Framework Hierarchy Classifier (Objective vs. Activity) (STORY-FOUNDATION-105).
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HierarchyClassifier:
    """Disambiguates Control Objectives from Granular Activities across all standards."""

    FRAMEWORK_PATTERNS = {
        "NIST_ACT": re.compile(r"^[A-Z]{2}-\d+\(\d+\)"),
        "NIST_OBJ": re.compile(r"^[A-Z]{2}-\d+$"),
        "CIS_ACT": re.compile(r"^(?:CIS\s+)?Safeguard\s+\d+\.\d+", re.IGNORECASE),
        "CIS_OBJ": re.compile(r"^(?:CIS\s+)?Control\s+\d+", re.IGNORECASE),
        "ISO_ACT": re.compile(r"^A\.\d+\.\d+\.\d+"),
        "ISO_OBJ": re.compile(r"^A\.\d+(?:\.\d+)?$"),
        "PCI_ACT": re.compile(r"^\d+\.\d+\.\d+"),
        "PCI_OBJ": re.compile(r"^\d+\.\d+$"),
    }

    def classify(self, node_id: str, prose: str = "", facets: Optional[Dict[str, Any]] = None) -> str:
        """Classify node as 'OBJECTIVE' or 'ACTIVITY'."""
        node_id_clean = node_id.strip()

        # Tier 1: Framework Regex Registry
        for key, pattern in self.FRAMEWORK_PATTERNS.items():
            if pattern.search(node_id_clean):
                if key.endswith("_ACT"):
                    return "ACTIVITY"
                elif key.endswith("_OBJ"):
                    return "OBJECTIVE"

        # Tier 2: AST Dot-Depth
        dots = node_id_clean.count(".")
        if dots >= 2:
            return "ACTIVITY"
        elif dots == 1:
            return "OBJECTIVE"

        # Tier 3: 6-Facet Context Disambiguation
        if facets:
            nature = str(facets.get("control_nature", "")).upper()
            role = str(facets.get("target_role_facet", "")).upper()
            if nature == "PREVENTATIVE" or role in ("SYSTEM_ADMINISTRATOR", "SOC_ANALYST", "OPERATOR"):
                return "ACTIVITY"
            if nature == "GOVERNANCE" or role in ("BOARD_OF_DIRECTORS", "CISO", "COMPLIANCE_OFFICER"):
                return "OBJECTIVE"

        return "OBJECTIVE"
