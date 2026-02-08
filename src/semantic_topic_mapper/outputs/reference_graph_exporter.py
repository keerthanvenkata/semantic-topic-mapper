"""
Reference graph exporter: serialize topic reference graph to PDF.

Builds a directed graph from the adjacency dict (topic_id.raw -> set of
referenced topic_id.raw) and renders it as PDF using networkx and matplotlib.
Nodes are topic IDs; edges are references. Thin serializer only; no LLM or inference.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx


def export_reference_graph(graph: dict[str, set[str]], path: str) -> None:
    """
    Generate a directed graph PDF. Nodes are topic IDs (raw strings); edges
    are references from source to target. Uses networkx and matplotlib to
    lay out and render the graph.
    """
    g = nx.DiGraph()
    g.add_nodes_from(graph.keys())
    for source, targets in graph.items():
        for target in targets:
            g.add_edge(source, target)
            g.add_node(target)
    pos = nx.spring_layout(g, k=1.5, iterations=50, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw(
        g,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=800,
        font_size=8,
        arrows=True,
        edge_color="gray",
    )
    plt.tight_layout()
    plt.savefig(path, format="pdf", bbox_inches="tight")
    plt.close()
