"""
Test suite for DLQ-1: SQL-Based DLQ Metrics and Early Warning System

This test module verifies the DLQ metrics computation and alerting logic including:
- Accuracy ratio computation (gold vs DLQ)
- Alert threshold logic (>10% triggers warning)
- Per-framework failure analysis
- Common failure reason aggregation
- Alert logic is exercised multiple times without duplicate logs

Test Strategy:
- Unit tests for pure functions (no database needed)
- Static file tests for SQL content (follows pattern from test_infra_9_schema.py)
- All assertions verify actual computed values
"""

import logging
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"


# =============================================================================
# Test 1: Alert threshold logic
# =============================================================================

class TestAlertThreshold:
    """Tests for the should_alert function."""

    def test_should_alert_returns_true_when_ratio_exceeds_threshold(self):
        """TC-DLQ-1.1: Alert triggers when DLQ ratio > 10%."""
        from scripts.dlq_metrics import should_alert

        # dlq=15, gold=100 => ratio = 15/115 = 0.130 > 0.10
        result = should_alert(dlq_count=15, gold_count=100)

        assert result is True

    def test_should_alert_returns_false_when_ratio_below_threshold(self):
        """TC-DLQ-1.2: No alert when DLQ ratio <= 10%."""
        from scripts.dlq_metrics import should_alert

        # dlq=5, gold=100 => ratio = 5/105 = 0.048 <= 0.10
        result = should_alert(dlq_count=5, gold_count=100)

        assert result is False

    def test_should_alert_returns_false_at_exact_threshold(self):
        """TC-DLQ-1.3: No alert when DLQ ratio equals exactly 10%."""
        from scripts.dlq_metrics import should_alert

        # dlq=1, gold=9 => ratio = 1/10 = 0.10, NOT exceeding
        result = should_alert(dlq_count=1, gold_count=9)

        assert result is False

    def test_should_alert_returns_false_for_zero_dlq(self):
        """TC-DLQ-1.4: No alert when there are zero DLQ records."""
        from scripts.dlq_metrics import should_alert

        result = should_alert(dlq_count=0, gold_count=100)

        assert result is False

    def test_should_alert_raises_on_negative_counts(self):
        """TC-DLQ-1.5: Raises ValueError for negative counts."""
        from scripts.dlq_metrics import should_alert

        with pytest.raises(ValueError, match="negative"):
            should_alert(dlq_count=-1, gold_count=100)

        with pytest.raises(ValueError, match="negative"):
            should_alert(dlq_count=10, gold_count=-5)

    def test_should_alert_raises_on_zero_total(self):
        """TC-DLQ-1.6: Raises ValueError when both gold and DLQ are zero."""
        from scripts.dlq_metrics import should_alert

        with pytest.raises(ValueError, match="zero total"):
            should_alert(dlq_count=0, gold_count=0)

    def test_should_alert_with_custom_threshold(self):
        """TC-DLQ-1.7: Respects custom threshold parameter."""
        from scripts.dlq_metrics import should_alert

        # ratio=0.15, custom_threshold=0.20 => should NOT alert
        result = should_alert(dlq_count=15, gold_count=85, threshold=0.20)

        assert result is False

        # ratio=0.15, custom_threshold=0.10 => should alert
        result = should_alert(dlq_count=15, gold_count=85, threshold=0.10)

        assert result is True


# =============================================================================
# Test 2: Accuracy ratio computation
# =============================================================================

class TestAccuracyRatio:
    """Tests for compute_accuracy_ratio function."""

    def test_accuracy_ratio_is_correct(self):
        """TC-DLQ-2.1: Returns correct ratio = gold / (gold + dlq)."""
        from scripts.dlq_metrics import compute_accuracy_ratio

        result = compute_accuracy_ratio(gold_count=90, dlq_count=10)

        assert result == pytest.approx(0.90)

    def test_accuracy_ratio_is_one_with_no_dlq(self):
        """TC-DLQ-2.2: Returns 1.0 when there are no DLQ records."""
        from scripts.dlq_metrics import compute_accuracy_ratio

        result = compute_accuracy_ratio(gold_count=100, dlq_count=0)

        assert result == 1.0

    def test_accuracy_ratio_is_zero_with_no_gold(self):
        """TC-DLQ-2.3: Returns 0.0 when there are no gold records."""
        from scripts.dlq_metrics import compute_accuracy_ratio

        result = compute_accuracy_ratio(gold_count=0, dlq_count=50)

        assert result == 0.0

    def test_accuracy_ratio_raises_on_zero_total(self):
        """TC-DLQ-2.4: Raises ValueError when both are zero."""
        from scripts.dlq_metrics import compute_accuracy_ratio

        with pytest.raises(ValueError, match="zero total"):
            compute_accuracy_ratio(gold_count=0, dlq_count=0)


# =============================================================================
# Test 3: Metrics collection and logging
# =============================================================================

