"""
Deterministic header detection for topic modeling.

Identifies lines that begin new topics and produces HeaderCandidate objects.
Does NOT build hierarchy, does NOT create TopicBlock or TopicNode, and does NOT use LLMs.
Later stages (e.g. block extraction, hierarchy_builder) will segment text and assign hierarchy.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_topic_mapper.structure.topic_id_parser import parse_topic_id


@dataclass
class HeaderCandidate:
    """
    A line that has been detected as starting a new topic.

    - topic_id_raw: the topic ID string as it appears (e.g. "2.1", "18.3")
    - title: optional title text after the ID (None for standalone ID lines)
    - start_char: character offset of the start of this line in the document
    - line_text: the full line text (for traceability)
    """

    topic_id_raw: str
    title: str | None
    start_char: int
    line_text: str


def detect_headers(text: str) -> list[HeaderCandidate]:
    """
    Detect lines that start new topics. Returns only lines that confidently
    match known header patterns. Does not build hierarchy or modify text.

    Supported patterns:
    - A: "TOPIC X: TITLE" (case-insensitive TOPIC, valid ID, then : and optional title)
    - B: "2.1 Initial Registration" (line starts with valid topic ID, then whitespace and title)
    - C: "3.5.2" (line is only a valid topic ID, no title)

    Does not detect: subclauses (a)/(b), bullet points, in-line mentions like "Topic 12",
    or lines where numbers are not at the start.
    """
    if not text:
        return []

    results: list[HeaderCandidate] = []
    pos = 0
    lines = text.splitlines(keepends=True)

    for line in lines:
        start_char = pos
        pos += len(line)
        stripped = line.strip()

        if not stripped:
            continue

        # Pattern A: "TOPIC X: TITLE"
        if stripped.upper().startswith("TOPIC"):
            candidate = _try_pattern_a(stripped, start_char, line)
            if candidate is not None:
                results.append(candidate)
            continue

        # Pattern C: standalone topic ID (no title on same line)
        if " " not in stripped:
            tid = parse_topic_id(stripped)
            if tid is not None:
                results.append(
                    HeaderCandidate(
                        topic_id_raw=tid.raw,
                        title=None,
                        start_char=start_char,
                        line_text=line.rstrip("\n\r"),
                    )
                )
            continue

        # Pattern B: "ID title text..."
        parts = stripped.split(None, 1)
        if len(parts) >= 2:
            id_candidate, title_part = parts[0], parts[1]
            tid = parse_topic_id(id_candidate)
            if tid is not None:
                results.append(
                    HeaderCandidate(
                        topic_id_raw=tid.raw,
                        title=title_part.strip() or None,
                        start_char=start_char,
                        line_text=line.rstrip("\n\r"),
                    )
                )

    return results


def _try_pattern_a(stripped: str, start_char: int, raw_line: str) -> HeaderCandidate | None:
    """
    Pattern A: "TOPIC X: TITLE". Case-insensitive TOPIC, then valid ID, then : and optional title.
    """
    after_topic = stripped[5:].lstrip()  # skip "TOPIC"
    colon_idx = after_topic.find(":")
    if colon_idx < 0:
        return None
    id_part = after_topic[:colon_idx].strip()
    title_part = after_topic[colon_idx + 1 :].strip()
    tid = parse_topic_id(id_part)
    if tid is None:
        return None
    return HeaderCandidate(
        topic_id_raw=tid.raw,
        title=title_part or None,
        start_char=start_char,
        line_text=raw_line.rstrip("\n\r"),
    )
