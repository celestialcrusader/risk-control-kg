"""
Parser for MIT TASRA AI Risk Database and Threat Inventories (STORY-FOUNDATION-103).
"""

import openpyxl
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class RiskCatalogParser:
    """Parses Risk Databases into RCKG RiskNode entities."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse(self) -> List[Dict[str, Any]]:
        wb = openpyxl.load_workbook(self.file_path, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))

        # Dynamically locate the header row (matching 'Title' or 'Ev_ID')
        header_idx = None
        for idx, row in enumerate(rows[:10]):
            row_str = [str(c).lower() for c in row if c is not None]
            if "title" in row_str and ("ev_id" in row_str or "quickref" in row_str):
                header_idx = idx
                break

        if header_idx is None:
            header_idx = 2  # Default to Row 3 (0-indexed 2)

        risks = []
        header = [str(c).lower().strip() if c is not None else "" for c in rows[header_idx]]
        
        title_idx = next((i for i, h in enumerate(header) if "title" in h), 0)
        quickref_idx = next((i for i, h in enumerate(header) if "quickref" in h), 1)
        ev_id_idx = next((i for i, h in enumerate(header) if "ev_id" in h), 2)
        cat_idx = next((i for i, h in enumerate(header) if "category level" in h or "category" in h), None)
        if cat_idx is None:
            cat_idx = next((i for i, h in enumerate(header) if "cat_id" in h), 7)


        for row in rows[header_idx + 1:]:
            if not row or len(row) <= title_idx or not row[title_idx]:
                continue
            title = str(row[title_idx]).strip()
            # Skip duplicated header
            if title.lower() == "title":
                continue

            quick_ref = str(row[quickref_idx]).strip() if len(row) > quickref_idx and row[quickref_idx] else "RISK"
            ev_id = str(row[ev_id_idx]).strip() if len(row) > ev_id_idx and row[ev_id_idx] else quick_ref
            category = str(row[cat_idx]).strip() if len(row) > cat_idx and row[cat_idx] else "OPERATIONAL"

            risks.append({
                "risk_id": f"RISK-{ev_id}",
                "risk_name": title,
                "description": title,
                "category": category,
                "severity_level": "MEDIUM",
            })

        logger.info("RiskCatalogParser extracted %d risks from %s", len(risks), self.file_path)
        return risks
