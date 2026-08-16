"""
TDD Tests for Downstream GraphRAG Translation Layer Interface (RCKG-405).
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.api.extract import router as extract_router
from app.services.graphrag_translator import (
    GraphRAGTranslationService,
    GraphRAGExportPayload,
)

app = FastAPI()
app.include_router(extract_router, prefix="/api/v1")
client = TestClient(app)


def test_graphrag_subgraph_translation_export():
    """AC-1 & AC-2: Translates Memgraph nodes & edges into standard GraphRAG Entity, Relationship, Community JSON."""
    service = GraphRAGTranslationService()

    nodes = [
        {"node_id": "REG-01", "type": "StatutoryRequirement", "title": "GDPR Article 32"},
        {"node_id": "POL-01", "type": "InternalPolicy", "title": "SecOps Data Protection Policy"},
    ]
    edges = [
        {"source_id": "REG-01", "target_id": "POL-01", "relation_type": "EQUIVALENT_TO", "confidence": 0.95},
    ]

    export = service.export_subgraph(nodes=nodes, edges=edges, as_of_date="2026-07-30T00:00:00Z")

    assert isinstance(export, GraphRAGExportPayload)
    assert len(export.entities) == 2
    assert len(export.relationships) == 1
    assert len(export.community_summaries) >= 1
    assert export.entities[0]["id"] == "REG-01"
    assert export.relationships[0]["type"] == "EQUIVALENT_TO"


def test_graphrag_export_rest_api():
    """AC-3: REST endpoint GET /api/v1/graph/graphrag-export returns exported GraphRAG payload."""
    response = client.get("/api/v1/graph/graphrag-export?as_of_date=2026-07-30T00:00:00Z")

    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "relationships" in data
    assert "community_summaries" in data
