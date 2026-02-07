# ingestion: load and normalize raw text; optional PDF→txt utility

from semantic_topic_mapper.ingestion.loader import load_text, load_text_from_config
from semantic_topic_mapper.ingestion.text_normalizer import normalize, normalize_for_parsing

__all__ = [
    "load_text",
    "load_text_from_config",
    "normalize",
    "normalize_for_parsing",
]
