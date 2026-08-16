# Work Log: [CFIX-203] Fix Seed Ingestion to Distinguish ControlObjective vs ControlActivity Nodes

**Developer:** SWE Agent  
**Date:** 2026-08-02  
**Status:** READY_FOR_QA  
**Target Story:** [CFIX-203](file:///home/zackchow/coding/rckg/docs/04-deepdive/claude-remediation-sprint.md#cfix-203-fix-seed-ingestion-to-distinguish-controlobjective-vs-controlactivity-nodes)  

---

## 1. Executive Summary & Work Accomplished
Updated `ComplianceSeedIngester.ingest_file()` in `backend/app/services/seed_ingestion.py` to inspect `framework_obj_id`. Base controls (e.g. `AC-2`) are instantiated as `FrameworkControlObjectiveNode`, while control enhancements containing parenthesis syntax (e.g. `AC-2(1)`) are instantiated as `FrameworkControlActivityNode`.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/app/services/seed_ingestion.py` | MODIFIED | Differentiated objective vs activity node creation based on enhancement syntax |
| `backend/tests/test_cfix_203_seed_node_types.py` | [NEW] | TDD unit test verifying base control and enhancement node creation |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_cfix_203_seed_node_types.py`
- **Initial Failure Reason:** `assert 2 == 1` because all nodes were instantiated as `FrameworkControlObjectiveNode`.

### 🟢 GREEN Phase
- **Implementation:** Added conditional check `if "(" in node_id and ")" in node_id:` to instantiate `FrameworkControlActivityNode`.
- **Passing Verification:** `pytest backend/tests/test_cfix_203_seed_node_types.py` passed 100%.

## 4. Test Execution Evidence
```bash
$ pytest backend/tests/test_cfix_203_seed_node_types.py -v
========================== 1 passed in 0.02s ==========================
```

## 5. Notes for QA Reviewer
- Verified `FrameworkControlObjectiveNode` created for base controls.
- Verified `FrameworkControlActivityNode` created for granular enhancements.
