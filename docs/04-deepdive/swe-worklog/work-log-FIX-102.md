# Work Log: [FIX-102] Create 3-Tier Document-Type Prompt Templates (ControlObjective & ControlActivity)

**Developer:** SWE Agent  
**Date:** 2026-07-31  
**Status:** READY_FOR_QA  
**Target Story:** [FIX-102](file:///home/zackchow/coding/rckg/docs/04-deepdive/real-mvp.md#fix-102-create-3-tier-document-type-prompt-templates-controlobjective--controlactivity)  

---

## 1. Executive Summary & Work Accomplished
Created two new prompt templates to complete the 3-tier GRC document taxonomy extraction pipeline:
1. `backend/app/prompts/extraction_control_objective.md`: Dedicated extraction prompt for Tier 2 Enterprise Policy documents, extracting `control_objectives` with `domain_facet` classification.
2. `backend/app/prompts/extraction_control_activity.md`: Dedicated extraction prompt for Tier 3 SOP/procedure documents, extracting `control_activities` with `execution_type` and `frequency` fields.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/prompts/extraction_control_objective.md` | [NEW] | Tier 2 Enterprise Policy ControlObjective extraction prompt template |
| `backend/app/prompts/extraction_control_activity.md` | [NEW] | Tier 3 SOP ControlActivity extraction prompt template |
| `backend/tests/test_prompt_templates.py` | [NEW] | TDD Unit test for prompt template existence and schema validation |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_prompt_templates.py`
- **Initial Failure Reason:** `AssertionError: prompts/extraction_control_objective.md does not exist` and `prompts/extraction_control_activity.md does not exist`.

### 🟢 GREEN Phase
- **Implementation Files:** `backend/app/prompts/extraction_control_objective.md`, `backend/app/prompts/extraction_control_activity.md`
- **Passing Verification:** `pytest backend/tests/test_prompt_templates.py -v` passed (2/2 passed).

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Standardized JSON formatting, placeholders (`{{markdown_content}}`), and field names across all 3 prompt templates.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_prompt_templates.py -v
========================== 2 passed in 0.01s ==========================
```

## 5. Notes for QA Reviewer
- Check that output JSON schema examples match the Pydantic models in `backend/app/schemas/obligation.py`.
