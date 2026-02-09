"""
LLM API wrapper (Gemini via google.genai).

Provides get_genai_client() and generate_content_text() for use by enrichment
modules. All LLM calls are isolated here; deterministic modules do not import this.
"""

from __future__ import annotations

import json
import re


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


def _serialize_response(response: object) -> dict:
    """Build a JSON-serializable dict from a generate_content response for debug saving."""
    out: dict = {}
    if hasattr(response, "prompt_feedback") and response.prompt_feedback is not None:
        pf = response.prompt_feedback
        out["prompt_feedback"] = {
            "block_reason": getattr(pf, "block_reason", None),
            "block_reason_message": getattr(pf, "block_reason_message", None),
        }
    if hasattr(response, "candidates") and response.candidates:
        candidates = []
        for c in response.candidates:
            cand: dict = {}
            if hasattr(c, "finish_reason"):
                cand["finish_reason"] = str(getattr(c, "finish_reason", None))
            if hasattr(c, "content") and c.content is not None and hasattr(c.content, "parts"):
                parts = []
                for p in c.content.parts:
                    text = getattr(p, "text", None) if hasattr(p, "text") else (p.get("text") if isinstance(p, dict) else None)
                    parts.append({"text": text})
                cand["parts"] = parts
            candidates.append(cand)
        out["candidates"] = candidates
    return out


def _parts_to_text(candidate: object) -> str:
    """Extract and concatenate text from all parts of a candidate."""
    if not getattr(candidate, "content", None) or not getattr(candidate.content, "parts", None):
        return ""
    parts = candidate.content.parts
    if not parts:
        return ""
    texts = []
    for part in parts:
        t = getattr(part, "text", None) if hasattr(part, "text") else (part.get("text") if isinstance(part, dict) else None)
        if t and isinstance(t, str):
            texts.append(t)
    return "".join(texts).strip() or ""


def generate_content_text(
    prompt: str,
    *,
    temperature: float = 0.0,
    debug_label: str | None = None,
) -> str | None:
    """
    Call Gemini with the given prompt and return the response text, or None on failure.

    Uses LLM_MODEL from config. Temperature defaults to 0 for deterministic JSON.
    When config.LLM_DEBUG is True and debug_label is set, saves prompt and raw response
    under <output_dir>/llm_debug/ (uses LLM_DEBUG_OUTPUT_DIR from env if set by pipeline, else OUTPUT_DIR).
    """
    import os
    from pathlib import Path

    from semantic_topic_mapper.config import LLM_DEBUG, LLM_MODEL, OUTPUT_DIR

    debug_dir_path: Path | None = None
    if LLM_DEBUG and debug_label:
        out = os.environ.get("LLM_DEBUG_OUTPUT_DIR")
        if out:
            debug_dir_path = Path(out) / "llm_debug"
        elif OUTPUT_DIR is not None:
            debug_dir_path = Path(OUTPUT_DIR) / "llm_debug"

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

    # Debug: save prompt and response for inspection
    if debug_dir_path is not None:
        safe_label = re.sub(r"[^\w\-]", "_", debug_label).strip("_") or "llm_call"
        debug_dir_path.mkdir(parents=True, exist_ok=True)
        debug_dir = debug_dir_path
        try:
            (debug_dir / f"{safe_label}_prompt.txt").write_text(prompt, encoding="utf-8")
            payload = _serialize_response(response)
            (debug_dir / f"{safe_label}_response.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    # Check for prompt-level block (e.g. safety)
    if hasattr(response, "prompt_feedback") and response.prompt_feedback is not None:
        reason = getattr(response.prompt_feedback, "block_reason", None)
        if reason is not None and str(reason) != "BLOCK_REASON_UNSPECIFIED":
            return None

    if not response or not getattr(response, "candidates", None) or not response.candidates:
        return None

    # Collect text from all parts of the first candidate
    text = _parts_to_text(response.candidates[0])
    return text if text else None
