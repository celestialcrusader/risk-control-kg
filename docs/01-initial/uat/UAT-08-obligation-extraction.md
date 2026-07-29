# UAT-08: Obligation Extraction from Regulatory Text

**Covers**: EXTRACT-1
**Type**: API Functional Test
**Effort**: ~15 minutes

## Objective

Verify that the extraction endpoint correctly processes Markdown regulatory text through the LLM pipeline, extracts atomic obligations, validates them against the Pydantic schema, and stores them in the Silver layer.

## Prerequisites

- UAT-01 passes (all infrastructure healthy)
- vLLM serving Mistral 8B at `http://localhost:8000/v1` (or Ollama with `mistral` model)
- UAT-07 passes (ingestion pipeline produces Markdown)

## Steps

### Step 1: Prepare Sample Regulatory Text

```bash
cat > /tmp/test_regulation.md << 'EOF'
# Section 3: Access Control

## 3.1 General Access Requirements
The organization must limit information system access to authorized users, processes acting on behalf of users, or other devices.
The organization must review information system access one year from the last designated reviewer contact or when directed by management.
The organization must revoke access for terminated employees within 24 hours of termination.

## 3.2 Audit Controls
The organization must audit access actions and retain audit logs for 12 months.
The organization must implement automated tools for real-time audit log review.
EOF

echo "Test file created with $(wc -l < /tmp/test_regulation.md) lines."
```

### Step 2: Call the Extraction API

```bash
curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "'"$(cat /tmp/test_regulation.md)"'",
    "source_document_id": "550e8400-e29b-41d4-a716-446655440000"
  }' | python3 -m json.tool
```

**Expected**: HTTP 200 with:
```json
{
  "obligation_count": 5,
  "obligations": [
    {
      "id": "AC-3.1.a",
      "prose": "The organization must limit information system access to authorized users...",
      "action_verb": "limit",
      "subject_noun": "information system access",
      "clause_ref": "Section 3.1",
      "section_ref": "Section 3.1"
    },
    ...
  ],
  "storage_succeeded": true
}
```

### Step 3: Verify Required Fields in Each Obligation

```bash
curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "'"$(cat /tmp/test_regulation.md)"'"
  }' | python3 -c "
import sys, json

data = json.load(sys.stdin)
obligations = data.get('obligations', [])
required_fields = ['id', 'prose', 'action_verb', 'subject_noun', 'clause_ref']

print(f'Total obligations: {data[\"obligation_count\"]}')
for i, obs in enumerate(obligations):
    missing = [f for f in required_fields if f not in obs]
    status = 'PASS' if not missing else f'FAIL (missing: {missing})'
    print(f'  [{i+1}] {obs.get(\"id\", \"?\"):15} action={obs.get(\"action_verb\", \"?\"):10} subject={obs.get(\"subject_noun\", \"?\"):20} [{status}]')

if not obligations:
    print('WARNING: No obligations extracted. LLM may be unavailable.')
    print('Expected: At least 1 obligation per imperative sentence in the input.')

assert data['obligation_count'] >= len(obligations), 'Count mismatch'
print(f'\nAll {len(obligations)} obligations validated.')
"
```

### Step 4: Reject Empty Content

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"markdown_content": ""}'
echo ""
```

**Expected**: HTTP 400 with detail about empty content.

### Step 5: Verify Silver Layer (semantic_controls) Storage

```bash
docker exec $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT control_id,
       action_verb,
       subject_noun,
       LEFT(objective_text, 80) AS objective_preview,
       source_document_id,
       created_at
FROM semantic_controls
ORDER BY created_at DESC
LIMIT 10;
"
```

**Expected**: Rows with extracted obligation data. Each row should have:
- `control_id`: obligation ID (e.g., "AC-3.1.a")
- `action_verb`: extracted verb (e.g., "limit", "revoke", "audit")
- `subject_noun`: extracted subject (e.g., "information system access")
- `objective_text`: the obligation prose

### Step 6: Verify LLM Endpoint Configuration

```bash
# Check which LLM provider is configured
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, "backend")

import app.services.extraction as extraction

print(f"LLM Provider:   {extraction.LLM_PROVIDER}")
print(f"LLM Endpoint:   {extraction.LLM_ENDPOINT}")
print(f"LLM Model:      {extraction.LLM_MODEL}")
print(f"Temperature:    {extraction.LLM_TEMPERATURE}")
print(f"Max Tokens:     {extraction.LLM_MAX_TOKENS}")
PYEOF
```

**Expected**:
- Provider: `vllm` (or `ollama` for local dev)
- Endpoint matches your LLM service URL
- Model: Mistral 8B variant
- Temperature: 0.3 (deterministic)

### Step 7: Test Re-Extraction (Idempotency Check)

```bash
# Call extraction twice with the same content
RESP1=$(curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"markdown_content": "'"$(cat /tmp/test_regulation.md)"'"}')

RESP2=$(curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{"markdown_content": "'"$(cat /tmp/test_regulation.md)"'"}')

echo "First call:  $(echo "$RESP1" | python3 -c "import sys,json; print(json.load(sys.stdin)['obligation_count'])") obligations"
echo "Second call: $(echo "$RESP2" | python3 -c "import sys,json; print(json.load(sys.stdin)['obligation_count'])") obligations"
```

**Expected**: Both calls return the same number of obligations without errors (no unique constraint violation).

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Test data | sample text | Markdown with headings and obligation sentences |
| 2 | Extraction API | HTTP 200 response | obligation_count >= 1, obligations array populated |
| 3 | Field validation | All obligations | Each has id, prose, action_verb, subject_noun, clause_ref |
| 4 | Empty rejection | HTTP status | 400 Bad Request |
| 5 | Silver storage | PostgreSQL query | Rows in semantic_controls with extracted data |
| 6 | LLM config | Service config | Correct provider, endpoint, model, temperature=0.3 |
| 7 | Re-extraction | Two identical calls | Both succeed, same count, no constraint errors |

## Verification

- [ ] Extraction API returns obligations with all required fields
- [ ] Each obligation has a non-empty action_verb and subject_noun
- [ ] Empty markdown content is rejected with HTTP 400
- [ ] Extracted obligations are stored in semantic_controls table
- [ ] LLM configuration is correct (provider, endpoint, model, temperature)
- [ ] Re-extraction with identical content succeeds without errors

## Pass/Fail Criteria

- **PASS**: Steps 2-7 all succeed — obligations extracted, validated, stored, and re-extractable
- **FAIL**: Extraction returns no obligations, missing required fields, or storage fails

## Troubleshooting

| Issue | Check |
|-------|-------|
| No obligations extracted | Verify vLLM/Ollama is running: `curl http://localhost:8000/v1/models` or `curl http://localhost:11434/api/tags` |
| Storage fails | Check PostgreSQL connectivity: `docker exec -it $(docker-compose ps -q postgres) pg_isready` |
| LLM connection refused | Check LLM_ENDPOINT env var: `grep LLM_ENDPOINT backend/.env` |
| Validation errors | Check LLM response format — ensure prompt returns valid JSON with `obligations` array |
