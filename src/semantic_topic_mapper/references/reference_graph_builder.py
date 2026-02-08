"""
Reference graph builder and broken-reference detection.

Builds a directed graph of topic-to-topic references (adjacency list keyed by
topic_id.raw). Detects structural issues: references to missing topics or to
synthetic (placeholder) topics. This layer only validates structural presence
of targets, not semantic correctness. Does not use LLMs or modify the hierarchy.

Optional future enhancements (not in v1): additional issue types such as
"self_reference" or "circular_reference"; per-edge reference counts; or
storing a reverse graph for backward lookups.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_topic_mapper.models.reference_models import TopicReference
from semantic_topic_mapper.models.topic_models import TopicID, TopicNode


@dataclass
class ReferenceIssue:
    """
    A structural problem with a reference: the target topic is missing from the
    hierarchy or is a synthetic (placeholder) node with no content.
    """

    source_topic_id: TopicID
    target_topic_id: TopicID
    issue_type: str  # "missing_topic" or "synthetic_target"
    start_char: int
    end_char: int


def build_reference_graph(
    nodes: dict[str, TopicNode],
    references: list[TopicReference],
) -> tuple[dict[str, set[str]], list[ReferenceIssue]]:
    """
    Build a directed reference graph and list of structural reference issues.

    - Graph edges connect TopicNodes by topic_id.raw; keys and set elements
      are raw topic ID strings. The graph is an adjacency list: each key maps
      to the set of raw IDs it references.
    - This layer only validates structural presence (target exists, target is
      real vs synthetic); it does not assess semantic correctness.

    Returns:
        (graph, issues): graph is dict[str, set[str]]; issues is one
        ReferenceIssue per problematic reference occurrence.
    """
    graph: dict[str, set[str]] = {}
    issues: list[ReferenceIssue] = []

    for ref in references:
        source_raw = ref.source_topic_id.raw
        target_raw = ref.target_topic_id.raw

        graph.setdefault(source_raw, set()).add(target_raw)

        if target_raw not in nodes:
            issues.append(
                ReferenceIssue(
                    source_topic_id=ref.source_topic_id,
                    target_topic_id=ref.target_topic_id,
                    issue_type="missing_topic",
                    start_char=ref.start_char,
                    end_char=ref.end_char,
                )
            )
        elif nodes[target_raw].synthetic:
            issues.append(
                ReferenceIssue(
                    source_topic_id=ref.source_topic_id,
                    target_topic_id=ref.target_topic_id,
                    issue_type="synthetic_target",
                    start_char=ref.start_char,
                    end_char=ref.end_char,
                )
            )

    return (graph, issues)
