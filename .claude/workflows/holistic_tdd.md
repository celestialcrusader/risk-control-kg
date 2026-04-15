---
description: A holistic TDD workflow (ZOMBIES + AAA) for robust, production-grade software development.
---

# Holistic TDD Protocol
**Philosophy**: We do not just write tests that pass; we write tests that prove the system is bulletproof.
**Core Rhythm**: Red -> Green -> Refactor.
**Core Strategy**: ZOMBIES + 4-Paths Analysis.

## Phase 1: Test Design (The "What")
Before writing a single line of feature code, design the test suite using **ZOMBIES** to ensure completeness.

### 1. ZOMBIES Analysis
Ask these questions for the feature:
- **Z (Zero)**: What happens with empty inputs, nulls, or zero items?
- **O (One)**: The simplest Happy Path (single item).
- **M (Many)**: Stress test (loops, lists, pagination).
- **B (Boundary)**: Edge cases (Max-1, Max, Max+1).
- **I (Interface)**: API contracts / Schema validation.
- **E (Exceptions)**: Force errors (DB down, Network timeout).
- **S (Simple)**: Keep scenarios atomic.

### 2. Path Categorization
Ensure coverage across the 4 Paths:
- **Happy Path**: "It works."
- **Sad Path**: "It fails gracefully (400 Bad Request, not 500 Crash)."
- **Bad Path (Security)**: "It rejects malice (SQLi, XSS)."
- **Scary Path (Resource)**: "It handles exhaustion (Large files, high concurrency)."

## Phase 2: Implementation (The "Red")
Write the test code FIRST. Ideally, create a new test file `tests/test_feature_name.py`.

### Structure: AAA Pattern
Every test must follow:
1. **Arrange**: Setup inputs, mocks, and state.
2. **Act**: Execute the function/API.
3. **Assert**: Verify status, body, side-effects.

*Example*:
```python
def test_upload_invalid_type():
    # Arrange
    file = create_dummy_exe()
    
    # Act
    response = client.post("/upload", files={"file": file})
    
    # Assert
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
```

## Phase 3: Execution (The "Green" & "Refactor")
1. **Run Tests**: `docker-compose exec backend pytest tests/test_feature_name.py` -> **MUST FAIL (Red)**.
2. **Implement**: Write the minimal code to satisfy the test.
3. **Run Tests**: Verify Pass -> **(Green)**.
4. **Refactor**: Clean up code/tests without breaking Green state.

## Phase 4: Verification (The Pyramid)
Check your balance:
- [ ] **Unit (70%)**: Fast, mocked logic tests?
- [ ] **Integration (20%)**: DB/API contracts?
- [ ] **E2E (10%)**: Full user flows?

---
**Usage**:
When asking the agent to build a feature, refer to this workflow:
"/holistic_tdd implementation for [Feature Name]"
