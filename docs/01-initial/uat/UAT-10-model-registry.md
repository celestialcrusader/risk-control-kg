# UAT-10: Model Registry Validation

**Covers**: INFRA-8
**Type**: Service Verification Test
**Effort**: ~5 minutes

## Objective

Verify that the model registry tracks available AI models, their download status, and provides health checks for the model infrastructure.

## Prerequisites

- UAT-01 passes (all infrastructure healthy)

## Steps

### Step 1: Check Model Registry Database

```bash
docker exec -it $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT model_name,
       version,
       model_path,
       is_available,
       downloaded_at,
       file_size_bytes,
       hash_sha256
FROM model_registry
ORDER BY model_name, version;
"
```

**Expected**: Rows for required models:
- Mistral 7B/8B Instruct (for extraction)
- BGE-M3 (for dense embeddings)
- ColBERT v2.0 (for token-level embeddings)

### Step 2: Verify Model Registry Module

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.model_registry import get_model_info, list_models, check_model_availability

# List all registered models
models = list_models()
print(f"Registered models: {len(models)}")
for m in models:
    print(f"  - {m['model_name']} v{m['version']} ({'available' if m['is_available'] else 'unavailable'})")

# Check availability of a specific model
for name in ["mistral", "bge-m3", "colbert"]:
    try:
        info = get_model_info(name)
        print(f"\n{name}: {info}")
    except Exception as e:
        print(f"\n{name}: not found - {e}")

# Health check
try:
    status = check_model_availability()
    print(f"\nModel health: {status}")
except Exception as e:
    print(f"\nModel health check (may fail without models): {e}")
PYEOF
```

### Step 3: Verify Model Configuration

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

# Check LLM model config used by extraction service
import app.services.extraction as extraction

print("Extraction LLM Configuration:")
print(f"  Provider:    {extraction.LLM_PROVIDER}")
print(f"  Endpoint:    {extraction.LLM_ENDPOINT}")
print(f"  Model:       {extraction.LLM_MODEL}")
print(f"  Temperature: {extraction.LLM_TEMPERATURE}")
print(f"  Max Tokens:  {extraction.LLM_MAX_TOKENS}")

# Check prompt template
try:
    template = extraction._load_prompt_template()
    print(f"\nPrompt template loaded: {len(template)} chars")
    print(f"First 200 chars: {template[:200]}...")
except Exception as e:
    print(f"\nPrompt template error: {e}")
PYEOF
```

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Model registry table | PostgreSQL query | Rows for Mistral, BGE-M3, ColBERT |
| 2 | Model registry module | Python API calls | list_models returns registered models |
| 3 | LLM configuration | Extraction service config | Provider, endpoint, model name, temperature |
| 4 | Prompt template | Template loading | Template file exists and loads correctly |

## Verification

- [ ] Model registry table contains entries for required AI models
- [ ] Model registry Python module can list and query models
- [ ] Extraction service is configured with the correct LLM endpoint and model
- [ ] Prompt template file exists and loads without error

## Pass/Fail Criteria

- **PASS**: All 4 checks succeed — models registered, API functional, extraction configured
- **FAIL**: Model registry empty, API errors, or extraction not configured

## Notes

- Model availability (`is_available` flag) may be false if models haven't been downloaded yet
- The extraction pipeline will use Ollama as fallback if vLLM is unavailable
- For full validation, models must be downloaded (see INFRA-8 story for download procedure)
