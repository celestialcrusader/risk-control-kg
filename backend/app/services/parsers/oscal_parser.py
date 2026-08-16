"""
OSCAL 1.1.3 YAML Catalog Parser for NIST SP 800-53 Rev 5.2.0.
"""

import yaml
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Attempt to use C-accelerated YAML loader if available
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


class OscalYamlCatalogParser:
    """Parses OSCAL YAML compliance catalogs into RCKG Framework Nodes."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def _extract_prose_from_parts(self, parts: List[Dict[str, Any]]) -> str:
        """Recursively collect prose text from OSCAL parts hierarchy."""
        prose_segments = []
        for part in parts or []:
            if isinstance(part, dict):
                if "prose" in part and part["prose"]:
                    prose_segments.append(str(part["prose"]).strip())
                if "parts" in part and isinstance(part["parts"], list):
                    nested = self._extract_prose_from_parts(part["parts"])
                    if nested:
                        prose_segments.append(nested)
        return "\n".join(filter(None, prose_segments))

    def parse(self) -> Dict[str, List[Dict[str, Any]]]:
        """Stream and parse OSCAL YAML into Framework Control Objectives and Activities."""
        logger.info("Opening OSCAL YAML file: %s", self.file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=SafeLoader)

        catalog = data.get("catalog", {}) if isinstance(data, dict) else {}
        metadata = catalog.get("metadata", {})
        fw_name = metadata.get("title", "NIST SP 800-53")
        fw_version = str(metadata.get("version", "Rev 5"))

        objectives = []
        activities = []
        edges = []

        groups = catalog.get("groups", [])
        for group in groups:
            for ctrl in group.get("controls", []):
                ctrl_id = str(ctrl.get("id", "")).upper()
                ctrl_title = str(ctrl.get("title", ctrl_id))
                ctrl_text = self._extract_prose_from_parts(ctrl.get("parts", []))

                obj_id = f"NIST-{ctrl_id}"
                objectives.append({
                    "framework_obj_id": obj_id,
                    "framework_name": "NIST SP 800-53",
                    "framework_version": fw_version,
                    "objective_name": ctrl_title,
                    "objective_text": ctrl_text,
                })

                # Process child control enhancements
                for sub_ctrl in ctrl.get("controls", []):
                    sub_id = str(sub_ctrl.get("id", "")).upper()
                    sub_title = str(sub_ctrl.get("title", sub_id))
                    sub_text = self._extract_prose_from_parts(sub_ctrl.get("parts", []))

                    act_id = f"NIST-{sub_id}"
                    activities.append({
                        "framework_act_id": act_id,
                        "framework_name": "NIST SP 800-53",
                        "framework_version": fw_version,
                        "activity_name": sub_title,
                        "activity_text": sub_text,
                    })

                    edges.append({
                        "source_id": obj_id,
                        "target_id": act_id,
                        "relation": "REFINES",
                        "is_golden": True,
                        "status": "HUMAN_ATTESTED",
                    })

        logger.info("Parsed %d objectives, %d activities from OSCAL YAML", len(objectives), len(activities))
        return {
            "nodes": objectives + activities,
            "objectives": objectives,
            "activities": activities,
            "edges": edges,
        }
