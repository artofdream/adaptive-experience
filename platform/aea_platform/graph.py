"""Session State & Adaptive Workspace Property Graph Model.

Implements explicit graph representation for session intent nodes, tile nodes T-01..T-08,
recommendation nodes, customization nodes, and directed dependency/invalidation edges.
Coherent with ADR-001, ADR-005, ADR-009, and ADR-011.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Set, Optional


class NodeType(str, Enum):
    INTENT = "INTENT"
    TILE = "TILE"
    RECOMMENDATION = "RECOMMENDATION"
    CUSTOMIZATION = "CUSTOMIZATION"
    ORDER = "ORDER"


class EdgeType(str, Enum):
    DEPENDS_ON = "DEPENDS_ON"
    INVALIDATES = "INVALIDATES"
    DERIVED_FROM = "DERIVED_FROM"


@dataclass
class GraphNode:
    id: str
    node_type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    context_version: int = 1


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: Dict[str, Any] = field(default_factory=dict)


class SessionPropertyGraph:
    """Directed property graph representing active session state and tile relationships."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adj_out: Dict[str, List[GraphEdge]] = {}
        self._adj_in: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node_id: str, node_type: NodeType, properties: Optional[Dict[str, Any]] = None, context_version: int = 1) -> GraphNode:
        node = GraphNode(id=node_id, node_type=node_type, properties=properties or {}, context_version=context_version)
        self.nodes[node_id] = node
        self._adj_out.setdefault(node_id, [])
        self._adj_in.setdefault(node_id, [])
        return node

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, properties: Optional[Dict[str, Any]] = None) -> GraphEdge:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"Both nodes must exist in graph: {source_id}, {target_id}")

        edge = GraphEdge(source_id=source_id, target_id=target_id, edge_type=edge_type, properties=properties or {})
        self.edges.append(edge)
        self._adj_out[source_id].append(edge)
        self._adj_in[target_id].append(edge)
        return edge

    def get_invalidated_nodes(self, updated_node_id: str) -> Set[str]:
        """Traverse INVALIDATES and DEPENDS_ON edges to return nodes impacted by an intent update."""
        invalidated: Set[str] = set()
        queue = [updated_node_id]

        while queue:
            current_id = queue.pop(0)
            for edge in self._adj_out.get(current_id, []):
                if edge.edge_type in (EdgeType.INVALIDATES, EdgeType.DEPENDS_ON):
                    if edge.target_id not in invalidated:
                        invalidated.add(edge.target_id)
                        queue.append(edge.target_id)

        return invalidated

    def to_dict(self) -> Dict[str, Any]:
        """Serialize property graph state to a dictionary structure."""
        return {
            "session_id": self.session_id,
            "nodes": [
                {
                    "id": n.id,
                    "type": n.node_type.value,
                    "context_version": n.context_version,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type.value,
                    "properties": e.properties,
                }
                for e in self.edges
            ],
        }
