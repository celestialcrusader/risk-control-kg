import os
import shutil
from fastapi import UploadFile
from typing import Dict, Any

from app.core.database import Database
from app.core.llm import LLMClient
from app.core.knowledge import KnowledgeExtractor
from app.ingest.enricher import GraphEnricher
from app.ingest.loader import OSCALGraphLoader

from app.ingest.adapters.csa_ccm import CSACCMAdapter
from app.ingest.adapters.nist_csv import NISTCSVAdapter
# Import conditionally if specialized libs missing
try:
    from app.ingest.adapters.docling_pdf import DoclingPDFAdapter
except ImportError:
    DoclingPDFAdapter = None
from app.ingest.adapters.excel import ExcelAdapter

UPLOAD_DIR = "/home/rckg/coding/rckg/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestionService:
    def __init__(self, db: Database, llm: LLMClient):
        self.db = db
        self.llm = llm
        self.loader = OSCALGraphLoader(db)
        self.extractor = KnowledgeExtractor(llm)
        self.enricher = GraphEnricher(db, self.extractor)

    def process_upload(self, file: UploadFile) -> Dict[str, Any]:
        # 1. Save File
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Select Adapter
        ext = file.filename.lower().split('.')[-1]
        adapter = None
        
        if ext == "json":
            # Assume CCM for now
            adapter = CSACCMAdapter()
        elif ext == "csv":
            adapter = NISTCSVAdapter()
        elif ext == "pdf":
            if DoclingPDFAdapter:
                adapter = DoclingPDFAdapter()
            else:
                return {"status": "error", "message": "PDF Support not installed"}
        elif ext in ["xlsx", "xls"]:
            adapter = ExcelAdapter()
        else:
            return {"status": "error", "message": f"Unsupported file type: {ext}"}
            
        # 3. Adapt to OSCAL
        try:
            catalog = adapter.to_oscal(file_path)
        except Exception as e:
            return {"status": "error", "message": f"Parsing failed: {str(e)}"}
            
        # 4. Load to Graph
        try:
            # We don't have return stats from loader yet, maybe just void
            self.loader.load_catalog(catalog)
        except Exception as e:
            return {"status": "error", "message": f"Graph Loading failed: {str(e)}"}
            
        # 5. Enrich (LLM Extraction)
        # This can be slow, might want to be async in real world
        try:
            self.enricher.enrich_catalog(catalog)
        except Exception as e:
            return {"status": "warning", "message": f"Loaded but enrichment failed: {str(e)}"}
            
        return {
            "status": "success",
            "filename": file.filename,
            "catalog_title": catalog.metadata.title,
            "controls_processed": len(catalog.controls) + sum(len(g.controls) for g in catalog.groups)
        }
