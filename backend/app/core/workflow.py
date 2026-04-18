"""Workflow integration module (re-exports from app.workflows)."""

from app.workflows.base import (
    BaseWorkflow,
    WorkflowEngine,
    DEFAULT_NAMESPACE,
    DEFAULT_TARGET_HOST,
    DEFAULT_TASK_QUEUE,
)

# Backward compat alias
TemporalClient = WorkflowEngine

__all__ = [
    "BaseWorkflow",
    "WorkflowEngine",
    "TemporalClient",
    "DEFAULT_NAMESPACE",
    "DEFAULT_TARGET_HOST",
    "DEFAULT_TASK_QUEUE",
]
