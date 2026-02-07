"""
Minimal text normalization for parsing.

In scope: normalize line endings, strip trailing whitespace per line, and
optionally replace or remove control characters. Keeps the document as
plain text suitable for structure detection.

Out of scope (per assumptions): reconstruct layout, columns, tables,
visual indentation from PDFs, or infer bullets from indentation.
"""

from __future__ import annotations

import unicodedata
from typing import Optional


def normalize(
    text: str,
    normalize_line_endings: bool = True,
    strip_trailing_per_line: bool = True,
    normalize_unicode: bool = True,
    replace_control_chars: bool = True,
) -> str:
    """
    Apply minimal normalization to raw text for downstream parsing.

    Args:
        text: Raw document string.
        normalize_line_endings: Replace \\r\\n and \\r with \\n.
        strip_trailing_per_line: Remove trailing whitespace from each line.
        normalize_unicode: Apply Unicode NFKC normalization (e.g. fullwidth
            to ASCII) so that structure patterns match consistently.
        replace_control_chars: Replace ASCII control chars (0x00-0x1F except
            \\t, \\n, \\r) with space to avoid parse issues.

    Returns:
        Normalized text string.
    """
    if not text:
        return ""

    if normalize_unicode:
        text = unicodedata.normalize("NFKC", text)

    if replace_control_chars:
        # Replace control chars except tab, newline, carriage return
        text = "".join(
            c if c in "\t\n\r" or ord(c) >= 32 else " "
            for c in text
        )

    if normalize_line_endings:
        text = text.replace("\r\n", "\n").replace("\r", "\n")

    if strip_trailing_per_line:
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

    return text


def normalize_for_parsing(text: str, normalize_unicode: Optional[bool] = None) -> str:
    """
    Convenience wrapper with defaults suitable for structure parsing.

    Uses config for normalize_unicode if the optional flag is not provided.
    """
    if normalize_unicode is None:
        try:
            from semantic_topic_mapper.config import NORMALIZE_UNICODE
            normalize_unicode = NORMALIZE_UNICODE
        except ImportError:
            normalize_unicode = True
    return normalize(
        text,
        normalize_line_endings=True,
        strip_trailing_per_line=True,
        normalize_unicode=normalize_unicode,
        replace_control_chars=True,
    )
