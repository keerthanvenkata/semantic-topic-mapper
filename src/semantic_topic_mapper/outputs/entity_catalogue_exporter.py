"""
Entity catalogue exporter: serialize entity list to CSV.

Maps internal Entity list to the assignment deliverable format (entity_id,
canonical_name, entity_type, first_seen_topic, definition_topic, mention_count).
Thin serializer only; no LLM or inference.
"""

from __future__ import annotations

import csv

from semantic_topic_mapper.entities.entity_models import Entity


def export_entity_catalogue(entities: list[Entity], path: str) -> None:
    """
    Write a CSV file with columns: entity_id, canonical_name, entity_type,
    first_seen_topic, definition_topic, mention_count. Topic IDs are written
    as raw strings; empty string when None.
    """
    columns = [
        "entity_id",
        "canonical_name",
        "entity_type",
        "first_seen_topic",
        "definition_topic",
        "mention_count",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for e in entities:
            w.writerow({
                "entity_id": e.entity_id,
                "canonical_name": e.canonical_name,
                "entity_type": e.entity_type or "",
                "first_seen_topic": e.first_seen_topic.raw,
                "definition_topic": e.definition_topic.raw if e.definition_topic else "",
                "mention_count": len(e.mentions),
            })
