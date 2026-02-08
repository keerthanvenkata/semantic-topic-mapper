# Semantic Topic Mapper — Feature Plan & Config Design

**Phase:** Early structure  
**Purpose:** Define what each capability needs, delivers, and how config/env are structured.

---

## 1. Proposed Structure Review

Your `src/semantic_topic_mapper/` layout aligns well with the architecture and assignment:

| Aspect | Assessment |
|--------|------------|
| **Separation of concerns** | Ingestion → structure → references → entities → graph → audit → outputs is clear and matches the pipeline. |
| **Deterministic vs LLM** | Good: `reference_detector.py` (deterministic) vs `llm_reference_enricher.py`; same pattern in entities. |
| **Data models** | Shared `models/` package: `topic_models.py`, `reference_models.py`, `entity_models.py`, `ambiguity_models.py` — system-wide vocabulary, reduces circular imports. |
| **Graph** | Having `topic_graph.py`, `reference_graph.py`, `entity_graph.py` under `graph/` is fine; clarify whether these are in-memory models or builders that write to a unified store used by exporters. |
| **Audit** | `gap_analyzer.py`, `unresolved_detector.py`, `risk_scorer.py` map well to “missing numbers”, “broken refs/undefined entities”, “confidence”. |

**Suggestions:**

- **Config location:** Put a single `config.py` (or `config/`) at package root (e.g. `src/semantic_topic_mapper/config.py`) so every subpackage can import one place. See Section 3.
- **Shared types:** Consider a small `models/` or keep `*_models.py` in each package; both are fine as long as cross-package types (e.g. span, topic_id) are defined once and imported.
- **Pipeline:** `main_pipeline.py` is the only pipeline file for now; when you add stages (e.g. “structure-only”, “full run”), you can add `pipeline/stages.py` or flags in config without changing the layout.

---

## 2. Feature Plan — Needs & Deliverables

For each **system capability**, the table below states: **inputs needed**, **outputs produced**, and **config/env used**.

---

### 2.1 Ingestion & Normalization

The **pipeline ingests normalized .txt**; that is the start of the pipeline. Loader and normalizer are implemented; PDF→txt is an optional utility.

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Load raw text** | File path; encoding | Raw text string | `INPUT_PATH`, `INPUT_ENCODING`; `load_text()` / `load_text_from_config()` |
| **Normalize text** | Raw text | Normalized string (line endings, strip trailing, optional Unicode/control chars) | `NORMALIZE_UNICODE`; `normalize()` / `normalize_for_parsing()` |
| **PDF → .txt (utility)** | PDF path | .txt file on disk (for later ingestion) | Optional; `pdf_to_txt()` in `ingestion/pdf_to_txt.py`; requires `pypdf` |
| **Coarse segmentation** | Normalized text | List of segments (e.g. by paragraph); optional span offsets | — (segmenter) |

**Output layout:** Default `OUTPUT_DIR` is `output/`. Each document/job should use a subfolder (e.g. `output/<job_id>/`) for that run’s deliverables. See [Ingestion and Output](arch/ingestion.md).

**Deliverable (internal):** Normalized document text; optional segment boundaries. No layout reconstruction (per assumptions).

---

