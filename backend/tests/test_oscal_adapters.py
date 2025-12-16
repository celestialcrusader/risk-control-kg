import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ingest.adapters.csa_ccm import CSACCMAdapter
from app.core.oscal import Catalog, Group, Control

# Path to sample data
SAMPLE_CCM_PATH = "/home/zack/coding/rckg/data/raw/oscal/primary-dataset.json"

@pytest.mark.skipif(not os.path.exists(SAMPLE_CCM_PATH), reason="Sample data not found")
def test_csa_ccm_adapter_parsing():
    """
    Test that CSACCMAdapter can parse the real sample file
    and produces a valid OSCAL Catalog structure.
    """
    adapter = CSACCMAdapter()
    catalog = adapter.to_oscal(SAMPLE_CCM_PATH)
    
    # 1. Check Root
    assert isinstance(catalog, Catalog)
    assert catalog.metadata.title == "Cloud Controls Matrix"
    assert catalog.metadata.version == "4.0.12"
    
    # 2. Check Groups (Domains)
    assert len(catalog.groups) > 0
    first_group = catalog.groups[0]
    assert first_group.id == "A&A"
    assert first_group.title == "Audit & Assurance"
    
    # 3. Check Controls
    # A&A-01 should be in the first group
    assert len(first_group.controls) > 0
    first_control = first_group.controls[0]
    assert first_control.id == "A&A-01"
    assert first_control.title == "Audit and Assurance Policy and Procedures"
    
    # 4. Check Properties (Description mapped to spec)
    desc_prop = next((p for p in first_control.props if p.name == "description"), None)
    assert desc_prop is not None
    assert "Establish, document" in desc_prop.value
