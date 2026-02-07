"""
Deterministic detection of explicit topic references.

Extracts references like "Topic 12" or "topic 5.1" from TopicBlocks by scanning
for the literal word "Topic" (case-insensitive) followed by a valid topic ID.
Does not use LLMs and does not build graphs. Implicit or semantic references
will be handled in later LLM enrichment.
"""

from __future__ import annotations

import re

from semantic_topic_mapper.models.reference_models import TopicReference
from semantic_topic_mapper.models.topic_models import TopicBlock, TopicID, Subclause
from semantic_topic_mapper.structure.topic_id_parser import parse_topic_id


def detect_references(blocks: list[TopicBlock]) -> list[TopicReference]:
    """
    Detect explicit "Topic <ID>" references in each block's title, paragraph,
    and subclauses. Returns one TopicReference per occurrence; no deduplication.
    """
    refs: list[TopicReference] = []
    for block in blocks:
        if block.topic_id is None:
            continue
        source_id = block.topic_id

        # a) Title
        # Title reference spans are approximate in v1; header line offsets are not separately tracked.
        if block.title:
            base = block.start_char
            for match_text, rel_start, rel_end in _find_topic_mentions(block.title):
                tid = _parse_mention(match_text)
                if tid is not None:
                    refs.append(
                        TopicReference(
                            source_topic_id=source_id,
                            target_topic_id=tid,
                            relation_type="explicit",
                            start_char=base + rel_start,
                            end_char=base + rel_end,
                            source_region_type="title",
                            source_region_label=None,
                        )
                    )

        # b) Paragraph (raw_text)
        base = block.start_char
        for match_text, rel_start, rel_end in _find_topic_mentions(block.raw_text):
            tid = _parse_mention(match_text)
            if tid is not None:
                refs.append(
                    TopicReference(
                        source_topic_id=source_id,
                        target_topic_id=tid,
                        relation_type="explicit",
                        start_char=base + rel_start,
                        end_char=base + rel_end,
                        source_region_type="paragraph",
                        source_region_label=None,
                    )
                )

        # c) Each subclause
        for sub in block.subclauses:
            sub_base = sub.start_char
            for match_text, rel_start, rel_end in _find_topic_mentions(sub.text):
                tid = _parse_mention(match_text)
                if tid is not None:
                    refs.append(
                        TopicReference(
                            source_topic_id=source_id,
                            target_topic_id=tid,
                            relation_type="explicit",
                            start_char=sub_base + rel_start,
                            end_char=sub_base + rel_end,
                            source_region_type="subclause",
                            source_region_label=sub.label,
                        )
                    )

    return refs


def _find_topic_mentions(text: str) -> list[tuple[str, int, int]]:
    """
    Find all "Topic <ID>" mentions (case-insensitive) in text.
    Returns list of (match_text, start_offset, end_offset) in document order.
    Offsets are relative to the start of `text`.
    """
    if not text:
        return []
    pattern = re.compile(r"\b[tT]opic\b", re.IGNORECASE)
    result: list[tuple[str, int, int]] = []
    for mo in pattern.finditer(text):
        start_offset = mo.start()
        # Skip past "topic" and any whitespace
        i = mo.end()
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            continue
        token_start = i
        # Consume token: digits, dots, letters
        while i < len(text):
            c = text[i]
            if c.isalnum() or c == ".":
                i += 1
            else:
                break
        token_end = i
        if token_start == token_end:
            continue
        token = text[token_start:token_end]
        # Strip trailing punctuation for validation only; span may include it
        token_clean = token.rstrip(".,;)]")
        if not token_clean:
            continue
        if parse_topic_id(token_clean) is None:
            continue
        # Include trailing punctuation in span if present
        while i < len(text) and text[i] in ".,;)]":
            i += 1
        end_offset = i
        match_text = text[start_offset:end_offset]
        result.append((match_text, start_offset, end_offset))
    return result


def _parse_mention(match_text: str) -> TopicID | None:
    """
    Extract the topic ID token from a "Topic X" mention and validate it.
    Strips trailing punctuation before parsing.
    """
    pattern = re.compile(r"\b[tT]opic\s+", re.IGNORECASE)
    mo = pattern.search(match_text)
    if not mo:
        return None
    i = mo.end()
    while i < len(match_text) and match_text[i].isspace():
        i += 1
    token_start = i
    while i < len(match_text) and (match_text[i].isalnum() or match_text[i] == "."):
        i += 1
    token = match_text[token_start:i].rstrip(".,;)]")
    return parse_topic_id(token) if token else None
