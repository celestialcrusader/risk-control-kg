-- =============================================================================
-- DLQ-1: SQL-Based DLQ Metrics and Early Warning System
-- =============================================================================
--
-- These queries surface accuracy metrics against dead-letter queues (DLQs)
-- to help the team detect when to "stop the line" and fix prompts.
--
-- Default usage:
--   psql -f backend/scripts/dlq_metrics.sql
--
-- DLQ Tables (created by INFRA-2 / DLQ workflow):
--   - extraction_dlq:  Failed extractions (score < 0.80 after 3 repair attempts)
--   - validation_dlq:  Failed dual-judge validations (Logic < 0.95 or Technical < 1.0)
--   - crosswalk_dlq:   Failed crosswalk mappings (low confidence)
-- =============================================================================

-- =============================================================================
-- Query 1: Gold vs. DLQ Ratio
-- =============================================================================
-- Overall accuracy indicator: what fraction of total records (gold + DLQ) are
-- approved. A ratio below 0.90 (i.e., DLQ > 10%) triggers an alert.

SELECT
    COUNT(*) AS gold_count,
    (SELECT COUNT(*) FROM extraction_dlq) AS dlq_count,
    COUNT(*)::FLOAT / (COUNT(*) + (SELECT COUNT(*) FROM extraction_dlq)) AS accuracy_ratio
FROM semantic_controls
WHERE status = 'approved';

-- =============================================================================
-- Query 2: Framework with Most Failures
-- =============================================================================
-- Identifies which frameworks have the highest number of DLQ entries,
-- helping prioritize prompt tuning efforts.

SELECT
    sc.framework_name,
    COUNT(*) AS failure_count
FROM extraction_dlq edq
JOIN semantic_controls sc ON edq.bronze_record_id = sc.id
GROUP BY sc.framework_name
ORDER BY failure_count DESC
LIMIT 10;

-- =============================================================================
-- Query 3: Common Failure Reason Codes
-- =============================================================================
-- Surfaces the most frequent failure reasons so the team can target
-- prompt improvements or schema fixes.

SELECT
    reason,
    COUNT(*) AS count
FROM extraction_dlq
GROUP BY reason
ORDER BY count DESC
LIMIT 10;
