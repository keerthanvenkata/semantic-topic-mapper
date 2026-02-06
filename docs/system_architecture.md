# Semantic Topic Mapper — System Architecture

## Purpose

Semantic Topic Mapper is a deterministic + LLM-assisted system that extracts structured knowledge from long, complex regulatory-style documents.

The system produces:

- Topic hierarchies
- Cross-references between topics
- Entity inventories and relationships
- Structural and semantic ambiguity reports

This is **not** a chatbot, summarizer, or RAG system. It is a **document structure intelligence engine**.

---

## Input Assumptions

- Input is **normalized plain text** (e.g. UTF-8 `.txt`). PDFs are converted to text *before* entering the system.
- Layout artifacts (line breaks, headers, footers) may exist and are handled in preprocessing.
- Topic headers are detected deterministically using pattern matching and conservative heuristics (e.g. title must not end with a period; standalone numbers > 50 rejected) so numbered sentences and years are not misclassified.
- Documents may contain inconsistent numbering, missing sections, implicit references, and undefined entities.
- The system **detects and reports** such issues rather than silently fixing them.

For the full set of operational assumptions, see [Assumptions](assumptions.md).

---

## High-Level Pipeline

```text
Raw Text
    ↓
Text Normalization
    ↓
Deterministic Structural Parsing
    ↓
Topic Hierarchy Construction
    ↓
Reference Detection (Deterministic)
    ↓
LLM Semantic Enrichment (Constrained, Structured Output)
    ↓
Graph Construction
    ↓
Consistency & Ambiguity Analysis
    ↓
Deliverable Exports
```

---

## Two-Layer Architecture

The system is built as two distinct layers: a **deterministic backbone** (source of structural truth) and an **LLM semantic layer** (semantic enrichment only). The LLM never creates, deletes, or reorganizes the topic hierarchy; all structure comes from the backbone.

For principles, responsibility split, and the compiler analogy, see **[Two-Layer Architecture](arch/two_layer_architecture.md)**.

---

## Topic Modeling Foundations

Document structure is represented by three core models: **TopicID** (parsed identifier, e.g. 2.1.a), **TopicBlock** (raw text container with span; no hierarchy), and **TopicNode** (hierarchy graph node; may reference a TopicBlock; synthetic nodes for gaps). Topic IDs follow a strict grammar; list markers like (a), (b) are content within a topic unless explicitly promoted.

For grammar, list-marker handling, and pipeline placement, see **[Topic Modeling Foundations](arch/topic_modeling.md)**.

---

## Core Subsystems

| Subsystem | Responsibility |
|-----------|----------------|
| Ingestion | Load and normalize raw text |
| Structure | Detect topic blocks and build hierarchy |
| References | Detect and classify topic references |
| Entities | Extract entities and their roles |
| LLM Layer | Provide structured semantic enrichment |
| Graph | Maintain topic + entity relationship graphs |
| Audit | Detect inconsistencies and ambiguities |
| Outputs | Generate assignment deliverables |

---

## Out of Scope (For Now)

- PDF / DOCX filetype input
- PDF layout parsing
- Legal reasoning or interpretation
- Summarization or Q&A interfaces
- UI or visualization dashboards

---

## Future Enhancements

### LLM-Assisted Ambiguity Confidence Scoring

Future versions may incorporate LLM-based evaluation to estimate confidence levels for structural or semantic ambiguities.

Potential applications:

- Scoring topic boundary uncertainty
- Assessing whether bullet lists imply substructure
- Ranking the severity of unresolved references
- Providing natural language explanations for ambiguous regions

These signals would remain **advisory** and would not alter the deterministic structural backbone. All LLM-derived confidence scores would be stored as metadata and surfaced in reports rather than used for automatic structural corrections.

### Subclause promotion (v1: out of scope)

In v1, subclauses (a), (b), (c) never become TopicNodes; they remain local structure inside TopicBlock. Future versions could introduce optional, LLM-based analysis to suggest when a subclause might be promoted to a structural element (e.g. as a synthetic topic or as a first-class navigation target). Any such feature would remain advisory and configurable; the default would stay deterministic (no promotion).

### Missed topic boundaries (false negatives)

The header detector is conservative; some true topic boundaries may be missed and merged into a single TopicBlock. This is an accepted v1 tradeoff (false positives are more damaging than false negatives). Refs and entities are still extracted; ambiguity detection may flag long or heterogeneous blocks. Future versions may add **LLM-assisted semantic boundary analysis** (detect topic shifts, suggest missing headers, confidence scores) as advisory signals in the ambiguity report. See [Topic Modeling Foundations](arch/topic_modeling.md#5b-handling-missed-topic-boundaries-false-negatives).
