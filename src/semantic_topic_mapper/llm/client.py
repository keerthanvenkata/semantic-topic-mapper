"""
LLM API wrapper (Gemini via google.genai).

Provides get_genai_client() and generate_content_text() for use by enrichment
modules. All LLM calls are isolated here; deterministic modules do not import this.
"""

from __future__ import annotations


def get_genai_client():  # noqa: ANN201
    """
    Return a configured google.genai Client for structured enrichment.

    Reads LLM_API_KEY from environment. Model name is read from LLM_MODEL when
    generating (default gemini-3-flash-preview). Callers should use
    config.skip_llm() before calling LLM code.

    Returns:
        genai.Client instance.

    Raises:
        ValueError: If LLM_API_KEY is not set or empty.
    """
    from semantic_topic_mapper.config import LLM_API_KEY

    if not LLM_API_KEY or not LLM_API_KEY.strip():
        raise ValueError(
            "LLM_API_KEY is not set. Set it in .env or disable LLM with SKIP_LLM=true."
        )

    from google import genai

    return genai.Client(api_key=LLM_API_KEY.strip())


def generate_content_text(prompt: str, *, temperature: float = 0.0) -> str | None:
    """
    Call Gemini with the given prompt and return the response text, or None on failure.

    Uses LLM_MODEL from config. Temperature defaults to 0 for deterministic JSON.
    """
    from semantic_topic_mapper.config import LLM_MODEL

    try:
        client = get_genai_client()
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config={"temperature": temperature},
        )
    except ValueError:
        raise
    except Exception:
        return None

    if not response or not response.candidates:
        return None

    # google-genai: text is in candidates[0].content.parts[0]
    candidate = response.candidates[0]
    if not getattr(candidate, "content", None) or not getattr(candidate.content, "parts", None):
        return None
    parts = candidate.content.parts
    if not parts:
        return None
    part = parts[0]
    text = getattr(part, "text", None) if hasattr(part, "text") else (part.get("text") if isinstance(part, dict) else None)
    if not text or not isinstance(text, str):
        return None
    return text
