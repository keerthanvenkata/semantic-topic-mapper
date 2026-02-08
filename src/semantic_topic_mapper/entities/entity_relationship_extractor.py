"""
Entity relationship extraction.

Produces list of EntityRelationship from entities and blocks. v1: returns
empty list; relationship inference may be added later (deterministic or LLM).
"""

from __future__ import annotations

from semantic_topic_mapper.entities.entity_models import Entity, EntityRelationship
from semantic_topic_mapper.models.topic_models import TopicBlock


def extract_entity_relationships(
    entities: list[Entity],
    blocks: list[TopicBlock],
) -> list[EntityRelationship]:
    """
    Extract directed relationships between entities (e.g. source reports to
    target). v1: returns empty list; no inference implemented yet.
    """
    return []
