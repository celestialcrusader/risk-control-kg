"""Pytest configuration for the backend test suite."""

import sys
from pathlib import Path

# Add the backend directory to the Python path so 'app' imports work
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
