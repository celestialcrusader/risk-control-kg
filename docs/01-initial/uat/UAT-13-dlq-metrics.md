# UAT-13: DLQ Metrics and Early Warning System

**Covers**: DLQ-1
**Type**: CLI Functional Test
**Effort**: ~10 minutes

## Objective

Verify that DLQ metrics SQL queries and the Python CLI runner produce accurate accuracy ratios, framework failure rankings, and alert triggers when DLQ counts exceed the 10% threshold.

## Prerequisites

- UAT-01 passes (PostgreSQL running)
- DLQ tables exist (`extraction_dlq`, `validation_dlq`, `crosswalk_dlq`)
- At least some data in `semantic_controls` (from EXTRACT-1)

## Steps

### Step 1: Verify SQL File Content

```bash
echo "=== DLQ Metrics SQL File ==="
ls -la /home/zackchow/coding/rckg/backend/scripts/dlq_metrics.sql

echo ""
echo "=== Query sections ==="
grep "^--" /home/zackchow/coding/rckg/backend/scripts/dlq_metrics.sql

echo ""
echo "=== Query names ==="
grep "^-- name:" /home/zackchow/coding/rckg/backend/scripts/dlq_metrics.sql || \
  grep "SELECT" /home/zackchow/coding/rckg/backend/scripts/dlq_metrics.sql
```

**Expected**: File exists with 3 queries: gold_dlq_ratio, framework_failures, failure_reasons.

### Step 2: Verify Python Module Structure

```bash
cd /home/zackchow/coding/rckg/backend
python3 << 'PYEOF'
from scripts import dlq_metrics

# Verify required functions exist
assert hasattr(dlq_metrics, "should_alert"), "Missing should_alert()"
assert hasattr(dlq_metrics, "compute_accuracy_ratio"), "Missing compute_accuracy_ratio()"
assert hasattr(dlq_metrics, "collect_and_report_metrics"), "Missing collect_and_report_metrics()"
assert hasattr(dlq_metrics, "run_metrics"), "Missing run_metrics()"

# Verify default threshold
assert dlq_metrics.DEFAULT_ALERT_THRESHOLD == 0.10, f"Expected 0.10 threshold, got {dlq_metrics.DEFAULT_ALERT_THRESHOLD}"

print("PASS: All required functions present")
print(f"  DEFAULT_ALERT_THRESHOLD = {dlq_metrics.DEFAULT_ALERT_THRESHOLD}")

# Test alert threshold logic
assert dlq_metrics.should_alert(5, 50) == False, "5/55 = 9.1% NOT > 10%"
assert dlq_metrics.should_alert(10, 50) == True, "10/60 = 16.7% > 10%"
assert dlq_metrics.should_alert(5, 45) == False, "5/50 = 10.0% NOT > 10% should be False"
assert dlq_metrics.should_alert(1, 9) == False, "1/10 = 10.0% NOT > 10% should be False"
assert dlq_metrics.should_alert(11, 45) == True, "11/56 = 19.6% > 10% should be True"

# Test accuracy ratio
assert dlq_metrics.compute_accuracy_ratio(90, 10) == 0.9, "90/100 = 0.9"
assert dlq_metrics.compute_accuracy_ratio(100, 0) == 1.0, "100/100 = 1.0"
assert dlq_metrics.compute_accuracy_ratio(0, 10) == 0.0, "0/10 = 0.0"

print("PASS: Alert and accuracy logic verified")
PYEOF
```

### Step 3: Run DLQ Metrics CLI

```bash
cd /home/zackchow/coding/rckg/backend
python3 -m scripts.run_dlq_metrics --verbose

echo ""
echo "Exit code: $?"
```

**Expected**:
- Script runs without error
- Prints accuracy ratio, DLQ count, gold count
- Prints framework failures summary
- Prints failure reasons summary
- No alert if accuracy >= 90%
- Alert warning if accuracy < 90%
- Exit code 0 (no alert) or 2 (alert triggered)

### Step 4: Verify Alert Threshold with Custom Threshold

```bash
cd /home/zackchow/coding/rckg/backend
python3 << 'PYEOF'
from scripts.run_dlq_metrics import run_metrics
import logging

# Test with very low threshold (always triggers alert)
print("=== Testing alert with threshold=0.01 (should always alert) ===")
try:
    run_metrics(threshold=0.01, verbose=True)
except SystemExit as e:
    print(f"Exit code: {e.code}")
    if e.code == 2:
        print("PASS: Alert triggered with low threshold")
PYEOF
```

**Expected**: With threshold=0.01, alert triggers immediately (exit code 2).

### Step 5: Verify Documentation

```bash
echo "=== DLQ Metrics Documentation ==="
head -30 /home/zackchow/coding/rckg/docs/01-initial/dlq-metrics.md

echo ""
echo "=== File locations ==="
ls -la /home/zackchow/coding/rckg/backend/scripts/dlq_metrics.py
ls -la /home/zackchow/coding/rckg/backend/scripts/dlq_metrics.sql
ls -la /home/zackchow/coding/rckg/backend/scripts/run_dlq_metrics.py
ls -la /home/zackchow/coding/rckg/docs/01-initial/dlq-metrics.md
```

**Expected**: All files exist and documentation describes queries, usage, and alert thresholds.

### Step 6: Run Unit Tests

```bash
cd /home/zackchow/coding/rckg/backend
python3 -m pytest tests/test_dlq_metrics.py -v
```

**Expected**: All 32 tests pass. Coverage includes:
- Alert threshold logic (above/below/boundary/zero/negative)
- Accuracy ratio computation
- Metrics collection with mocked DB
- SQL file content verification
- CLI entry point

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | SQL file | File exists with 3 queries | gold_dlq_ratio, framework_failures, failure_reasons |
| 2 | Module structure | Functions exist | should_alert, compute_accuracy_ratio, collect_and_report_metrics |
| 3 | CLI run | run_dlq_metrics succeeds | Accuracy ratio printed, no crash |
| 4 | Alert threshold | threshold=0.01 triggers alert | Exit code 2 |
| 5 | Documentation | doc file exists | Describes queries, thresholds, usage |
| 6 | Unit tests | test_dlq_metrics.py | 32/32 pass |

## Verification

- [ ] SQL file contains 3 correct queries
- [ ] Python module functions work correctly
- [ ] CLI runs without error
- [ ] Alert triggers when DLQ ratio > threshold
- [ ] Alert does not trigger when DLQ ratio <= threshold (exactly 10%)
- [ ] Documentation exists and is accurate
- [ ] All 32 unit tests pass

## Pass/Fail Criteria

- **PASS**: Steps 1-6 all succeed — queries, metrics, alerting, and tests work correctly
- **FAIL**: CLI crashes, alert logic incorrect, or tests fail

## Troubleshooting

| Issue | Check |
|-------|-------|
| Module not found | Ensure running from backend/ directory: `cd backend && python3 -m scripts.run_dlq_metrics` |
| Alert always triggers | Check DB has data; with empty DLQ and empty gold, edge case may trigger |
| SQL query errors | Verify `extraction_dlq` table exists in PostgreSQL |
| Exit code 1 | Script error (check logs); exit code 2 means alert triggered |
