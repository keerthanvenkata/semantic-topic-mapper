"""
Configuration for Semantic Topic Mapper.

Loads from environment (and optional .env file). All secrets and
user-specific paths live in .env; defaults are defined here.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# Load .env from project root if python-dotenv is available
try:
    from dotenv import load_dotenv
    _project_root = Path(__file__).resolve().parents[2]
    load_dotenv(_project_root / ".env")
except ImportError:
    pass


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)


def _env_path(key: str, default: Optional[Path] = None) -> Optional[Path]:
    v = _env(key)
    return Path(v) if v else default


def _env_int(key: str, default: int) -> int:
    v = _env(key)
    return int(v) if v is not None and v.strip() else default


def _env_bool(key: str, default: bool = False) -> bool:
    v = _env(key)
    if v is None or not v.strip():
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
INPUT_PATH: Optional[Path] = _env_path("INPUT_PATH")
INPUT_ENCODING: str = _env("INPUT_ENCODING") or "utf-8"

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
OUTPUT_DIR: Path = _env_path("OUTPUT_DIR") or Path("output")
TOPIC_MAP_FILENAME: str = _env("TOPIC_MAP_FILENAME") or "topic_map.json"
CROSS_REF_GRAPH_FILENAME: str = _env("CROSS_REF_GRAPH_FILENAME") or "cross_reference_graph.pdf"
ENTITY_CATALOGUE_FILENAME: str = _env("ENTITY_CATALOGUE_FILENAME") or "entity_catalogue.csv"
ENTITY_RELATIONSHIPS_FILENAME: str = _env("ENTITY_RELATIONSHIPS_FILENAME") or "entity_relationships.json"
AMBIGUITY_REPORT_FILENAME: str = _env("AMBIGUITY_REPORT_FILENAME") or "ambiguity_report.csv"

# ---------------------------------------------------------------------------
# Ingestion (defaults; override via env if needed)
# ---------------------------------------------------------------------------
NORMALIZE_UNICODE: bool = _env_bool("NORMALIZE_UNICODE", True)
ORPHAN_MIN_LENGTH: int = _env_int("ORPHAN_MIN_LENGTH", 20)

# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------
CREATE_PLACEHOLDER_FOR_MISSING: bool = _env_bool("CREATE_PLACEHOLDER_FOR_MISSING", True)

# ---------------------------------------------------------------------------
# LLM — Google Gemini via google.genai SDK
# ---------------------------------------------------------------------------
LLM_API_KEY: Optional[str] = _env("LLM_API_KEY")
LLM_MODEL: str = _env("LLM_MODEL") or "gemini-3-flash-preview"
LLM_TIMEOUT: int = _env_int("LLM_TIMEOUT", 60)
PROMPTS_DIR: Optional[Path] = _env_path("PROMPTS_DIR")


def skip_llm() -> bool:
    """True if LLM enrichment should be skipped (no API key or explicit disable)."""
    key = _env("LLM_API_KEY")
    if not key or not key.strip():
        return True
    return _env_bool("SKIP_LLM", False)
