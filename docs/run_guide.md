# How to Run the Semantic Topic Mapper

This guide describes how to run the pipeline and where to find detailed instructions.

---

## Prerequisites

The package uses a **src layout**. From the project root, install it in editable mode so `python -m semantic_topic_mapper` can find the module:

```bash
# From project root (where pyproject.toml and src/ live)
pip install -e .
```

Use an active virtual environment (e.g. `venv`). Then run the commands below from the same project root.

---

## Quick start

**Run with a path to a text file:**

```bash
# From project root (where src/ and data/ live)
python -m semantic_topic_mapper data/sample_document.txt
```

Output is written to the default output directory (`output/` unless overridden). See [CLI reference](run/cli.md) for options.

**Run using config (no arguments):**

Set `INPUT_PATH` in `.env` (or environment), then:

```bash
python -m semantic_topic_mapper
```

Uses `INPUT_PATH` and `OUTPUT_DIR` from config. See [Configuration](run/config_reference.md).

---

## What the pipeline does

1. Loads the input .txt file  
2. Detects topic headers and segments the document into topic blocks  
3. Builds the topic hierarchy (with synthetic nodes for gaps)  
4. Detects explicit "Topic X" references and builds the reference graph  
5. Detects entities and links definitions  
6. Extracts entity relationships (deterministic; optional LLM adds more)  
7. **Optional LLM enrichment** (when `LLM_API_KEY` is set): entity type classification, relationship extraction, entity ambiguity detection  
8. Runs the audit (synthetic topics, reference issues, undefined/single-mention entities, plus LLM entity ambiguities)  
9. Writes deliverables to the output directory  

Without an API key (or with `SKIP_LLM=true`), the pipeline runs deterministically only. See [System Architecture](system_architecture.md) for the full pipeline.

---

## Output files

All files are written under the output directory you specify (or `OUTPUT_DIR`):

| File | Description |
|------|-------------|
| `topic_map.json` | Topic hierarchy (title, synthetic, children per topic) |
| `entity_catalogue.csv` | Entities with mention count and definition topic |
| `entity_relationships.json` | Entity relationships (deterministic + optional LLM) |
| `ambiguity_report.csv` | Audit issues (warnings, errors, info) |
| `cross_reference_graph.pdf` | Directed graph of topic references |

---

## Detailed docs

| Document | Contents |
|----------|----------|
| [CLI reference](run/cli.md) | Command-line options and examples |
| [Configuration reference](run/config_reference.md) | Config variables and .env |

---

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt` (e.g. `pip install -r requirements.txt`)
- Input: plain text (`.txt`). For PDFs, convert to .txt first (see [Ingestion](arch/ingestion.md)).
- Optional: copy `.env.example` to `.env` and set `INPUT_PATH`, `OUTPUT_DIR`; for LLM enrichment set `LLM_API_KEY`. Set `LLM_DEBUG=true` to save prompts and responses under the run’s `llm_debug/` folder for debugging.
