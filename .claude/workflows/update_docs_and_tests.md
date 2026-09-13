---
description: Update documentation and create tests based on recent code changes
---

# Documentation & Test Sync Protocol

Use this workflow to clean up after a feature implementation, ensuring docs are true-to-code and tests cover the new logic.

## 1. Review Documentation
Start by loading the current state of documentation.
- **List Docs**: `list_dir(DirectoryPath="/home/rckg/coding/deepeval_ui/docs")`
- **Read Context**: Read `docs/reference.md` and `docs/technical_requirements.md` (or other relevant files) to see what is currently documented.

## 2. Analyze & Update Docs
Compare the *actual* code behavior with the *documentation*.
- **Identify Changes**: Look at `task.md` or recent code edits to recall what was changed (e.g., "Project Deletion now cascades", "Threshold Tuning added").
- **Update Files**: Use `replace_file_content` to update the docs.
    - *Example*: If a new API endpoint was added, document it in `reference.md`.
    - *Example*: If a UI feature was added (like Tuning), update the "Features" section.

## 3. Test Driven Development (TDD)
Verify the new features are robust.
- **Design Tests**: Plan what needs testing.
    - *Backend*: `backend/tests/` (e.g., `test_projects.py`, `test_runs.py`).
    - *Frontend*: `frontend/src/__tests__/` (if applicable) or manual verification plans.
- **Implement Tests**: Write the test code.
    - *Example*: `def test_cascade_delete(): ...`
- **Run Tests**: Execute tests in the container.
    - `run_command("docker-compose exec backend pytest")`
    - `run_command("npm test")` (if configured)
