"""
Entity extraction: Entity and EntityMention models.

These models represent entities and their mentions in the document. They are
part of the semantic layer (entity extraction and enrichment), not the
structural hierarchy (topics, blocks, nodes). This module defines data
structures only; detection and grouping logic live in other modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from semantic_topic_mapper.models.topic_models import TopicID


RegionType = Literal["paragraph", "subclause", "title"]


@dataclass
class EntityMention:
    """
    A single occurrence of an entity in the document.

    Carries exact span (start_char, end_char) and the surface text at that
    span, plus region metadata (paragraph, subclause, or title and optional
    subclause label) for traceability. Multiple mentions may be aggregated
    into one canonical Entity.
    """

    topic_id: TopicID
    start_char: int
    end_char: int
    text: str
    region_type: RegionType
    region_label: str | None  # e.g. subclause label "b"


@dataclass
class Entity:
    """
    A canonical entity aggregated across one or more mentions.

    In v1, entities are grouped purely by canonical string match; more
    advanced alias resolution may be added later. entity_type (e.g.
    "organization", "role", "temporal") may be None in v1 and filled later
    by deterministic or LLM enrichment.

    Entity = one logical thing (e.g. "the Commission"); EntityMention = one
    place in the document where that thing is referred to.
    """

    entity_id: str  # internal unique ID like "E12"
    canonical_name: str
    entity_type: str | None  # e.g. "organization", "role", "temporal"; may be None in v1
    first_seen_topic: TopicID
    mentions: list[EntityMention]
    definition_text: str | None = None  # set by definition_linker when explicit "X" means ... is found
    definition_topic: TopicID | None = None  # topic where definition appears
