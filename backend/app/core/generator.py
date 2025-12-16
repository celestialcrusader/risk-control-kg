from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.core.database import Database
from app.core.llm import LLMClient

class AuditStep(BaseModel):
    control_id: str
    control_title: str
    test_objective: str
    test_steps: List[str]
    expected_evidence: List[str]

class AuditProgram(BaseModel):
    topic: str
    overview: str
    audit_steps: List[AuditStep]

class AuditGenerator:
    def __init__(self, db: Database, llm: LLMClient):
        self.db = db
        self.llm = llm

    def generate_program(self, topic: str) -> Dict[str, Any]:
        """
        Generates an audit program by finding relevant controls in the graph
        and asking the LLM to define test steps.
        """
        
        # 1. Search Knowledge Graph
        # Find relevant controls where name/description matches topic keywords
        keywords = [w.lower() for w in topic.split() if len(w) > 3]
        if not keywords:
             return {"error": "Topic too short"}
             
        conditions = " OR ".join([f"toLower(n.name) CONTAINS '{k}' OR toLower(n.description) CONTAINS '{k}' OR toLower(n.title) CONTAINS '{k}'" for k in keywords])
        
        # We target Controls and Risks
        cypher = f"""
        MATCH (n)
        WHERE (n:Control OR n:Risk OR n:Requirement) AND ({conditions})
        RETURN n.id as id, n.title as title, n.name as name, n.description as description, labels(n) as labels
        LIMIT 10
        """
        
        results = self.db.execute_read(cypher)
        
        if not results:
             return {
                 "topic": topic,
                 "overview": "No relevant controls found in the knowledge graph.",
                 "audit_steps": []
             }
             
        # 2. Prepare Context for LLM
        context_items = []
        for r in results:
            lbl = r['labels'][0] if r['labels'] else "Entity"
            display_name = r.get('title') or r.get('name') or "Unknown"
            desc = r.get('description', '')
            cid = r.get('id', 'N/A')
            context_items.append(f"ID: {cid} | Type: {lbl} | Name: {display_name} | Description: {desc}")
            
        context_str = "\\n".join(context_items)
        
        # 3. LLM Synthesis using Structured Output
        system_prompt = """
        You are an expert IT Auditor. Create a risk-based audit program based EXCLUSIVELY on the provided Controls/Risks context.
        For each relevant item from the context, define:
        1. Test Objective (what are we verifying?)
        2. Test Steps (step-by-step instructions)
        3. Expected Evidence (logs, configs, screenshots)
        
        Do not hallucinate controls not in the context.
        """
        
        user_prompt = f"""
        Topic: {topic}
        
        Context from Knowledge Graph:
        {context_str}
        
        Generate the audit program.
        """
        
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            program = self.llm.generate_structured(
                prompt=full_prompt,
                response_model=AuditProgram
            )
            return program.model_dump()
        except Exception as e:
            # Fallback if structured generation fails (though it shouldn't with our setup)
            return {
                "topic": topic,
                "overview": f"Error generating program: {str(e)}",
                "audit_steps": []
            }
