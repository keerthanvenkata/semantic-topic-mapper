# Project Status — What’s Done vs Not Yet Done

Audit of the Semantic Topic Mapper codebase: implemented features, stubs, and gaps.

---

## Implemented and Used in the Pipeline

| Area | Module / component | Status |
|------|--------------------|--------|
| **Ingestion** | `loader.load_text_file`, `text_normalizer` | Used |
| **Ingestion** | `segmenter.segment_into_topic_blocks` | Used |
| **Structure** | `topic_id_parser`, `header_detector.detect_headers` | Used |
| **Structure** | `hierarchy_builder.build_topic_hierarchy` | Used |
| **References** | `reference_detector.detect_references` | Used |
| **References** | `reference_graph_builder.build_reference_graph` | Used |
| **Entities** | `deterministic_entity_detector.detect_entities` | Used |
| **Entities** | `definition_linker.link_entity_definitions` | Used |
| **Entities** | `entity_relationship_extractor.extract_entity_relationships` | Used (returns `[]` in v1) |
| **Audit** | `ambiguity_detector.run_audit` | Used |
| **Outputs** | All 5 exporters (topic_map, entity_catalogue, entity_relationships, ambiguity_report, reference_graph PDF) | Used |
| **Pipeline** | `main_pipeline.run_pipeline`, `run_pipeline_from_config` | Used |
| **CLI** | `__main__.py` | Used |
| **Config** | `config.py` (paths, LLM env vars, `skip_llm()`) | Used |
| **Ingestion (utility)** | `pdf_to_txt.pdf_to_txt` | Implemented; not in pipeline (pre-step only) |

---

## Stubs (Comment-Only or Single-Line; No Logic)

These files exist for layout/placeholders but have **no executable implementation**:

| File | Purpose (from comment) |
|------|------------------------|
| **LLM** | |
| `llm/client.py` | Implemented (Gemini via google.genai); stubs below |
| `llm/schemas.py` | JSON output schemas for LLM responses |
| `llm/validator.py` | Validate LLM responses against schemas |
| `references/llm_reference_enricher.py` | LLM-based interpretation of implicit references |
| `entities/llm_entity_enricher.py` | Implemented (entity types, relationships, ambiguity); reference enricher stub |
| **Prompts** | |
| `llm/prompts/entity_semantics.txt` | Entity semantics prompt template |
| `llm/prompts/reference_semantics.txt` | Reference semantics prompt template |
| `llm/prompts/topic_semantics.txt` | Topic semantics prompt template |
| **Audit (extra)** | |
| `audit/consistency_checker.py` | Check structural and reference consistency |
| `audit/gap_analyzer.py` | Missing topic numbers (e.g. 18.2) |
| `audit/risk_scorer.py` | Confidence / risk scoring for findings |
| `audit/unresolved_detector.py` | Broken references; undefined entities |
| **Graph** | |
| `graph/topic_graph.py` | Topic hierarchy graph |
| `graph/reference_graph.py` | Topic–topic reference graph |
| `graph/entity_graph.py` | Entity graph and topic–entity edges |
| **Structure / Entities** | |
| `structure/orphan_detector.py` | Find text outside any topic block |
| `entities/entity_graph_builder.py` | Build entity graph and topic–entity edges |
| **Models** | |
| `models/entity_models.py` | Entity, Mention, Role data classes (placeholder; entity types live in `entities/entity_models.py`) |

The **pipeline does not import** any of the stub audit modules, graph modules, orphan_detector, or entity_graph_builder. It only uses `ambiguity_detector` for audit.

---

## Implemented but Intentionally Minimal (v1)

| Component | Limitation |
|-----------|------------|
| `entity_relationship_extractor` | Returns `[]`; no relationship inference yet (docstring: “may be added later deterministic or LLM”). |
| `reference_detector` | Title reference spans “approximate in v1”; implicit/semantic refs documented as “later LLM enrichment”. |
| `reference_models.Reference.relation_type` | Plain `str` in v1; docs say later e.g. `Literal["explicit","implicit","range","llm_inferred"]`. |
| `entity_models.Entity.entity_type` | May be `None` in v1; “filled later” (e.g. organization, role, temporal). |
| `definition_linker` | “First occurrence only; later” (multi-occurrence not implemented). |
| `topic_models.TopicNode` | Docstring: “Future methods (not implemented yet): parent(), ancestors()”. |

---

## Not Implemented / Optional (Docs or Code)

- **LLM layer:** Client and entity enricher (types, relationships, ambiguity) are implemented; pipeline calls them when `skip_llm()` is false. Config: `LLM_API_KEY`, `LLM_MODEL`, `skip_llm()`, `LLM_DEBUG`. Schemas/validator and reference enricher remain stubs.
- **Graph layer:** `graph/*` are placeholders; hierarchy and reference “graph” are built in `hierarchy_builder` and `reference_graph_builder` (in-memory structures), and exporters write from those. No separate graph data structures from `graph/` are used.
- **Orphan detection:** `orphan_detector` is a stub; not used in pipeline. Feature plan mentions `ORPHAN_MIN_LENGTH` and orphan spans.
- **Extra audit modules:** `consistency_checker`, `gap_analyzer`, `risk_scorer`, `unresolved_detector` are stubs. Current audit is only `ambiguity_detector.run_audit` (synthetic topics, reference issues, undefined entities, single-mention entities).
- **Entity graph builder:** Stub; pipeline does not build or export an entity graph (only entity catalogue CSV and entity_relationships JSON).

---

## Tests and Tooling

| Item | Status |
|------|--------|
| **Unit tests** | Only `tests/test_topic_models.py` (topic ID parser + topic models). No tests for header_detector, segmenter, hierarchy_builder, reference_detector, entity_detector, definition_linker, ambiguity_detector, or pipeline. |
| **Test run** | `tests/README.md` uses `PYTHONPATH=src`. With `pip install -e .`, tests can be run without setting `PYTHONPATH` (e.g. `pytest tests/ -v`). |
| **CI** | No CI config (e.g. GitHub Actions) in repo. |
| **Linting/formatting** | No `ruff`, `mypy`, or `pre-commit` config in repo. |

---

## Summary

- **Pipeline is end-to-end** for the deterministic path: load → structure → references → entities (with empty relationships) → single audit (ambiguity_detector) → all five exports. No LLM or graph/entity-graph code is executed.
- **Missing for “full” documented design:** LLM client + schemas + validator, LLM enrichers (references + entities), prompt bodies, optional audit modules (gap_analyzer, consistency_checker, risk_scorer, unresolved_detector), graph modules, orphan_detector, entity_graph_builder.
- **Tests** cover only topic models and topic_id_parser; other subsystems are untested.
