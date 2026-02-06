# Cursor Context — Semantic Topic Mapper

You are helping build a **deterministic document structure intelligence system**.

## Project Goals

The system parses regulatory-style documents and extracts:

- Topic hierarchies
- Cross-references between topics
- Entities and their roles
- Structural ambiguities

This is a **modular, deterministic system with LLM-assisted semantic enrichment**.
It is NOT a chatbot, RAG system, or agent framework.

---

## Engineering Philosophy

1. Deterministic structure comes first
2. LLMs are used only for semantic interpretation, never structural control
3. Every LLM output must be:
   - Structured (JSON schema)
   - Grounded in text spans
   - Validated before entering the knowledge graph
4. No overengineering — clarity > cleverness
5. Small, testable modules over large abstractions

---

## Repo Structure Overview

```text

src/semantic_topic_mapper/
models/    # shared data models (topic, reference, entity, ambiguity)
ingestion/ # text loading and normalization
structure/ # topic blocks and hierarchy
references/ # cross-reference detection
entities/ # entity extraction
llm/ # LLM client, schemas, validators
graph/ # graph models
audit/ # ambiguity + consistency checks
outputs/ # exporters for deliverables
pipeline/ # orchestration

```

---

## LLM Stack

Semantic enrichment uses **Google Gemini**, specifically the **gemini-3-flash** model, via the **google-generativeai** Python SDK. The LLM client in `llm/client.py` should be implemented against this SDK; config uses `LLM_API_KEY` (Google AI API key) and `LLM_MODEL` (default `gemini-3-flash`).

---

## Coding Guidelines

- Prefer explicit data models over loose dicts
- Use type hints everywhere
- Functions should do one thing
- Avoid hidden magic and global state
- Add docstrings explaining reasoning, not just mechanics

---

## What NOT to Do

- Do not introduce heavy frameworks
- Do not add UI
- Do not replace deterministic parsing with LLM guesses
- Do not auto-correct structural inconsistencies silently
