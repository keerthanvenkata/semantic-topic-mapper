# Entity Extraction Pipeline — Deterministic + LLM Enrichment

High-level flow of entity extraction and enrichment. The pipeline runs with or without LLM; when `skip_llm()` is true, only the deterministic backbone runs.

---

## Flow Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INPUT: Normalized .txt                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DETERMINISTIC BACKBONE (always runs)                                        │
│  • Structure: headers → topic blocks → hierarchy                              │
│  • References: detect "Topic X" → reference graph + issues                   │
│  • Entities: detect mentions (rules A/B) → canonical entities                 │
│  • Definition linker: "X" means / shall mean / The term "X" means           │
│  • Entity relationships (v1): deterministic extractor (currently returns []) │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                        entities (canonical_name, mentions, definition_text…)
                        relationships (deterministic list, may be empty)
                                        │
                    ┌───────────────────┴───────────────────┐
                    │  skip_llm() ?                         │
                    └───────────────────┬───────────────────┘
                        YES │                    │ NO
                            │                    ▼
                            │     ┌─────────────────────────────────────────────┐
                            │     │  OPTIONAL LLM ENRICHMENT (Gemini)           │
                            │     │  • enrich_entity_types(entities, text)      │
                            │     │    → set entity_type where None             │
                            │     │  • extract_llm_entity_relationships(...)    │
                            │     │    → append to relationships              │
                            │     │  • detect_entity_ambiguities(...)           │
                            │     │    → list of AuditIssue (entity_ambiguity)  │
                            │     └─────────────────────────────────────────────┘
                            │                    │
                            └────────────────────┼─────────────────────────────┘
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AUDIT                                                                       │
│  • run_audit(nodes, reference_issues, entities) → structural/semantic issues │
│  • If LLM ran: issues.extend(llm_ambiguity_issues)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DELIVERABLES                                                                │
│  • topic_map.json          • entity_catalogue.csv (includes entity_type)    │
│  • entity_relationships.json (deterministic + LLM)                          │
│  • ambiguity_report.csv    • cross_reference_graph.pdf                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Rules

- **Deterministic extraction is the backbone:** entities and structure come from rules and patterns only.
- **LLM only enriches:** it classifies entity types, suggests relationships between existing entities, and flags entity ambiguities. It does not create new entities or change topic structure.
- **All LLM outputs are structured JSON** and validated; only then applied or appended to deliverables.
- **Pipeline runs when `skip_llm()` is true:** no Gemini calls; entity_type stays None where not set; relationships and ambiguity report contain only deterministic results.

---

*This document can be exported to PDF (e.g. via pandoc or your editor’s “Print to PDF”) for submission or sharing.*
