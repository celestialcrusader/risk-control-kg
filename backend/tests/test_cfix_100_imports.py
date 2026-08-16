"""
Unit test for CFIX-100: Import Path Normalization.
Ensures zero occurrences of 'from backend.app.' exist in backend/app/ source directory.
"""

import os
import subprocess
import pytest


def test_no_backend_app_imports_in_app_directory():
    """Verify that all files under backend/app/ use normalized 'app.' imports."""
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    
    # Run grep for 'from backend.app.' in backend/app
    cmd = ["grep", "-rn", "from backend.app.", app_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    assert result.returncode != 0, (
        f"Found 'from backend.app.' imports in production code:\n{result.stdout}"
    )
