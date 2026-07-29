# COVERAGE-2: Gap Lifecycle State Machine

**Type**: Story
**Sprint**: Sprint 6
**Story Points**: 8
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, gap, state-machine

---

## User Story

> As a **risk manager**, I want a Gap lifecycle state machine that tracks remediation progress from NEW to CLOSED, so that I can assign owners, set due dates, and track completion.

---

## Context and Background

Per TRD Section 5.3, the Gap lifecycle must:
- States: NEW -> IN_REMEDIATION -> REMEDIATED -> VERIFIED -> CLOSED
- Transitions are triggered by user actions or automated events
- Each state transition is logged with `changed_by` and `changed_at`
- ACCEPTED gaps can have review date extensions

---

## Acceptance Criteria

1. Given a Gap node is created, when it is queried, then its initial state is `NEW`
2. Given a Gap is in `NEW` state, when `assign_gap(gap_id, assignee_id)` is called, then the state transitions to `IN_REMEDIATION`
3. Given a Gap is in `IN_REMEDIATION` state, when `mark_remediated(gap_id)` is called, then the state transitions to `REMEDIATED`
4. Given a Gap is in `REMEDIATED` state, when `verify_remediation(gap_id, verified_by)` is called, then the state transitions to `VERIFIED`
5. Given a Gap is in `VERIFIED` state, when `close_gap(gap_id)` is called, then the state transitions to `CLOSED`
6. All state transitions are logged in the `gap_lifecycle_audit` table with `from_state`, `to_state`, `changed_by`, `changed_at`, `notes`

---

## Technical Notes

- Gap state machine definition (in `/backend/app/models/gap.py`):
  ```python
  from enum import Enum
  from pydantic import BaseModel

  class GapState(str, Enum):
      NEW = "NEW"
      IN_REMEDIATION = "IN_REMEDIATION"
      REMEDIATED = "REMEDIATED"
      VERIFIED = "VERIFIED"
      CLOSED = "CLOSED"
      ACCEPTED = "ACCEPTED"

  GAP_TRANSITIONS = [
      GapTransition(from_state=GapState.NEW, to_state=GapState.IN_REMEDIATION, allowed=True),
      GapTransition(from_state=GapState.IN_REMEDIATION, to_state=GapState.REMEDIATED, allowed=True),
      GapTransition(from_state=GapState.REMEDIATED, to_state=GapState.VERIFIED, allowed=True),
      GapTransition(from_state=GapState.VERIFIED, to_state=GapState.CLOSED, allowed=True),
      GapTransition(from_state=GapState.NEW, to_state=GapState.ACCEPTED, allowed=True),
      GapTransition(from_state=GapState.ACCEPTED, to_state=GapState.IN_REMEDIATION, allowed=True),
  ]
  ```
- State transition validation must reject invalid transitions
- Log all transitions to PostgreSQL `gap_lifecycle_audit` table

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for state machine transitions
- [ ] Integration tests for gap lifecycle API
- [ ] All acceptance criteria verified
- [ ] Documentation updated

---

## Dependencies

- **Blocked by**: CROSSWALK-4
- **Blocks**: None
