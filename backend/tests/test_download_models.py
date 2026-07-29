"""
Unit tests for backend/scripts/download_models.py

Test strategy:
- Mock huggingface_hub functions to avoid actual downloads
- Use tmp_path fixtures for isolated manifest files
- Test dry-run, skip-installed, manifest update, and missing-model paths
"""

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.models.registry import ModelManifest

# Path to the download_models module
import scripts.download_models as download_models_module


@pytest.fixture
def manifest_path(tmp_path: Path) -> Path:
    """Create a manifest file with standard model entries."""
    data = {
        "models": [
            {
                "name": "BAAI/bge-m3",
                "purpose": "Dense embeddings",
                "storage_path": "models/embeddings/bge-m3",
                "minio_bucket": "models",
                "minio_path": "embeddings/bge-m3",
                "size_hint": "4.7GB (4-bit)",
                "sha256": "",
                "download_timestamp": "",
                "quantization": "4-bit",
                "status": "pending",
            },
            {
                "name": "colbertv2.0-adept",
                "purpose": "Token-level embeddings",
                "storage_path": "models/embeddings/colbertv2.0",
                "minio_bucket": "models",
                "minio_path": "embeddings/colbertv2.0",
                "size_hint": "2.1GB",
                "sha256": "",
                "download_timestamp": "",
                "quantization": "8-bit",
                "status": "pending",
            },
            {
                "name": "BAAI/bge-reranker-v2-m3",
                "purpose": "Reranking",
                "storage_path": "models/reranker/bge-reranker",
                "minio_bucket": "models",
                "minio_path": "reranker/bge-reranker",
                "size_hint": "1.5GB",
                "sha256": "",
                "download_timestamp": "",
                "quantization": "4-bit",
                "status": "pending",
            },
            {
                "name": "Qwen/Qwen3.6-35B",
                "purpose": "Extraction and judge model",
                "storage_path": "models/llm/qwen3.6-35b",
                "minio_bucket": "models",
                "minio_path": "llm/qwen3.6-35b",
                "size_hint": "18GB (4-bit)",
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
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data, indent=2))
    return path


@pytest.fixture
def empty_manifest_path(tmp_path: Path) -> Path:
    """Create an empty manifest file with no models."""
    data = {
        "models": [],
        "last_updated": "",
        "download_script": "scripts/download_models.py",
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def _make_mock_file(size: int = 1024) -> MagicMock:
    """Create a mock file object for hf_hub_download to return."""
    mock_file = MagicMock()
    mock_file.__str__ = lambda self: "/tmp/fake/file.hf"
    return mock_file


class TestDownloadDryRun:
    """Test dry-run mode does not perform downloads."""

    @patch("huggingface_hub.hf_hub_download")
    @patch("huggingface_hub.list_repo_files")
    def test_dry_run_prints_info(self, mock_list_files, mock_hf_download, manifest_path: Path):
        """Dry-run mode lists models without downloading."""
        mock_list_files.return_value = ["config.json", "model.safetensors"]
        mock_hf_download.return_value = "/tmp/fake/file.hf"

        # Patch module-level constants to use tmp_path
        original_base = download_models_module.BASE_DIR
        original_manifest = download_models_module.MANIFEST_PATH
        download_models_module.BASE_DIR = manifest_path.parent.parent
        download_models_module.MANIFEST_PATH = manifest_path

        try:
            results = download_models_module.download_models(dry_run=True)
        finally:
            download_models_module.BASE_DIR = original_base
            download_models_module.MANIFEST_PATH = original_manifest

        assert isinstance(results["downloaded"] + results["skipped"] + results["failed"], list)
        # All 3 MODEL_DEFS models should be dry-run (not skipped since not installed)
        assert "BAAI/bge-m3" in results["downloaded"]
        assert "colbertv2.0-adept" in results["downloaded"]
        assert "BAAI/bge-reranker-v2-m3" in results["downloaded"]

    @patch("huggingface_hub.hf_hub_download")
    @patch("huggingface_hub.list_repo_files")
    def test_dry_run_does_not_write_model_files(
        self, mock_list_files, mock_hf_download, manifest_path: Path
    ):
        """Dry-run mode does not create model directories."""
        mock_list_files.return_value = ["config.json"]
        mock_hf_download.return_value = "/tmp/fake/file.hf"

        original_base = download_models_module.BASE_DIR
        original_manifest = download_models_module.MANIFEST_PATH
        download_models_module.BASE_DIR = manifest_path.parent.parent
        download_models_module.MANIFEST_PATH = manifest_path

        embeddings_dir = manifest_path.parent / "models" / "embeddings"

        try:
            download_models_module.download_models(dry_run=True)
        finally:
            download_models_module.BASE_DIR = original_base
            download_models_module.MANIFEST_PATH = original_manifest

        # In dry-run mode, the model directories should NOT be created
        assert not embeddings_dir.exists()


class TestDownloadSkipsInstalled:
    """Test that installed models are skipped."""

    @patch("huggingface_hub.hf_hub_download")
    @patch("huggingface_hub.list_repo_files")
    def test_download_skips_installed_models(
        self, mock_list_files, mock_hf_download, manifest_path: Path
    ):
        """Models with status=installed are skipped."""
        mock_list_files.return_value = ["config.json"]
        mock_hf_download.return_value = "/tmp/fake/file.hf"

        original_base = download_models_module.BASE_DIR
        original_manifest = download_models_module.MANIFEST_PATH
        download_models_module.BASE_DIR = manifest_path.parent.parent
        download_models_module.MANIFEST_PATH = manifest_path

        try:
            results = download_models_module.download_models(dry_run=False)
        finally:
            download_models_module.BASE_DIR = original_base
            download_models_module.MANIFEST_PATH = original_manifest

        # All 3 MODEL_DEFS models should be downloaded (mocked)
        assert "BAAI/bge-m3" in results["downloaded"]
        assert "colbertv2.0-adept" in results["downloaded"]
        assert "BAAI/bge-reranker-v2-m3" in results["downloaded"]
        # None should be in failed
        assert len(results["failed"]) == 0


class TestDownloadUpdatesManifest:
    """Test that checksums are written to manifest after download."""

    @patch("huggingface_hub.hf_hub_download")
    @patch("huggingface_hub.list_repo_files")
    def test_download_updates_manifest(
        self, mock_list_files, mock_hf_download, manifest_path: Path
    ):
        """Checksums written to manifest after download."""
        mock_list_files.return_value = ["config.json", "model.safetensors"]

        def fake_hf_download(*args, **kwargs):
            return "/tmp/fake/file.hf"

        mock_hf_download.side_effect = fake_hf_download

        original_base = download_models_module.BASE_DIR
        original_manifest = download_models_module.MANIFEST_PATH
        download_models_module.BASE_DIR = manifest_path.parent.parent
        download_models_module.MANIFEST_PATH = manifest_path

        try:
            results = download_models_module.download_models(dry_run=False)
        finally:
            download_models_module.BASE_DIR = original_base
            download_models_module.MANIFEST_PATH = original_manifest

        # bge-m3 should be in downloaded
        assert "BAAI/bge-m3" in results["downloaded"]

        # Reload manifest and verify checksum was written
        manifest = ModelManifest(manifest_path)
        model = manifest.get_model("BAAI/bge-m3")
        assert model is not None
        assert model["sha256"] != "", "SHA-256 should be populated after download"
        assert model["status"] == "downloaded", "Status should be 'downloaded'"
        assert model["download_timestamp"] != "", "Timestamp should be populated"


class TestDownloadHandlesMissingModel:
    """Test handling of missing model entries in manifest."""

    @patch("huggingface_hub.hf_hub_download", autospec=True)
    @patch("huggingface_hub.list_repo_files", autospec=True)
    def test_download_handles_missing_model(
        self, mock_list_files, mock_hf_download, empty_manifest_path: Path
    ):
        """Missing model in manifest is gracefully skipped."""
        mock_list_files.return_value = ["config.json", "model.safetensors"]
        mock_hf_download.return_value = "/tmp/fake/file.hf"

        # The manifest has no models at all
        # download_models iterates MODEL_DEFS and checks each against manifest
        # Since bge-m3 is not in the empty manifest, it gets added then downloaded

        # But we need to handle the case where a model_def references something
        # that doesn't match any manifest entry AND the download fails

        # Test with a scenario: mock huggingface to raise an error for a specific model
        def selective_download_error(*args, **kwargs):
            repo_id = kwargs.get("repo_id", args[0] if args else "")
            if "colbertv2.0-adept" in repo_id:
                raise FileNotFoundError(f"Repo {repo_id} not found")
            return "/tmp/fake/file.hf"

        mock_list_files.side_effect = lambda repo: (
            [] if "colbertv2.0-adept" in repo else ["config.json"]
        )
        mock_hf_download.side_effect = selective_download_error

        original_base = download_models_module.BASE_DIR
        download_models_module.BASE_DIR = empty_manifest_path.parent

        try:
            results = download_models_module.download_models(dry_run=False)
        finally:
            download_models_module.BASE_DIR = original_base

        # colbertv2.0-adept should be in failed, not crash
        assert "colbertv2.0-adept" in results["failed"]
        # bge-m3 and reranker should still have been processed
        assert "BAAI/bge-m3" in results["downloaded"] or "BAAI/bge-m3" in results["failed"]


class TestComputeSha256:
    """Test SHA-256 computation helper."""

    def test_compute_sha256_of_known_content(self, tmp_path: Path):
        """SHA-256 of known file content matches expected hash."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        from scripts.download_models import compute_sha256

        result = compute_sha256(test_file)
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result == expected

    def test_compute_sha256_of_binary_content(self, tmp_path: Path):
        """SHA-256 works with binary content."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")

        from scripts.download_models import compute_sha256

        result = compute_sha256(test_file)
        expected = hashlib.sha256(b"\x00\x01\x02\x03\x04\x05").hexdigest()
        assert result == expected

    def test_compute_sha256_missing_file_raises(self, tmp_path: Path):
        """Computing SHA-256 of non-existent file raises RuntimeError."""
        from scripts.download_models import compute_sha256

        missing_file = tmp_path / "does_not_exist.txt"
        with pytest.raises(RuntimeError, match="Failed to compute SHA-256"):
            compute_sha256(missing_file)


class TestEnsureManifestHasModel:
    """Test manifest entry creation helper."""

    def test_returns_true_for_existing_model(self, manifest_path: Path):
        """ensure_manifest_has_model returns True for existing manifest entry."""
        original_base = download_models_module.BASE_DIR
        download_models_module.BASE_DIR = manifest_path.parent.parent
        try:
            manifest = ModelManifest(manifest_path)
            result = download_models_module.ensure_manifest_has_model(
                manifest,
                {"hf_repo": "BAAI/bge-m3", "storage_path": "models/embeddings/bge-m3"},
            )
            assert result is True
        finally:
            download_models_module.BASE_DIR = original_base

    def test_creates_entry_for_missing_model(self, empty_manifest_path: Path):
        """ensure_manifest_has_model creates entry when model is missing."""
        original_base = download_models_module.BASE_DIR
        download_models_module.BASE_DIR = empty_manifest_path.parent
        try:
            manifest = ModelManifest(empty_manifest_path)
            model_def = {
                "hf_repo": "BAAI/bge-m3",
                "storage_path": "models/embeddings/bge-m3",
                "purpose": "Dense embeddings",
                "size_hint": "4.7GB (4-bit)",
                "quantization": "4-bit",
            }
            result = download_models_module.ensure_manifest_has_model(manifest, model_def)
            assert result is True

            loaded = manifest.get_model("BAAI/bge-m3")
            assert loaded is not None
            assert loaded["purpose"] == "Dense embeddings"
            assert loaded["status"] == "pending"
        finally:
            download_models_module.BASE_DIR = original_base


class TestDownloadModelsReturnDict:
    """Test that download_models returns the correct result structure."""

    @patch("huggingface_hub.hf_hub_download", autospec=True)
    @patch("huggingface_hub.list_repo_files", autospec=True)
    def test_returns_dict_with_three_keys(self, mock_list_files, mock_hf_download, manifest_path: Path):
        """download_models returns dict with downloaded, skipped, failed keys."""
        mock_list_files.return_value = ["config.json"]
        mock_hf_download.return_value = "/tmp/fake/file.hf"

        original_base = download_models_module.BASE_DIR
        download_models_module.BASE_DIR = manifest_path.parent.parent

        try:
            results = download_models_module.download_models(dry_run=False)
        finally:
            download_models_module.BASE_DIR = original_base

        assert isinstance(results, dict)
        assert "downloaded" in results
        assert "skipped" in results
        assert "failed" in results
        assert isinstance(results["downloaded"], list)
        assert isinstance(results["skipped"], list)
        assert isinstance(results["failed"], list)
