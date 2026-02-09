# Semantic Topic Mapper

A **document intelligence** pipeline that extracts structured knowledge from long, regulatory-style documents: topic hierarchies, cross-references, entities, and ambiguity reports. Built as a deterministic backbone with optional LLM enrichment (Gemini) for entity typing, relationships, and ambiguity detection.

---

## Features

- **Topic structure** — Detect section headers (e.g. `TOPIC 2.1`, `2.1.a`), segment into topic blocks, and build a parent–child hierarchy with synthetic nodes for numbering gaps.
- **Cross-references** — Find explicit “Topic X” references in titles, paragraphs, and subclauses; build a directed reference graph; flag missing or placeholder targets.
- **Entity extraction** — Identify defined terms and entities (deterministic rules + optional LLM), link definitions (“X” means …), classify entity types (organization, role, temporal, etc.), and extract relationships (reports_to, oversees, obligation_to, etc.).
- **Audit & ambiguity** — Report synthetic topics, broken references, undefined entities, single-mention entities, and (with LLM) entity ambiguities. No silent resolution; all issues surface in an ambiguity report.
- **Deliverables** — JSON topic map, CSV entity catalogue, JSON entity relationships, CSV ambiguity report, and a PDF cross-reference graph.

**Design:** Deterministic parsing is the source of truth. The LLM only enriches existing entities (types, relationships, ambiguity flags); it does not create entities or change structure. Pipeline runs with or without an API key; set `SKIP_LLM=true` or leave `LLM_API_KEY` unset to use the deterministic-only path.

---

## Tech stack

- **Python 3.10+**
- **Deterministic:** Regex and pattern-based header detection, topic ID grammar, reference detection, entity rules, definition linking.
- **LLM (optional):** Google Gemini via [google.genai](https://pypi.org/project/google-genai/) (e.g. `gemini-3-flash-preview`) for entity type classification, relationship extraction, and entity ambiguity detection.
- **Export:** JSON, CSV, and PDF (NetworkX + Matplotlib for the reference graph). Optional PDF→text utility (pypdf) for ingestion prep.

---

## Quick start

```bash
# Clone and enter project
cd semantic-topic-mapper

# Create venv and install
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -e .

# Run on sample document (deterministic only if no LLM_API_KEY)
python -m semantic_topic_mapper data/sample_document.txt

# Custom output directory
python -m semantic_topic_mapper data/sample_document.txt --output output/my_run
```

**With LLM enrichment:** Copy `.env.example` to `.env`, set `LLM_API_KEY` (e.g. from [Google AI Studio](https://aistudio.google.com/apikey)), and run again. Optionally set `LLM_DEBUG=true` to save prompts and responses under `output/llm_debug/` for debugging.

---

## Outputs

| File | Description |
|------|-------------|
| `topic_map.json` | Topic hierarchy (id, title, synthetic, children). |
| `entity_catalogue.csv` | Entities: id, name, type, first_seen_topic, definition_topic, mention_count. |
| `entity_relationships.json` | Directed relationships: source, target, relation_type, topic_id. |
| `ambiguity_report.csv` | Audit issues: type, severity, message, topic_id, spans. |
| `cross_reference_graph.pdf` | Directed graph of topic-to-topic references. |

---

## Document intelligence use cases

- **Compliance & regulatory** — Map structure and “Topic X” references in standards, regulations, or contracts; trace obligations and roles.
- **Knowledge graph ingestion** — Export topic hierarchy and entity relationships for graph DBs or RAG indexing (structure as backbone, entities and refs as edges).
- **Quality and ambiguity review** — Use the ambiguity report to find undefined terms, broken references, and LLM-flagged entity ambiguities for human review.
- **Navigation and search** — Use the topic map and reference graph to build section-aware navigation or “see also” features (see [Navigation agent design](docs/navigation_agent_design.md)).

---

## Project structure

```
semantic-topic-mapper/
├── src/semantic_topic_mapper/
│   ├── ingestion/      # Load, normalize, segment
│   ├── structure/      # Headers, topic IDs, hierarchy
│   ├── references/     # Reference detection, graph
│   ├── entities/       # Entity detection, definitions, LLM enrichment
│   ├── audit/          # Ambiguity detector
│   ├── llm/            # Gemini client (google.genai)
│   ├── outputs/        # Exporters (JSON, CSV, PDF)
│   └── pipeline/       # Orchestration
├── data/               # Sample input
├── docs/               # Architecture, run guide, config
└── tests/
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Documentation index](docs/README.md) | Full list of architecture, run, and reference docs. |
| [Run guide](docs/run_guide.md) | How to run, prerequisites, outputs. |
| [CLI reference](docs/run/cli.md) | Command-line options. |
| [Configuration](docs/run/config_reference.md) | Environment variables and `.env`. |
| [System architecture](docs/system_architecture.md) | Pipeline, two-layer design, subsystems. |
| [Entity extraction pipeline](docs/entity_extraction_pipeline.md) | Deterministic + LLM entity flow. |
| [Disambiguation logics](docs/disambiguation_logics.md) | How ambiguity is detected and reported (incl. “Zone-C” style cases). |
| [Navigation agent design](docs/navigation_agent_design.md) | Using topic/entity/reference graphs for navigation. |
| [Project status](docs/PROJECT_STATUS.md) | Implemented vs optional/future work. |

---

## Status

**Phase complete.** The pipeline runs end-to-end: ingestion → structure → references → entities (deterministic + optional LLM enrichment) → audit → five deliverables. LLM enrichment (entity types, relationships, entity ambiguity) is implemented and optional; the deterministic path does not require an API key. Future work may add implicit reference enrichment, extra audit modules, or graph-layer abstractions (see [PROJECT_STATUS.md](docs/PROJECT_STATUS.md)).

---

## License

MIT. See [LICENSE](LICENSE).
