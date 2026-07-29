# GRAG-3: Temporal Compliance Query Support

**Type**: Story
**Sprint**: Sprint 7
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, temporal, query

---

## User Story

> As a **compliance officer**, I want temporal query support so that I can query the compliance posture as of any historical date, so that auditors can verify historical compliance states.

---

## Context and Background

Per TRD Section 4.2 and Section 6.1, temporal queries must:
- Accept `as_of_date` parameter on any query
- Return compliance posture that existed at that point in time
- Respect bitemporal tags (`valid_from`, `valid_to`, `ingested_at`)
- Exclude superseded obligations from active queries

---

## Acceptance Criteria

1. Given an `as_of_date` parameter, when a query is executed, then only obligations with `valid_from <= as_of_date AND (valid_to IS NULL OR valid_to > as_of_date)` are returned
2. Given a temporal query, when the result is verified, then superseded regulations are excluded from the result
3. Given a historical query for a date before any data was ingested, when the query is executed, then an empty result is returned with message "No data exists for this date"
4. Temporal query API endpoint: `GET /api/v1/query?as_of_date=2024-01-01&q=...`
5. Temporal queries use PostgreSQL cold store for dates > 90 days ago (hot/cold separation)
6. Query result includes `query_date` in the response metadata

---

## Technical Notes

- Temporal filter in SQL:
  ```sql
  WHERE valid_from <= :as_of_date
    AND (valid_to IS NULL OR valid_to > :as_of_date)
  ```
- Hot/cold routing logic:
  ```python
  def route_temporal_query(as_of_date: datetime) -> str:
      today = datetime.utcnow()
      days_ago = (today - as_of_date).days
      if days_ago > 90:
          return "cold_store"  # PostgreSQL
      else:
          return "hot_store"  # Memgraph
  ```
- PostgreSQL cold store query:
  ```sql
  SELECT * FROM golden_controls
  WHERE valid_from <= $as_of_date
    AND (valid_to IS NULL OR valid_to > $as_of_date)
  ```

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for temporal query logic
- [ ] Integration tests for hot/cold routing
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: GRAG-2
- **Blocks**: GRAG-4
