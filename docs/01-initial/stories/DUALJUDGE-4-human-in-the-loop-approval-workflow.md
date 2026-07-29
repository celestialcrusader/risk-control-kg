# DUALJUDGE-4: Human-in-the-Loop Approval Workflow

**Type**: Story
**Sprint**: Sprint 4
**Story Points**: 5
**Priority**: High
**Assigned To**: Backend Engineer
**Labels**: backend, temporal, workflow, hitl

---

## User Story

> As a **backend developer**, I want a Temporal workflow with human-in-the-loop approval gates, so that low-confidence dual-judge failures can be reviewed and corrected by SMEs.

---

## Context and Background

Per TRD Section 19.3, the HITL workflow must:
- Pause at approval gates when dual-judge fails
- Await callback signals (approve/reject/modify)
- Resume workflow upon callback with decision applied
- Include timeout handling (48 hours for extraction, 72 hours for mapping)

---

## Acceptance Criteria

1. Given a dual-judge failure, when `start_hitl_approval(obligation_id, request_type)` is called, then a Temporal workflow is started and paused at `approval_gate` signal
2. Given a workflow is paused, when the HITL UI submits a decision, then the callback signal is received and workflow resumes
3. Given a callback with `decision=approve`, when the workflow resumes, then the obligation is promoted to Gold
4. Given a callback with `decision=reject`, when the workflow resumes, then the obligation is sent to dead-letter queue
5. Given a callback with `decision=modify` and `corrected_text`, when the workflow resumes, then the corrected text is written to Silver layer and re-queued for dual-judge
6. Workflow timeout handling: If no callback within 48/72 hours, move to dead-letter queue with `reason: hitl_timeout`

---

## Technical Notes

- Temporal workflow definition (in `/backend/app/workflows/dual_judge.py`):
  ```python
  @workflow.defn
  class DualJudgeValidationWorkflow:
      @workflow.run
      async def run(self, obligation_id: str) -> Dict:
          logic_score = await workflow.execute_activity(
              "logic_judge_activity",
              args=[obligation_id],
              start_to_close_timeout=workflow.timedelta(minutes=30)
          )
          tech_score = await workflow.execute_activity(
              "technical_judge_activity",
              args=[obligation_id],
              start_to_close_timeout=workflow.timedelta(minutes=30)
          )
          result = aggregate_scores(logic_score, tech_score)
          
          if result["status"] == "requires_human_review":
              await workflow.wait_condition(
                  lambda: signal_received("approval_callback"),
                  timeout=workflow.timedelta(hours=72)
              )
              callback = workflow.get_signal("approval_callback")
              if callback["decision"] == "approve":
                  return promote_to_gold(obligation_id)
              elif callback["decision"] == "reject":
                  return send_to_dlq(obligation_id, "human_rejection")
              elif callback["decision"] == "modify":
                  return requeue_for_validation(callback["corrected_text"])
          
          return result
  ```
- Signal definition: `approval_callback` with fields: `decision`, `reviewer_id`, `timestamp`, `corrected_text?`
- Use Temporal Python SDK

---

## Definition of Done

- [ ] Code written and peer-reviewed
- [ ] Unit tests for Temporal workflow
- [ ] Integration tests for HITL callback simulation
- [ ] All acceptance criteria verified
- [ ] Documentation in `docs/01-initial/hitl-workflows.md`

---

## Dependencies

- **Blocked by**: DUALJUDGE-3, INFRA-6
- **Blocks**: None
