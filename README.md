# Semantic Topic Mapper

Semantic Topic Mapper is a deterministic + LLM-assisted system for extracting
structured knowledge from complex regulatory-style documents.

It identifies:

- Topic hierarchies
- Cross-references between sections
- Entities and their roles
- Structural and semantic ambiguities

This project focuses on **system design, structured parsing, and auditable knowledge graph construction** — not chatbot-style summarization.

## Status

Early architecture and structural parsing phase.

## Input

Plain text documents (PDFs converted to text beforehand).

## How to run

From project root, install the package in editable mode:

```bash
pip install -e .
```

Then:

```bash
# With a path to a text file (output goes to output/ by default)
python -m semantic_topic_mapper data/sample_document.txt

# Custom output directory
python -m semantic_topic_mapper data/sample_document.txt --output output/my_run

# From config: set INPUT_PATH in .env, then
python -m semantic_topic_mapper
```

See **[docs/run_guide.md](docs/run_guide.md)** for the full run guide and **docs/run/** for CLI and configuration details.

## Outputs

- Topic hierarchy map (`topic_map.json`)
- Cross-reference graph (`cross_reference_graph.pdf`)
- Entity catalogue and relationships (`entity_catalogue.csv`, `entity_relationships.json`)
- Ambiguity and consistency report (`ambiguity_report.csv`)
