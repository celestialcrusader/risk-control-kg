#!/usr/bin/env python3
"""
DLQ Metrics CLI — DLQ-1: SQL-Based DLQ Metrics and Early Warning System

Runs DLQ accuracy metrics against the configured database and prints
results to the console.

Usage:
    python -m scripts.run_dlq_metrics                  # Normal run
    python -m scripts.run_dlq_metrics --threshold 0.15  # Custom threshold
"""

import argparse
import logging
import sys
from pathlib import Path

from scripts.dlq_metrics import collect_and_report_metrics, DEFAULT_ALERT_THRESHOLD

BACKEND_ROOT = Path(__file__).resolve().parent


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the script."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def run_metrics(threshold: float = DEFAULT_ALERT_THRESHOLD) -> dict:
    """
    Run DLQ metrics collection and reporting.

    Args:
        threshold: Alert threshold ratio (default 0.10 for 10%).

    Returns:
        Metrics dictionary from collect_and_report_metrics.
    """
    log = setup_logging()
    log.info("Running DLQ metrics...")
    log.info("Alert threshold: %.2f%%", threshold * 100)

    metrics = collect_and_report_metrics(
        logger=log,
        threshold=threshold,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("DLQ Metrics Summary")
    print("=" * 60)
    print(f"  Gold count:   {metrics['gold_count']}")
    print(f"  DLQ count:    {metrics['dlq_count']}")
    print(f"  Accuracy:     {metrics['accuracy_ratio']:.4f}")
    print(f"  Alert:        {'YES' if metrics['alert_triggered'] else 'NO'}")

    if metrics["framework_failures"]:
        print("\n  Framework Failures (top 10):")
        for fw in metrics["framework_failures"]:
            print(f"    {fw['framework_name']}: {fw['failure_count']}")

    if metrics["failure_reasons"]:
        print("\n  Failure Reasons (top 10):")
        for r in metrics["failure_reasons"]:
            print(f"    {r['reason']}: {r['count']}")

    print("=" * 60)

    return metrics


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run DLQ accuracy metrics and report results.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_ALERT_THRESHOLD,
        help=f"Alert threshold ratio (default: {DEFAULT_ALERT_THRESHOLD:.2f})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    args = parser.parse_args()

    try:
        metrics = run_metrics(threshold=args.threshold)
    except Exception as e:
        logging.getLogger(__name__).error("DLQ metrics failed: %s", e)
        sys.exit(1)

    if metrics["alert_triggered"]:
        sys.exit(2)  # Non-zero exit code signals alert condition


if __name__ == "__main__":
    main()
