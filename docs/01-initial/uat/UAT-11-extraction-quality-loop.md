# UAT-11: Extraction with Quality Loop (Judge + Repair + Silver Layer)

**Covers**: EXTRACT-2, EXTRACT-3, EXTRACT-4
**Type**: API Functional Test
**Effort**: ~25 minutes

## Objective

Verify the complete obligation extraction quality loop: extract from Markdown, judge the quality via LLM-as-Judge, repair low-scoring obligations iteratively, and store validated results in the Silver layer.

## Prerequisites

- UAT-01 passes (all infrastructure healthy)
- LLM serving Mistral (or Ollama with `mistral` model) for extraction
- LLM serving Llama 3.1 for judge (or same Mistral model as fallback)
- UAT-08 passes (basic extraction works)

## Steps

### Step 1: Prepare Sample Regulatory Text

```bash
cat > /tmp/test_judge_repair.md << 'EOF'
# Section 5: Data Protection

## 5.1 Data Classification
All personally identifiable information shall be classified as sensitive data and protected with encryption at rest and in transit.
Financial records shall be retained for a minimum of seven years in compliance with regulatory requirements.
Access to patient health information shall be restricted to authorized personnel with a documented need-to-know.

## 5.2 Security Controls
The organization shall implement multi-factor authentication for all systems handling regulated data.
Automated scanning tools shall be deployed to detect unauthorized access attempts on a continuous basis.
EOF

echo "Test file: $(wc -l < /tmp/test_judge_repair.md) lines"
```

### Step 2: Extract Obligations

```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_content": "'"$(cat /tmp/test_judge_repair.md)"'",
    "source_document_id": "550e8400-e29b-41d4-a716-446655440000"
  }')

echo "$RESPONSE" | python3 -m json.tool

# Extract first obligation ID and the full obligations array
OBL_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; obls=json.load(sys.stdin).get('obligations',[]); print(obls[0]['id'] if obls else '')")
echo "Extracted obligation ID: $OBL_ID"
```

**Expected**: HTTP 200 with at least 3 obligations extracted.

### Step 3: Judge the First Extracted Obligation

```bash
OBLIGATION_JSON=$(echo "$RESPONSE" | python3 -c "
import sys, json
obls = json.load(sys.stdin).get('obligations', [])
if obls:
    print(json.dumps(obls[0]))
else:
    print('{}')
")

TRACE_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trace_id',''))")
echo "Trace ID: $TRACE_ID"

curl -s -X POST http://localhost:8000/api/v1/judge \
  -H "Content-Type: application/json" \
  -d '{
    "obligation": '"$OBLIGATION_JSON"',
    "original_markdown": "'"$(cat /tmp/test_judge_repair.md)"'",
    "trace_id": "'"$TRACE_ID"'"
  }' | python3 -m json.tool
```

**Expected**: HTTP 200 with judgment containing:
- `scores`: dict with `metadata_accuracy`, `legal_alignment`, `rule_semantics` (each 0.0-1.0)
- `status`: either `"approved"` (all >= 0.80) or `"repair"` (any < 0.80)
- `feedback`: string explaining scores
- `trace_id`: links to parent extraction trace

### Step 4: Repair a Low-Scoring Obligation

```bash
# Submit the obligation back through the repair endpoint with judge feedback
curl -s -X POST http://localhost:8000/api/v1/repair \
  -H "Content-Type: application/json" \
  -d '{
    "obligation": '"$OBLIGATION_JSON"',
    "judgment_feedback": "The action_verb should include the modal verb shall for regulatory compliance.",
    "original_markdown": "'"$(cat /tmp/test_judge_repair.md)"'",
    "max_attempts": 3,
    "trace_id": "'"$TRACE_ID"'"
  }' | python3 -m json.tool
```

**Expected**: HTTP 200 with one of:
- `status: "repaired"` — obligation fixed in one or more attempts
- `status: "rejected"` — all repair attempts exhausted
- `status: "original_kept"` — empty feedback provided

### Step 5: Verify Trace ID Linkage

