import csv
import uuid
from datetime import datetime
from typing import List, Dict

from app.ingest.adapters.base import BaseAdapter
from app.core.oscal import Catalog, Group, Control, Metadata, Property

class NISTCSVAdapter(BaseAdapter):
    def to_oscal(self, file_path: str) -> Catalog:
        groups: Dict[str, Group] = {}
        
        # NIST CSVs often use CP1252 (Windows) encoding for smart quotes
        with open(file_path, 'r', encoding='cp1252') as f:
            # Normalize headers
            reader = csv.DictReader(f)
            # We can't easily change fieldnames after init in DictReader, 
            # so we handle it by normalizing access
            
            for row in reader:
                # Normalize keys: strip whitespace, remove potential BOM artifact
                row = {k.strip().lstrip('\ufeff'): v for k, v in row.items() if k}
                
                # Expected columns: "nist_ctrl_id", "ctrl_grp", "ctrl_txt"
                
                group_title = row.get("ctrl_grp", "Uncategorized")
                
                # Check if group exists, else create
                if group_title not in groups:
                    groups[group_title] = Group(
                        id=group_title.replace(" ", "_").lower(), # simple ID generation
                        title=group_title,
                        controls=[]
                    )
                
                # Create Control
                ctrl_id = row.get("nist_ctrl_id", "").strip()
                if not ctrl_id:
                    continue
                    
                c = Control(
                    id=ctrl_id,
                    title=f"NIST Control {ctrl_id}", # CSV doesn't have explicit title per control, usually
                    props=[
                        Property(name="description", value=row.get("ctrl_txt", ""))
                    ]
                )
                
                groups[group_title].controls.append(c)
        
        # Metadata
        metadata = Metadata(
            title="NIST SP 800-53 Rev 5",
            **{"last-modified": datetime.now().isoformat()},
            version="Rev 5",
            **{"oscal-version": "1.0.0"}
        )
        
        return Catalog(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            groups=list(groups.values()),
            controls=[]
        )
