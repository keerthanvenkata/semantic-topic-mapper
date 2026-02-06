"""
Topic modeling: TopicID, TopicBlock, TopicNode, Subclause.

These models represent document structure. Hierarchy and gap-filling
are the responsibility of hierarchy_builder; this module only defines structure.

Architectural rule (v1): Subclauses (a), (b), (c) are local structural elements
inside a TopicBlock. They are NOT topics and do NOT become TopicNodes.
Graph edges always connect TopicNodes only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TopicID:
    """
    Structured identity of a topic.

    - raw: original string form (e.g. "2.1.a")
    - parts: hierarchical parts (e.g. ["2", "1", "a"])
    - level: depth (1-based; len(parts))

    Future methods (not implemented yet): parent(), ancestors(),
    is_parent_of(other), same_branch_as(other).
    """

    # Future helpers: parent(), ancestors(), is_parent_of(), same_branch_as()

    raw: str
    parts: tuple[str, ...]
    level: int

    def __post_init__(self) -> None:
        if self.level != len(self.parts):
            raise ValueError("level must equal len(parts)")


@dataclass
class Subclause:
    """
    Local structural element inside a TopicBlock (e.g. (a), (b), (c)).

    Subclauses are NOT topics and must NOT become TopicNodes. They live
    only inside TopicBlock; the topic graph has no nodes for subclauses.
    """

    label: str  # e.g. "a", "b"
    text: str
    start_char: int
    end_char: int


@dataclass
class TopicBlock:
    """
    Chunk of document text associated with a topic.

    - topic_id=None allows orphan content (no ID assigned).
    - No hierarchy info here; hierarchy is in TopicNode.
    - raw_text kept intact for LLM grounding, reference span tracking, exports.
    - subclauses: list of (a), (b), (c) etc. inside this block; in v1 remain
      inside TopicBlock, not promoted to topic hierarchy.
    """

    topic_id: TopicID | None
    title: str | None
    raw_text: str
    start_char: int
    end_char: int
    subclauses: list[Subclause] = field(default_factory=list)


@dataclass
class TopicNode:
    """
    Node in the topic hierarchy graph.

    - block=None for synthetic nodes (gap placeholders).
    - synthetic=True when the node was created for a missing topic number
      (e.g. 18.2 missing between 18.1 and 18.3); maintains structural
      correctness without pretending content exists.
    """

    topic_id: TopicID
    parent_id: TopicID | None
    children_ids: list[TopicID]
    block: TopicBlock | None
    synthetic: bool
