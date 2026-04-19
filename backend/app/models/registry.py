"""
Model manifest management for RCKG AI models.

Tracks model versions, checksums, download timestamps, and status.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

MANIFEST_PATH = Path(__file__).parent.parent.parent.parent / "models" / "manifest.json"


class ModelManifest:
    """Manage the models/manifest.json metadata file."""

    def __init__(self, manifest_path: Optional[Path] = None) -> None:
        self.manifest_path = manifest_path or MANIFEST_PATH
        self._data = self._load()

    def _load(self) -> dict:
        """Load manifest from disk."""
        if not self.manifest_path.exists():
            return {
                "models": [],
                "last_updated": "",
                "download_script": "scripts/download_models.py",
            }
        try:
            with open(self.manifest_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {
                "models": [],
                "last_updated": "",
                "download_script": "scripts/download_models.py",
            }

    def save(self) -> None:
        """Save manifest to disk."""
        self._data["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_model(self, name: str) -> Optional[dict]:
        """Get model metadata by name."""
        for model in self._data["models"]:
            if model["name"] == name:
                return model
        return None

    def set_model_status(self, name: str, status: str) -> None:
        """Update a model's status."""
        for model in self._data["models"]:
            if model["name"] == name:
                model["status"] = status
                self.save()
                return
        raise ValueError(f"Model '{name}' not found in manifest")

    def set_model_checksum(self, name: str, sha256: str) -> None:
        """Update a model's checksum."""
        for model in self._data["models"]:
            if model["name"] == name:
                model["sha256"] = sha256
                model["download_timestamp"] = datetime.now(timezone.utc).isoformat()
                self.save()
                return
        raise ValueError(f"Model '{name}' not found in manifest")

    def pending_models(self) -> list[dict]:
        """Return models that need to be downloaded."""
        return [m for m in self._data["models"] if m.get("status") == "pending"]

    def completed_models(self) -> list[dict]:
        """Return models that have been downloaded."""
        return [m for m in self._data["models"] if m.get("status") == "downloaded"]

    def installed_models(self) -> list[dict]:
        """Return models that are already installed (e.g., via vLLM)."""
        return [m for m in self._data["models"] if m.get("status") == "installed"]

    @property
    def data(self) -> dict:
        return self._data
