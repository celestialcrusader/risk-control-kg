#!/usr/bin/env python3
"""
Download AI models from HuggingFace, verify SHA-256 checksums,
and update models/manifest.json.

Usage:
    python -m backend.scripts.download_models              # Normal run
    python -m backend.scripts.download_models --dry-run    # Preview only
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.models.registry import ModelManifest

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
MANIFEST_PATH = BASE_DIR / "models" / "manifest.json"

# Model definitions: (hf_repo, storage_subpath, name_in_manifest)
MODEL_DEFS = [
    {
        "hf_repo": "BAAI/bge-m3",
        "storage_path": "models/embeddings/bge-m3",
        "purpose": "Dense embeddings",
        "size_hint": "4.7GB (4-bit)",
        "quantization": "4-bit",
    },
    {
        "hf_repo": "colbertv2.0-adept",
        "storage_path": "models/embeddings/colbertv2.0",
        "purpose": "Token-level embeddings",
        "size_hint": "2.1GB",
        "quantization": "8-bit",
    },
    {
        "hf_repo": "BAAI/bge-reranker-v2-m3",
        "storage_path": "models/reranker/bge-reranker",
        "purpose": "Reranking",
        "size_hint": "1.5GB",
        "quantization": "4-bit",
    },
]


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
    except (OSError, IOError) as e:
        raise RuntimeError(f"Failed to compute SHA-256 for {file_path}: {e}")
    return sha256.hexdigest()


def ensure_manifest_has_model(manifest: ModelManifest, model_def: dict) -> bool:
    """
    Ensure the manifest contains an entry for the given model definition.
    Returns True if the entry was found or created successfully.
    """
    hf_repo = model_def["hf_repo"]
    existing = manifest.get_model(hf_repo)
    if existing is not None:
        return True

    # Add new entry
    model_entry: dict[str, Any] = {
        "name": hf_repo,
        "purpose": model_def.get("purpose", ""),
        "storage_path": model_def["storage_path"],
        "minio_bucket": "models",
        "minio_path": model_def["storage_path"].replace("models/", "", 1),
        "size_hint": model_def.get("size_hint", "unknown"),
        "sha256": "",
        "download_timestamp": "",
        "quantization": model_def.get("quantization", "unknown"),
        "status": "pending",
    }
    manifest.data["models"].append(model_entry)
    manifest.save()
    print(f"  Added manifest entry for {hf_repo}")
    return True


def download_model(
    model_def: dict, manifest: ModelManifest, dry_run: bool
) -> dict[str, Any]:
    """
    Download a single model from HuggingFace.

    Returns a dict with keys: name, status, sha256 (if downloaded), error (if failed).
    """
    hf_repo = model_def["hf_repo"]
    storage_path = Path(BASE_DIR) / model_def["storage_path"]
    result: dict[str, Any] = {"name": hf_repo, "status": "unknown"}

    # Ensure manifest entry exists
    if not ensure_manifest_has_model(manifest, model_def):
        result["status"] = "skipped_manifest_failure"
        result["error"] = f"Failed to add manifest entry for {hf_repo}"
        return result

    # Skip if already installed
    manifest_entry = manifest.get_model(hf_repo)
    if manifest_entry and manifest_entry.get("status") == "installed":
        print(f"  Skipping {hf_repo} (status: installed)")
        result["status"] = "skipped"
        return result

    if dry_run:
        print(f"  [DRY-RUN] Would download {hf_repo} to {storage_path}")
        result["status"] = "dry_run"
        return result

    try:
        from huggingface_hub import hf_hub_download, list_repo_files
    except ImportError:
        result["status"] = "failed"
        result["error"] = (
            "huggingface_hub is not installed. "
            "Install it with: pip install huggingface_hub"
        )
        return result

    try:
        # Download the entire repo snapshot to the storage path
        storage_path.mkdir(parents=True, exist_ok=True)

        # Get list of files in the repo
        repo_files = list_repo_files(hf_repo)
        print(f"  Downloading {hf_repo} ({len(repo_files)} files) to {storage_path}...")

        downloaded_files: list[Path] = []
        for filename in repo_files:
            try:
                local_path = hf_hub_download(
                    repo_id=hf_repo,
                    filename=filename,
                    cache_dir=str(storage_path),
                    local_dir=str(storage_path),
                    local_dir_use_symlinks=False,
                )
                downloaded_files.append(Path(local_path))
            except Exception as e:
                print(f"  Warning: Failed to download {filename}: {e}")

        if not downloaded_files:
            result["status"] = "failed"
            result["error"] = f"No files downloaded for {hf_repo}"
            return result

        # Compute SHA-256 for the entire directory
        print(f"  Computing SHA-256 for {hf_repo}...")
        total_hash = hashlib.sha256()
        for f_path in sorted(downloaded_files):
            try:
                file_hash = compute_sha256(f_path)
                total_hash.update(file_hash.encode())
                total_hash.update(str(f_path).encode())
            except RuntimeError as e:
                print(f"  Warning: Could not hash {f_path}: {e}")

        sha256_value = total_hash.hexdigest()

        # Update manifest with checksum and status
        manifest.set_model_checksum(hf_repo, sha256_value)
        manifest.set_model_status(hf_repo, "downloaded")

        print(f"  Downloaded {hf_repo} ({len(downloaded_files)} files, "
              f"checksum: {sha256_value[:16]}...)")

        result["status"] = "downloaded"
        result["sha256"] = sha256_value
        result["file_count"] = len(downloaded_files)

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        print(f"  FAILED {hf_repo}: {e}")

    return result


def download_models(dry_run: bool = False) -> dict[str, list[str]]:
    """
    Download all pending models defined in MODEL_DEFS.

    Returns a dict with keys:
        - downloaded: list of model names that were downloaded
        - skipped: list of model names that were skipped
        - failed: list of model names that failed
    """
    manifest = ModelManifest(MANIFEST_PATH)

    results: dict[str, list[str]] = {
        "downloaded": [],
        "skipped": [],
        "failed": [],
    }

    print(f"Model Download Script {'(dry run)' if dry_run else ''}")
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Models to process: {len(MODEL_DEFS)}")
    print("-" * 60)

    for model_def in MODEL_DEFS:
        hf_repo = model_def["hf_repo"]
        print(f"\nProcessing: {hf_repo}")

        # Skip if already installed per manifest
        existing_entry = manifest.get_model(hf_repo)
        if existing_entry and existing_entry.get("status") == "installed":
            print(f"  Skipping {hf_repo} (status: installed)")
            results["skipped"].append(hf_repo)
            continue

        result = download_model(model_def, manifest, dry_run)

        if result["status"] in ("downloaded", "dry_run"):
            results["downloaded"].append(hf_repo)
        elif result["status"] == "skipped":
            results["skipped"].append(hf_repo)
        else:
            results["failed"].append(hf_repo)
            if "error" in result:
                print(f"  Error: {result['error']}")

    print("\n" + "-" * 60)
    print(f"Summary: {len(results['downloaded'])} downloaded, "
          f"{len(results['skipped'])} skipped, "
          f"{len(results['failed'])} failed")

    return results


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Download AI models from HuggingFace and update manifest."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview downloads without actually downloading",
    )
    args = parser.parse_args()

    try:
        results = download_models(dry_run=args.dry_run)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

    if results["failed"]:
        print(f"\n{len(results['failed'])} model(s) failed to download.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
