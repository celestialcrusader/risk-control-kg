# QA Review Report: INFRA-8 -- AI Model Download and Local Registry Setup (Rev. 2)

**Reviewer**: QA Engineer (Automated)
**Review Date**: 2026-04-19
**Story**: INFRA-8 -- AI Model Download and Local Registry Setup
**Status**: PARTIAL APPROVAL

---

## 1. Story/Sprint Plan Consistency Check

### 1.1 Model Count Discrepancy

The sprint plan (`docs/01-initial/sprint-plan-rckg.md`, lines 399-395) contains a conflicting statement:

> **AC1**: "all 5 models are downloaded and verified against SHA-256 checksums"

But the Models Required table in the sprint plan lists only 3 models:

| Model | Purpose | Size | Storage Path |
|---|---|---|---|
| `BAAI/bge-m3` | Dense embeddings | 4.7GB | `models/embeddings/bge-m3` |
| `colbertv2.0-adept` | Token-level embeddings | 2.1GB | `models/embeddings/colbertv2.0` |
| `BAAI/bge-reranker-v2-m3` | Reranking | 1.5GB | `models/reranker/bge-reranker` |

And the Context section states: "we already have qwen3.6 35b in vllm" -- confirming 1 model is already installed locally.

**Corrected scope**: 3 download-pending models + 1 already-installed model = **4 total models**. The "5 models" in AC1 of the sprint plan is incorrect.

**Fix required in sprint plan** (line 399): Change "all 5 models are downloaded" to "all 3 download-pending models are downloaded" (or equivalently, "all 4 models are accounted for, including 1 pre-installed").

**Story ticket consistency**: The story ticket (`docs/01-initial/stories/INFRA-8-ai-model-download-and-local-registry-setup.md`) correctly lists all 4 models in its table (3 pending + 1 installed = Qwen3.6-35B). This aligns with the actual manifest.

**Verdict**: After correcting AC1 in the sprint plan, the story and sprint plan agree on scope.

---

## 2. Implementation Completeness Assessment

### 2.1 Acceptance Criteria Cross-Check

| # | Acceptance Criterion | Status | Notes |
|---|---|---|---|
| AC1 | Models downloaded and validated against SHA-256 checksums | **NOT DONE** | No `scripts/download_models.py` exists. The `scripts/` directory is empty. |
| AC2 | Models accessible via MinIO registry | **NOT DONE** | No MinIO upload logic in `registry.py`. No integration test. |
| AC3 | `models/manifest.json` tracks model versions, checksums, timestamps | **DONE** | `ModelManifest` class supports CRUD on model metadata. |
| AC4 | Air-gapped deployment checklist documented | **NOT DONE** | No `docs/01-initial/air-gapped-deployment.md` or equivalent file found. |
| AC5 | GPU routing configuration documented | **NOT DONE** | No GPU routing or sequential execution strategy document found. |

### 2.2 Definition of Done Cross-Check

| DoD Item | Status | Notes |
|---|---|---|
| Model download script with checksum verification | **MISSING** | No `scripts/download_models.py` file exists anywhere in the repo. |
| `models/manifest.json` tracks metadata | **DONE** | `models/manifest.json` exists with 4 models. `ModelManifest` class supports read/update. |
| Air-gapped deployment procedure documented | **MISSING** | No documentation file found. |
| GPU routing and sequential execution strategy documented | **MISSING** | No documentation file found. |
| All acceptance criteria verified | **PARTIAL** | Only AC3 is implemented. |
| QA Checkpoint: Verify all assertions are meaningful | **DONE** (in tests) | 11 tests written, all assertions meaningful (see Section 4.2). |

### 2.3 What Is Implemented (Complete)

1. **`backend/app/models/registry.py`** -- `ModelManifest` class providing:
   - Manifest load/save from `models/manifest.json`
   - `get_model(name)` lookup
   - `set_model_status(name, status)` update
   - `set_model_checksum(name, sha256)` update with timestamp
   - `pending_models()`, `completed_models()`, `installed_models()` query helpers
   - `data` property for raw access

2. **`models/manifest.json`** -- Tracks 4 models:
   - `BAAI/bge-m3` (pending, 4.7GB, 4-bit)
   - `colbertv2.0-adept` (pending, 2.1GB, 8-bit)
   - `BAAI/bge-reranker-v2-m3` (pending, 1.5GB, 4-bit)
   - `Qwen/Qwen3.6-35B` (installed, 18GB, 4-bit, served via vLLM)

3. **Test file** -- 11 unit tests covering manifest CRUD operations (see Section 4).

### 2.4 What Is Still Missing

1. **`scripts/download_models.py`** -- The download script referenced in the manifest (`"download_script": "scripts/download_models.py"`) and required by AC1 and the DoD does not exist. This script is the core operational piece of this story -- it should:
   - Use `huggingface-cli download` or equivalent to download each pending model
   - Compute SHA-256 checksums of downloaded model files
   - Verify checksums against expected values (or populate them if not yet known)
   - Update the manifest with checksums and status changes
   - Handle partial failures gracefully (retry, rollback)

