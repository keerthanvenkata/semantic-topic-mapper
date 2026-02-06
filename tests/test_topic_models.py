r"""
Topic models and topic ID parser tests.

Run from project root with venv activated and PYTHONPATH including src:

    cd <project_root>
    venv\Scripts\Activate.ps1   # or: venv\Scripts\activate on Windows
    $env:PYTHONPATH = "src"
    python tests/test_topic_models.py

Or: python -m pytest tests/test_topic_models.py -v (with PYTHONPATH=src)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on path when run from project root
_root = Path(__file__).resolve().parents[1]
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from semantic_topic_mapper.models import (
    Subclause,
    TopicBlock,
    TopicID,
    TopicNode,
    TopicReference,
)
from semantic_topic_mapper.structure.topic_id_parser import parse_topic_id


def test_parse_topic_id_valid() -> None:
    assert parse_topic_id("2") == TopicID(raw="2", parts=("2",), level=1)
    assert parse_topic_id("2.1") == TopicID(raw="2.1", parts=("2", "1"), level=2)
    assert parse_topic_id("2.1.a") == TopicID(
        raw="2.1.a", parts=("2", "1", "a"), level=3
    )
    assert parse_topic_id("  18.3  ") == TopicID(
        raw="18.3", parts=("18", "3"), level=2
    )


def test_parse_topic_id_invalid() -> None:
    assert parse_topic_id(".2") is None
    assert parse_topic_id("2.") is None
    assert parse_topic_id("2..1") is None
    assert parse_topic_id("Topic 2") is None
    assert parse_topic_id("2.a.1") is None
    assert parse_topic_id("") is None


def test_topic_block_with_subclauses() -> None:
    tid = parse_topic_id("5.1")
    assert tid is not None
    sub = Subclause(label="a", text="Be suitable for the client", start_char=10, end_char=35)
    block = TopicBlock(
        topic_id=tid,
        title="Investment Recommendations",
        raw_text="All investment recommendations must:\n(a) Be suitable...",
        start_char=0,
        end_char=100,
        subclauses=[sub],
    )
    assert block.topic_id == tid
    assert len(block.subclauses) == 1
    assert block.subclauses[0].label == "a"


def test_topic_node_synthetic() -> None:
    tid = parse_topic_id("18.2")
    assert tid is not None
    node = TopicNode(
        topic_id=tid,
        parent_id=parse_topic_id("18"),
        children_ids=[],
        block=None,
        synthetic=True,
    )
    assert node.synthetic is True
    assert node.block is None


def test_topic_reference_source_region() -> None:
    src_id = parse_topic_id("5.1")
    tgt_id = parse_topic_id("4.2")
    assert src_id and tgt_id
    ref = TopicReference(
        source_topic_id=src_id,
        target_topic_id=tgt_id,
        relation_type="explicit",
        start_char=50,
        end_char=62,
        source_region_type="subclause",
        source_region_label="a",
    )
    assert ref.source_region_type == "subclause"
    assert ref.source_region_label == "a"


if __name__ == "__main__":
    test_parse_topic_id_valid()
    test_parse_topic_id_invalid()
    test_topic_block_with_subclauses()
    test_topic_node_synthetic()
    test_topic_reference_source_region()
    print("All tests passed.")
