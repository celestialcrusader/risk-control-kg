# DLQ-1: SQL-Based DLQ Metrics and Early Warning System

## Overview

This document describes the SQL-based metrics system for monitoring Dead Letter Queue (DLQ) accuracy. These queries serve as a "poor man's dashboard" for accuracy tracking until a full Prometheus/Grafana stack is built.

## Purpose

As a team lead, you need visibility into system accuracy without a dedicated dashboard. The DLQ metrics system surfaces:

- **Overall accuracy ratio**: What fraction of records make it to the Gold layer vs. ending up in the DLQ.
- **Framework failure breakdown**: Which frameworks (SOC2, HIPAA, etc.) have the most DLQ entries.
- **Common failure reasons**: Which error codes appear most frequently, guiding prompt tuning.

## Alert Threshold

The system triggers a **WARNING** alert when:

```
dlq_count / (gold_count + dlq_count) > 0.10  (10%)
```

When this threshold is exceeded, a warning is logged:

```
ALERT: DLQ ratio 0.1304 exceeds threshold 0.1000 (gold=100, dlq=15, threshold=10.00%)
```

**Action**: When the alert fires, "stop the line" -- investigate prompt quality for the affected framework and reason codes before continuing data ingestion.

## DLQ Tables

| Table | Description |
|---|---|
| `extraction_dlq` | Failed extractions (score < 0.80 after 3 repair attempts) |
| `validation_dlq` | Failed dual-judge validations (Logic < 0.95 or Technical < 1.0) |
| `crosswalk_dlq` | Failed crosswalk mappings (low confidence) |

## SQL Queries

Three essential queries are defined in `backend/scripts/dlq_metrics.sql`:

### Query 1: Gold vs. DLQ Ratio

```sql
SELECT
    COUNT(*) AS gold_count,
    (SELECT COUNT(*) FROM extraction_dlq) AS dlq_count,
    COUNT(*)::FLOAT / (COUNT(*) + (SELECT COUNT(*) FROM extraction_dlq)) AS accuracy_ratio
FROM semantic_controls
WHERE status = 'approved';
```

### Query 2: Framework with Most Failures

```sql
SELECT
    sc.framework_name,
    COUNT(*) AS failure_count
FROM extraction_dlq edq
JOIN semantic_controls sc ON edq.bronze_record_id = sc.id
GROUP BY sc.framework_name
ORDER BY failure_count DESC
LIMIT 10;
```

### Query 3: Common Failure Reason Codes

```sql
SELECT
    reason,
    COUNT(*) AS count
FROM extraction_dlq
GROUP BY reason
ORDER BY count DESC
LIMIT 10;
```

## Usage

### Running the Metrics Script

```bash
# Run with default 10% threshold
python -m backend.scripts.run_dlq_metrics

# Run with custom threshold (15%)
python -m backend.scripts.run_dlq_metrics --threshold 0.15

# Verbose output
python -m backend.scripts.run_dlq_metrics --verbose
```

### Running SQL Directly

```bash
psql -d rckg_db -f backend/scripts/dlq_metrics.sql
```

### Programmatic Usage

```python
from scripts.dlq_metrics import should_alert, compute_accuracy_ratio

# Check alert condition
if should_alert(dlq_count=15, gold_count=100):
    print("ALERT: Accuracy below threshold")

# Compute accuracy
accuracy = compute_accuracy_ratio(gold_count=90, dlq_count=10)
print(f"Accuracy: {accuracy:.4f}")
```

## Files

| File | Description |
|---|---|
| `backend/scripts/dlq_metrics.sql` | SQL queries |
| `backend/scripts/dlq_metrics.py` | Core metrics module |
| `backend/scripts/run_dlq_metrics.py` | CLI entry point |
| `backend/tests/test_dlq_metrics.py` | Unit tests |

## Future Work (Out of Scope for DLQ-1)

- Daily cron scheduling (scheduled for a later infra story)
- Email alerts via notification system
- Langfuse integration for trend tracking (covered by OBSERV-1)
- Temporal workflow integration for automated DLQ resolution
- Kafka event publishing for DLQ alerts
