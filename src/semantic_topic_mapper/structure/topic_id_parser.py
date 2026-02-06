"""
Topic ID parser: pure, deterministic, strict.

Grammar (v1): <number> ( "." <number> )* [ "." <letter> ]?
  (Letter allowed only once, at the end. E.g. 2, 2.1, 2.1.a.)

Valid: 2, 2.1, 2.1.a, 10.4.b
Invalid: .2, 2., 2..1, "Topic 2", 2.a.1 (letter before number at same depth)

Parser only parses structure. It does not detect headers, infer hierarchy,
or handle missing numbers.
"""

from __future__ import annotations

from semantic_topic_mapper.models.topic_models import TopicID


def parse_topic_id(candidate: str) -> TopicID | None:
    """
    Parse a string into a TopicID if it matches the grammar.

    - Trim whitespace
    - Validate format: <number> ( "." <number> )* [ "." <letter> ]? (letter only at end)
    - Split into parts, normalize letters to lowercase
    - Return TopicID or None if invalid
    """
    if not isinstance(candidate, str):
        return None
    s = candidate.strip()
    if not s:
        return None

    parts = s.split(".")
    if not parts:
        return None

    normalized: list[str] = []
    seen_letter = False

    for i, seg in enumerate(parts):
        seg = seg.strip()
        if not seg:
            return None  # empty segment (e.g. "2..1")

        if seg.isdigit():
            if seen_letter:
                return None  # letter before number at same depth (e.g. 2.a.1)
            normalized.append(seg)
        elif len(seg) == 1 and seg.isalpha():
            seg_lower = seg.lower()
            if seen_letter:
                return None  # at most one letter part, and it must be last
            seen_letter = True
            normalized.append(seg_lower)
        else:
            return None  # invalid character or multi-char non-digit

    if not normalized:
        return None

    return TopicID(raw=s, parts=tuple(normalized), level=len(normalized))
