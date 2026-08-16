"""
Transitive Reduction & Graph Pruning Engine (STORY-MAINT-102).

Detects redundant multi-hop transitive triangles, generates direct shortcut edges,
and maintains clean graph topology without transitive confidence dilution.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str = "EQUIVALENT_TO"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    is_golden: bool = False


class TransitiveReductionEngine:
    """Computes transitive reduction and shortcut collapse on knowledge graph topology."""

    def __init__(self, shortcut_threshold: float = 0.75):
        self.shortcut_threshold = shortcut_threshold

    def identify_prunable_edges(self, edges: List[GraphEdge]) -> Dict[str, List[GraphEdge]]:
        """
        Identifies redundant edges where A -> B and B -> C exist, and A -> C is non-golden / weaker.
        """
        adjacency: Dict[str, Dict[str, GraphEdge]] = {}
        for edge in edges:
            adjacency.setdefault(edge.source_id, {})[edge.target_id] = edge

        redundant_edges = []

        for a in adjacency:
            for b in adjacency[a]:
                if b in adjacency:
                    for c in adjacency[b]:
                        # Check if direct edge A -> C exists
                        if c in adjacency[a]:
                            direct_edge = adjacency[a][c]
                            # If direct edge is non-golden or weaker than the transitive chain, flag for prune
                            if not direct_edge.is_golden:
                                redundant_edges.append(direct_edge)

        return {"redundant_edges": redundant_edges}

    def generate_transitive_shortcuts(self, edges: List[GraphEdge]) -> List[GraphEdge]:
        """
        Generates direct A -> C shortcuts when A -> B and B -> C are high-confidence EQUIVALENT_TO edges.
        """
        adjacency: Dict[str, Dict[str, GraphEdge]] = {}
        for edge in edges:
            adjacency.setdefault(edge.source_id, {})[edge.target_id] = edge

        shortcuts = []

        for a in adjacency:
            for b in adjacency[a]:
                edge_ab = adjacency[a][b]
                if edge_ab.relation == "EQUIVALENT_TO" and b in adjacency:
                    for c in adjacency[b]:
                        if c == a:
                            continue
                        edge_bc = adjacency[b][c]
                        if edge_bc.relation == "EQUIVALENT_TO":
                            combined_conf = round(edge_ab.confidence * edge_bc.confidence, 4)
                            if combined_conf >= self.shortcut_threshold and c not in adjacency[a]:
                                shortcuts.append(
                                    GraphEdge(
                                        source_id=a,
                                        target_id=c,
                                        relation="EQUIVALENT_TO",
                                        confidence=combined_conf,
                                        is_golden=False,
                                    )
                                )

        logger.info("Generated %d transitive shortcut edges", len(shortcuts))
        return shortcuts
