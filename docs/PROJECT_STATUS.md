# Project Status — What’s Done vs Not Yet Done

**Phase:** Complete for core document intelligence: deterministic pipeline + optional LLM entity enrichment. Pipeline runs end-to-end with or without an API key.

Audit of the Semantic Topic Mapper codebase: implemented features, stubs, and optional/future work.

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
| **Config** | `config.py` (paths, LLM env vars, `skip_llm()`, `LLM_DEBUG`) | Used |
| **LLM** | `llm/client.py` (Gemini via google.genai), `entities/llm_entity_enricher.py` (entity types, relationships, ambiguity) | Used when `skip_llm()` is false |
| **Ingestion (utility)** | `pdf_to_txt.pdf_to_txt` | Implemented; not in pipeline (pre-step only) |

---

## Stubs (Comment-Only or Single-Line; No Logic)

These files exist for layout/placeholders but have **no executable implementation**:

| File | Purpose (from comment) |
|------|------------------------|
| **LLM** | |
| `llm/schemas.py` | JSON output schemas for LLM responses (not yet used; prompts inline in enricher) |
| `llm/validator.py` | Validate LLM responses against schemas |
| `references/llm_reference_enricher.py` | LLM-based interpretation of implicit references |
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

## Optional / Future (Not Required for Phase)

- **LLM reference enricher:** `references/llm_reference_enricher.py` is a stub; implicit/semantic reference interpretation is not implemented. Entity enrichment (types, relationships, ambiguity) is implemented.
- **Graph layer:** `graph/*` are placeholders; hierarchy and reference graph are built in `hierarchy_builder` and `reference_graph_builder` (in-memory); exporters write from those. No separate `graph/` data structures are used.
- **Orphan detection:** `orphan_detector` is a stub; not used in pipeline.
- **Extra audit modules:** `consistency_checker`, `gap_analyzer`, `risk_scorer`, `unresolved_detector` are stubs. Current audit is `ambiguity_detector.run_audit` (synthetic topics, reference issues, undefined/single-mention entities, plus LLM entity ambiguities).
- **Entity graph builder:** Stub; pipeline exports entity catalogue and relationships but does not build a separate entity graph structure.

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

- **Pipeline is end-to-end:** load → structure → references → entities (deterministic + optional LLM: types, relationships, ambiguity) → audit → all five exports. Runs with or without `LLM_API_KEY`; when set, LLM enriches entities only (no new entities, no structure changes).
- **Optional/future:** Implicit reference enricher, schemas/validator, extra audit modules (gap_analyzer, consistency_checker, risk_scorer, unresolved_detector), graph modules, orphan_detector, entity_graph_builder.
- **Tests:** Only `tests/test_topic_models.py` (topic ID parser + topic models); other subsystems are untested.
