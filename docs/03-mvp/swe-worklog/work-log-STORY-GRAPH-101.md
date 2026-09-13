# Work Log: [STORY-GRAPH-101] Dependencies, Config & Consolidated Model Matrix Setup (Qwen3.6-35B-A3B)

**Developer:** SWE Agent  
**Date:** 2026-08-12  
**Status:** READY_FOR_QA  
**Target Story:** [STORY-GRAPH-101](docs/06-add-ai/upgrade-graph-agent.md#story-graph-101-dependencies-config--consolidated-model-matrix-setup-qwen36-35b-a3b)  

---

## 1. Executive Summary & Work Accomplished
Installed `langgraph`, `langchain-core`, and `langgraph-checkpoint-postgres`. Updated `.env`, `.env.example`, `requirements.txt`, `extraction.py`, and `judge.py` to use `Qwen/Qwen3.6-35B-A3B` as the consolidated primary extractor and judge endpoint.

## 2. Files Modified & Created
| File Path | Change Type | Purpose |
|---|---|---|
| `backend/requirements.txt` | [MODIFY] | Added `langgraph` and `langchain-core` dependencies |
| `.env` | [MODIFY] | Configured `Qwen/Qwen3.6-35B-A3B` model endpoint defaults |
| `backend/app/services/extraction.py` | [MODIFY] | Updated `LLM_MODEL` default to `Qwen/Qwen3.6-35B-A3B` |
| `backend/app/services/judge.py` | [MODIFY] | Updated `JUDGE_ENDPOINT` to `http://localhost:8000/v1` and `JUDGE_MODEL` to `Qwen/Qwen3.6-35B-A3B` |
| `backend/tests/test_graph_101_config.py` | [NEW] | TDD unit test verifying langgraph imports and model configuration |

## 3. TDD Cycle Summary
### 🔴 RED Phase
- **Test File:** `backend/tests/test_graph_101_config.py`
- **Initial Failure Reason:** `ModuleNotFoundError: No module named 'langgraph'` and model defaults mismatch.

### 🟢 GREEN Phase
- **Implementation:** Installed packages via pip and updated configuration constants in `.env`, `extraction.py`, `judge.py`.
- **Passing Verification:** `pytest backend/tests/test_graph_101_config.py -v` passed 2/2.

### 🔵 REFACTOR Phase
- **Refactoring Applied:** Cleaned up dependency sections and environment documentation comments.

## 4. Test Execution Evidence
```bash
$ python3 -m pytest backend/tests/test_graph_101_config.py -v
========================== 2 passed in 0.17s ==========================
```
