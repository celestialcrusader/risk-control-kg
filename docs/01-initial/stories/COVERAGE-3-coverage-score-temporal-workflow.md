# COVERAGE-3: Coverage Score Temporal Workflow

**Type**: Story
**Sprint**: Sprint 6
**Story Points**: 3
**Priority**: Medium
**Assigned To**: DevOps Engineer
**Labels**: infrastructure, temporal, workflow

---

## User Story

> As a **system**, I want a daily scheduled Temporal workflow that recalculates coverage scores and publishes alerts, so that the coverage metrics remain current without manual intervention.

---

## Context and Background

Per TRD Section 19.2, the `coverage_score_workflow` must:
- Run daily at 06:00 UTC via Cron trigger
- Calculate coverage for all registered frameworks
- Publish `coverage.alert` events when thresholds are breached
- Update dashboard cache with new scores

---

## Acceptance Criteria

1. Given the Temporal workflow is configured with cron trigger `0 6 * * *`, when it runs, then coverage is calculated for all frameworks
2. Given coverage is breached, when the workflow task runs, then a `coverage.alert` Kafka message is published
3. Given coverage is not breached, when the workflow task runs, then only the coverage score is updated without alerting
4. Workflow includes error handling: if coverage calculation fails, the failure is logged and an alert is sent to Slack/Email
5. Workflow logs all coverage scores to PostgreSQL `coverage_scores_history` table for trend analysis
6. Workflow is idempotent and can be replayed without side effects

---

## Technical Notes

- Temporal workflow definition (in `/backend/app/workflows/coverage_score_workflow.py`):
  ```python
  from temporalio import workflow
  from temporalio.activity import define as activity_def
  from datetime import timedelta

  @workflow.defn
  class CoverageScoreWorkflow:
      @workflow.run
      async def run(self) -> Dict:
          coverage_data = await workflow.execute_activity(
              "calculate_coverage_activity",
              start_to_close_timeout=workflow.timedelta(minutes=10)
          )
          await workflow.execute_activity(
              "publish_alerts_activity",
              args=[coverage_data],
              start_to_close_timeout=workflow.timedelta(minutes=5)
          )
          return coverage_data
  ```
- Cron trigger setup: `cron_schedule="0 6 * * *"` (daily at 06:00 UTC)
- PostgreSQL history table: `coverage_scores_history` with framework_id, coverage_percentage, snapshot_date

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for coverage calculation
- [ ] Integration tests for Temporal workflow execution
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: COVERAGE-1
- **Blocks**: None
