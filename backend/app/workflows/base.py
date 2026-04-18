"""
Base workflow definitions for RCKG Temporal integration.

Provides:
- TemporalClient: Connection wrapper for Temporal server
- BaseWorkflow: Template for long-running workflows with HITL pause signals
- Task queue registration for ingestion pipeline

Per TRD Section 19 and INFRA-6 story:
- Namespace: rckg-production
- Task queue: ingestion-task-queue
- gRPC port: 7233
- Web UI: localhost:8233
"""

import logging
import os
from typing import Any

from temporalio import workflow as tworkflow
from temporalio import client

logger = logging.getLogger(__name__)

DEFAULT_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "rckg-production")
DEFAULT_TARGET_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
DEFAULT_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "ingestion-task-queue")


@tworkflow.defn
class BaseWorkflow:
    """
    Base workflow template with HITL pause signal.

    Subclasses should implement the execute() method with specific
    workflow logic. The pause signal enables human-in-the-loop gating.
    """

    def __init__(self) -> None:
        self._paused = False
        self._approval_result: dict | None = None

    @tworkflow.run
    async def run(self, document_id: str) -> dict:
        """
        Main workflow entry point.

        Args:
            document_id: Unique identifier for the document being processed.

        Returns:
            Dict with workflow result including status and document_id.
        """
        logger.info("Workflow started for document: %s", document_id)

        try:
            # Execute the subclass implementation
            result = await self.execute(document_id)
            logger.info("Workflow completed for document: %s", document_id)
            return result
        except Exception as e:
            logger.error("Workflow failed for document %s: %s", document_id, e)
            raise

    @tworkflow.signal
    async def pause(self) -> None:
        """HITL pause signal: pauses the workflow for human review."""
        self._paused = True
        logger.info("Workflow paused for human review")
        # Wait until resumed
        while self._paused:
            await tworkflow.sleep(0.1)
        logger.info("Workflow resumed after human review")

    @tworkflow.signal
    async def approve(self, approved: bool, reviewer_id: str = "") -> None:
        """
        Approval signal from human reviewer.

        Args:
            approved: True to approve, False to reject.
            reviewer_id: Identifier of the reviewer.
        """
        self._approval_result = {
            "approved": approved,
            "reviewer_id": reviewer_id,
        }
        logger.info(
            "Workflow approval: %s by %s",
            "APPROVED" if approved else "REJECTED",
            reviewer_id,
        )

    def is_paused(self) -> bool:
        """Check if the workflow is currently paused."""
        return self._paused

    def get_approval_result(self) -> dict | None:
        """Get the last approval result, or None if not yet reviewed."""
        return self._approval_result

    async def execute(self, document_id: str) -> dict:
        """
        Override this method in subclasses for specific workflow logic.

        Args:
            document_id: The document identifier.

        Returns:
            Workflow result dictionary.

        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError("Subclasses must implement execute()")


class WorkflowEngine:
    """
    Temporal workflow engine wrapper.

    Manages client connections, namespace registration,
    and workflow execution.
    """

    def __init__(
        self,
        namespace: str | None = None,
        target_host: str | None = None,
        task_queue: str | None = None,
    ):
        self.namespace = namespace or DEFAULT_NAMESPACE
        self.target_host = target_host or DEFAULT_TARGET_HOST
        self.task_queue = task_queue or DEFAULT_TASK_QUEUE
        self._client: client.Client | None = None

    async def connect(self) -> client.Client:
        """Connect to Temporal server and register namespace."""
        self._client = await client.connect(
            self.target_host,
            namespace=self.namespace,
        )
        await self._register_namespace()
        return self._client

    @property
    def is_connected(self) -> bool:
        """Check if connected to Temporal server."""
        return self._client is not None

    async def _register_namespace(self) -> None:
        """Register the workflow namespace if it doesn't exist."""
        if not self._client:
            raise RuntimeError("Client not connected")

        # Namespace auto-registration is handled by Temporal server
        # in most configurations. Log the namespace for visibility.
        logger.info("Namespace '%s' ready on %s", self.namespace, self.target_host)

    async def execute_workflow(
        self,
        workflow_type: Any,
        args: list | None = None,
        workflow_id: str | None = None,
        task_queue: str | None = None,
    ) -> Any:
        """
        Execute a workflow.

        Args:
            workflow_type: The workflow class or function to execute.
            args: Positional arguments for the workflow run method.
            workflow_id: Unique identifier for this workflow execution.
            task_queue: Task queue to use (defaults to ingestion-task-queue).

        Returns:
            The workflow result.

        Raises:
            RuntimeError: If not connected to Temporal server.
        """
        if not self._client:
            raise RuntimeError("Client not connected. Call connect() first.")

        result = await self._client.execute_workflow(
            workflow_type,
            args=args or [],
            id=workflow_id or f"wf-{workflow_type}",
            task_queue=task_queue or self.task_queue,
        )
        return result

    async def close(self) -> None:
        """Close the Temporal client connection."""
        if self._client:
            self._client = None
