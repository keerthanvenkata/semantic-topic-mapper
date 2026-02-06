"""
Reference models: TopicReference.

Graph edges always connect TopicNodes. References are attached to text spans
within a topic; source_region_type indicates whether the span is in a paragraph,
subclause, or title. Subclauses never become nodes in the topic graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from semantic_topic_mapper.models.topic_models import TopicID


SourceRegionType = Literal["paragraph", "subclause", "title"]


@dataclass
class TopicReference:
    """
    A reference from one topic to another (or to a topic range).

    - source_topic_id: always a real TopicNode (the topic where the reference text appears).
    - target_topic_id: the topic (or start of range) being referred to.
    - relation_type: str in v1; later may be Literal["explicit", "implicit", "range", "llm_inferred"].
    - start_char, end_char: span of the reference text in the source document.
    - source_region_type: where within the topic the reference appears
      ("paragraph" | "subclause" | "title").
    - source_region_label: optional; e.g. "b" when reference is inside subclause (b).
    """

    source_topic_id: TopicID
    target_topic_id: TopicID
    relation_type: str  # v1: open; later e.g. Literal["explicit","implicit","range","llm_inferred"]
    start_char: int
    end_char: int
    source_region_type: SourceRegionType
    source_region_label: str | None = None
