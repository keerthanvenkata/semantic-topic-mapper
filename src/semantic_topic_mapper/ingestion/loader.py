"""
Load plain text documents from disk.

The pipeline ingests normalized .txt content. This module loads the raw bytes
and returns a string; encoding is configurable. It does not normalize text
(see text_normalizer). File parsing (PDF, DOCX, etc.) is handled separately
(e.g. pdf_to_txt utility) before the result is passed to the loader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def load_text(
    path: Path | str,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> str:
    """
    Load a plain text file and return its contents as a string.

    Args:
        path: Path to the .txt file.
        encoding: Character encoding (default utf-8).
        errors: How to handle decode errors; default "replace" to avoid
            raising on bad bytes.

    Returns:
        Raw text string (not normalized; use text_normalizer for that).

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: On read failure.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding=encoding, errors=errors)


def load_text_from_config() -> str:
    """
    Load text using INPUT_PATH and INPUT_ENCODING from config.

    Use this when running the pipeline with env/config. Raises if
    INPUT_PATH is not set or file is missing.
    """
    from semantic_topic_mapper.config import INPUT_ENCODING, INPUT_PATH

    if INPUT_PATH is None:
        raise ValueError("INPUT_PATH is not set; set it in .env or environment")
    return load_text(INPUT_PATH, encoding=INPUT_ENCODING)