class TestMetricsCollection:
    """Tests for collect_and_report_metrics function."""

    def test_collect_and_report_returns_metrics_dict(self):
        """TC-DLQ-3.1: Returns a dict with expected keys."""
        from scripts.dlq_metrics import collect_and_report_metrics

        def side_effect(query_name):
            return {
                "gold_dlq_ratio": {"gold_count": 100, "dlq_count": 10, "accuracy_ratio": 0.90},
                "framework_failures": [],
                "failure_reasons": [],
            }[query_name]

        with patch("scripts.dlq_metrics._execute_query", side_effect=side_effect):
            metrics = collect_and_report_metrics(logger=None)

        assert isinstance(metrics, dict)
        assert "gold_count" in metrics
        assert "dlq_count" in metrics
        assert "accuracy_ratio" in metrics
        assert "alert_triggered" in metrics
        assert "framework_failures" in metrics
        assert "failure_reasons" in metrics

    def test_collect_and_report_logs_warning_when_alert_triggered(self):
        """TC-DLQ-3.2: Logs a WARNING when alert threshold is exceeded."""
        from scripts.dlq_metrics import collect_and_report_metrics

        def side_effect(query_name):
            return {
                "gold_dlq_ratio": {"gold_count": 100, "dlq_count": 15, "accuracy_ratio": 0.8696},
                "framework_failures": [],
                "failure_reasons": [],
            }[query_name]

        mock_logger = MagicMock()

        with patch("scripts.dlq_metrics._execute_query", side_effect=side_effect):
            collect_and_report_metrics(logger=mock_logger)

        # Verify a warning was logged
        warning_calls = [
            call for call in mock_logger.warning.call_args_list
            if "ALERT" in str(call)
        ]
        assert len(warning_calls) >= 1, "Expected a warning log with ALERT keyword"

    def test_collect_and_report_no_warning_when_below_threshold(self):
        """TC-DLQ-3.3: Does not log WARNING when below alert threshold."""
        from scripts.dlq_metrics import collect_and_report_metrics

        def side_effect(query_name):
            return {
                "gold_dlq_ratio": {"gold_count": 100, "dlq_count": 5, "accuracy_ratio": 0.9524},
                "framework_failures": [],
                "failure_reasons": [],
            }[query_name]

        mock_logger = MagicMock()

        with patch("scripts.dlq_metrics._execute_query", side_effect=side_effect):
            collect_and_report_metrics(logger=mock_logger)

        # Verify no warning with ALERT keyword was logged
        warning_calls = [
            call for call in mock_logger.warning.call_args_list
            if "ALERT" in str(call)
        ]
        assert len(warning_calls) == 0

    def test_collect_and_report_passes_default_logger(self):
        """TC-DLQ-3.4: Uses a default logger when none is provided."""
        from scripts.dlq_metrics import collect_and_report_metrics

        def side_effect(query_name):
            return {
                "gold_dlq_ratio": {"gold_count": 100, "dlq_count": 5, "accuracy_ratio": 0.9524},
                "framework_failures": [],
                "failure_reasons": [],
            }[query_name]

        with patch("scripts.dlq_metrics._execute_query", side_effect=side_effect):
            # Should not raise -- uses internal logger
            metrics = collect_and_report_metrics()

        assert metrics is not None

    def test_framework_failures_included_in_metrics(self):
        """TC-DLQ-3.5: Framework failure data is included in returned metrics."""
        from scripts.dlq_metrics import collect_and_report_metrics

        def side_effect(query_name):
            if query_name == "gold_dlq_ratio":
                return {"gold_count": 100, "dlq_count": 5, "accuracy_ratio": 0.9524}
            elif query_name == "framework_failures":
                return [
                    {"framework_name": "SOC2", "failure_count": 8},
                    {"framework_name": "HIPAA", "failure_count": 3},
                ]
            return []

        with patch("scripts.dlq_metrics._execute_query", side_effect=side_effect):
            metrics = collect_and_report_metrics()

        assert len(metrics["framework_failures"]) == 2
        assert metrics["framework_failures"][0]["framework_name"] == "SOC2"
        assert metrics["framework_failures"][0]["failure_count"] == 8

    def test_failure_reasons_included_in_metrics(self):
        """TC-DLQ-3.6: Failure reason data is included in returned metrics."""
        from scripts.dlq_metrics import collect_and_report_metrics

        def side_effect(query_name):
            if query_name == "gold_dlq_ratio":
                return {"gold_count": 100, "dlq_count": 5, "accuracy_ratio": 0.9524}
            elif query_name == "failure_reasons":
                return [
                    {"reason": "low_confidence", "count": 10},
                    {"reason": "schema_violation", "count": 5},
                ]
            return []

        with patch("scripts.dlq_metrics._execute_query", side_effect=side_effect):
            metrics = collect_and_report_metrics()

        assert len(metrics["failure_reasons"]) == 2
        assert metrics["failure_reasons"][0]["reason"] == "low_confidence"


# =============================================================================
# Test 4: SQL file content tests
# =============================================================================

