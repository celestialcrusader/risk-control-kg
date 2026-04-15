from typing import List, Dict, Any
from app.core.database import Database
from app.core.llm import LLMClient

class GraphRAG:
    def __init__(self, db: Database, llm: LLMClient):
        self.db = db
        self.llm = llm

    def query(self, user_message: str) -> Dict[str, Any]:
        """
        1. Extract keywords.
        2. Find relevant nodes.
        3. Generate answer.
        """
        # 1. Simple Keyword Extraction (v1)
        # Split, lower, remove short words
        keywords = [w.lower() for w in user_message.split() if len(w) > 3]
        
        if not keywords:
             return {"response": "I didn't capture enough context. Can you be more specific?", "sources": []}

        # 2. Graph Retrieval
        # Find nodes where name or description contains keywords
        # We limit to 5 most relevant nodes to fit in context
        
        # Construct dynamic OR clause
        conditions = " OR ".join([f"toLower(n.name) CONTAINS '{k}' OR toLower(n.description) CONTAINS '{k}'" for k in keywords])
        
        cypher = f"""
        MATCH (n)
        WHERE {conditions}
        RETURN n.name as name, n.description as description, labels(n) as labels
        LIMIT 10
        """
        
        results = self.db.execute_read(cypher)
        
        if not results:
             return {"response": "I couldn't find any relevant information in the knowledge graph.", "sources": []}
             
        # Format Context
        context_lines = []
        sources = []
        for r in results:
            name = r.get('name') or "Unknown"
            desc = r.get('description', '')
            lbl = r['labels'][0] if r['labels'] else "Entity"
            context_lines.append(f"- [{lbl}] {name}: {desc}")
            if name and name != "Unknown":
                sources.append(name)
            
        context_str = "\\n".join(context_lines)
        
        # 3. LLM Synthesis
        prompt = f"""
        You are an expert compliance assistant. Use the provided context to answer the user's question.
        If the context doesn't contain the answer, say "I don't have enough information."
        
        Context from Knowledge Graph:
        {context_str}
        
        User Question: "{user_message}"
        
        Answer:
        """
        
        try:
            answer = self.llm.generate(prompt)
        except Exception as e:
            print(f"RAG ERROR: {str(e)}")
            answer = f"I encountered an error generating the response: {str(e)}"
            
        return {
            "response": answer,
            "sources": list(set(sources))
        }
