# Semantic Topic Mapper — Documentation

Documentation for the Semantic Topic Mapper: a document intelligence pipeline that extracts topic hierarchies, cross-references, entities, and ambiguity reports from regulatory-style text.

---

## Getting started

| Document | Description |
|----------|-------------|
| [Run guide](run_guide.md) | How to run the pipeline, prerequisites, outputs, and requirements. |
| [CLI reference](run/cli.md) | Command-line options and examples. |
| [Configuration reference](run/config_reference.md) | Environment variables, `.env`, and config. |

---

## Architecture and design

| Document | Description |
|----------|-------------|
| [System architecture](system_architecture.md) | Pipeline overview, two-layer design, subsystems, and scope. |
| [Entity extraction pipeline](entity_extraction_pipeline.md) | Flow: deterministic extraction + optional LLM enrichment (types, relationships, ambiguity). |
| [Two-layer architecture](arch/two_layer_architecture.md) | Deterministic backbone vs LLM layer; principles and responsibility split. |
| [Topic modeling](arch/topic_modeling.md) | TopicID, TopicBlock, TopicNode, grammar, header detection. |
| [References and subclauses](arch/references_and_subclauses.md) | Explicit reference detection, reference graph, subclauses. |
| [Ingestion and output](arch/ingestion.md) | Input (normalized .txt), loader, normalizer, PDF→txt utility, output layout. |

---

## Disambiguation and navigation

| Document | Description |
|----------|-------------|
| [Disambiguation logics](disambiguation_logics.md) | How ambiguity is detected and reported; deterministic vs LLM; “Zone-C” style cases. |
| [Navigation agent design](navigation_agent_design.md) | Using topic, reference, and entity outputs for intelligent navigation. |

---

## Project and config

| Document | Description |
|----------|-------------|
| [Project status](PROJECT_STATUS.md) | What’s implemented vs optional/future; tests and tooling. |
| [Assumptions](assumptions.md) | Operational assumptions for the pipeline. |
| [Feature plan and config](feature_plan_and_config.md) | Feature plan, config design, and `.env` layout. |

---

For a high-level project overview and quick start, see the [main README](../README.md) in the project root.
