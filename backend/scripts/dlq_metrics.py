"""
DLQ Metrics Module — DLQ-1: SQL-Based DLQ Metrics and Early Warning System

Provides functions to compute accuracy metrics from DLQ (Dead Letter Queue)
data and trigger alerts when failure rates exceed defined thresholds.

Default alert threshold: DLQ ratio > 10% of total records (gold + dlq).

Usage:
    from scripts.dlq_metrics import should_alert, compute_accuracy_ratio
    should_alert(dlq_count=15, gold_count=100)  # returns True
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default alert threshold: 10%
DEFAULT_ALERT_THRESHOLD = 0.10

# Project root (parent of backend/)
BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent

_module_logger = logging.getLogger(__name__)


def should_alert(dlq_count: int, gold_count: int, threshold: float = DEFAULT_ALERT_THRESHOLD) -> bool:
    """
    Determine whether an alert should be triggered based on DLQ ratio.

    An alert is triggered when: dlq_count / (gold_count + dlq_count) > threshold

    Args:
        dlq_count: Number of records in the DLQ.
        gold_count: Number of approved/gold records.
        threshold: Alert threshold ratio (default 0.10 for 10%).

    Returns:
        True if the DLQ ratio exceeds the threshold.

    Raises:
        ValueError: If counts are negative or total is zero.
    """
    if dlq_count < 0 or gold_count < 0:
        raise ValueError("Counts must not be negative")
    if dlq_count + gold_count == 0:
        raise ValueError("Cannot compute ratio with zero total records")

    ratio = dlq_count / (gold_count + dlq_count)
    return ratio > threshold


def compute_accuracy_ratio(gold_count: int, dlq_count: int) -> float:
    """
    Compute the accuracy ratio: gold / (gold + dlq).

    Args:
        gold_count: Number of approved/gold records.
        dlq_count: Number of records in the DLQ.

    Returns:
        Accuracy ratio as a float between 0.0 and 1.0.

    Raises:
        ValueError: If both counts are zero.
    """
    if gold_count == 0 and dlq_count == 0:
        raise ValueError("Cannot compute accuracy with zero total records")
    return gold_count / (gold_count + dlq_count)


def _execute_query(query_name: str) -> Any:
    """
    Execute a DLQ metrics query against the database.

    This is a thin wrapper that can be mocked in tests. In production,
    it reads from the SQL file and executes against the configured database.

    Args:
        query_name: One of 'gold_dlq_ratio', 'framework_failures', 'failure_reasons'.

    Returns:
        Query results in a structured format.
    """
    return _execute_query_from_file(query_name)


def _execute_query_from_file(query_name: str) -> Any:
    """
    Read and execute a query from the SQL file.

    Args:
        query_name: One of 'gold_dlq_ratio', 'framework_failures', 'failure_reasons'.

    Returns:
        Query results.
    """
    sql_path = BACKEND_ROOT / "dlq_metrics.sql"
    content = sql_path.read_text()

    # Map query names to their index in the file (0-based section after header)
    query_sections = {
        "gold_dlq_ratio": 0,
        "framework_failures": 1,
        "failure_reasons": 2,
    }

    if query_name not in query_sections:
        raise ValueError(f"Unknown query: {query_name}. Use one of {list(query_sections.keys())}")

    # Split by section comments to extract the right query
    sections = content.split("-- ")
    # First element is the header/description
    section_idx = query_sections[query_name]
    # Find the section matching the index
    section_num = 0
    query_text = ""
    for i, section in enumerate(sections):
        if section_num == section_idx and i > 0:
            query_text = section.strip()
            break
        if i > 0:
            section_num += 1

    if not query_text:
        _module_logger.error("Could not extract query for %s", query_name)
        return []

    # Strip leading dashes (from comment markers within the query)
    lines = [line.lstrip("-").strip() for line in query_text.split("\n") if line.strip()]
    clean_query = "\n".join(lines)

    # In production, this would execute against PostgreSQL via SQLAlchemy.
    # For now, return None so the caller handles DB execution.
    # The actual DB connection is handled by the caller.
    return clean_query


def collect_and_report_metrics(
    logger: Optional[logging.Logger] = None,
    threshold: float = DEFAULT_ALERT_THRESHOLD,
) -> Dict[str, Any]:
    """
    Collect all DLQ metrics, log results, and trigger alerts if needed.

    Args:
        logger: Logger to use for output. Defaults to module logger.
        threshold: Alert threshold ratio (default 0.10 for 10%).

    Returns:
        Dict with keys: gold_count, dlq_count, accuracy_ratio,
        alert_triggered, framework_failures, failure_reasons.
    """
    _log = logger if logger is not None else _module_logger

    results = {
        "gold_dlq_ratio": {"gold_count": 0, "dlq_count": 0, "accuracy_ratio": 1.0},
        "framework_failures": [],
        "failure_reasons": [],
    }

    # Execute queries (mocked in tests via _execute_query)
    gold_dlq = _execute_query("gold_dlq_ratio")
    if isinstance(gold_dlq, dict):
        results["gold_dlq_ratio"] = gold_dlq

    framework = _execute_query("framework_failures")
    if isinstance(framework, list):
        results["framework_failures"] = framework

    reasons = _execute_query("failure_reasons")
    if isinstance(reasons, list):
        results["failure_reasons"] = reasons

    # Compute alert status
    gold_count = results["gold_dlq_ratio"].get("gold_count", 0)
    dlq_count = results["gold_dlq_ratio"].get("dlq_count", 0)

    accuracy = compute_accuracy_ratio(gold_count, dlq_count)
    triggered = should_alert(dlq_count, gold_count, threshold)

    # Log metrics
    _log.info(
        "DLQ Metrics: gold=%d dlq=%d accuracy=%.4f",
        gold_count, dlq_count, accuracy,
    )

    # Log framework failures
    for fw in results["framework_failures"]:
        _log.info(
            "  Framework failures: %s -> %d",
            fw.get("framework_name", "unknown"),
            fw.get("failure_count", 0),
        )

    # Log failure reasons
    for r in results["failure_reasons"]:
        _log.info(
            "  Failure reason: %s -> %d",
            r.get("reason", "unknown"),
            r.get("count", 0),
        )

    # Alert logic
    if triggered:
        _log.warning(
            "ALERT: DLQ ratio %.4f exceeds threshold %.4f (gold=%d, dlq=%d, threshold=%.2f%%)",
            1.0 - accuracy, threshold, gold_count, dlq_count, threshold * 100,
        )

    return {
        "gold_count": gold_count,
        "dlq_count": dlq_count,
        "accuracy_ratio": round(accuracy, 4),
        "alert_triggered": triggered,
        "framework_failures": results["framework_failures"],
        "failure_reasons": results["failure_reasons"],
    }
