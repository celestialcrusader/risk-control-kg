# DUALJUDGE-3: Aggregate Scoring and Gold Promotion

**Type**: Story
**Sprint**: Sprint 4
**Story Points**: 8
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, validation, aggregation

---

## User Story

> As a **backend developer**, I want an aggregate scoring system that combines Logic Judge and Technical Judge results, so that obligations can be promoted to Gold tier or sent to dead-letter queue based on combined scores.

---

## Context and Background

Per TRD Section 19.3, the aggregate scoring must:
- Combine Logic Judge score (weighted 0.6) and Technical Judge score (weighted 0.4)
- Threshold for Gold promotion: Weighted mean >= 0.95 AND Technical Judge = 1.0
- Failure: Send to dead-letter queue with `reason` field

---

## Acceptance Criteria

1. Given Logic Judge score and Technical Judge score, when `aggregate_scores(logic_score, tech_score)` is called, then the weighted mean is calculated correctly
2. Given Logic Score = 0.97 and Technical Score = 1.0, when aggregated, then the status is `gold_promoted`
3. Given Logic Score = 0.93 and Technical Score = 1.0, when aggregated, then the status is `requires_human_review` (Logic < 0.95)
4. Given Technical Score = 0.95 (any value < 1.0), when aggregated, then the status is `requires_human_review` (Technical < 1.0)
5. Given a record is promoted to Gold, when it is written to `golden_controls` table, then it has all bitemporal tags (`valid_from`, `valid_to`, `ingested_at`)
6. Given a record fails, when it is written to `validation_dlq` table, then it has `logic_score`, `tech_score`, `reason` fields

---

## Technical Notes

- Aggregation logic:
  ```python
  def aggregate_scores(logic_score: float, tech_score: float) -> Dict:
      weighted_mean = (logic_score * 0.6) + (tech_score * 0.4)
      
      if logic_score >= 0.95 and tech_score == 1.0:
          return {"status": "gold_promoted", "mean_confidence": weighted_mean}
      else:
          reason = []
          if logic_score < 0.95:
              reason.append("Logic score below threshold")
          if tech_score < 1.0:
              reason.append("Technical score below threshold")
          return {"status": "requires_human_review", "reason": "; ".join(reason)}
  ```
- Gold promotion: Write to PostgreSQL `golden_controls` table
- Dead-letter queue: Write to PostgreSQL `validation_dlq` table

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for score aggregation
- [ ] Integration tests for Gold promotion and DLQ
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: DUALJUDGE-1, DUALJUDGE-2
- **Blocks**: DUALJUDGE-4
