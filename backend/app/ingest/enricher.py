from app.core.database import Database
from app.core.knowledge import KnowledgeExtractor
from app.core.oscal import Control, Catalog

class GraphEnricher:
    def __init__(self, db: Database, extractor: KnowledgeExtractor):
        self.db = db
        self.extractor = extractor

    def enrich_catalog(self, catalog: Catalog):
        """
        Iterates through the catalog and enriches each control with LLM-extracted entities.
        """
        for group in catalog.groups:
            for control in group.controls:
                self.enrich_control(control)
        
        # Also process top-level controls if any
        for control in catalog.controls:
            self.enrich_control(control)

    def enrich_control(self, control: Control):
        valid_labels = ["Risk", "Control", "Definition", "Actor", "System"]
        
        knowledge = self.extractor.extract_from_control(control)
        
        if not knowledge or not knowledge.entities:
            return

        for entity in knowledge.entities:
            # Sanitize label
            label = entity.type if entity.type in valid_labels else "Entity"
            
            # Cypher to merge entity and link to Requirement
            query = f"""
            MERGE (e:{label} {{name: $name}})
            ON CREATE SET e.description = $desc, e.status = 'DRAFT'
            ON MATCH SET e.description = $desc
            
            WITH e
            MATCH (r:Requirement {{id: $req_id}})
            MERGE (e)-[:MENTIONED_IN {{confidence: 'high'}}]->(r)
            """
            
            params = {
                "name": entity.name,
                "desc": entity.description,
                "req_id": control.id
            }
            
            # Use execute_write (which also logs audit)
            # We use a generic action name
            self.db.execute_write(query, params, action=f"ENRICH_{label.upper()}")
