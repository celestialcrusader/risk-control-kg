# UAT-14: Golden 50 Local Validation

**Covers**: GOLDEN-1
**Type**: Local Validation Test
**Effort**: ~5 minutes

## Objective

Verify the Golden 50 benchmark dataset is correctly structured, the evaluation pipeline processes all 50 entries, and accuracy thresholds are enforced. This is the "shift-left" validation that blocks commits when extraction quality is below 90%.

## Prerequisites

- UAT-01 passes (infrastructure healthy)
- Python 3.12+ with pytest installed
- No external LLM or database required (fully deterministic)

## Steps

### Step 1: Verify Golden 50 Dataset Exists and Is Complete

```bash
echo "=== Golden 50 Dataset Validation ==="
python3 << 'PYEOF'
import json
from pathlib import Path

GOLDEN_50_PATH = Path("backend/tests/fixtures/golden_50.json")
assert GOLDEN_50_PATH.exists(), f"Missing: {GOLDEN_50_PATH}"

data = json.loads(GOLDEN_50_PATH.read_text())
assert len(data) == 50, f"Expected 50 entries, got {len(data)}"
print(f"PASS: {len(data)} entries")

# Validate required fields on each entry
REQUIRED_FIELDS = ["id", "paragraph_text", "expected_obligations", "framework_id", "annotated_by", "annotated_at"]
REQUIRED_OBL_FIELDS = ["prose", "action_verb", "subject_noun", "clause_ref"]
VALID_FRAMEWORKS = {"DORA", "HIPAA", "SOX", "GDPR", "PCI-DSS"}

for i, entry in enumerate(data):
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    assert not missing, f"Entry {i} ({entry.get('id', '?')}) missing: {missing}"
    
    # Validate ID format
    assert entry["id"].startswith("golden-"), f"Entry {i}: ID must start with 'golden-'"
    
    # Validate paragraph text is non-empty
    assert len(entry["paragraph_text"].strip()) > 10, f"Entry {i}: paragraph too short"
    
    # Validate obligations
    for j, obs in enumerate(entry["expected_obligations"]):
        obs_missing = [f for f in REQUIRED_OBL_FIELDS if f not in obs]
        assert not obs_missing, f"Entry {i} obs {j} missing: {obs_missing}"
    
    # Validate framework_id
    assert entry["framework_id"] in VALID_FRAMEWORKS, f"Entry {i}: invalid framework '{entry['framework_id']}'"

# Check framework diversity
frameworks = set(e["framework_id"] for e in data)
print(f"Frameworks: {sorted(frameworks)}")
assert len(frameworks) >= 3, f"Need >= 3 frameworks, got {len(frameworks)}"

# Check IDs are unique
ids = [e["id"] for e in data]
assert len(ids) == len(set(ids)), "Duplicate IDs found"

print(f"\nPASS: All {len(data)} entries valid")
print(f"  Frameworks: {sorted(frameworks)}")
print(f"  Unique IDs: {len(ids)}")
PYEOF
```

**Expected**: 50 entries, all with required fields, 3+ frameworks, no duplicate IDs.

### Step 2: Run the Golden 50 Test (Mock LLM — 100% Accuracy)

```bash
cd ./backend
python3 -m pytest tests/test_golden50.py::TestGolden50Integration::test_golden_50_passes_with_mocked_llm -v
```

**Expected**: PASS — mock LLM returns expected obligations, 50/50 match, 100% accuracy.

### Step 3: Run Full Golden 50 Test Suite

```bash
cd ./backend
python3 -m pytest tests/test_golden50.py -v
```

**Expected**: All 28 tests pass:
- `TestGolden50Fixture` (11 tests): Dataset validation
- `TestGolden50Evaluation` (8 tests): Accuracy computation and threshold logic
- `TestGolden50Integration` (7 tests): End-to-end pipeline
- `TestObligationSchema` (3 tests): Pydantic model validation

### Step 4: Verify Results File

