# UAT-03: PDF-to-Markdown Conversion

**Covers**: INGEST-2
**Type**: Service Layer Test
**Effort**: ~10 minutes

## Objective

Verify that the PDF-to-Markdown conversion service correctly converts regulatory PDFs to structured Markdown text using MinerU (with Marker fallback).

## Prerequisites

- UAT-01 passes (all infrastructure healthy)
- MinerU or Marker model available (see INFRA-8 model registry)

## Steps

### Step 1: Verify Model Registry

```bash
# Check if Mistral model is registered
docker exec -it $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT model_name, version, model_path, is_available, downloaded_at
FROM model_registry
ORDER BY model_name;
"
```

### Step 2: Run PDF-to-Markdown Conversion

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.pdf_to_markdown import convert_pdf_to_markdown

input_pdf = "tests/test_data/sample_regulation.pdf"
output_md = "tests/test_data/sample_regulation.md"

try:
    result = convert_pdf_to_markdown(input_pdf, output_path=output_md)
    print(f"Status: {result.get('status')}")
    print(f"Output path: {result.get('output_path')}")
    print(f"Method: {result.get('method')}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
PYEOF
```

### Step 3: Verify Markdown Output

```bash
cat tests/test_data/sample_regulation.md
```

**Expected**:
- File exists at `tests/test_data/sample_regulation.md`
- Content contains structured Markdown text (headings, paragraphs)
- The regulation text "The organization must implement access controls" or similar appears in the output

### Step 4: Verify Conversion Metadata

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.pdf_to_markdown import convert_pdf_to_markdown
import json

result = convert_pdf_to_markdown("tests/test_data/sample_regulation.pdf")
print(json.dumps(result, indent=2, default=str))
PYEOF
```

**Expected**: Response includes:
- `status`: "success"
- `output_path`: path to generated Markdown file
- `method`: "mineru" or "marker" (whichever was used)
- `page_count`: number of pages in the PDF

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Model registry | `model_registry` table | Shows available models (e.g., Mistral, BGE-M3, ColBERT) |
| 2 | Conversion service | `convert_pdf_to_markdown()` | Returns status=success with output path |
| 3 | Output file | Markdown file content | Structured text with headings and paragraphs matching PDF content |
| 4 | Metadata | Response structure | Contains status, output_path, method, page_count fields |

## Verification

- [ ] Model registry table contains entries for required models
- [ ] PDF-to-Markdown conversion completes without error
- [ ] Output Markdown file contains the regulation text from the input PDF
- [ ] Response includes all required metadata fields

## Pass/Fail Criteria

- **PASS**: Steps 2-4 all succeed — conversion completes, output file exists with correct content, metadata is complete
- **FAIL**: Conversion raises an exception, output file is missing/empty, or metadata fields are missing

## Fallback Notes

If MinerU is unavailable:
- The service should fall back to Marker automatically
- If neither model is available, expect a graceful error message listing which models were tried
