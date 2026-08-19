"""Catalog & Policy Knowledge Graph Exporter.

Converts catalog products, occasion rules, recipient constraints, and delivery slot compatibility
into a queryable JSON-LD and adjacency graph topology format for multi-hop recommendation traversal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeNode:
    id: str
    type: str  # Product, Occasion, Recipient, Palette, DeliveryWindow
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeRelation:
    source_id: str
    target_id: str
    relation: str  # SUITABLE_FOR, MATCHES_PALETTE, DELIVERABLE_IN, HAS_ADDON


class CatalogKnowledgeGraph:
    """Domain knowledge graph for product taxonomy, occasion matching, and policy compatibility."""

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: List[KnowledgeRelation] = []

    def add_node(self, node_id: str, node_type: str, name: str, properties: Optional[Dict[str, Any]] = None) -> KnowledgeNode:
        node = KnowledgeNode(id=node_id, type=node_type, name=name, properties=properties or {})
        self.nodes[node_id] = node
        return node

    def add_relation(self, source_id: str, target_id: str, relation: str) -> KnowledgeRelation:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"Both nodes must exist in knowledge graph: {source_id}, {target_id}")

        rel = KnowledgeRelation(source_id=source_id, target_id=target_id, relation=relation)
        self.relations.append(rel)
        return rel

    def get_products_for_occasion(self, occasion_id: str) -> List[KnowledgeNode]:
        """Find products suitable for a specific occasion by traversing SUITABLE_FOR relations."""
        product_ids = [rel.source_id for rel in self.relations if rel.target_id == occasion_id and rel.relation == "SUITABLE_FOR"]
        return [self.nodes[pid] for pid in product_ids if pid in self.nodes]

    def export_json_ld(self) -> Dict[str, Any]:
        """Export knowledge graph topology as JSON-LD compatible graph structure."""
        graph_nodes = []
        for node in self.nodes.values():
            graph_nodes.append({
                "@id": f"aea:{node.id}",
                "@type": node.type,
                "name": node.name,
                "properties": node.properties
            })

        for rel in self.relations:
            graph_nodes.append({
                "@id": f"rel:{rel.source_id}->{rel.target_id}",
                "@type": "Relationship",
                "source": f"aea:{rel.source_id}",
                "target": f"aea:{rel.target_id}",
                "relation": rel.relation
            })

        return {
            "@context": {
                "aea": "https://schema.lily-florist.com/aea/",
                "name": "https://schema.org/name"
            },
            "@graph": graph_nodes
        }
