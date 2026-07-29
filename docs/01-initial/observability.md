# Langfuse Observability Configuration

## Dashboard Access

- **URL**: `http://localhost:3000`
- **Default credentials**: Check your `.env` file for `LANGFUSE_SECRET_KEY` and `LANGFUSE_PUBLIC_KEY`

## Environment Variables

Add the following to your `.env` file:

```bash
# Langfuse tracing
LANGFUSE_HOST=http://localhost:3000
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_RELEASE=1.0.0
LANGFUSE_ENVIRONMENT=dev
```

## Trace ID Linkage

The extraction pipeline creates a trace on every extraction call:

1. **Extraction** creates a trace with a `trace_id`
2. **Judge** receives the `trace_id` and links as a child span
3. **Repair** receives the `trace_id` and links as a grandchild span

### API Usage

```bash
# Step 1: Extract — returns trace_id in response
RESP=$(curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"markdown_content": "# Test", "source_document_id": "doc-001"}')

TRACE_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trace_id',''))")

# Step 2: Judge — pass trace_id for linkage
curl -s -X POST http://localhost:8000/api/v1/judge \
  -H "Content-Type: application/json" \
  -d "{\"obligation\": {\"id\": \"AC-1\", ...}, \"original_markdown\": \"...\", \"trace_id\": \"$TRACE_ID\"}"

# Step 3: Repair — pass trace_id for linkage
curl -s -X POST http://localhost:8000/api/v1/repair \
  -H "Content-Type: application/json" \
  -d "{\"obligation\": {...}, \"judgment_feedback\": \"...\", \"original_markdown\": \"...\", \"trace_id\": \"$TRACE_ID\"}"
```

## Traced Events

- `extraction.started` / `extraction.completed` — extraction call with prompt and completion
- `obligation-judge-evaluation` — judge scoring with parent observation
- `obligation-repair-attempt` — repair attempts with grandparent observation
- `extraction-failure` — failed extractions with judge feedback and repair count

## Token Usage

Each trace captures:
- `promptTokens` — input token count
- `completionTokens` — output token count
- `totalTokens` — sum of above

## Environment Scoping

Set `LANGFUSE_ENVIRONMENT` to `dev` or `prod` for project scoping in Langfuse.

## Graceful Degradation

If Langfuse is not installed or unavailable, all tracing functions return gracefully without breaking the pipeline. The conditional import pattern:

```python
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
```

All public functions wrap Langfuse calls in `try/except` so failures never propagate.
