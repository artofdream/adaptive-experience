"""Unit tests for SessionPropertyGraph in platform/aea_platform/graph.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.graph import SessionPropertyGraph, NodeType, EdgeType


class TestSessionPropertyGraph(unittest.TestCase):
    def setUp(self):
        self.graph = SessionPropertyGraph(session_id="test-session-123")

    def test_add_nodes_and_edges(self):
        intent = self.graph.add_node("intent:mother-birthday", NodeType.INTENT, {"occasion": "mother_birthday"})
        tile_t01 = self.graph.add_node("tile:T-01", NodeType.TILE, {"tile_id": "T-01"})
        tile_t02 = self.graph.add_node("tile:T-02", NodeType.TILE, {"tile_id": "T-02"})

        edge1 = self.graph.add_edge(intent.id, tile_t01.id, EdgeType.INVALIDATES)
        edge2 = self.graph.add_edge(tile_t01.id, tile_t02.id, EdgeType.DEPENDS_ON)

        self.assertEqual(len(self.graph.nodes), 3)
        self.assertEqual(len(self.graph.edges), 2)
        self.assertEqual(edge1.edge_type, EdgeType.INVALIDATES)

    def test_get_invalidated_nodes(self):
        intent = self.graph.add_node("intent:mother-birthday", NodeType.INTENT)
        tile_t01 = self.graph.add_node("tile:T-01", NodeType.TILE)
        tile_t02 = self.graph.add_node("tile:T-02", NodeType.TILE)
        tile_t03 = self.graph.add_node("tile:T-03", NodeType.TILE)

        self.graph.add_edge(intent.id, tile_t01.id, EdgeType.INVALIDATES)
        self.graph.add_edge(tile_t01.id, tile_t02.id, EdgeType.DEPENDS_ON)

        invalidated = self.graph.get_invalidated_nodes(intent.id)
        self.assertIn("tile:T-01", invalidated)
        self.assertIn("tile:T-02", invalidated)
        self.assertNotIn("tile:T-03", invalidated)

    def test_to_dict_serialization(self):
        self.graph.add_node("intent:1", NodeType.INTENT)
        payload = self.graph.to_dict()
        self.assertEqual(payload["session_id"], "test-session-123")
        self.assertEqual(len(payload["nodes"]), 1)


if __name__ == "__main__":
    unittest.main()
