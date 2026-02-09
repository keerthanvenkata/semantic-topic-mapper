# Configuration Reference

All configurables are defined in one place: **`src/semantic_topic_mapper/config.py`**. Values are read from the environment; use a `.env` file in the project root (copy from `.env.example`) for local settings. **Do not commit `.env`** (it is in `.gitignore`).

---

## Where config lives

- **Single source:** `src/semantic_topic_mapper/config.py` — all input, output, ingestion, structure, and LLM settings.
- **Load order:** `config.py` loads `.env` from the project root (two levels up from `config.py`) when `python-dotenv` is installed. Environment variables override `.env`.

---

## Variables

### Input

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `INPUT_PATH` | path | — | Path to the input .txt file. Required when running without CLI args. |
| `INPUT_ENCODING` | str | `utf-8` | Encoding for reading the input file. |

### Output

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OUTPUT_DIR` | path | `output` | Directory where deliverables are written. Pipeline creates it if missing. |
| `TOPIC_MAP_FILENAME` | str | `topic_map.json` | Filename for topic map (used if pipeline uses config filenames; current pipeline uses fixed names in output dir). |
| `CROSS_REF_GRAPH_FILENAME` | str | `cross_reference_graph.pdf` | Reference graph PDF filename. |
| `ENTITY_CATALOGUE_FILENAME` | str | `entity_catalogue.csv` | Entity catalogue CSV filename. |
| `ENTITY_RELATIONSHIPS_FILENAME` | str | `entity_relationships.json` | Entity relationships JSON filename. |
| `AMBIGUITY_REPORT_FILENAME` | str | `ambiguity_report.csv` | Ambiguity report CSV filename. |

### Ingestion

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `NORMALIZE_UNICODE` | bool | `true` | Whether to normalize Unicode (e.g. NFKC) during normalization. |
| `ORPHAN_MIN_LENGTH` | int | `20` | Minimum length for orphan region detection. |

### Structure

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CREATE_PLACEHOLDER_FOR_MISSING` | bool | `true` | Whether to create synthetic nodes for missing topic IDs. |

### LLM (optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_API_KEY` | str | — | Google AI API key for Gemini. If unset, LLM enrichment is skipped. |
| `LLM_MODEL` | str | `gemini-3-flash-preview` | Model name. |
| `LLM_TIMEOUT` | int | `60` | Timeout in seconds for LLM calls. |
| `PROMPTS_DIR` | path | — | Optional path to prompt templates. |
| `SKIP_LLM` | bool | `false` | If true, skip LLM even when API key is set. |
| `LLM_DEBUG` | bool | `false` | If true, save each LLM prompt and raw response under `OUTPUT_DIR/llm_debug/` (or the run’s `--output` dir). Use for debugging empty or unexpected responses; can be removed or disabled after. |

---

## Example .env

```bash
# Input
INPUT_PATH=data/sample_document.txt
INPUT_ENCODING=utf-8

# Output
OUTPUT_DIR=output

# LLM (leave empty to skip enrichment)
LLM_API_KEY=
LLM_MODEL=gemini-3-flash-preview
# LLM_DEBUG=true   # uncomment to save prompts/responses to output/llm_debug/
```

---

## Using config in code

```python
from semantic_topic_mapper.config import (
    INPUT_PATH,
    OUTPUT_DIR,
    INPUT_ENCODING,
    skip_llm,
)
```

See [Feature plan & config](../feature_plan_and_config.md) for the full config design.
