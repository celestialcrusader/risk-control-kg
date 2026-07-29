# DLQ-1: SQL-Based DLQ Metrics and Early Warning System

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 3
**Priority**: Medium
**Assigned To**: Backend Engineer
**Labels**: backend, database, metrics, dlq

---

## User Story

> As a **team lead**, I want SQL queries against dead-letter queues that surface accuracy metrics without a dashboard, so that I can detect when to "stop the line" and fix prompts.

---

## Context and Background

The CTO review identified that DLQs exist but no metrics are defined. Until Prometheus/Grafana is built in Sprint 9, these SQL queries serve as the "poor man's dashboard" for accuracy tracking.

**DLQ Tables:**
- `extraction_dlq`: Failed extractions (score < 0.80 after 3 repair attempts)
- `validation_dlq`: Failed dual-judge validations (Logic < 0.95 or Technical < 1.0)
- `crosswalk_dlq`: Failed crosswalk mappings (low confidence)

**Three Essential SQL Queries:**
```sql
-- 1. Gold vs. DLQ ratio (overall accuracy indicator)
SELECT 
    COUNT(*) as gold_count,
    (SELECT COUNT(*) FROM extraction_dlq) as dlq_count,
    COUNT(*)::FLOAT / (COUNT(*) + (SELECT COUNT(*) FROM extraction_dlq)) as accuracy_ratio
FROM semantic_controls WHERE status = 'approved';

-- 2. Framework with most failures
SELECT 
    framework_name,
    COUNT(*) as failure_count
FROM extraction_dlq edq
JOIN semantic_controls sc ON edq.bronze_record_id = sc.id
GROUP BY framework_name
ORDER BY failure_count DESC
LIMIT 10;

-- 3. Common failure reason codes
SELECT 
    reason,
    COUNT(*) as count
FROM extraction_dlq
GROUP BY reason
ORDER BY count DESC
LIMIT 10;
```

---

## Acceptance Criteria

1. Given the DLQ tables exist, when the SQL queries are executed, then accurate metrics are returned
2. Given a query shows DLQ count > 10% of Gold count, when the metric is reported, then an alert is sent to the team
3. SQL queries saved in `scripts/dlq_metrics.sql` with documentation
4. Metrics logged to Langfuse for trend tracking
5. Daily automated run of DLQ metrics via cron/job scheduler
6. Metrics displayed in team standup dashboard (simple text output or email)

---

## Technical Notes

- Save queries in `/backend/scripts/dlq_metrics.sql`
- Cron job runs at 9am and 5pm daily: `python scripts/run_dlq_metrics.py`
- Email alert if: `dlq_count / (gold_count + dlq_count) > 0.10`
- Integration with Temporal: Failed DLQ inserts trigger `accuracy.alert` Kafka event

---

## Definition of Done

- [ ] SQL queries written and tested
- [ ] Automated daily run configured
- [ ] Alert thresholds defined
- [ ] Documentation in `docs/01-initial/dlq-metrics.md`
- [ ] Team trained on interpreting metrics

---

## Dependencies

- **Blocked by**: INFRA-2 (DLQ tables exist)
- **Blocks**: None (runs in parallel with other sprints)
