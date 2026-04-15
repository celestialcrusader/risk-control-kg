import openpyxl
import uuid
from datetime import datetime
from typing import List, Dict

from app.ingest.adapters.base import BaseAdapter
from app.core.oscal import Catalog, Group, Control, Metadata, Property

class ExcelAdapter(BaseAdapter):
    def to_oscal(self, file_path: str) -> Catalog:
        groups: Dict[str, Group] = {}
        controls = []
        
        # Open workbook
        wb = openpyxl.load_workbook(file_path, read_only=True)
        # Use active sheet
        ws = wb.active
        
        # Iterate rows. We assume header is row 1
        # Simple heuristic: Look for columns "Control ID", "Domain", "Control Title", "Description" or similar
        # For now, simplistic mapping based on user sample (often col 0=ID, 1=Title/Desc)
        
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return Catalog(uuid=str(uuid.uuid4()), metadata=Metadata(title="Empty Excel", version="1.0", last_modified=datetime.now().isoformat(), oscal_version="1.0.0"))
            
        header = [str(h).lower() for h in rows[0]]
        
        # Try to find index of key columns
        try:
            id_idx = next(i for i, h in enumerate(header) if "id" in h or "code" in h)
        except StopIteration:
            id_idx = 0 # Default to first col
            
        try:
            desc_idx = next(i for i, h in enumerate(header) if "desc" in h or "specification" in h or "text" in h)
        except StopIteration:
            desc_idx = 1 # Default
            
        try:
            group_idx = next(i for i, h in enumerate(header) if "domain" in h or "category" in h or "group" in h)
        except StopIteration:
            group_idx = None

        for row in rows[1:]:
            if not row or not row[id_idx]:
                continue
                
            ctrl_id = str(row[id_idx]).strip()
            desc = str(row[desc_idx]) if len(row) > desc_idx else ""
            
            c = Control(
                id=ctrl_id,
                title=f"Control {ctrl_id}",
                props=[Property(name="description", value=desc)]
            )
            
            if group_idx is not None and len(row) > group_idx and row[group_idx]:
                grp_title = str(row[group_idx]).strip()
                if grp_title not in groups:
                    groups[grp_title] = Group(id=grp_title.replace(" ", "_"), title=grp_title, controls=[])
                groups[grp_title].controls.append(c)
            else:
                controls.append(c)
                
        # Combine grouped and flat controls
        final_groups = list(groups.values())
        
        metadata = Metadata(
            title=f"Imported Excel: {file_path.split('/')[-1]}",
            **{"last-modified": datetime.now().isoformat()},
            version="1.0",
            **{"oscal-version": "1.0.0"}
        )
        
        return Catalog(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            groups=final_groups,
            controls=controls
        )
