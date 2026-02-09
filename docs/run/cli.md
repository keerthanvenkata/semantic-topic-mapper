# CLI Reference

The pipeline is run via the package entry point:

```bash
python -m semantic_topic_mapper [INPUT_PATH] [--output OUTPUT_DIR]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `INPUT_PATH` | No* | Path to the input .txt file. If omitted, the pipeline uses `INPUT_PATH` from config (see [Configuration](config_reference.md)). |
| `-o`, `--output` | No | Output directory for all deliverables. If omitted, `OUTPUT_DIR` from config is used (default `output/`). |

\* Required when not using config: either pass `INPUT_PATH` on the command line or set it in `.env`.

---

## Examples

**Run with explicit input and default output dir:**

```bash
python -m semantic_topic_mapper data/sample_document.txt
```

**Run with explicit input and custom output dir:**

```bash
python -m semantic_topic_mapper data/sample_document.txt --output output/my_run
```

**Run from config only (no arguments):**

```bash
# Ensure .env contains INPUT_PATH=data/sample_document.txt (and optionally OUTPUT_DIR)
python -m semantic_topic_mapper
```

**Using a path with spaces (Windows):**

```bash
python -m semantic_topic_mapper "C:\Documents\my file.txt" --output output/run1
```

---

## Programmatic use

You can also call the pipeline from Python:

```python
from semantic_topic_mapper.pipeline.main_pipeline import run_pipeline, run_pipeline_from_config

# Explicit paths
run_pipeline("path/to/document.txt", "output/my_run")

# From config (INPUT_PATH, OUTPUT_DIR)
run_pipeline_from_config()
```

See [Configuration](config_reference.md) for config variables.
