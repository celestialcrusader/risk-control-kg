import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Conditional import
try:
    from app.ingest.adapters.docling_pdf import DoclingPDFAdapter
    from app.core.oscal import Catalog
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

SAMPLE_PDF_PATH = "data/raw/pdf/NIST.AI.600-1.pdf"

@pytest.mark.skipif(not DOCLING_AVAILABLE, reason="Docling not installed")
@pytest.mark.skipif(not os.path.exists(SAMPLE_PDF_PATH), reason="Sample PDF not found")
def test_docling_pdf_adapter():
    """
    Test successful parsing of NIST PDF into OSCAL Catalog.
    """
    adapter = DoclingPDFAdapter()
    catalog = adapter.to_oscal(SAMPLE_PDF_PATH)
    
    assert isinstance(catalog, Catalog)
    assert "NIST.AI.600-1.pdf" in catalog.metadata.title
    
    # Check that we got controls (chunks)
    assert len(catalog.controls) > 0
    
    # Check for some expected content from NIST AI RMF
    # e.g., "Generative AI", "Risk", "Governance"
    content_found = False
    for ctrl in catalog.controls:
        desc = ctrl.props[0].value
        if "generative ai" in desc.lower() or "risk" in desc.lower():
            content_found = True
            break
            
    assert content_found, "Did not find expected keywords in parsed content"
