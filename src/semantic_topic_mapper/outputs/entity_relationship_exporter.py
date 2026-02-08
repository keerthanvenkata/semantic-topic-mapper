"""
Entity relationship exporter: serialize entity relationships to JSON.

Maps internal EntityRelationship list to the assignment deliverable format
(source, target, relation_type, topic_id). Thin serializer only; no LLM or inference.
"""

from __future__ import annotations

import json

from semantic_topic_mapper.entities.entity_models import EntityRelationship


def export_entity_relationships(
    relationships: list[EntityRelationship],
    path: str,
) -> None:
    """
    Write a JSON list of objects with source, target, relation_type, and
    topic_id (raw string). One object per relationship.
    """
    data = [
        {
            "source": r.source_entity_id,
            "target": r.target_entity_id,
            "relation_type": r.relation_type,
            "topic_id": r.topic_id.raw,
        }
        for r in relationships
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
