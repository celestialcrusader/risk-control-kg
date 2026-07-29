# UAT-12: Langfuse Observability and Trace Linkage

**Covers**: OBSERV-1
**Type**: Observability Integration Test
**Effort**: ~15 minutes

## Objective

Verify that Langfuse tracing is correctly integrated across the extraction pipeline: extraction creates a trace with trace_id, judge links as child span, repair links as grandchild span. Confirm graceful degradation when Langfuse is unavailable.

## Prerequisites

- UAT-11 passes (quality loop works)
- Langfuse running at `http://localhost:3000` (optional — pipeline degrades gracefully without it)
- LLM serving Mistral model
- Environment variables set: `LANGFUSE_HOST`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`

## Steps

### Step 1: Verify Langfuse is Available

```bash
# Check if Langfuse is running
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health)
echo "Langfuse health endpoint returned: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "Langfuse is RUNNING"
    LANGFUSE_AVAILABLE=true
else
    echo "Langfuse is NOT available (pipeline will degrade gracefully)"
    LANGFUSE_AVAILABLE=false
fi
```

### Step 2: Check Environment Configuration

```bash
python3 << 'PYEOF'
import os

print("Langfuse Configuration:")
print(f"  LANGFUSE_HOST:      {os.getenv('LANGFUSE_HOST', 'NOT SET')}")
print(f"  LANGFUSE_SECRET_KEY: {os.getenv('LANGFUSE_SECRET_KEY', 'NOT SET')[:10]}...")
print(f"  LANGFUSE_PUBLIC_KEY: {os.getenv('LANGFUSE_PUBLIC_KEY', 'NOT SET')[:10]}...")
print(f"  LANGFUSE_RELEASE:   {os.getenv('LANGFUSE_RELEASE', 'NOT SET')}")
print(f"  LANGFUSE_ENVIRONMENT: {os.getenv('LANGFUSE_ENVIRONMENT', 'NOT SET')}")

# Verify langfuse is importable
try:
    import langfuse
    print(f"\n  langfuse package: INSTALLED (version {langfuse.__version__ if hasattr(langfuse, '__version__') else 'unknown'})")
except ImportError:
    print(f"\n  langfuse package: NOT INSTALLED (pipeline degrades gracefully)")
PYEOF
```

### Step 3: Extract and Verify Trace ID in Response

```bash
cat > /tmp/test_trace.md << 'EOF'
# Section 2: Network Security
The organization shall implement firewalls to protect information systems from unauthorized external access.
Access logs shall be generated for all network connections and retained for 12 months.
EOF

RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "'"$(cat /tmp/test_trace.md)"'"
  }')

echo "Extraction response:"
echo "$RESPONSE" | python3 -m json.tool

# Validate trace_id is present
TRACE_ID=$(echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
trace_id = data.get('trace_id', '')
print(f'Trace ID: [{trace_id}]')
# Validate UUID format if present
if trace_id:
    import re
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', trace_id), 'trace_id must be valid UUID4'
    print('Trace ID format: VALID UUID4')
else:
    print('NOTE: trace_id empty - Langfuse may not be configured (graceful degradation)')
")
echo "$TRACE_ID"
```

**Expected**: If Langfuse is available, `trace_id` should be a valid UUID4. If not available, empty string (graceful degradation).

### Step 4: Verify Trace Linkage with Judge

```bash
OBLIGATION_JSON=$(echo "$RESPONSE" | python3 -c "
import sys, json
obls = json.load(sys.stdin).get('obligations', [])
if obls:
    print(json.dumps(obls[0]))
else:
    print('{}')
")

# Pass trace_id to judge
curl -s -X POST http://localhost:8000/api/v1/judge \
  -H "Content-Type: application/json" \
  -d '{
    "obligation": '"$OBLIGATION_JSON"',
    "original_markdown": "'"$(cat /tmp/test_trace.md)"'",
    "trace_id": "'"$TRACE_ID"'"
  }' | python3 -m json.tool
```

**Expected**: HTTP 200. If Langfuse is available, the judge span should appear under the extraction trace in Langfuse UI.

### Step 5: Verify Trace Linkage with Repair

```bash
# Submit for repair with same trace_id
curl -s -X POST http://localhost:8000/api/v1/repair \
  -H "Content-Type: application/json" \
  -d '{
    "obligation": '"$OBLIGATION_JSON"',
    "judgment_feedback": "Verify all required fields are present.",
    "original_markdown": "'"$(cat /tmp/test_trace.md)"'",
    "trace_id": "'"$TRACE_ID"'"
  }' | python3 -m json.tool
