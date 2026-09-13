# Model Setup Guide

## Overview of AI Models

The RCKG system uses four AI models: three downloaded from HuggingFace and one already deployed via vLLM.

| Model | Purpose | Storage Path | Source | Status |
|---|---|---|---|---|
| `BAAI/bge-m3` | Dense embeddings | `models/embeddings/bge-m3` | HuggingFace (download) | pending |
| `colbertv2.0-adept` | Token-level embeddings | `models/embeddings/colbertv2.0` | HuggingFace (download) | pending |
| `BAAI/bge-reranker-v2-m3` | Reranking | `models/reranker/bge-reranker` | HuggingFace (download) | pending |
| `Qwen/Qwen3.6-35B` | Extraction and judge model | `models/llm/qwen3.6-35b` | vLLM (pre-installed) | installed |

The first three models are downloaded from HuggingFace using `backend/scripts/download_models.py`.
The Qwen3.6-35B model is already installed and served via a local vLLM instance on the DGX. It is never downloaded by the script.

### Model Purposes

- **Dense embeddings (`bge-m3`)**: Used for semantic search and vector retrieval across the knowledge graph. This model produces fixed-size dense vector representations suitable for cosine similarity matching.
- **Token-level embeddings (`colbertv2.0`)**: Used for token-level relevance scoring. Unlike dense embeddings, colbert retains token-level representations enabling late-interaction matching between queries and documents.
- **Reranker (`bge-reranker`)**: Used as a cross-encoder reranker on top of initial retrieval results. Provides higher accuracy re-ranking at the cost of higher per-query compute.
- **LLM (`qwen3.6-35b`)**: Served via vLLM. Handles document extraction, governance judgment, and multi-turn reasoning tasks. This is the primary generative model.

---

## Running the Download Script

### Installation

Ensure `huggingface_hub` is installed:

```bash
pip install huggingface_hub
```

### Normal Download

```bash
cd .
python -m backend.scripts.download_models
```

This downloads all three models (bge-m3, colbertv2.0, bge-reranker) to their respective directories under `models/`, computes SHA-256 checksums, and updates `models/manifest.json`.

### Dry Run

Preview what would be downloaded without performing any downloads:

```bash
python -m backend.scripts.download_models --dry-run
```

### Manifest

The manifest file `models/manifest.json` tracks:

- Model name and purpose
- Storage path on disk
- SHA-256 checksum (populated after download)
- Download timestamp
- Quantization level
- Status (pending, downloaded, installed)

Models with status `installed` (such as Qwen3.6-35B) are automatically skipped by the download script.

---

## Air-Gapped Deployment Checklist

For environments without internet access, follow this checklist to deploy models on a disconnected machine.

### Step 1: Download Models on Connected Machine

On an internet-connected machine with the same OS and Python version:

```bash
cd /path/to/rckg
pip install huggingface_hub
python -m backend.scripts.download_models
```

Verify all three models downloaded successfully:

```bash
python -c "
import json
with open('models/manifest.json') as f:
    data = json.load(f)
for m in data['models']:
    if m['status'] == 'downloaded':
        print(f\"{m['name']}: checksum={m['sha256'][:16]}... files={m.get('file_count', 'unknown')}\")
"
```

### Step 2: Verify SHA-256 Checksums

Before transferring, record checksums:

```bash
python -c "
import json
with open('models/manifest.json') as f:
    data = json.load(f)
print(json.dumps(data, indent=2))
" > /tmp/manifest-checkpoint.json
```

### Step 3: Transfer Model Files to Disconnected Machine

Transfer both the model directories and the manifest:

```bash
# Using rsync or scp
rsync -avz models/ user@disconnected-host:/path/to/rckg/models/
```

Ensure the full directory structure is preserved:

```
models/
  embeddings/
    bge-m3/
    colbertv2.0/
  reranker/
    bge-reranker/
  llm/
    qwen3.6-35b/        # Already on DGX via vLLM
  manifest.json
```

### Step 4: Verify Checksums Match on Target Machine

On the disconnected machine, verify the manifest matches the pre-transfer checkpoint:

```bash
diff /tmp/manifest-checkpoint.json /path/to/rckg/models/manifest.json
```

If the diff shows only `last_updated` timestamp differences, the checksums match.

### Step 5: Update Manifest with Correct Checksums

If checksums differ (e.g., due to transfer corruption), re-verify:

