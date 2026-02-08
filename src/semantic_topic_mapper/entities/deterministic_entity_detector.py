"""
Deterministic entity mention detection.

High-precision, low-recall v1 detector: extracts entity mentions from
TopicBlocks using simple rule-based heuristics (capitalized multi-word phrases,
quoted defined terms). Does NOT use LLMs, alias resolution, or relationship
inference. Prioritizes precision over recall; some mentions may be missed.
Subsequent LLM enrichment can propose more or link implicit mentions; such
outputs are advisory and surfaced with confidence rather than altering the
deterministic backbone automatically.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import cast

from semantic_topic_mapper.entities.entity_models import Entity, EntityMention, RegionType
from semantic_topic_mapper.models.topic_models import TopicBlock, TopicID


# Rule A: 2–5 words, each capitalized or connector (of, and, for, the)
_CAP_PHRASE_PATTERN = re.compile(
    r"\b(?:[A-Z][a-z]*|of|and|for|the)(?:\s+(?:[A-Z][a-z]*|of|and|for|the)){1,4}\b"
)

# Rule B: double-quoted string (content captured; filter for ≥1 capitalized word in code)
_QUOTED_PATTERN = re.compile(r'"([^"]+)"')


def detect_entities(blocks: list[TopicBlock]) -> list[Entity]:
    """
    Extract high-confidence entity mentions from blocks and return entities
    with at least two mentions (grouped by exact canonical name match).
    """
    raw_mentions: list[tuple[str, int, int, TopicID, str, str | None]] = []
    # (canonical_name, start_char, end_char, topic_id, region_type, region_label)

    for block in blocks:
        if block.topic_id is None:
            continue
        tid = block.topic_id
        base: int

        if block.title:
            base = block.start_char
            for text, rel_start, rel_end in _rule_a_matches(block.title):
                raw_mentions.append((text, base + rel_start, base + rel_end, tid, "title", None))
            for text, rel_start, rel_end in _rule_b_matches(block.title):
                raw_mentions.append((text, base + rel_start, base + rel_end, tid, "title", None))

        base = block.start_char
        for text, rel_start, rel_end in _rule_a_matches(block.raw_text):
            raw_mentions.append((text, base + rel_start, base + rel_end, tid, "paragraph", None))
        for text, rel_start, rel_end in _rule_b_matches(block.raw_text):
            raw_mentions.append((text, base + rel_start, base + rel_end, tid, "paragraph", None))

        for sub in block.subclauses:
            base = sub.start_char
            for text, rel_start, rel_end in _rule_a_matches(sub.text):
                raw_mentions.append(
                    (text, base + rel_start, base + rel_end, tid, "subclause", sub.label)
                )
            for text, rel_start, rel_end in _rule_b_matches(sub.text):
                raw_mentions.append(
                    (text, base + rel_start, base + rel_end, tid, "subclause", sub.label)
                )

    by_name: dict[str, list[tuple[int, int, TopicID, str, str | None]]] = defaultdict(list)
    for canonical_name, start_char, end_char, topic_id, region_type, region_label in raw_mentions:
        by_name[canonical_name].append((start_char, end_char, topic_id, region_type, region_label))

    entities: list[Entity] = []
    eligible = [(name, tuples) for name, tuples in by_name.items() if len(tuples) >= 2]
    eligible.sort(key=lambda p: p[0])
    for idx, (canonical_name, mention_tuples) in enumerate(eligible, start=1):
        mention_tuples.sort(key=lambda t: t[0])
        mentions = [
            EntityMention(
                topic_id=topic_id,
                start_char=start_char,
                end_char=end_char,
                text=canonical_name,
                region_type=cast(RegionType, region_type),
                region_label=region_label,
            )
            for start_char, end_char, topic_id, region_type, region_label in mention_tuples
        ]
        first_topic = mentions[0].topic_id
        entities.append(
            Entity(
                entity_id=f"E{idx}",
                canonical_name=canonical_name,
                entity_type=None,
                first_seen_topic=first_topic,
                mentions=mentions,
            )
        )
    return entities


def _rule_a_matches(text: str) -> list[tuple[str, int, int]]:
    """Rule A: capitalized multi-word phrases (2–5 words). Returns (phrase, start, end) relative to text."""
    result: list[tuple[str, int, int]] = []
    for mo in _CAP_PHRASE_PATTERN.finditer(text):
        result.append((mo.group(0), mo.start(), mo.end()))
    return result


def _rule_b_matches(text: str) -> list[tuple[str, int, int]]:
    """Rule B: quoted defined terms; content must contain at least one capitalized word. Returns (inner text, start, end) relative to text (span includes quotes)."""
    result: list[tuple[str, int, int]] = []
    for mo in _QUOTED_PATTERN.finditer(text):
        inner = mo.group(1)
        if re.search(r"[A-Z][a-z]+", inner):
            result.append((inner, mo.start(), mo.end()))
    return result
