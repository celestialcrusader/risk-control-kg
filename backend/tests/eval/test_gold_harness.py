"""
TDD Tests for Gold Crosswalk Evaluation Benchmark Harness (RCKG-102).

Validates Recall@10, Recall@100, Recall@500, MRR, and comparative model evaluation reports.
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class MockEmbeddingService:
    """Mock vector search service for benchmark testing."""

    def search(self, query_text: str, top_k: int = 500) -> list[str]:
        if "information system accounts" in query_text:
            return ["ISO-27001-A.5.15", "MISC-1", "MISC-2"]
        elif "enforces approved authorizations" in query_text:
            return ["MISC-1", "ISO-27001-A.8.2", "MISC-2"]
        elif "AI system risks" in query_text:
            return ["EU-AI-ACT-ART-9"]
        elif "quarterly access audit" in query_text:
            return ["ACT-SOP-IAM-01"]
        elif "Logs recording user activities" in query_text:
            return ["ISO-27001-A.8.15"]
        return ["UNKNOWN"]


def test_gold_harness_evaluator_metrics():
    """AC-1: Verify GoldHarnessEvaluator calculates Recall@K and MRR metrics accurately."""
    from app.eval.gold_harness import GoldHarnessEvaluator

    benchmark_file = PROJECT_ROOT / "data" / "eval" / "gold_crosswalk_1000.json"
    evaluator = GoldHarnessEvaluator(str(benchmark_file))

    service = MockEmbeddingService()
    metrics = evaluator.evaluate_model(service, k_values=[10, 100, 500])

    assert "Recall@10" in metrics
    assert "Recall@100" in metrics
    assert "Recall@500" in metrics
    assert "MRR" in metrics
    assert "LatencyPerQueryMs" in metrics

    assert metrics["Recall@10"] == 1.0
    assert metrics["Recall@500"] == 1.0
    assert metrics["MRR"] > 0.8


def test_gold_harness_comparative_report():
    """AC-2: Verify comparative evaluation report generation for embedding model candidates."""
    from app.eval.gold_harness import GoldHarnessEvaluator

    benchmark_file = PROJECT_ROOT / "data" / "eval" / "gold_crosswalk_1000.json"
    evaluator = GoldHarnessEvaluator(str(benchmark_file))

    models = {
        "Qwen3-Embedding-8B": MockEmbeddingService(),
        "Voyage-law-2": MockEmbeddingService(),
        "BGE-M3": MockEmbeddingService(),
    }

    report_md = evaluator.generate_comparison_report(models)
    assert "# Dense Embedding Model Evaluation Report" in report_md
    assert "Qwen3-Embedding-8B" in report_md
    assert "Voyage-law-2" in report_md
    assert "BGE-M3" in report_md
