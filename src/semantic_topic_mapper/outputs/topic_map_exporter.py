"""
Topic map exporter: serialize topic hierarchy to JSON.

Maps internal TopicNode dict to the assignment deliverable format (topic_id.raw
-> title, synthetic, children). Thin serializer only; no LLM or inference.
"""

from __future__ import annotations

import json

from semantic_topic_mapper.models.topic_models import TopicNode


def export_topic_map(nodes: dict[str, TopicNode], path: str) -> None:
    """
    Write a JSON file mapping each topic_id.raw to title, synthetic flag,
    and list of child topic_id.raw strings. Block title is used when present.
    In v1, title is already clean (e.g. "Annual Renewal"); if segmentation
    ever includes full header text, keep title normalized here.
    """
    out: dict[str, dict] = {}
    for raw, node in nodes.items():
        title = node.block.title if node.block is not None else None
        children = [c.raw for c in node.children_ids]
        out[raw] = {
            "title": title,
            "synthetic": node.synthetic,
            "children": children,
        }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
