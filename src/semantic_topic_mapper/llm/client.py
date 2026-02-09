"""
LLM API wrapper (Gemini via google-generativeai).

Provides get_gemini_model() for use by enrichment modules. All LLM calls
are isolated here; deterministic modules do not import this.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel


def get_gemini_model() -> "GenerativeModel":
    """
    Return a configured Gemini GenerativeModel for structured enrichment.

    Reads LLM_API_KEY from environment; model name from LLM_MODEL
    (default gemini-3-flash). Fails gracefully if API key is missing
    (callers should use config.skip_llm() before calling LLM code).

    Returns:
        GenerativeModel instance ready for generate_content.

    Raises:
        ValueError: If LLM_API_KEY is not set or empty.
    """
    from semantic_topic_mapper.config import LLM_API_KEY, LLM_MODEL

    if not LLM_API_KEY or not LLM_API_KEY.strip():
        raise ValueError(
            "LLM_API_KEY is not set. Set it in .env or disable LLM with SKIP_LLM=true."
        )

    import google.generativeai as genai

    genai.configure(api_key=LLM_API_KEY.strip())
    return genai.GenerativeModel(LLM_MODEL)
