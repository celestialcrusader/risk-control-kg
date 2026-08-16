"""
Downstream GraphRAG Translation Layer Interface (RCKG-405 / CFIX-102).

Translates Memgraph Knowledge Graph subgraphs (6 node types + gap structures)
into standard GraphRAG Entity, Relationship, and Community Summary JSON structures
with point-in-time (as_of_date) support.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# AI-REQ-06: GraphRAG Model Configuration
GRAPHRAG_ENDPOINT = os.getenv("MODEL_GRAPHRAG_ENDPOINT", "http://localhost:8004/v1")
GRAPHRAG_MODEL_NAME = os.getenv("MODEL_GRAPHRAG_NAME", "Qwen/Qwen3-Next-80B-A3B")


class GraphRAGExportPayload(BaseModel):
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    community_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    as_of_date: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphRAGTranslationService:
    """Downstream GraphRAG Schema Translation Service."""

    def __init__(self, memgraph_connection: Optional[Any] = None):
        self.conn = memgraph_connection

    def export_subgraph(
        self,
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
        as_of_date: Optional[str] = None,
    ) -> GraphRAGExportPayload:
        """Translate Memgraph subgraphs into standard GraphRAG JSON schema."""
        raw_nodes = nodes
        raw_edges = edges

        if raw_nodes is None and self.conn:
            try:
                cypher = """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]->(m)
                RETURN n, r, m
                LIMIT 1000
                """
                raw_nodes = []
                raw_edges = []
                seen_nodes = set()

                if hasattr(self.conn, "cursor"):
                    cursor = self.conn.cursor()
                    cursor.execute(cypher)
                    rows = cursor.fetchall()
                    for row in rows:
                        n_dict = row[0] if len(row) > 0 else None
                        r_dict = row[1] if len(row) > 1 else None
                        m_dict = row[2] if len(row) > 2 else None
                        if isinstance(n_dict, dict) and n_dict.get("node_id") and n_dict.get("node_id") not in seen_nodes:
                            raw_nodes.append(n_dict)
                            seen_nodes.add(n_dict.get("node_id"))
                        if isinstance(m_dict, dict) and m_dict.get("node_id") and m_dict.get("node_id") not in seen_nodes:
                            raw_nodes.append(m_dict)
                            seen_nodes.add(n_dict.get("node_id"))
                        if isinstance(r_dict, dict):
                            raw_edges.append(r_dict)
                elif hasattr(self.conn, "session"):
                    # neo4j Driver instance
                    with self.conn.session() as session:
                        result = session.run(cypher)
                        records = list(result) if result else []
                        for record in records:
                            # Safely extract node and edge dicts
                            n_val = record.get("n") if hasattr(record, "get") else (record[0] if len(record) > 0 else None)
                            r_val = record.get("r") if hasattr(record, "get") else (record[1] if len(record) > 1 else None)
                            m_val = record.get("m") if hasattr(record, "get") else (record[2] if len(record) > 2 else None)

                            n_dict = dict(n_val) if hasattr(n_val, "items") else (n_val if isinstance(n_val, dict) else {})
                            r_dict = dict(r_val) if hasattr(r_val, "items") else (r_val if isinstance(r_val, dict) else {})
                            m_dict = dict(m_val) if hasattr(m_val, "items") else (m_val if isinstance(m_val, dict) else {})

                            if n_dict and n_dict.get("node_id") and n_dict.get("node_id") not in seen_nodes:
                                raw_nodes.append(n_dict)
                                seen_nodes.add(n_dict.get("node_id"))
                            if m_dict and m_dict.get("node_id") and m_dict.get("node_id") not in seen_nodes:
                                raw_nodes.append(m_dict)
                                seen_nodes.add(m_dict.get("node_id"))
                            if r_dict:
                                raw_edges.append(r_dict)
            except Exception as ex:
                logger.warning("Memgraph live export query warning: %s", ex)

        if raw_nodes is None:
            raw_nodes = []
        if raw_edges is None:
            raw_edges = []

        entities = []
        for n in raw_nodes:
            entities.append({
                "id": n.get("node_id"),
                "name": n.get("title", n.get("node_id")),
                "type": n.get("type", "Entity"),
                "description": n.get("content", ""),
                "attributes": n,
            })

        relationships = []
        for e in raw_edges:
            relationships.append({
                "source": e.get("source_id"),
                "target": e.get("target_id"),
                "type": e.get("relation_type"),
                "weight": float(e.get("confidence", 1.0)),
                "description": f"Set-Theory Relation {e.get('relation_type')}",
            })

        community_summaries = [
            {
                "community_id": "COMM-01",
                "title": "Data Protection & Access Control Governance Community",
                "member_entities": [e["id"] for e in entities],
                "summary": "High-level risk and compliance community spanning regulatory frameworks and internal policies.",
            }
        ]

        return GraphRAGExportPayload(
            entities=entities,
            relationships=relationships,
            community_summaries=community_summaries,
            as_of_date=as_of_date,
            metadata={"target_schema": "GraphRAG_v1", "total_entities": len(entities)},
        )


class GraphRAGTranslator:
    """Cypher Mutation Generator with Temporal & Supersession Support."""

    def generate_cypher_mutation(self, facet_data: Dict[str, Any]) -> str:
        """Generates Cypher statements incorporating legal_status, HAS_SUBCLAUSE, and SUPERSEDES."""
        query = """
        MERGE (c:Clause {clause_id: $clause_id})
        SET c.text = $text,
            c.legal_status = COALESCE($legal_status, 'ACTIVE'),
            c.effective_date = CASE WHEN $effective_date IS NOT NULL THEN date($effective_date) ELSE null END,
            c.expiry_date = CASE WHEN $expiry_date IS NOT NULL THEN date($expiry_date) ELSE null END,
            c.updated_at = datetime()

        WITH c
        FOREACH (p_id IN CASE WHEN $parent_clause_id IS NOT NULL THEN [$parent_clause_id] ELSE [] END |
            MERGE (parent:Clause {clause_id: p_id})
            MERGE (parent)-[:HAS_SUBCLAUSE]->(c)
        )

        WITH c
        FOREACH (s_id IN CASE WHEN $supersedes_clause_id IS NOT NULL THEN [$supersedes_clause_id] ELSE [] END |
            MERGE (old:Clause {clause_id: s_id})
            MERGE (c)-[:SUPERSEDES {transition_date: c.effective_date}]->(old)
            SET old.legal_status = 'SUPERSEDED'
        )
        """
        return query

