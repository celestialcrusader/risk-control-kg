"""
TDD Unit Test for CFIX-303: Reconcile Hardcoded bolt://localhost with Centralized Factory.
"""

import os
import subprocess
import pytest


def test_no_hardcoded_bolt_localhost_in_app_directory():
    """Verify zero hardcoded 'bolt://localhost' strings exist in backend/app/ source code."""
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    
    cmd = ["grep", "-rn", "bolt://localhost", app_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Filter out core/memgraph.py default fallback if present
    matches = [line for line in result.stdout.splitlines() if "app/core/memgraph.py" not in line]
    
    assert len(matches) == 0, (
        f"Found hardcoded bolt://localhost in production code:\n" + "\n".join(matches)
    )
