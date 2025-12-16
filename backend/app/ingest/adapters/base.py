from abc import ABC, abstractmethod
from typing import Any
import sys
import os

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.core.oscal import Catalog

class BaseAdapter(ABC):
    @abstractmethod
    def to_oscal(self, file_path: str) -> Catalog:
        """
        Parses the input file and returns a standardized OSCAL Catalog object.
        """
        pass
