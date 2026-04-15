from typing import List, Dict, Any
from app.core.database import Database
from app.core.llm import LLMClient

class LinkageDiscoverer:
    def __init__(self, db: Database, llm: LLMClient):
        self.db = db
        self.llm = llm

    def discover_mappings(self, source_fw_id: str, target_fw_id: str) -> Dict[str, Any]:
        """
        Discovers mappings between two frameworks.
        Iterates source controls -> Finds best match in target -> Creates DRAFT link.
        """
        
        # 1. Get Source Controls
        # We limit to 10 for prototype performance
        source_query = """
        MATCH (f:Framework {id: $fid})-[:DEFINES]->(r:Requirement)
        RETURN r.id, r.title, r.description
        LIMIT 10
        """
        source_controls = self.db.execute_read(source_query, {"fid": source_fw_id})
        
        if not source_controls:
            return {"status": "error", "message": "No source controls found"}

        # 2. Get Target Controls (Candidate Pool)
        target_query = """
        MATCH (f:Framework {id: $fid})-[:DEFINES]->(r:Requirement)
        RETURN r.id, r.title, r.description
        """
        target_controls = self.db.execute_read(target_query, {"fid": target_fw_id})
        
        if not target_controls:
            return {"status": "error", "message": "No target controls found"}
            
        mapped_count = 0
        
        # 3. For each source, find best match
        # We use a simplified LLM approach: "Which of these targets matches this source?"
        # Optimization: We should use embeddings for scale, but for 10 items, LLM selection is fine.
        
        # Prepare target summary for context
        target_summaries = [f"ID: {t['r.id']} | Title: {t['r.title']} | Desc: {t.get('r.description', '')[:100]}" for t in target_controls]
        target_context = "\\n".join(target_summaries[:20]) # Limit context window
        
        for src in source_controls:
            s_id = src['r.id']
            s_title = src['r.title']
            s_desc = src.get('r.description', '')
            
            prompt = f"""
            Task: Map the Source Control to the Best Matching Target Control.
            
            Source Control:
            ID: {s_id}
            Title: {s_title}
            Description: {s_desc}
            
            Target Candidates:
            {target_context}
            
            Instructions:
            - Identify the single best matching Target Control ID.
            - If no strong match exists, output "NONE".
            - Provide a brief rationale.
            - Output format: "MATCH: <Target_ID> | RATIONALE: <text>"
            """
            
            try:
                response = self.llm.generate(prompt)
                if "MATCH:" in response and "NONE" not in response:
                    # Parse ID
                    parts = response.split("|")
                    match_part = parts[0].replace("MATCH:", "").strip()
                    rationale = parts[1].replace("RATIONALE:", "").strip() if len(parts) > 1 else "AI proposed match"
                    
                    target_id = match_part
                    
                    # 4. Create Draft Link
                    link_query = """
                    MATCH (s:Requirement {id: $sid})
                    MATCH (t:Requirement {id: $tid})
                    MERGE (s)-[rel:RELATED_TO]->(t)
                    SET rel.status = 'DRAFT',
                        rel.rationale = $rationale,
                        rel.confidence = 'high'
                    """
                    self.db.execute_write(link_query, {
                        "sid": s_id,
                        "tid": target_id,
                        "rationale": rationale
                    }, action="CREATE_DRAFT_LINK")
                    
                    mapped_count += 1
                    
            except Exception as e:
                print(f"Error mapping {s_id}: {e}")
                continue
                
        return {
            "status": "success",
            "source_framework": source_fw_id,
            "target_framework": target_fw_id,
            "mappings_proposed": mapped_count
        }
