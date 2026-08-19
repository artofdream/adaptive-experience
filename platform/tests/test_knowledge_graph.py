"""Unit tests for CatalogKnowledgeGraph in platform/aea_platform/knowledge_graph.py."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.knowledge_graph import CatalogKnowledgeGraph


class TestCatalogKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        self.kg = CatalogKnowledgeGraph()

    def test_add_nodes_and_relations(self):
        p1 = self.kg.add_node("p:classic-rose", "Product", "Classic Rose Dozen", {"price": 79.99})
        occ = self.kg.add_node("occ:birthday", "Occasion", "Mother Birthday")

        rel = self.kg.add_relation(p1.id, occ.id, "SUITABLE_FOR")

        self.assertEqual(len(self.kg.nodes), 2)
        self.assertEqual(len(self.kg.relations), 1)
        self.assertEqual(rel.relation, "SUITABLE_FOR")

    def test_get_products_for_occasion(self):
        p1 = self.kg.add_node("p:classic-rose", "Product", "Classic Rose Dozen")
        p2 = self.kg.add_node("p:sunflower-spark", "Product", "Sunflower Bouquet")
        occ = self.kg.add_node("occ:birthday", "Occasion", "Mother Birthday")

        self.kg.add_relation(p1.id, occ.id, "SUITABLE_FOR")
        self.kg.add_relation(p2.id, occ.id, "SUITABLE_FOR")

        products = self.kg.get_products_for_occasion("occ:birthday")
        self.assertEqual(len(products), 2)
        p_ids = [p.id for p in products]
        self.assertIn("p:classic-rose", p_ids)
        self.assertIn("p:sunflower-spark", p_ids)

    def test_export_json_ld(self):
        self.kg.add_node("p:classic-rose", "Product", "Classic Rose Dozen")
        json_ld = self.kg.export_json_ld()
        self.assertIn("@context", json_ld)
        self.assertIn("@graph", json_ld)
        self.assertEqual(len(json_ld["@graph"]), 1)


if __name__ == "__main__":
    unittest.main()
