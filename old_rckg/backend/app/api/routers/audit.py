from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.core.database import Database
from app.core.llm import LLMClient
from app.core.generator import AuditGenerator

router = APIRouter()

class AuditGenRequest(BaseModel):
    topic: str

def get_generator():
    db = Database()
    db.connect()
    llm = LLMClient()
    return AuditGenerator(db=db, llm=llm)

@router.post("/generate")
def generate_audit_program(request: AuditGenRequest):
    """
    Generates a structured audit program for the given topic.
    """
    # Manual DI to ensure explicit control for now
    db = Database()
    db.connect()
    llm = LLMClient()
    generator = AuditGenerator(db, llm)
    
    try:
        result = generator.generate_program(request.topic)
        db.close()
        return result
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))
