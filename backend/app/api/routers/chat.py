from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import Database
from app.core.llm import LLMClient
from app.core.rag import GraphRAG

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[str]

def get_rag():
    # Dependency injection for RAG
    # We create new instances for now, connection pooling handled in Database
    db = Database()
    db.connect()
    llm = LLMClient() 
    return GraphRAG(db, llm)

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Manually create dependencies inside to ensure clean close or rely on garbage collection?
        # Ideally usage of Depends() but get_rag is complex with closing DB.
        # Let's use context manager approach inside the handler for safety, 
        # or rely on Database class handling its own pool?
        # Database.connect() just creates driver. 
        # Let's instantiate normally.
        
        db = Database()
        db.connect()
        llm = LLMClient()
        rag = GraphRAG(db, llm)
        
        result = rag.query(request.message)
        db.close()
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
