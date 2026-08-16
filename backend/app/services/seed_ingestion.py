"""
Compliance Seed Ingestion Service for Pure RCKG Baseline Graph (v1.0.0).

Parses official NIST OLIR XML exports and CSA CCM v4 Excel workbooks according to docs/03-mvp/nist-olir-schema-mapping.md.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.rckg_nodes import (
    FrameworkControlObjectiveNode,
    FrameworkControlActivityNode,
    ControlObjectiveFrameworkMapping,
    SetTheoryRelation,
)

logger = logging.getLogger(__name__)


class NistOlirXmlParser:
    """Parser for official NIST OLIR XML crosswalk files."""

    def __init__(self, xml_filepath: str):
        self.filepath = xml_filepath

    def _find_child(self, elem: ET.Element, tag_name: str) -> ET.Element:
        """Find child element ignoring XML namespaces."""
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag.lower() == tag_name.lower():
                return child
        return None

    def _find_text(self, elem: ET.Element, tag_name: str, default: str = "") -> str:
        """Extract text from child element ignoring XML namespaces."""
        child = self._find_child(elem, tag_name)
        if child is not None and child.text:
            return child.text.strip()
        return default

    def parse(self) -> Dict[str, List[Dict[str, Any]]]:
        tree = ET.parse(self.filepath)
        root = tree.getroot()
        nodes, edges = [], []
        seen_nodes = set()

        # Find all InformativeReference tags regardless of namespace
        ref_elements = [
            elem for elem in root.iter() 
            if (elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag).lower() == "informativereference"
        ]

        for ref in ref_elements:
            focal = self._find_child(ref, "FocalDocument")
            referenced = self._find_child(ref, "ReferencedDocument")

            if focal is None or referenced is None:
                continue

            focal_id = self._find_text(focal, "Identifier")
            focal_doc = self._find_text(focal, "DocumentIdentifier", "NIST SP 800-53")
            focal_text = self._find_text(focal, "Description", "")
            focal_title = self._find_text(focal, "Title", focal_id)

            if focal_id and focal_id not in seen_nodes:
                nodes.append({
                    "framework_obj_id": focal_id,
                    "framework_name": focal_doc,
                    "framework_version": "Rev 5",
                    "objective_name": focal_title,
                    "objective_text": focal_text,
                })
                seen_nodes.add(focal_id)

            ref_id = self._find_text(referenced, "Identifier")
            ref_doc = self._find_text(referenced, "DocumentIdentifier", "ISO/IEC 27001")
            ref_text = self._find_text(referenced, "Description", "")
            ref_title = self._find_text(referenced, "Title", ref_id)

            if ref_id and ref_id not in seen_nodes:
                nodes.append({
                    "framework_obj_id": ref_id,
                    "framework_name": ref_doc,
                    "framework_version": "2022",
                    "objective_name": ref_title,
                    "objective_text": ref_text,
                })
                seen_nodes.add(ref_id)

            if focal_id and ref_id:
                edges.append({
                    "source_id": focal_id,
                    "target_id": ref_id,
                    "relation": SetTheoryRelation.EQUIVALENT_TO.value,
                    "is_golden": True,
                    "status": "HUMAN_ATTESTED",
                })

        return {"nodes": nodes, "edges": edges}


class CcmExcelParser:
    """Parser for Cloud Security Alliance (CSA) Cloud Controls Matrix (CCM v4) Excel files."""

    def __init__(self, excel_filepath: str):
        self.filepath = excel_filepath

    def parse(self) -> Dict[str, List[Dict[str, Any]]]:
        nodes, edges = [], []
        try:
            import openpyxl
            wb = openpyxl.load_workbook(self.filepath, data_only=True)
            sheet = wb.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row and len(row) >= 3 and row[0]:
                    ctrl_id = str(row[0])
                    ctrl_title = str(row[1]) if len(row) > 1 else ctrl_id
                    ctrl_text = str(row[2]) if len(row) > 2 else ""
                    nodes.append({
                        "framework_obj_id": f"CCM-{ctrl_id}",
                        "framework_name": "CSA CCM",
                        "framework_version": "v4",
                        "objective_name": ctrl_title,
                        "objective_text": ctrl_text,
                    })
        except Exception as e:
            logger.warning(f"openpyxl failed to parse {self.filepath}: {e}")

        return {"nodes": nodes, "edges": edges}


class ComplianceSeedIngester:
    """Orchestrates seed data ingestion into SQLModel ORM and Memgraph graph store."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def ingest_file(self, source_type: str, file_path: str) -> Dict[str, int]:
        if source_type == "NIST_OLIR":
            parser = NistOlirXmlParser(file_path)
        elif source_type == "CSA_CCM":
            parser = CcmExcelParser(file_path)
        elif source_type == "NIST_OSCAL_YAML":
            from app.services.parsers.oscal_parser import OscalYamlCatalogParser
            parser = OscalYamlCatalogParser(file_path)
        else:
            raise ValueError(f"Unsupported seed source type: {source_type}")

        parsed_data = parser.parse()

        node_count = 0
        # If parser provided pre-separated objectives and activities, use them directly
        if "objectives" in parsed_data and "activities" in parsed_data:
            for obj in parsed_data["objectives"]:
                db_obj = FrameworkControlObjectiveNode(
                    framework_obj_id=obj["framework_obj_id"],
                    framework_name=obj["framework_name"],
                    framework_version=obj["framework_version"],
                    objective_name=obj["objective_name"],
                    objective_text=obj["objective_text"],
                )
                self.db.merge(db_obj)
                node_count += 1

            for act in parsed_data["activities"]:
                db_act = FrameworkControlActivityNode(
                    framework_act_id=act["framework_act_id"],
                    framework_name=act["framework_name"],
                    framework_version=act["framework_version"],
                    activity_name=act["activity_name"],
                    activity_text=act["activity_text"],
                )
                self.db.merge(db_act)
                node_count += 1
        else:
            for n in parsed_data.get("nodes", []):
                node_id = n.get("framework_obj_id") or n.get("framework_act_id", "")
                if ("(" in node_id and ")" in node_id) or n.get("is_activity"):
                    db_node = FrameworkControlActivityNode(
                        framework_act_id=node_id,
                        framework_name=n["framework_name"],
                        framework_version=n["framework_version"],
                        activity_name=n.get("activity_name") or n.get("objective_name", ""),
                        activity_text=n.get("activity_text") or n.get("objective_text", ""),
                    )
                else:
                    db_node = FrameworkControlObjectiveNode(
                        framework_obj_id=node_id,
                        framework_name=n["framework_name"],
                        framework_version=n["framework_version"],
                        objective_name=n["objective_name"],
                        objective_text=n["objective_text"],
                    )
                self.db.merge(db_node)
                node_count += 1


        edge_count = 0
        for e in parsed_data.get("edges", []):
            try:
                rel = e.get("relation", "EQUIVALENT_TO")
                rel_enum = SetTheoryRelation[rel] if rel in SetTheoryRelation.__members__ else SetTheoryRelation.EQUIVALENT_TO
            except Exception:
                rel_enum = SetTheoryRelation.EQUIVALENT_TO

            import uuid
            co_raw = e.get("control_objective_id") or e.get("source_id")
            try:
                co_uuid = uuid.UUID(str(co_raw))
            except Exception:
                co_uuid = uuid.uuid4()

            fo_raw = e.get("framework_objective_id") or e.get("target_id")
            try:
                fo_uuid = uuid.UUID(str(fo_raw))
            except Exception:
                fo_uuid = uuid.uuid4()

            db_edge = ControlObjectiveFrameworkMapping(
                control_objective_id=co_uuid,
                framework_objective_id=fo_uuid,
                set_theory_relation=rel_enum,
                status=e.get("status", "HUMAN_ATTESTED"),
                is_golden_assertion="TRUE" if e.get("is_golden", True) else "FALSE",
            )
            self.db.merge(db_edge)
            edge_count += 1

        self.db.commit()

        logger.info(f"Ingested {node_count} seed framework nodes and {edge_count} seed edges.")
        return {"nodes": node_count, "edges": edge_count}