2. **MinIO upload integration** -- AC2 requires models to be stored in MinIO and accessible via an internal registry URL. Neither the download script nor the `ModelManifest` class includes MinIO upload logic.

3. **Air-gapped deployment checklist** (`docs/01-initial/air-gapped-deployment.md`) -- Should document:
   - How to pre-download all models on a connected machine
   - How to transfer model files and manifest to the air-gapped environment
   - How to verify model integrity post-transfer
   - Prerequisite steps (MinIO running, paths configured)

4. **GPU routing documentation** (`docs/01-initial/gpu-routing.md`) -- Should document:
   - The sequential judge execution strategy (mentioned in sprint plan)
   - vLLM concurrency limits (`max_model_len`, `num-gpus`)
   - Model swapping strategy (load judge only when needed, unload after completion)
   - Dev vs prod environment configurations

---

## 3. Implementation Quality Assessment

### 3.1 `ModelManifest` Class -- `registry.py`

**Correctness**: The class correctly loads, parses, and saves `manifest.json`. The `_load()` method handles the missing-file case by returning a default structure. The `save()` method creates parent directories as needed. No logical errors found.

**MANIFEST_PATH evaluation** (previously flagged in REV1 as a bug):
```python
MANIFEST_PATH = Path(__file__).parent.parent.parent / "models" / "manifest.json"
```
Breaking down the path resolution from `backend/app/models/registry.py`:
- `__file__` = `.../backend/app/models/registry.py`
- `.parent` = `.../backend/app/models/`
- `.parent.parent` = `.../backend/app/`
- `.parent.parent.parent` = `.../backend/`
- `.parent.parent.parent / "models" / "manifest.json"` = `.../backend/models/manifest.json`

**This resolves to `backend/models/manifest.json`, NOT `models/manifest.json` at the project root.** However, the actual manifest used is at `models/manifest.json`. The `MANIFEST_PATH` default is therefore pointing to the wrong location.

The tests avoid this bug by always passing `manifest_file` (a `tmp_path` location) explicitly to the `ModelManifest` constructor, so the default path is never exercised in tests. This is a **latent defect** -- the default path will be wrong if anyone creates a `ModelManifest()` with no arguments in production code.

**Security**: No security concerns. The class reads and writes local files under explicit paths.

**Error Handling**: The `_load()` method silently creates a default manifest if the file doesn't exist, which is reasonable behavior. However, there is no `json.JSONDecodeError` handler in `_load()` -- if the manifest file is corrupted, a `json.JSONDecodeError` will propagate uncaught.

**Performance**: No performance concerns. The manifest is small (JSON with a few KB of metadata).

### 3.2 Test Quality Assessment -- `test_infra_8_model_registry.py`

#### 3.2.1 Per-Test Analysis

| # | Test Name | Criterion Covered | Test Correct? | Notes |
|---|---|---|---|---|
| 1 | `test_loads_existing_manifest` | AC3 | **BUG** | Test fixture has 3 models, asserts `len(m._data["models"]) == 2`. This is a stale assertion from an earlier fixture revision. Should be `== 3`. |
| 2 | `test_creates_empty_manifest` | AC3 | Correct | Verifies default empty structure. |
| 3 | `test_get_model_by_name` | AC3 | Correct | Tests lookup by name. |
| 4 | `test_get_model_returns_none_missing` | AC3 | Correct | Tests missing-model lookup returns None. |
| 5 | `test_set_model_status_updates_and_saves` | AC3 | Correct | Tests status update + persistence. |
| 6 | `test_set_model_checksum_updates_and_saves` | AC3 | Correct | Tests checksum + timestamp update. |
| 7 | `test_set_model_status_raises_for_missing` | AC3 | Correct | Tests ValueError for unknown model. |
| 8 | `test_pending_models` | AC3 | Correct | Tests `pending_models()` filter. |
| 9 | `test_completed_models` | AC3 | Correct | Tests `completed_models()` filter. |
| 10 | `test_installed_models` | AC3 | Correct | Tests `installed_models()` filter and verifies notes field. |
| 11 | `test_save_updates_timestamp` | AC3 | Correct | Tests that `save()` updates `last_updated`. |

#### 3.2.2 Test Issues

**Critical test bug**: Test #1 (`test_loads_existing_manifest`) asserts `len(m._data["models"]) == 2` but the fixture `_create_manifest()` creates 3 models. This is an incorrect assertion that will pass coincidentally with the current fixture but documents incorrect expected behavior. It should assert `== 3`.

**Note**: Despite this assertion bug, the test does not indicate that the previous REV1 QA report's specific complaint about "test assertion bug" was the same bug. The REV1 comment likely referred to a different assertion. The current state still has this one stale assertion.

