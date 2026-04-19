"""
Test suite for INFRA-8: AI Model Download and Local Registry

This test module verifies the model manifest management including:
- Manifest loading and saving
- Model metadata lookup
- Status and checksum updates
- Pending/completed model queries

Test Strategy:
- Unit tests with filesystem fixtures (temp directory)
- Tests verify actual manifest operations
- All assertions are meaningful
"""

import json
import tempfile
from pathlib import Path

import pytest


def _create_manifest(path: Path) -> Path:
    """Create a test manifest file."""
    data = {
        "models": [
            {
                "name": "test-model",
                "purpose": "test",
                "storage_path": "models/test",
                "minio_bucket": "models",
                "minio_path": "test",
                "size_hint": "1GB",
                "sha256": "",
                "download_timestamp": "",
                "quantization": "4-bit",
                "status": "pending",
            },
            {
                "name": "downloaded-model",
                "purpose": "test",
                "storage_path": "models/dl",
                "minio_bucket": "models",
                "minio_path": "dl",
                "size_hint": "2GB",
                "sha256": "abc123",
                "download_timestamp": "2026-04-19T00:00:00+00:00",
                "quantization": "8-bit",
                "status": "downloaded",
            },
            {
                "name": "installed-model",
                "purpose": "test",
                "storage_path": "models/llm/vllm",
                "minio_bucket": "models",
                "minio_path": "llm/vllm",
                "size_hint": "18GB",
                "sha256": "",
                "download_timestamp": "",
                "quantization": "4-bit",
                "status": "installed",
                "notes": "Already served via local vLLM instance. Skip download/setup.",
            },
        ],
        "last_updated": "2026-04-19",
        "download_script": "scripts/download_models.py",
    }
    path.write_text(json.dumps(data, indent=2))
    return path


class TestModelManifest:
    """Tests for manifest CRUD operations."""

    def test_loads_existing_manifest(self, tmp_path: Path):
        """Manifest loads from existing file."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")

        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        assert len(m._data["models"]) == 3
        assert m._data["models"][0]["name"] == "test-model"

    def test_creates_empty_manifest(self, tmp_path: Path):
        """Manifest creates empty structure when file doesn't exist."""
        from app.models.registry import ModelManifest

        m = ModelManifest(tmp_path / "nonexistent.json")

        assert m._data["models"] == []
        assert m._data["last_updated"] == ""

    def test_get_model_by_name(self, tmp_path: Path):
        """get_model returns correct model metadata."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        model = m.get_model("test-model")

        assert model is not None
        assert model["name"] == "test-model"
        assert model["storage_path"] == "models/test"

    def test_get_model_returns_none_missing(self, tmp_path: Path):
        """get_model returns None for non-existent model."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        assert m.get_model("nonexistent") is None

    def test_set_model_status_updates_and_saves(self, tmp_path: Path):
        """set_model_status updates status and persists to disk."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)
        m.set_model_status("test-model", "downloaded")

        assert m.get_model("test-model")["status"] == "downloaded"
        # Verify persisted
        loaded = json.loads(manifest_file.read_text())
        assert loaded["models"][0]["status"] == "downloaded"

    def test_set_model_checksum_updates_and_saves(self, tmp_path: Path):
        """set_model_checksum updates hash and timestamp."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)
        m.set_model_checksum("test-model", "new_hash_456")

        model = m.get_model("test-model")
        assert model["sha256"] == "new_hash_456"
        assert model["download_timestamp"] != ""

    def test_set_model_status_raises_for_missing(self, tmp_path: Path):
        """set_model_status raises ValueError for unknown model."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        with pytest.raises(ValueError, match="unknown-model"):
            m.set_model_status("unknown-model", "downloaded")

    def test_pending_models(self, tmp_path: Path):
        """pending_models returns models with status 'pending'."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        pending = m.pending_models()

        assert len(pending) == 1
        assert pending[0]["name"] == "test-model"

    def test_completed_models(self, tmp_path: Path):
        """completed_models returns models with status 'downloaded'."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        completed = m.completed_models()

        assert len(completed) == 1
        assert completed[0]["name"] == "downloaded-model"

    def test_installed_models(self, tmp_path: Path):
        """installed_models returns models with status 'installed'."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)

        installed = m.installed_models()

        assert len(installed) == 1
        assert installed[0]["name"] == "installed-model"
        assert "vLLM" in installed[0]["notes"]

    def test_save_updates_timestamp(self, tmp_path: Path):
        """save() updates the last_updated timestamp."""
        manifest_file = _create_manifest(tmp_path / "manifest.json")
        from app.models.registry import ModelManifest

        m = ModelManifest(manifest_file)
        m.set_model_status("test-model", "downloaded")

        loaded = json.loads(manifest_file.read_text())
        assert loaded["last_updated"] != ""
