import json
import uuid
from datetime import datetime
from typing import List

from app.ingest.adapters.base import BaseAdapter
from app.core.oscal import Catalog, Group, Control, Metadata, Property, Link

class CSACCMAdapter(BaseAdapter):
    def to_oscal(self, file_path: str) -> Catalog:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Metadata extraction
        metadata = Metadata(
            title=data.get("name", "Unknown Catalog"),
            **{"last-modified": datetime.now().isoformat()},
            version=data.get("version", "1.0"),
            **{"oscal-version": "1.0.0"},
            links=[Link(href=data.get("url", ""))] if data.get("url") else []
        )
        
        groups = []
        
        # CCM structure: "domains" -> [ { "id", "title", "controls": [...] } ]
        for domain in data.get("domains", []):
            controls = []
            for ctrl in domain.get("controls", []):
                # Map control
                c = Control(
                    id=ctrl.get("id"),
                    title=ctrl.get("title"),
                    props=[
                        Property(name="description", value=ctrl.get("specification", "")),
                        Property(name="is_lite", value=str(ctrl.get("is_lite", False)))
                    ]
                )
                controls.append(c)
                
            # Map domain to Group
            g = Group(
                id=domain.get("id"),
                title=domain.get("title"),
                controls=controls
            )
            groups.append(g)
            
        return Catalog(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            groups=groups,
            controls=[] # CCM has grouped controls, so they go in groups
        )
