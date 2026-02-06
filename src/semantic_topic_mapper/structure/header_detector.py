"""
Deterministic header detection for topic modeling.

Identifies lines that begin new topics and produces HeaderCandidate objects.
Does NOT build hierarchy, does NOT create TopicBlock or TopicNode, and does NOT use LLMs.
Later stages (e.g. block extraction, hierarchy_builder) will segment text and assign hierarchy.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_topic_mapper.models.topic_models import TopicID
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
    - B: "2.1 Initial Registration" (line starts with valid topic ID, then whitespace and title).
      Title must not end with a period (avoids numbered sentences like "2 Firms must comply immediately.").
      No word-count limit, so long legal headers are accepted.
    - C: "3.5.2" (line is only a valid topic ID, no title). Single-number IDs > 50 (e.g. years
      like "2023") are rejected to avoid false positives from standalone years or page numbers.

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
            if tid is not None and _accept_standalone_id(tid):
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
            if tid is not None and _title_looks_like_header(title_part):
                results.append(
                    HeaderCandidate(
                        topic_id_raw=tid.raw,
                        title=title_part.strip() or None,
                        start_char=start_char,
                        line_text=line.rstrip("\n\r"),
                    )
                )

    return results


def _title_looks_like_header(title_part: str) -> bool:
    """
    Conservative heuristic: reject titles that look like full sentences.
    Only check: title must not end with a period (numbered sentences do).
    No word-count limit, so long legal headers are accepted.
    """
    t = title_part.strip()
    if not t:
        return False
    if t.endswith("."):
        return False
    return True


def _accept_standalone_id(tid: TopicID) -> bool:
    """
    Reject standalone IDs that are likely years or page numbers (e.g. 2023, 2096).
    Single-segment IDs with value > 50 are not treated as topic headers.
    """
    if tid.level != 1:
        return True
    part = tid.parts[0]
    if not part.isdigit():
        return True
    return int(part) <= 50


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
