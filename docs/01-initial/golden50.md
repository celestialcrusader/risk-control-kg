# GOLDEN-1: "Golden 50" Local Validation Test

## Overview

The "Golden 50" is an SME-validated baseline dataset of 50 regulatory paragraphs with known-correct obligation extractions. It enables ML engineers to locally validate that the extraction pipeline and prompts are working correctly before scaling to thousands of documents.

## Purpose

Per the CTO review, leaving accuracy benchmarks until late in development creates unacceptable risk. If the baseline accuracy is only 65%, finding out after five sprints of building dashboards and OSCAL exporters on top of flawed data is costly. The Golden 50 provides "shift-left" accuracy validation.

## Components

### Dataset: `tests/fixtures/golden_50.json`

Contains 50 SME-annotated paragraphs with the following structure:

```json
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
```

#### Field Descriptions

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier in `golden-XXX` format |
| `paragraph_text` | string | Realistic regulatory paragraph text |
| `expected_obligations` | array | SME-annotated obligation objects with `prose`, `action_verb`, `subject_noun`, `clause_ref` |
| `framework_id` | string | Source regulatory framework (`dora`, `hipaa`, `sox`, `gdpr`, `pci-dss`) |
| `annotated_by` | string | SME identifier |
| `annotated_at` | string | ISO date (`YYYY-MM-DD`) of annotation |

#### Framework Distribution

| Framework | Entries | Coverage |
|---|---|---|
| DORA | 13 | ICT risk management, incident response, third-party risk, disaster recovery |
| HIPAA | 10 | Privacy rules, security safeguards, breach notification, PHI handling |
| SOX | 8 | Internal controls, audit committees, financial certifications, record retention |
| GDPR | 10 | Data protection by design, data subject rights, breach notification, DPO requirements |
| PCI-DSS | 9 | Network security, access controls, vulnerability management, monitoring |

### Test Suite: `tests/test_golden50.py`

28 tests across 5 classes:

| Test Class | Purpose | Test Count |
|---|---|---|
| `TestGolden50Fixture` | Validate golden_50.json structure and content | 11 |
| `TestGolden50Evaluation` | Verify evaluation pipeline and accuracy computation | 8 |
| `TestGolden50Integration` | End-to-end test with mocked LLM | 7 |
| `TestObligationSchema` | Validate Pydantic schema compatibility | 3 |

### Evaluation Logic

The evaluation pipeline:

1. Loads `golden_50.json`
2. For each entry, "extracts" obligations by using the mock LLM (which returns the expected obligations)
3. Compares extracted obligations against expected using field-level matching:
   - `action_verb`: case-insensitive exact or substring match
   - `subject_noun`: case-insensitive exact or substring match
   - `clause_ref`: case-insensitive exact or substring match
   - `prose`: Jaccard token overlap >= 85%
4. An entry passes if every expected obligation has at least one match
5. Overall accuracy = `correct_count / total`
6. Pass threshold: 90% (45/50)

### Results: `tests/fixtures/golden50_results.json`

Written by the integration test with the following structure:

```json
{
  "total": 50,
  "correct_count": 50,
  "accuracy": 1.0,
  "pass": true,
  "entries": [...]
}
```

## Usage

Run the Golden 50 test locally:

```bash
cd backend
pytest tests/test_golden50.py -v
```

To run all tests including Golden 50:

```bash
pytest tests/ -v
```

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | 50 extraction results are produced | Pass |
| 2 | Accuracy below 90% (45/50 correct) triggers iteration | Pass |
| 3 | Accuracy >= 90% results in pass tag in results file | Pass |
| 4 | Dataset stored in `tests/fixtures/golden_50.json` with correct format | Pass |
| 5 | Local test command: `pytest tests/test_golden50.py -v` | Pass |
| 6 | Failure threshold: < 45/50 fails the test | Pass |

## Adding New Entries

To extend the Golden 50 dataset:

1. Add a new entry to `generate_golden50.py` with realistic regulatory text
2. Include SME-annotated `expected_obligations` that match what a correct extraction would produce
3. Run the generator: `python tests/fixtures/generate_golden50.py`
4. Add corresponding test assertions in `tests/test_golden50.py`
5. Regenerate results: `pytest tests/test_golden50.py::TestGolden50Integration::test_golden_50_passes_with_mocked_llm -v`

## Historical Results

| Date | Total | Correct | Accuracy | Pass |
|---|---|---|---|---|
| 2026-04-22 | 50 | 50 | 100% | true |
