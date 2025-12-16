from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Dict, Any

from app.core.database import Database
from app.core.llm import LLMClient
from app.ingest.service import IngestionService

router = APIRouter()

@router.post("/", summary="Ingest Document")
def ingest_document(file: UploadFile = File(...)):
    """
    Uploads and processes a document (PDF, CSV, JSON, XLSX).
    1. Saves file.
    2. Detects type and parses to OSCAL.
    3. Loads to Graph.
    4. Enriches via LLM.
    """
    
    # Simple DI manually for now
    db = Database()
    db.connect()
    llm = LLMClient()
    
    service = IngestionService(db, llm)
    
    try:
        result = service.process_upload(file)
        db.close()
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))
