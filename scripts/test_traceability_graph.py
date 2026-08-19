#!/usr/bin/env python3
"""Unit tests for generate_traceability_graph.py."""

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_traceability_graph import load_traceability_chains, generate_mermaid_graph, generate_dot_graph


class TestTraceabilityGraph(unittest.TestCase):
    def test_load_traceability_chains(self):
        chains = load_traceability_chains()
        self.assertEqual(len(chains), 40)

    def test_generate_mermaid_graph(self):
        chains = load_traceability_chains()
        mermaid = generate_mermaid_graph(chains)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("BG-001", mermaid)
        self.assertIn("FR-001", mermaid)

    def test_generate_dot_graph(self):
        chains = load_traceability_chains()
        dot = generate_dot_graph(chains)
        self.assertIn("digraph TraceabilityDAG", dot)
        self.assertIn('"BG-001" -> "EP-001"', dot)


if __name__ == "__main__":
    unittest.main()