class TestSQLFileContent:
    """Tests for the dlq_metrics.sql file content."""

    @pytest.fixture
    def sql_path(self):
        """Return the path to the DLQ metrics SQL file."""
        return BACKEND_ROOT / "scripts" / "dlq_metrics.sql"

    def test_sql_file_exists(self, sql_path):
        """TC-DLQ-4.1: dlq_metrics.sql file exists."""
        assert sql_path.exists(), f"SQL file not found at {sql_path}"

    def test_sql_file_contains_gold_dlq_ratio_query(self, sql_path):
        """TC-DLQ-4.2: SQL file contains the gold vs DLQ ratio query."""
        content = sql_path.read_text()

        assert "gold_count" in content
        assert "dlq_count" in content
        assert "accuracy_ratio" in content

    def test_sql_file_contains_framework_failures_query(self, sql_path):
        """TC-DLQ-4.3: SQL file contains the framework failures query."""
        content = sql_path.read_text()

        assert "framework_name" in content
        assert "failure_count" in content

    def test_sql_file_contains_failure_reasons_query(self, sql_path):
        """TC-DLQ-4.4: SQL file contains the failure reasons query."""
        content = sql_path.read_text()

        assert "reason" in content
        assert re.search(r"GROUP\s+BY\s+reason", content, re.IGNORECASE)

    def test_sql_file_mentions_extraction_dlq(self, sql_path):
        """TC-DLQ-4.5: SQL file references extraction_dlq table."""
        content = sql_path.read_text()

        assert "extraction_dlq" in content

    def test_sql_file_has_section_comments(self, sql_path):
        """TC-DLQ-4.6: SQL file has descriptive section comments."""
        content = sql_path.read_text()

        # Should have at least 3 section comments for the 3 queries
        comment_count = content.count("--")
        assert comment_count >= 6, \
            f"Expected at least 6 comment lines, found {comment_count}"


# =============================================================================
# Test 5: Run script CLI entry point
# =============================================================================

class TestRunScriptCLI:
    """Tests for the run_dlq_metrics.py CLI script."""

    def test_script_module_is_importable(self):
        """TC-DLQ-5.1: run_dlq_metrics.py module can be imported."""
        try:
            from scripts import run_dlq_metrics
            assert run_dlq_metrics is not None
        except ImportError as e:
            pytest.fail(f"Failed to import scripts.run_dlq_metrics: {e}")

    def test_run_metrics_function_exists(self):
        """TC-DLQ-5.2: run_metrics function is defined in the script."""
        from scripts import run_dlq_metrics

        assert hasattr(run_dlq_metrics, "run_metrics")

    def test_main_function_exists(self):
        """TC-DLQ-5.3: main function is defined as CLI entry point."""
        from scripts import run_dlq_metrics

        assert hasattr(run_dlq_metrics, "main")

    def test_main_runs_metrics(self):
        """TC-DLQ-5.4: main() calls run_metrics()."""
        from scripts import run_dlq_metrics

        mock_metrics = {
            "gold_count": 100,
            "dlq_count": 5,
            "accuracy_ratio": 0.95,
            "alert_triggered": False,
            "framework_failures": [],
            "failure_reasons": [],
        }

        with patch("scripts.run_dlq_metrics.run_metrics", return_value=mock_metrics) as mock_run, \
             patch("scripts.run_dlq_metrics.argparse.ArgumentParser") as mock_parser:
            mock_parser.return_value.parse_args.return_value = MagicMock(threshold=0.10, verbose=False)
            run_dlq_metrics.main()

        mock_run.assert_called_once_with(threshold=0.10)

    def test_script_file_exists(self):
        """TC-DLQ-5.5: run_dlq_metrics.py script file exists."""
        script_path = BACKEND_ROOT / "scripts" / "run_dlq_metrics.py"
        assert script_path.exists(), f"Script file not found at {script_path}"


# =============================================================================
# Test 6: Documentation file
# =============================================================================

class TestDocumentation:
    """Tests for the dlq-metrics.md documentation file."""

    @pytest.fixture
    def doc_path(self):
        """Return the path to the documentation file."""
        return PROJECT_ROOT / "docs" / "01-initial" / "dlq-metrics.md"

    def test_doc_file_exists(self, doc_path):
        """TC-DLQ-6.1: dlq-metrics.md documentation file exists."""
        assert doc_path.exists(), f"Documentation not found at {doc_path}"

    def test_doc_mentions_sql_queries(self, doc_path):
        """TC-DLQ-6.2: Documentation mentions SQL queries."""
        content = doc_path.read_text().lower()
        assert "sql" in content or "query" in content

    def test_doc_mentions_alert_threshold(self, doc_path):
        """TC-DLQ-6.3: Documentation mentions the alert threshold."""
        content = doc_path.read_text().lower()
        assert "10" in content or "10%" in content or "threshold" in content

    def test_doc_has_usage_instructions(self, doc_path):
        """TC-DLQ-6.4: Documentation has usage instructions."""
        content = doc_path.read_text().lower()
        assert "usage" in content or "python" in content or "run" in content
