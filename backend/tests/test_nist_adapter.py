import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ingest.adapters.nist_csv import NISTCSVAdapter
from app.core.oscal import Catalog, Group, Control

SAMPLE_CSV_PATH = "/home/zack/coding/rckg/data/raw/csv/sp800-53r5-control-catalog.csv"

@pytest.mark.skipif(not os.path.exists(SAMPLE_CSV_PATH), reason="Sample data not found")
def test_nist_csv_adapter_parsing():
    """
    Test that NISTCSVAdapter can parse the real sample CSV file.
    """
    adapter = NISTCSVAdapter()
    catalog = adapter.to_oscal(SAMPLE_CSV_PATH)
    
    # 1. Check Root
    assert isinstance(catalog, Catalog)
    assert catalog.metadata.title == "NIST SP 800-53 Rev 5"
    
    # 2. Check Groups
    # We expect groups like "Policy and Procedures", etc. from the "ctrl_grp" column
    assert len(catalog.groups) > 0
    
    # Find a specific group, e.g., "Policy and Procedures" or matching the sample head
    # Sample head had "Policy and Procedures" in ctrl_grp for AC-1
    pp_group = next((g for g in catalog.groups if "Policy and Procedures" in g.title), None)
    assert pp_group is not None
    
    # 3. Check Controls
    # AC-1 should be in this group
    ac1 = next((c for c in pp_group.controls if c.id == "AC-1"), None)
    assert ac1 is not None
    assert "access control policy" in ac1.props[0].value