### 2.2 Structural Parsing

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Topic ID grammar** | — | Parser that recognizes e.g. `5`, `5.1`, `5.1.a`, `TOPIC 18` | Optional: `TOPIC_ID_PATTERNS` or grammar file path |
| **TopicBlock model** | — | Data class: topic_id, title, body, start/end span, parent_id (optional) | — |
| **Header detection** | Normalized text; topic ID parser | List of header candidates (topic_id_raw, title, start_char, line_text). Uses patterns A/B/C and conservative heuristics: Pattern B title must not end with period (avoids numbered sentences); no word-count limit (long legal headers accepted). Pattern C rejects standalone single-number IDs > 50 (e.g. years). **Missed headers** (false negatives) are an accepted v1 tradeoff: text may merge into one TopicBlock; refs/entities still extracted; see [Handling Missed Topic Boundaries](arch/topic_modeling.md#5b-handling-missed-topic-boundaries-false-negatives). | — |
| **Topic blocks** | Header candidates + full text | List of TopicBlocks with boundaries and spans. When a header is missed, content merges into the previous block. | — |
| **Orphan detection** | Topic blocks + full text | List of orphan regions (span, snippet) | `ORPHAN_MIN_LENGTH` (ignore tiny fragments) |

**Deliverable (internal):** List of `TopicBlock`; list of orphan spans. Consumed by hierarchy and audit.

---

### 2.3 Topic Hierarchy Construction

**Implemented:** `structure/hierarchy_builder.py` — `build_topic_hierarchy(blocks)` builds the topic tree from TopicBlocks: one TopicNode per block with a topic_id, parent resolution via ancestor candidates, synthetic nodes for missing intermediate IDs, parent–child linking (with duplicate guards), and numeric-aware sort of children. Returns `dict[str, TopicNode]`. Does not modify blocks or use LLMs.

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Parent-child inference** | List of TopicBlocks (with topic_id) | Tree: each node has children; root(s) identified | — |
| **Numbering gaps** | Topic tree; full topic_id set | List of “missing” topic_ids (e.g. 18.2) | — |
| **Placeholder nodes** | Missing topic_ids; optional policy | Synthetic nodes (e.g. 18.2) marked as placeholder; optional insert into tree | `CREATE_PLACEHOLDER_FOR_MISSING` (bool) |
| **Depth consistency** | Topic tree | Validation result: max depth, any depth anomalies | — |

**Deliverable (internal):** Topic tree (with optional placeholders); gap list. Feeds graph and exports.

---

### 2.4 Cross-Reference Extraction

**Implemented (deterministic):** `references/reference_detector.py` — `detect_references(blocks)` scans each block's title, paragraph (`raw_text`), and subclauses for explicit "Topic &lt;ID&gt;" (case-insensitive). Token after "Topic" is validated with `parse_topic_id`; trailing punctuation stripped. Produces `TopicReference` with `relation_type="explicit"`, absolute `start_char`/`end_char`, `source_region_type` (title/paragraph/subclause), and `source_region_label` for subclauses. **v1:** Title reference spans are approximate (header line offsets not tracked). No deduplication in the detector. Implicit/semantic refs are handled by the LLM enricher later.

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Deterministic detection** | TopicBlocks | List of TopicReference (explicit "Topic X" in title, paragraph, subclauses); spans; source_region_type/label | — |
| **Reference models** | — | TopicReference: source/target topic_id, relation_type, span, source_region_type, source_region_label | — |
| **LLM enricher** | Text spans (e.g. “as described above”); context | Structured annotations: implied topic_id, confidence, span | LLM config (see 2.7) |
| **Reference graph** | References + topic tree | Graph: nodes = topics; edges = reference (with type/label) | — |

**Deliverable (internal):** Reference list with spans; reference graph. **Export:** `cross_reference_graph.pdf`.

---

### 2.5 Entity Extraction

**Design (deterministic detector):** The deterministic entity detector **prioritizes precision over recall**. Some entity mentions may be missed in this stage. LLM-based enrichment can propose additional entities or link implicit mentions; such outputs are advisory and surfaced with confidence signals rather than altering the deterministic backbone automatically.

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Entity models** | — | Data classes: Entity, Mention (topic_id, span), Role, Definition | — |
| **Deterministic detection** | Text; optional allowlist | Candidate mentions (span, surface form) | Optional: `ENTITY_TYPES_FIRST_PASS`, stopwords |
| **Definition linker** | Mentions; text | Definitions linked to canonical entity (“hereinafter referred to as X”) | — |
| **LLM enricher** | Mention + context | Role, obligation, type; structured only | LLM config |
| **Entity graph** | Entities + mentions + relationships | Graph: entities; edges = relationship type | — |

**Deliverable (internal):** Entity catalogue (with mentions per topic); entity graph. **Exports:** `entity_catalogue.csv`, `entity_relationships.json`.

---

### 2.6 Knowledge Graph Construction

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Topic graph** | Topic tree | Graph: topic nodes, parent-child edges | — |
| **Reference graph** | References | Graph: topic → topic edges (reference) | — |
| **Entity graph** | Entities, relationships | Graph: entity nodes, relationship edges | — |
| **Topic–Entity edges** | Topic blocks + entity mentions | Edges linking topic ↔ entity (for “which entities appear in which topic”) | — |

**Deliverable (internal):** Unified or separate graph structures. **Exports:** used by all exporters; `topic_map.json` from topic graph + hierarchy.

---

### 2.7 LLM Semantic Enrichment

**LLM stack:** We use **Google Gemini**, specifically the **gemini-3-flash** model, via the **google-generativeai** Python SDK. The client in `llm/client.py` should call this SDK; config uses `LLM_API_KEY` (Google AI API key) and `LLM_MODEL` (default `gemini-3-flash`).

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **LLM client** | API key, model | Wrapper: call with prompt + schema; return parsed JSON (uses google-generativeai) | `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT` |
| **Schemas** | — | JSON schemas for: topic semantics, reference semantics, entity semantics | — |
| **Validator** | LLM response + schema | Validated dict or Pydantic model; errors logged, not merged | — |
| **Prompts** | Template files | Loaded prompt templates (topic_semantics, reference_semantics, entity_semantics) | `PROMPTS_DIR` or default next to `prompts/` |

**Deliverable (internal):** Structured annotations only. No structural changes; audit may flag LLM disagreement.

---

### 2.8 Consistency & Ambiguity Analysis

**Implemented (deterministic):** `audit/ambiguity_detector.py` — **`run_audit(nodes, reference_issues, entities)`** returns **list[AuditIssue]**. Aggregates: (1) synthetic topic nodes → `missing_topic_content` (warning); (2) reference issues → `missing_topic` (error) or `synthetic_target` (warning); (3) entities with no definition → `undefined_entity` (warning); (4) entities with one mention → `single_mention_entity` (info). **AuditIssue** has issue_type, severity, message, topic_id, start_char, end_char. No LLM; surfaces ambiguity for reporting only.

| Responsibility | Needs | Delivers | Config / Env |
|----------------|--------|----------|--------------|
| **Gap analyzer** | Topic tree; topic_id set | Missing topic numbers (e.g. 18.2) | — |
| **Unresolved refs** | Reference list; topic_id set | References pointing to non-existent or placeholder topics | — |
| **Unresolved entities** | Entity mentions; definition linkage | Undefined or partially defined entities (e.g. “Zone-C”) | — |
| **Circular refs** | Reference graph | Cycles in topic references | — |
| **Orphan content** | Orphan list from structure | Orphan regions with optional severity | — |
| **LLM disagreement** | Multiple LLM runs or validations | Flags where LLM output is inconsistent | Optional: only if you run multiple samples |
| **Risk/confidence** | All of the above | Per-issue or global confidence/risk score | `RISK_WEIGHTS` (optional) |

**Deliverable (internal):** Structured ambiguity/consistency report. **Export:** `ambiguity_report.csv`.

---

### 2.9 Deliverable Export

**Implemented:** Exporters in `outputs/` are thin serializers only (no LLM or inference): **topic_map_exporter** (nodes → JSON), **entity_catalogue_exporter** (entities → CSV), **entity_relationship_exporter** (list of **EntityRelationship** → JSON; **EntityRelationship** is defined in `entities/entity_models.py` alongside Entity and EntityMention), **ambiguity_report_exporter** (AuditIssue list → CSV), **reference_graph_exporter** (adjacency dict → PDF via networkx/matplotlib). Topic map uses **block.title** for each node; in v1 title is already clean; if segmentation ever includes full header text, keep title normalized in the exporter.

| Output File | Source | Config / Env |
|-------------|--------|--------------|
| `topic_map.json` | Topic hierarchy + graph | `OUTPUT_DIR`, `TOPIC_MAP_FILENAME` |
| `cross_reference_graph.pdf` | Reference graph | `OUTPUT_DIR`, graph layout options (e.g. engine) |
| `entity_catalogue.csv` | Entity catalogue | `OUTPUT_DIR`, column list |
| `entity_relationships.json` | Entity graph | `OUTPUT_DIR` |
| `ambiguity_report.csv` | Audit results | `OUTPUT_DIR`, columns |

All exporters need: **output directory** and optional **file names**. No secrets.

---

## 3. Config and Environment Design

### 3.1 Principles

- **Secrets and host-specific values** → `.env` (never committed); load via `python-dotenv` or equivalent.
- **Non-secret defaults and feature flags** → `config.py` (or config module) with sensible defaults; overridable by env vars.
- **Single source of truth:** One `config` object (or a small set of typed config objects) imported across the package.

### 3.2 What Goes Where

| Kind | Where | Examples |
|------|--------|----------|
| Secrets | `.env` only | `LLM_API_KEY` |
| Paths (user-specific) | `.env` preferred | `INPUT_PATH`, `OUTPUT_DIR` |
| Feature flags / behavior | `config.py` (default) + optional override in `.env` | `CREATE_PLACEHOLDER_FOR_MISSING`, `NORMALIZE_UNICODE` |
| LLM model / API key | `.env` | `LLM_API_KEY`, `LLM_MODEL` (Gemini) |
| Defaults that are same for everyone | `config.py` | Default encoding `utf-8`, default timeout 60s |

### 3.3 `.env` (and `.env.example`)

Variables to define (LLM uses **Gemini** via **google-generativeai**; model **gemini-3-flash**):

```bash
# ---- Input ----
INPUT_PATH=data/sample_document.txt
INPUT_ENCODING=utf-8

# ---- Output ----
OUTPUT_DIR=output

# ---- LLM: Gemini (google-generativeai SDK); leave LLM_API_KEY blank to skip enrichment ----
LLM_API_KEY=
LLM_MODEL=gemini-3-flash
LLM_TIMEOUT=60
```

- `.env`: real values (and optionally `INPUT_PATH` / `OUTPUT_DIR`); **must be in `.gitignore`**.
- `.env.example`: same keys, no secrets; committed so others know what to set.

### 3.4 `config.py` Structure

- **Load `.env`** at module load (e.g. `load_dotenv()` in `config.py` or in `main_pipeline.py` before importing config).
- **Single place** that reads `os.environ` and exposes typed settings:

  - **Ingestion:** `input_path`, `input_encoding`, `normalize_unicode`, `header_footer_patterns`, `page_number_pattern`, `whitespace_normalization`
  - **Structure:** `topic_id_patterns` (optional path or built-in), `orphan_min_length`, `create_placeholder_for_missing`
  - **References:** optional `reference_patterns` path
  - **LLM:** `llm_api_key`, `llm_model`, `llm_timeout`, `prompts_dir`; `skip_llm` if no API key (Gemini via google-generativeai)
  - **Output:** `output_dir`, `topic_map_filename`, etc.

- Use **defaults** for everything that can be defaulted; override from env only where needed (paths, API key, model).

### 3.5 File Layout

```text
semantic-topic-mapper/
├── .env                    # Local only; in .gitignore
├── .env.example            # Committed; no secrets
├── src/
│   └── semantic_topic_mapper/
│       ├── config.py       # Loads .env; defines Config dataclass or module-level settings
│       ├── ingestion/
│       ├── structure/
│       └── ...
```

Optional: if config grows large, split into `config/__init__.py` (re-exports), `config/settings.py` (env + defaults), `config/schemas.py` (Pydantic/dataclass for validation).

### 3.6 Implemented Artifacts

- **`.env.example`** — Committed template; copy to `.env` and set values.
- **`.gitignore`** — Includes `.env` so secrets are never committed.
- **`src/semantic_topic_mapper/config.py`** — Loads `.env` via `python-dotenv` if installed; exposes `INPUT_PATH`, `OUTPUT_DIR`, `skip_llm()`, and other settings. LLM defaults: **Gemini** (model **gemini-3-flash**); the LLM client is implemented with the **google-generativeai** SDK. Use:

  ```python
  from semantic_topic_mapper.config import INPUT_PATH, OUTPUT_DIR, skip_llm
  ```

  Dependencies: see root `requirements.txt` (includes `google-generativeai`, `python-dotenv`).

---

## 4. Dependency Flow (Pipeline Order)

For implementation order and testing:

1. **Config** → no dependency on other packages.
2. **Ingestion** → depends only on config (and possibly a small span type).
3. **Structure** → depends on ingestion output (normalized text); config.
4. **Hierarchy** → depends on structure (TopicBlocks); config.
5. **References (deterministic)** → depend on normalized text + topic_id set; config.
6. **LLM** → depends on config; used by reference enricher and entity enricher.
7. **Entities** → depend on normalized text + topic blocks (for context); config.
8. **Graph** → depends on hierarchy, references, entities.
9. **Audit** → depends on graph + structure (orphans, gaps).
10. **Outputs** → depend on graph + audit; config for paths.

---

## 5. Next Steps

1. **Create** `.env.example` and add `.env` to `.gitignore` (if not already).
2. **Add** `config.py` (or `config/`) with env loading and typed settings; no logic, only configuration.
3. **Implement** ingestion and structure (loader → normalizer → segmenter → topic_id_parser → topic_models + header_detector) and validate on `sample_document.txt`.
4. **Add** hierarchy builder and orphan detector; then reference detection and entity detection (deterministic only) so you can export a first `topic_map.json` and `ambiguity_report.csv` without LLM.
5. **Introduce** LLM layer and enrichers when the deterministic backbone is stable.

This keeps the “deterministic first, LLM as constrained enricher” design and gives you a clear feature-by-feature plan with explicit needs, deliverables, and config/env boundaries.
