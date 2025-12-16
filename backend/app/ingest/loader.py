from app.core.oscal import Catalog, Group, Control
from app.core.database import Database
import json

class OSCALGraphLoader:
    def __init__(self, db: Database):
        self.db = db

    def load_catalog(self, catalog: Catalog):
        """
        Loads an OSCAL Catalog into Neo4j.
        Creates Framework, Source, and Requirement nodes.
        """
        framework_id = catalog.metadata.title.replace(" ", "-").upper()
        
        # 1. Create Framework Node
        # We also treat the Catalog as a "Source" or linked to a Source
        # For simplicity, we'll create a Framework node
        query_framework = """
        MERGE (f:Framework {id: $id})
        SET f.name = $title, 
            f.version = $version,
            f.last_modified = $last_modified
        """
        params_framework = {
            "id": framework_id,
            "title": catalog.metadata.title,
            "version": catalog.metadata.version,
            "last_modified": catalog.metadata.last_modified
        }
        self.db.execute_write(query_framework, params_framework, action="CREATE_FRAMEWORK")
        
        # 2. Process Groups (Recursively if needed, but we'll do flat for now)
        for group in catalog.groups:
            self._process_group(group, framework_id)
            
    def _process_group(self, group: Group, framework_id: str):
        # We can create Topic nodes for groups if we want hierarchy
        # For now, let's just create Requirements and link them to Framework
        
        for control in group.controls:
            self._process_control(control, framework_id, group.title)
            
    def _process_control(self, control: Control, framework_id: str, group_title: str):
        # Extract description from props
        description = "No description"
        for prop in control.props:
            if prop.name == "description":
                description = prop.value
                break
                
        query_req = """
        MERGE (r:Requirement {id: $id})
        SET r.title = $title,
            r.description = $description,
            r.group = $group
            
        WITH r
        MATCH (f:Framework {id: $fid})
        MERGE (f)-[:DEFINES]->(r)
        """
        
        params = {
            "id": control.id,
            "title": control.title,
            "description": description,
            "group": group_title,
            "fid": framework_id
        }
        
        self.db.execute_write(query_req, params, action="CREATE_REQUIREMENT")
