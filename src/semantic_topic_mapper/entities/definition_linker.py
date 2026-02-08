"""
Deterministic entity definition linking.

Finds explicit definitions in text (e.g. "X" means ..., The term "X" shall
mean ...) and enriches existing Entity objects with definition metadata. Handles
only explicit definition patterns; does not use LLMs or infer definitions from
context. Does not create new entities.
"""

from __future__ import annotations

import re

from semantic_topic_mapper.entities.entity_models import Entity
from semantic_topic_mapper.models.topic_models import TopicBlock


# Definition text runs until first period or newline
_DEF_TAIL = r"([^.\n]*)"

# Pattern A: "X" means ...
_PATTERN_A = re.compile(r'"([^"]+)"\s+means\s+' + _DEF_TAIL)

# Pattern B: "X" shall mean ...
_PATTERN_B = re.compile(r'"([^"]+)"\s+shall\s+mean\s+' + _DEF_TAIL)

# Pattern C: The term "X" means ...
_PATTERN_C = re.compile(r"The\s+term\s+" r'"([^"]+)"\s+means\s+' + _DEF_TAIL)


def link_entity_definitions(
    entities: list[Entity],
    blocks: list[TopicBlock],
) -> None:
    """
    Find explicit definition patterns in blocks and attach definition_text and
    definition_topic to matching entities. First occurrence only; later
    definitions for an entity are ignored (v1). Mutates Entity objects in place.
    """
    lookup: dict[str, Entity] = {e.canonical_name: e for e in entities}

    for block in blocks:
        if block.topic_id is None:
            continue
        text = block.raw_text
        tid = block.topic_id

        for pattern in (_PATTERN_A, _PATTERN_B, _PATTERN_C):
            for mo in pattern.finditer(text):
                quoted_term = mo.group(1).strip()
                definition = mo.group(2).strip()
                if not quoted_term or not definition:
                    continue
                entity = lookup.get(quoted_term)
                if entity is None:
                    continue
                if entity.definition_text is not None:
                    continue
                entity.definition_text = definition
                entity.definition_topic = tid
