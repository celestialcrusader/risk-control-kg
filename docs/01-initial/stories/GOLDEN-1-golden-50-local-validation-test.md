# GOLDEN-1: "Golden 50" Local Validation Test

**Type**: Story
**Sprint**: Sprint 3
**Story Points**: 5
**Priority**: High
**Assigned To**: ML/AI Engineer + SME
**Labels**: testing, benchmark, validation

---

## User Story

> As a **ML engineer**, I want a "Golden 50" SME-validated baseline that I can test against locally, so that I know if my prompts are working before scaling to thousands of documents.

---

## Context and Background

The CTO review identified that leaving TEST-3 (accuracy benchmarks) until Sprint 10 is too late. If the baseline accuracy is only 65%, you don't want to find that out five sprints later after building dashboards and OSCAL exporters on top of flawed data.

**This Story:**
- By end of Sprint 2, SMEs manually annotate **50 critical paragraphs** (the "Golden 50")
- ML engineer runs extraction script locally against those 50 paragraphs
- If 20 are wrong, they don't commit the code
- Iterate on the prompt until 45/50 pass
- This is the "shift-left" accuracy validation

---

## Acceptance Criteria

1. Given the "Golden 50" dataset exists, when the extraction script is run, then 50 extraction results are produced
2. Given the results are evaluated, when accuracy < 90% (45/50 correct), then the ML engineer iterates on the prompt
3. Given accuracy >= 90%, when the code is committed, then a pass tag is recorded in `tests/fixtures/golden50_results.json`
4. The "Golden 50" dataset is stored in `tests/fixtures/golden_50.json` with:
   - `paragraph_text`: Original regulatory text
   - `expected_obligations`: SME-annotated obligation objects
   - `framework_id`: Source framework
5. Local test command: `pytest tests/test_golden50.py -v`
6. Failure threshold: < 45/50 correct fails the test and blocks commit

---

## Technical Notes

- Golden 50 format:
  ```json
  [
    {
      "id": "golden-001",
      "paragraph_text": "Financial institutions shall maintain...",
      "expected_obligations": [
        {
          "prose": "Financial institutions shall maintain...",
          "action_verb": "maintain",
          "subject_noun": "ICT systems",
          "clause_ref": "DORA Article 11(2)(a)"
        }
      ],
      "framework_id": "dora",
      "annotated_by": "sme-001",
      "annotated_at": "2026-04-13"
    }
  ]
  ```
- Test script: `tests/test_golden50.py`
- SME coordination: Schedule 4-hour annotation session with 2 compliance officers

---

## Definition of Done

- [ ] "Golden 50" dataset annotated by SMEs
- [ ] Local test script working
- [ ] Accuracy >= 90% achieved before commit
- [ ] Results recorded in `tests/fixtures/golden50_results.json`
- [ ] Documentation in `docs/01-initial/golden50.md`

---

## Dependencies

- **Blocked by**: INGEST-5 (SMEs available for annotation after upload pipeline works)
- **Blocks**: None (runs in parallel with EXTRACT-1)