```bash
python -c "
import hashlib
from pathlib import Path

models = {
    'BAAI/bge-m3': 'models/embeddings/bge-m3',
    'colbertv2.0-adept': 'models/embeddings/colbertv2.0',
    'BAAI/bge-reranker-v2-m3': 'models/reranker/bge-reranker',
}

for name, storage_path in models.items():
    path = Path(storage_path)
    if path.exists():
        # Hash all files in the directory
        total_hash = hashlib.sha256()
        for f in sorted(path.rglob('*')):
            if f.is_file():
                with open(f, 'rb') as fh:
                    for chunk in iter(lambda: fh.read(8192), b''):
                        total_hash.update(fh.name.encode())
                        total_hash.update(chunk)
        print(f'{name}: {total_hash.hexdigest()[:32]}...')
    else:
        print(f'{name}: MISSING')
"
```

### Step 6: Validate All Services Start Correctly

After model transfer:

1. Ensure vLLM is running with Qwen3.6-35B:
   ```bash
   curl http://localhost:8000/v1/models
   ```

2. Verify embedding models are loadable:
   ```bash
   python -c "
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('models/embeddings/bge-m3')
   embeddings = model.encode(['test query'])
   print(f'bge-m3: loaded, embedding dim={len(embeddings[0])}')
   "
   ```

3. Verify reranker is loadable:
   ```bash
   python -c "
   from sentence_transformers import CrossEncoder
   model = CrossEncoder('models/reranker/bge-reranker')
   scores = model.predict([['query', 'document']])
   print(f'bge-reranker: loaded, score={scores[0]:.4f}')
   "
   ```

4. Confirm all services start without errors:
   ```bash
   # Start each service and verify no model loading errors
   ```

---

## GPU Routing Documentation

### Architecture Overview

The system uses sequential execution of AI judges to avoid VRAM contention across multiple models.

### vLLM (Primary LLM)

- **Model**: `Qwen/Qwen3.6-35B` (4-bit quantized)
- **Runtime**: vLLM on dedicated GPU
- **VRAM Budget**: ~79-95GB
- **Concurrency Config**:
  - `max_model_len`: 8192 (controls maximum sequence length)
  - `num-gpus`: 1 (single GPU per vLLM instance)
  - `tensor-parallel-size`: 1 (no tensor parallelism for single GPU)

vLLM serves one model per instance. The Qwen3.6-35B model handles extraction and judgment tasks. The `num-gpus` flag in the vLLM startup command determines how many GPUs are allocated. For air-gapped deployments, ensure the model weights are already present on the target GPU.

### Embedding and Reranker Models (CPU)

- **Models**: `bge-m3`, `colbertv2.0`, `bge-reranker-v2-m3`
- **Runtime**: Python via `sentence-transformers` library
- **Device**: CPU (not GPU)
- **Memory Budget**: ~39GB RAM for Docker stack
- **Loading**: Loaded at Python runtime, not pre-loaded

These models load on-demand during query processing. They are not kept resident on GPU to avoid VRAM pressure on the vLLM instance.

### Sequential Judge Execution

To prevent VRAM contention:

1. **Extraction phase**: vLLM runs the Qwen3.6-35B model to extract structured data from documents.
2. **Embedding phase**: After extraction completes, embedding models load on CPU to create vector representations.
3. **Retrieval phase**: Vector search identifies relevant governance documents.
4. **Reranking phase**: The cross-encoder reranker scores retrieved documents.
5. **Judgment phase**: vLLM runs again to produce final governance judgments based on reranked results.

Each phase completes before the next begins. No two models load simultaneously on the same GPU.

### Memory Budget Summary

| Component | Memory | Device |
|---|---|---|
| vLLM (Qwen3.6-35B) | ~79-95GB | GPU |
| Docker stack (PostgreSQL, Redis, Kafka, Qdrant, etc.) | ~39GB | RAM |
| Python process (embedding/reranker models at load time) | ~6-8GB | RAM |
| **Total** | **~128GB** | |

The DGX has 128GB total memory. vLLM takes priority for GPU memory. Embedding and reranker models use system RAM, not GPU memory. This separation ensures no VRAM contention between the LLM and embedding pipelines.

### Configuration Recommendations

For production deployments:

- Set `--max-model-len 4096` if most documents are under 3K tokens (reduces vLLM memory by ~40%)
- Use `--num-gpus 1` for single-GPU DGX setup; increase only if running additional vLLM instances
- Monitor GPU memory with `nvidia-smi` during judge execution to confirm no overlap
- Consider running embedding/reranker on a separate CPU-only worker if document throughput becomes a bottleneck
