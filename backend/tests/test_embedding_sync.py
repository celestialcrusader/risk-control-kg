"""
TDD Tests for PostgreSQL Outbox Event-Driven Embedding Sync Controller (RCKG-404).
"""

import pytest
from app.services.embedding_sync import (
    EmbeddingSyncController,
    QdrantVectorStoreMock,
    OutboxEvent,
)


@pytest.fixture
def vector_store():
    store = QdrantVectorStoreMock()
    store.upsert_point(
        point_id="OBL-101",
        vector=[0.1] * 128,
        payload={"content": "Old password policy", "valid_from": "2025-01-01T00:00:00Z"},
    )
    return store


@pytest.fixture
def sync_controller(vector_store):
    return EmbeddingSyncController(vector_store=vector_store)


def test_embedding_sync_supersede_node_outbox_event(sync_controller, vector_store):
    """AC-1, AC-2, AC-3: Intercepts SUPERSEDE_NODE outbox events and updates valid_to in Qdrant payloads."""
    event = OutboxEvent(
        event_id="EVT-9001",
        event_type="SUPERSEDE_NODE",
        payload={
            "node_id": "OBL-101",
            "valid_to": "2026-07-30T00:00:00Z",
            "superseded_by": "OBL-101-V2",
        },
    )

    sync_result = sync_controller.process_outbox_event(event)

    assert sync_result["status"] == "SUCCESS"
    updated_point = vector_store.get_point("OBL-101")
    assert updated_point["payload"]["valid_to"] == "2026-07-30T00:00:00Z"
    assert updated_point["payload"]["superseded_by"] == "OBL-101-V2"


def test_embedding_sync_bitemporal_time_travel_filter(sync_controller, vector_store):
    """AC-3: Vector search filters points using valid_to bitemporal filter."""
    points = vector_store.search_with_bitemporal_filter(as_of_date="2025-06-01T00:00:00Z")
    assert len(points) == 1

    # Apply supersede event
    event = OutboxEvent(
        event_id="EVT-9001",
        event_type="SUPERSEDE_NODE",
        payload={
            "node_id": "OBL-101",
            "valid_to": "2026-07-30T00:00:00Z",
            "superseded_by": "OBL-101-V2",
        },
    )
    sync_controller.process_outbox_event(event)

    # After supersede date
    points_after = vector_store.search_with_bitemporal_filter(as_of_date="2026-08-01T00:00:00Z")
    assert len(points_after) == 0

