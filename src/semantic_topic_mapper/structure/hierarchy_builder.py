"""
Deterministic topic hierarchy builder.

Builds parent–child relationships between topics and inserts synthetic nodes
when intermediate topic IDs are missing (e.g. 18.2 missing between 18.1 and 18.3).
Does not modify TopicBlocks, use LLMs, or validate cross-references.
"""

from __future__ import annotations

from semantic_topic_mapper.models.topic_models import TopicBlock, TopicID, TopicNode
from semantic_topic_mapper.structure.topic_id_parser import parse_topic_id


def build_topic_hierarchy(blocks: list[TopicBlock]) -> dict[str, TopicNode]:
    """
    Build a topic hierarchy from a list of TopicBlocks.

    - Creates a TopicNode for each block that has a topic_id (blocks with
      topic_id=None are ignored).
    - Determines each node's parent by ancestor candidates; creates synthetic
      nodes for missing intermediate IDs.
    - Links parent and child; sorts each node's children_ids with a
      numeric-aware sort.

    Returns:
        Dict mapping topic_id.raw -> TopicNode (real and synthetic).
    """
    nodes: dict[str, TopicNode] = {}

    # 1. Create a TopicNode for each TopicBlock with a topic_id
    for block in blocks:
        if block.topic_id is None:
            continue
        tid = block.topic_id
        if tid.raw in nodes:
            continue  # avoid duplicate blocks for same ID
        node = TopicNode(
            topic_id=tid,
            parent_id=None,
            children_ids=[],
            block=block,
            synthetic=False,
        )
        nodes[tid.raw] = node

    # 2. Determine parent for each node (and create synthetics as needed)
    initial_raws = list(nodes.keys())
    for raw in initial_raws:
        node = nodes[raw]
        parent_tid = _find_or_create_parent(node.topic_id, nodes)
        if parent_tid is not None:
            node.parent_id = parent_tid
            if node.topic_id not in nodes[parent_tid.raw].children_ids:
                nodes[parent_tid.raw].children_ids.append(node.topic_id)

    # 3. Sort children_ids for every node (numeric-aware)
    for node in nodes.values():
        node.children_ids.sort(key=_topic_sort_key)

    return nodes


def _ancestor_raw_candidates(topic_id: TopicID) -> list[str]:
    """
    Return possible parent raw IDs from nearest to root.
    E.g. for 18.3.a with parts ("18","3","a") -> ["18.3", "18"].
    """
    parts = topic_id.parts
    if len(parts) <= 1:
        return []
    candidates: list[str] = []
    for i in range(len(parts) - 1, 0, -1):
        parent_parts = parts[:i]
        candidates.append(".".join(parent_parts))
    return candidates


def _find_or_create_parent(topic_id: TopicID, nodes: dict[str, TopicNode]) -> TopicID | None:
    """
    Find the nearest existing parent for this topic_id, or create a synthetic
    node for the missing ancestor and return it. Returns None if topic is root.
    """
    candidates = _ancestor_raw_candidates(topic_id)
    if not candidates:
        return None

    nearest_raw = candidates[0]
    if nearest_raw in nodes:
        return nodes[nearest_raw].topic_id

    # Nearest ancestor is missing: create synthetic node for it
    parsed = parse_topic_id(nearest_raw)
    if parsed is None:
        return None
    synthetic = TopicNode(
        topic_id=parsed,
        parent_id=None,
        children_ids=[],
        block=None,
        synthetic=True,
    )
    nodes[nearest_raw] = synthetic
    # Set the synthetic's parent recursively
    parent_tid = _find_or_create_parent(parsed, nodes)
    if parent_tid is not None:
        synthetic.parent_id = parent_tid
        if parsed not in nodes[parent_tid.raw].children_ids:
            nodes[parent_tid.raw].children_ids.append(parsed)
    return synthetic.topic_id


def _topic_sort_key(topic_id: TopicID) -> tuple:
    """
    Sort key for topic IDs: numeric parts compared as ints, letter parts as (type, value).
    E.g. 2.1, 2.2, 2.10, 2.10.a order correctly.
    """
    key: list[tuple[int, int | str]] = []
    for part in topic_id.parts:
        if part.isdigit():
            key.append((0, int(part)))
        else:
            key.append((1, part))
    return tuple(key)
