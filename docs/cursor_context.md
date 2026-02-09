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
ingestion/ # loader, text normalizer; optional PDF→txt utility (see docs/arch/ingestion.md)
structure/ # topic_id_parser, header_detector, hierarchy_builder (topic tree + synthetic nodes)
references/ # reference_detector (explicit "Topic X"); reference_graph_builder (graph + ReferenceIssue)
entities/ # entity_models (Entity, EntityMention, EntityRelationship); deterministic_entity_detector; definition_linker
llm/ # LLM client, schemas, validators
graph/ # graph models
audit/ # ambiguity_detector (run_audit → AuditIssue: synthetic topics, ref issues, undefined/single-mention entities)
outputs/ # thin serializers: topic_map, entity_catalogue, entity_relationships, ambiguity_report, reference_graph (PDF)
pipeline/ # main_pipeline.run_pipeline(input_path, output_dir); run_pipeline_from_config() uses config

```

---

## LLM Stack

Semantic enrichment uses **Google Gemini**, specifically the **gemini-3-flash-preview** model, via the **google.genai** Python SDK. The LLM client in `llm/client.py` uses this SDK; config uses `LLM_API_KEY` (Google AI API key) and `LLM_MODEL` (default `gemini-3-flash-preview`). Optional: `SKIP_LLM`, `LLM_DEBUG` (saves prompts/responses for debugging).

---

## Coding Guidelines

- Prefer explicit data models over loose dicts
- Use type hints everywhere
- Functions should do one thing
- Avoid hidden magic and global state
- Add docstrings explaining reasoning, not just mechanics

---

## Running the pipeline

- **With a text file path:** `python -m semantic_topic_mapper path/to/document.txt` (optional: `--output output/my_run`).
- **From config:** Set `INPUT_PATH` in `.env`, then `python -m semantic_topic_mapper`.
See [Run guide](docs/run_guide.md) and [docs/run/](docs/run/) for CLI and configuration.

---

## What NOT to Do

- Do not introduce heavy frameworks
- Do not add UI
- Do not replace deterministic parsing with LLM guesses
- Do not auto-correct structural inconsistencies silently