#### 3.2.3 Test Gaps

Tests exist only for manifest CRUD. The following should have tests but do not:

1. **`_load()` corrupted JSON handling** -- If `manifest.json` contains invalid JSON, `json.load()` will raise `json.JSONDecodeError`. There is no test for graceful handling.
2. **`set_model_checksum()` raises for missing model** -- Consistent with `set_model_status()`, this should raise `ValueError`. No test verifies this behavior.
3. **`_load()` on non-existent file creates default structure** -- Already covered by `test_creates_empty_manifest`, good.
4. **Save creates parent directories** -- `save()` calls `mkdir(parents=True, exist_ok=True)`. No test verifies this behavior when the parent directory does not exist.

---

## 4. QA Verdict

### Overall Status: PARTIAL APPROVAL

The core manifest management implementation (`ModelManifest` class) is functionally correct and well-tested for its CRUD operations. However, the story as a whole is incomplete -- only 1 of 5 acceptance criteria (AC3) and 1 of 4 Definition of Done items are delivered. The story remains fundamentally incomplete until the download script and documentation are added.

### Critical Issues (Blockers)

1. **Download script (`scripts/download_models.py`) does not exist** -- This is the primary deliverable of AC1 and the DoD. Without it, there is no mechanism to actually download, validate, and store models. The entire story purpose is unfulfilled.

2. **Air-gapped deployment documentation does not exist** -- AC4 and a DoD item are completely unmet.

3. **GPU routing documentation does not exist** -- AC5 and a DoD item are completely unmet.

4. **Sprint plan AC1 has wrong model count ("5 models" vs actual 3-4)** -- The sprint plan must be corrected to align with the story ticket (4 total models: 3 pending download + 1 installed).

### Minor Issues (Non-Blockers for future merge)

1. **Test #1 assertion bug**: `test_loads_existing_manifest` asserts `len(m._data["models"]) == 2` but the fixture creates 3 models. The assertion should be `== 3`.

2. **Default `MANIFEST_PATH` is incorrect**: `Path(__file__).parent.parent.parent / "models" / "manifest.json"` resolves to `backend/models/manifest.json` instead of the project root `models/manifest.json`. Either the path calculation is wrong (should be `.parent.parent.parent.parent`) or the manifest file should live at `backend/models/`. Since the manifest is at the project root, the path should be:
   ```python
   MANIFEST_PATH = Path(__file__).parent.parent.parent.parent / "models" / "manifest.json"
   ```
   (going up 4 levels: `registry.py` -> `models/` -> `app/` -> `backend/` -> project root).

3. **No error handling for corrupted manifest JSON**: `_load()` has no `try/except json.JSONDecodeError`. If the manifest file is corrupted, the error will propagate uncaught.

4. **No test for `set_model_checksum()` raising `ValueError` on missing model**: Inconsistent with `set_model_status()` behavior.

5. **No test for `save()` creating parent directories**: The `mkdir(parents=True, exist_ok=True)` call is untested.

### Suggested Additional Tests

1. Test that `_load()` raises a meaningful error (or returns a default) when the manifest file contains invalid JSON.
2. Test that `set_model_checksum()` raises `ValueError` for a non-existent model name.
3. Test that `save()` successfully creates parent directories when they do not exist.
4. Test `pending_models()` returns an empty list when no models have "pending" status.

---

## 5. QA Sign-Off Checklist

- [ ] All acceptance criteria have corresponding tests -- **FAIL** (AC1, AC2, AC4, AC5 have no tests)
- [ ] All acceptance criteria tests pass -- **N/A** (no tests for AC1, AC2, AC4, AC5)
- [ ] Edge cases are covered -- **PARTIAL** (missing corrupted JSON, missing parent dirs)
- [ ] Error paths are tested -- **PARTIAL** (missing JSONDecodeError, missing checksum ValueError)
- [ ] No obvious security vulnerabilities introduced -- **PASS**
- [ ] No regressions introduced in existing test suite -- **PASS** (tests run successfully with 1 assertion bug)
- [ ] Code is readable and maintainable -- **PASS**
- [ ] Documentation is updated where required -- **FAIL** (3 documentation items missing)
- [ ] PR is ready for merge -- **NO** (story incomplete)

---

**Final Status: PARTIAL APPROVAL**

The `ModelManifest` class is solid infrastructure for the manifest CRUD operations. However, the story deliverable (download models + validate + store + document) is only 20-25% complete. The download script, MinIO integration, air-gapped checklist, and GPU routing documentation are all missing. These are not trivial additions -- they are the core purpose of this story.

The story can be approved for the manifest portion if the team wants to merge the `ModelManifest` class separately, but the INFRA-8 story as a whole should not be considered complete until all items above are delivered.

The sprint plan AC1 should be corrected (5 models -> 3 download-pending + 1 installed = 4 total) and committed before merge.