```bash
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, "backend")

# Verify that trace_id flows through the pipeline
from app.api.extract import ExtractionResponse
from app.api.judge import JudgeRequest
from app.api.repair import RepairRequest

# Check that all schemas accept/return trace_id
extract_resp = ExtractionResponse(obligation_count=1, obligations=[{}], storage_succeeded=True, trace_id="test-trace-123")
assert extract_resp.trace_id == "test-trace-123", "ExtractResponse should include trace_id"
print("PASS: ExtractionResponse includes trace_id")

judge_req = JudgeRequest(
    obligation={"id": "test-1", "prose": "test", "action_verb": "test", "subject_noun": "test", "clause_ref": "test"},
    original_markdown="test",
    trace_id="test-trace-123"
)
assert judge_req.trace_id == "test-trace-123", "JudgeRequest should accept trace_id"
print("PASS: JudgeRequest accepts trace_id")

repair_req = RepairRequest(
    obligation={"id": "test-1", "prose": "test", "action_verb": "test", "subject_noun": "test", "clause_ref": "test"},
    judgment_feedback="test",
    original_markdown="test",
    trace_id="test-trace-123"
)
assert repair_req.trace_id == "test-trace-123", "RepairRequest should accept trace_id"
print("PASS: RepairRequest accepts trace_id")

print("\nAll trace_id linkage schemas verified.")
PYEOF
```

### Step 6: Verify Silver Layer Storage

```bash
docker exec $(docker-compose ps -q postgres) psql -U rckg -d rckg -c "
SELECT control_id,
       action_verb,
       subject_noun,
       LEFT(objective_text, 60) AS preview,
       status,
       version
FROM semantic_controls
ORDER BY created_at DESC
LIMIT 10;
"
```

**Expected**: Rows with extracted obligation data. Status will be `'pending_validation'` by default — quality-based status updates are planned for a later sprint.

### Step 7: Test Empty Feedback Path (original_kept)

```bash
curl -s -X POST http://localhost:8000/api/v1/repair \
  -H "Content-Type: application/json" \
  -d '{
    "obligation": '"$OBLIGATION_JSON"',
    "judgment_feedback": "",
    "original_markdown": "'"$(cat /tmp/test_judge_repair.md)"'"
  }' | python3 -c "
import sys, json
resp = json.load(sys.stdin)
print(f'Status: {resp[\"status\"]}')
assert resp['status'] == 'original_kept', f'Expected original_kept, got {resp[\"status\"]}'
assert resp['attempts'] == 0, f'Expected 0 attempts, got {resp[\"attempts\"]}'
print('PASS: Empty feedback returns original_kept with 0 attempts')
"
```

**Expected**: `status: "original_kept"`, `attempts: 0`.

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Test data | Markdown file | Multiple obligation sentences with headings |
| 2 | Extract | HTTP 200 | Obligations extracted with all required fields |
| 3 | Judge | HTTP 200 | Scores (0-1), status (approved/repair), feedback, trace_id |
| 4 | Repair | HTTP 200 | Obligation repaired, rejected, or original_kept |
| 5 | Trace linkage | Schema validation | All 3 endpoints accept/pass trace_id correctly |
| 6 | Silver layer | PostgreSQL query | Stored rows with status/version tracking |
| 7 | Empty feedback | Repair with empty feedback | Returns original_kept, 0 attempts |

## Verification

- [ ] Extraction produces obligations from regulatory Markdown
- [ ] Judge returns scores, status, and feedback for each obligation
- [ ] Repair re-submits obligations with judge feedback
- [ ] Repair returns repaired/rejected/original_kept correctly
- [ ] Trace ID is returned by extraction and accepted by judge/repair
- [ ] Silver layer stores obligations with quality status
- [ ] Empty judge feedback returns original_kept immediately

## Pass/Fail Criteria

- **PASS**: Steps 2-7 all succeed — extraction, judgment, repair, trace linkage, and storage work end-to-end
- **FAIL**: Any step returns error, missing required fields, or trace_id linkage breaks

## Troubleshooting

| Issue | Check |
|-------|-------|
| LLM returns no obligations | Verify LLM model is loaded and responding |
| Judge returns HTTP 500 | Check LLM provider is reachable for judgment |
| Repair returns always rejected | Check that LLM can parse repair prompts; try increasing LLM_MAX_TOKENS |
| Trace ID is empty | Verify langfuse_tracing module is importable; check extraction.py wiring |
