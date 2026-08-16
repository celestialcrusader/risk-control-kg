"""
Compliance Extraction Quality & Precision Evaluation Test Suite for STORY-PARSE-106.
Evaluates Parent Hierarchy Precision and Deontic Accuracy metrics.
"""

import json
import pytest
from pathlib import Path


def test_compliance_extraction_benchmark():
    gold_path = Path("data/eval/gold_compliance_50.json")
    if not gold_path.exists():
        pytest.skip("Ground-truth gold evaluation dataset not found")

    with open(gold_path, "r") as f:
        gold_data = json.load(f)

    correct_parents = 0
    correct_deontic = 0
    total = len(gold_data)

    for item in gold_data:
        if item.get("extracted_parent_id") == item["ground_truth"]["parent_clause_id"]:
            correct_parents += 1
        if item.get("extracted_modality") == item["ground_truth"]["modality"]:
            correct_deontic += 1

    parent_precision = correct_parents / total if total > 0 else 0
    deontic_accuracy = correct_deontic / total if total > 0 else 0

    assert parent_precision >= 0.95, f"Parent Hierarchy Precision {parent_precision:.2f} < 0.95"
    assert deontic_accuracy >= 0.95, f"Deontic Accuracy {deontic_accuracy:.2f} < 0.95"
