# COVERAGE-1: Coverage Score Model

**Type**: Story
**Sprint**: Sprint 6
**Story Points**: 8
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, metrics, coverage

---

## User Story

> As a **compliance officer**, I want a Coverage Score Model that calculates per-framework and aggregate compliance coverage, so that I can understand the organization's compliance posture at a glance.

---

## Context and Background

Per TRD Section 8.5, the Coverage Score Model must:
- Calculate coverage percentage per framework (e.g., "NIST CSF: 87% covered")
- Calculate aggregate coverage across all frameworks
- Track coverage changes over time (coverage_delta)
- Generate alerts when coverage drops below threshold (e.g., < 80%)

---

## Acceptance Criteria

1. Given all control-obligation mappings exist, when `calculate_framework_coverage(framework_id)` is called, then a coverage percentage is returned
2. Given the coverage is calculated, when the result is compared to the previous snapshot, then coverage_delta is computed correctly
3. Given coverage drops below 80%, when the calculation is performed, then a `coverage.alert` event is published to Kafka
4. Coverage calculation includes: total_obligations, mapped_obligations, equivalent_count, superset_count, subset_count, no_relationship_count
5. Coverage breakdown by control type: automated_count, manual_count, preventive_count, detective_count
6. Results cached in Redis with TTL 300 seconds

---

## Technical Notes

- Coverage calculation query:
  ```sql
  SELECT
      COUNT(DISTINCT o.id) AS total_obligations,
      COUNT(DISTINCT CASE WHEN m.relationship_type IN ('EQUIVALENT_TO', 'SUPERSET_OF') THEN m.id END) AS mapped_obligations,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'EQUIVALENT_TO' THEN m.id END) AS equivalent_count,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'SUPERSET_OF' THEN m.id END) AS superset_count,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'SUBSET_OF' THEN m.id END) AS subset_count,
      COUNT(DISTINCT CASE WHEN m.relationship_type = 'NO_RELATIONSHIP' THEN m.id END) AS no_relationship_count
  FROM obligations o
  LEFT JOIN control_obligation_mappings m ON o.id = m.obligation_id
  WHERE o.framework_id = $framework_id
  ```
- Coverage percentage formula: `(equivalent_count + superset_count) / total_obligations * 100`
- Kafka alert topic: `coverage.alert`

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for coverage calculation
- [ ] Integration tests for Kafka alerting
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: CROSSWALK-4
- **Blocks**: COVERAGE-2