```

**Expected**: HTTP 200. If Langfuse is available, repair attempt should appear as grandchild span under extraction trace.

### Step 6: Verify Graceful Degradation

```bash
# Use Python-based approach: temporarily remove langfuse_tracing from module cache
# and replace the module at import time to test conditional import path
python3 << 'PYEOF'
import sys, os, json, subprocess

# 1. Clear any cached import of langfuse_tracing
for key in list(sys.modules.keys()):
    if "langfuse" in key.lower():
        del sys.modules[key]

# 2. Rename the file temporarily
tracing_path = "backend/app/services/langfuse_tracing.py"
backup_path = tracing_path + ".bak"
os.rename(tracing_path, backup_path)

try:
    # 3. Run extraction without langfuse_tracing available
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:8000/api/v1/extract",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"markdown_content": open("/tmp/test_trace.md").read()})],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    print(f"obligation_count: {data.get('obligation_count', '?')}")
    print(f"trace_id: [{data.get('trace_id', '')}]")
    print(f"storage_succeeded: {data.get('storage_succeeded', '?')}")

    assert data.get('obligation_count', 0) >= 0, "Extraction should still work"
    assert data.get('storage_succeeded', False) == True, "Storage should succeed"
    assert data.get('trace_id', '') == '', "trace_id should be empty without langfuse"
    print("PASS: Graceful degradation works — extraction succeeds with empty trace_id")
finally:
    # 4. Restore the file
    os.rename(backup_path, tracing_path)
PYEOF
```

**Expected**: Extraction succeeds (HTTP 200) with empty `trace_id` when Langfuse tracing module is unavailable. No errors or 500 responses.

### Step 7: Verify Langfuse Trace in Dashboard

```bash
if [ "$LANGFUSE_AVAILABLE" = true ]; then
    echo "Open Langfuse dashboard: http://localhost:3000"
    echo "Search for trace ID: $TRACE_ID"
    echo "Expected: 1 trace with 1-3 linked spans (extraction, judge, repair)"
else
    echo "Langfuse not available — cannot verify dashboard linkage"
    echo "Install and run Langfuse to verify: docker run -p 3000:3000 langfuse/langfuse:latest"
fi
```

**Expected**: In Langfuse UI, see extraction trace with judge (child) and repair (grandchild) spans if Langfuse is available.

### Step 8: Run Unit Tests

```bash
cd /home/zackchow/coding/rckg/backend
python3 -m pytest tests/test_langfuse_tracing.py -v
```

**Expected**: All tests pass. Tests verify UUID format generation and conditional import behavior.

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Langfuse health | HTTP status | 200 (or skip if not running — pipeline degrades gracefully) |
| 2 | Config check | Environment variables | LANGFUSE_HOST, keys, release, environment set |
| 3 | Trace ID | Extraction response | Valid UUID4 or empty string (graceful degradation) |
| 4 | Judge linkage | HTTP 200 | Judge accepts trace_id parameter |
| 5 | Repair linkage | HTTP 200 | Repair accepts trace_id parameter |
| 6 | Graceful degradation | Extraction without Langfuse | HTTP 200, trace_id empty, no errors |
| 7 | Dashboard | Langfuse UI | Trace with linked spans visible |
| 8 | Unit tests | test_langfuse_tracing.py | All tests pass |

## Verification

- [ ] Extraction returns valid UUID4 trace_id when Langfuse is available
- [ ] Judge and repair accept trace_id and link to parent trace
- [ ] Extraction works (HTTP 200) when Langfuse is unavailable (graceful degradation)
- [ ] Empty string trace_id returned when Langfuse is unavailable
- [ ] Langfuse dashboard shows linked traces when available
- [ ] All langfuse_tracing unit tests pass

## Pass/Fail Criteria

- **PASS**: Steps 1-5 succeed with trace_id linking; Step 6 confirms graceful degradation; Step 8 tests pass
- **FAIL**: Extraction fails with 500 when Langfuse unavailable, or trace_id format is invalid

## Troubleshooting

| Issue | Check |
|-------|-------|
| trace_id always empty | Check LANGFUSE env vars are set; verify langfuse_tracing.py exists |
| Langfuse connection refused | Check LANGFUSE_HOST matches running container; `curl http://localhost:3000/api/health` |
| Trace not visible in dashboard | Check LANGFUSE_ENVIRONMENT matches filter; verify trace_id format is UUID4 |
| Tests fail when langfuse not installed | Verify conditional import works: `python3 -c "from app.services.langfuse_tracing import extract_and_trace"` should not raise ImportError |
