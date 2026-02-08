"""
Segment document into TopicBlocks using detected headers.

Takes full text and list of HeaderCandidate; returns list of TopicBlock
(slices between consecutive headers). Does not detect headers or build hierarchy.
"""

from __future__ import annotations

from semantic_topic_mapper.models.topic_models import TopicBlock
from semantic_topic_mapper.structure.header_detector import HeaderCandidate
from semantic_topic_mapper.structure.topic_id_parser import parse_topic_id


def segment_into_topic_blocks(text: str, headers: list[HeaderCandidate]) -> list[TopicBlock]:
    """
    Split text into TopicBlocks using header positions. Each block runs from
    one header's start_char to the next header's start_char (or end of text).
    topic_id and title come from the header; subclauses are left empty in v1.
    """
    if not headers:
        return []
    sorted_headers = sorted(headers, key=lambda h: h.start_char)
    blocks: list[TopicBlock] = []
    for i, h in enumerate(sorted_headers):
        start = h.start_char
        end = sorted_headers[i + 1].start_char if i + 1 < len(sorted_headers) else len(text)
        raw_text = text[start:end]
        topic_id = parse_topic_id(h.topic_id_raw)
        blocks.append(
            TopicBlock(
                topic_id=topic_id,
                title=h.title,
                raw_text=raw_text,
                start_char=start,
                end_char=end,
                subclauses=[],
            )
        )
    return blocks