```bash
python3 << 'PYEOF'
import json
from pathlib import Path

RESULTS_PATH = Path("backend/tests/fixtures/golden50_results.json")
assert RESULTS_PATH.exists(), f"Missing: {RESULTS_PATH}"

results = json.loads(RESULTS_PATH.read_text())

# Verify required fields
assert "total" in results, "Missing 'total' field"
assert "correct" in results, "Missing 'correct' field"
assert "accuracy" in results, "Missing 'accuracy' field"
assert "pass" in results, "Missing 'pass' field"
assert "entries" in results, "Missing 'entries' field"

assert results["total"] == 50, f"Expected total=50, got {results['total']}"
assert isinstance(results["pass"], bool), "pass must be boolean"
assert 0.0 <= results["accuracy"] <= 1.0, "accuracy must be 0.0-1.0"

print(f"Golden 50 Results:")
print(f"  Total:     {results['total']}")
print(f"  Correct:   {results['correct']}/{results['total']}")
print(f"  Accuracy:  {results['accuracy']:.1%}")
print(f"  Pass:      {results['pass']}")

assert results["pass"] == True, "Results should show pass when accuracy >= 90%"
print("\nPASS: Results file valid")
PYEOF
```

### Step 5: Verify Failure Path (Below 90% Threshold)

```bash
cd ./backend
python3 -m pytest tests/test_golden50.py::TestGolden50Integration::test_golden_50_fails_when_accuracy_below_threshold -v
```

**Expected**: PASS — test correctly fails when accuracy is 0% (all deliberately wrong). This confirms the 90% threshold blocks the pipeline.

### Step 6: Verify Threshold Boundary

```bash
cd ./backend
python3 << 'PYEOF'
import sys
sys.path.insert(0, ".")
from tests.test_golden50 import _accuracy_passes

# Test boundary values
assert _accuracy_passes(0.89) == False, "89% should fail"
assert _accuracy_passes(0.899) == False, "89.9% should fail"
assert _accuracy_passes(0.90) == True, "90% should pass"
assert _accuracy_passes(0.91) == True, "91% should pass"
assert _accuracy_passes(1.0) == True, "100% should pass"
assert _accuracy_passes(0.0) == False, "0% should fail"

print("PASS: Threshold boundary correct (>= 0.90)")
PYEOF
```

**Expected**: 90% is the minimum passing accuracy.

### Step 7: Verify Documentation

```bash
echo "=== Golden 50 Documentation ==="
head -40 ./docs/01-initial/golden50.md

echo ""
echo "=== File locations ==="
ls -la backend/tests/fixtures/golden_50.json
ls -la backend/tests/fixtures/golden50_results.json
ls -la backend/tests/test_golden50.py
ls -la docs/01-initial/golden50.md
```

**Expected**: Documentation exists with dataset format, usage instructions, and threshold details.

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Dataset structure | 50 entries, all fields | All validations pass |
| 2 | Mock LLM test | 100% accuracy | PASS |
| 3 | Full test suite | All 28 tests | All 28 pass |
| 4 | Results file | Valid JSON with correct fields | pass=true, accuracy>=0.90 |
| 5 | Failure path | Below 90% accuracy | Test correctly fails |
| 6 | Threshold boundary | 0.89 fail, 0.90 pass | Boundary correct |
| 7 | Documentation | File exists with key content | All files present |

## Verification

- [ ] golden_50.json has exactly 50 entries with all required fields
- [ ] Multiple frameworks represented (DORA, HIPAA, SOX, GDPR, PCI-DSS)
- [ ] Mock LLM test passes (50/50 accuracy)
- [ ] All 28 unit tests pass
- [ ] Results file is valid JSON with pass=true
- [ ] Below-90% accuracy correctly fails the test
- [ ] 90% boundary is correct (0.89 fail, 0.90 pass)
- [ ] Documentation exists

## Pass/Fail Criteria

- **PASS**: Steps 1-7 all succeed — dataset is complete, tests pass, threshold works, documentation present
- **FAIL**: Dataset has < 50 entries, tests fail, or threshold logic is incorrect

## Troubleshooting

| Issue | Check |
|-------|-------|
| `golden_50.json` not found | Ensure running from repo root: `cd .` |
| Tests import error | Ensure pytest is installed: `pip install pytest` |
| Wrong framework in data | Check golden_50.json entries — must be DORA, HIPAA, SOX, GDPR, or PCI-DSS |
| Accuracy < 90% in results | Re-generate results: re-run `test_golden_50_passes_with_mocked_llm` |
