# Ingestion and Output Layout

## What Is Actually Ingested

The pipeline **starts from normalized plain text** (.txt). That is the ingested input:

1. **Loader** (`loader.py`) reads a .txt file from disk and returns a raw string (with configurable encoding).
2. **Text normalizer** (`text_normalizer.py`) applies minimal cleanup: line endings → `\n`, strip trailing whitespace per line, optional Unicode normalization and control-char replacement.
3. The **normalized string** is what downstream stages (structure, references, entities) consume. Ingestion ends there.

File parsing (PDF, DOCX, etc.) is **not** part of the core ingestion contract. It is preprocessing: convert the document to .txt first, then run the pipeline on the .txt.

## Loader

- **`load_text(path, encoding, errors)`** — Load a .txt file; returns raw string. Uses `errors="replace"` by default so decode errors do not crash.
- **`load_text_from_config()`** — Uses `INPUT_PATH` and `INPUT_ENCODING` from config; convenient for pipeline runs.

## Text Normalizer

- **`normalize(text, ...)`** — Configurable: line endings, strip trailing per line, Unicode NFKC, replace control chars.
- **`normalize_for_parsing(text)`** — Same with defaults suitable for structure parsing; reads `NORMALIZE_UNICODE` from config when available.

Scope stays minimal: no layout reconstruction, no bullet inference from indentation (see [Assumptions](../assumptions.md)).

## PDF → .txt Utility (Optional)

- **`pdf_to_txt(pdf_path, output_path=None, encoding="utf-8")`** in `ingestion/pdf_to_txt.py` — Extracts text from a PDF via pypdf and writes a .txt file. Use when the source is PDF; then point the pipeline at the resulting .txt.

This is a **utility for preprocessing**, not part of the ingestion API. Future work may cover layout-aware extraction, OCR for scanned PDFs, and other formats.

## Output Directory and Per-Job Folders

- **`output/`** at project root is the default output directory (config: `OUTPUT_DIR`).
- **Per document/job:** create a subfolder per run, e.g. `output/<job_id>/` or `output/<document_name>/`, and write all deliverables for that run there (topic_map.json, cross_reference_graph.pdf, entity_catalogue.csv, entity_relationships.json, ambiguity_report.csv). This keeps runs isolated and reproducible.

The pipeline (or caller) is responsible for creating the per-job subfolder; config provides `OUTPUT_DIR` only. Future docs can detail job naming and file naming inside the job folder.
