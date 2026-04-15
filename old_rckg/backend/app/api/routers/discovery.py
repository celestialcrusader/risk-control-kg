from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.database import Database
from app.core.llm import LLMClient
from app.core.discovery import LinkageDiscoverer

router = APIRouter()

class DiscoveryRequest(BaseModel):
    source_framework_id: str
    target_framework_id: str

@router.post("/map")
def discover_mappings(request: DiscoveryRequest):
    """
    Triggers AI discovery of relationships between two frameworks.
    Creates DRAFT links in the graph.
    """
    db = Database()
    db.connect()
    llm = LLMClient()
    discoverer = LinkageDiscoverer(db, llm)
    
    try:
        result = discoverer.discover_mappings(request.source_framework_id, request.target_framework_id)
        db.close()
        return result
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))
