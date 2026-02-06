# Two-Layer Architecture: Deterministic Backbone and LLM Semantic Layer

This document details the split between the deterministic structural backbone and the LLM semantic layer. See [System Architecture](../system_architecture.md) for the high-level view.

---

## The Two Layers

1. **Deterministic backbone** — The source of structural truth. It parses the document, detects topic boundaries and IDs, builds the topic hierarchy (see [Topic Modeling Foundations](topic_modeling.md)), and extracts explicit references and entity mentions using rules, grammars, and regex. Its outputs are reproducible and fully controlled by the implementation.

2. **LLM semantic layer** — Used only for semantic enrichment. It interprets natural-language signals (e.g. “as described above”, entity roles, obligation wording) and produces structured annotations that are attached to spans and nodes already established by the backbone. It does not create, delete, or reorganize structure.

The LLM never creates, deletes, or reorganizes the topic hierarchy. All structural decisions—what counts as a topic, how topics are nested, which text is orphan—come from the deterministic backbone. The LLM only adds interpretations (e.g. “this phrase likely refers to Topic 8”) that are schema-bound, grounded in text spans, and validated before they enter the knowledge graph. Any uncertainty or ambiguity detected by the LLM is surfaced in the ambiguity report and never silently resolved.

---

## Architectural Principles

1. **Deterministic backbone and LLM semantic layer** — The system has a deterministic backbone and an LLM semantic layer. Structure is owned by the backbone; the LLM layer only enriches with semantic annotations.

2. **Deterministic backbone as source of structural truth** — All topic boundaries, topic IDs, parent-child relationships, and explicit reference targets are determined by the backbone. The knowledge graph’s structure (topic tree, topic nodes, reference edges) is derived solely from backbone outputs.

3. **LLMs only for semantic enrichment, not structural control** — LLMs are used to interpret meaning (implicit references, entity roles, obligation semantics, boundary ambiguities). They do not decide what is a topic, how topics are nested, or what the “correct” structure is.

4. **LLM never mutates hierarchy** — The LLM never creates, deletes, or reorganizes topic hierarchy. It may propose annotations (e.g. “span X implies reference to Topic N”); such annotations are validated and attached to existing nodes/spans. Structural changes are out of scope for the LLM.

5. **Structured, schema-bound, span-grounded LLM output** — Every LLM output must conform to a defined JSON schema, be bound to specific text spans (so it can be audited), and never introduce new structural nodes or edges on its own.

6. **Validation before graph inclusion** — All LLM outputs are validated (schema and consistency checks) before they are allowed to enter the knowledge graph. Invalid or malformed LLM output is logged and discarded; it does not alter the graph.

7. **Uncertainty and ambiguity surfaced, not resolved** — Any uncertainty or ambiguity detected by the LLM (e.g. low confidence, multiple possible referents) is recorded in the ambiguity report with resolution strategies. The system does not silently pick one interpretation; it flags the issue for human or downstream review.

---

## Deterministic Backbone vs LLM Layer

| Responsibility | Deterministic Backbone | LLM Layer |
|----------------|------------------------|-----------|
| **Topic boundary detection** | Yes. Identifies where topics start and end using header patterns and topic ID grammar. Conservative heuristics (e.g. title must not end with a period; standalone ID > 50 rejected) avoid misclassifying numbered sentences and years as headers. | No. May flag *candidate* boundary ambiguities (e.g. “this sentence could belong to 5.1 or 5.2”) as annotations; does not move or redefine boundaries. |
| **Topic ID hierarchy** | Yes. Parses topic IDs (e.g. 5, 5.1, 5.1.a), infers parent-child relationships, creates placeholders for gaps. | No. Does not assign, change, or infer topic IDs or hierarchy. |
| **Cross-reference detection** | Yes. Detects explicit references (“See Topic 8”, “per Topic 12”, “Topics 5–9”) and records targets and spans. | No for structure. Enriches with interpretation of *implicit* references (e.g. “as described above” → suggested topic ID); output is annotation only. |
| **Implicit reference interpretation** | No. Only explicit reference strings and patterns. | Yes. Interprets phrases like “as described above”, “the foregoing”, “that section” and produces structured suggestions (topic ID, confidence) tied to spans. |
| **Entity role interpretation** | No. Deterministic layer can detect entity mentions and “hereinafter” definitions. | Yes. Interprets roles, obligations, and relationships (e.g. “must report”, “subject to”) as structured annotations. |
| **Ambiguity detection** | Yes. Detects missing topic numbers, broken references, orphan text, circular references, undefined entities (e.g. “Zone-C” never defined). | Yes. Flags semantically suspicious or ambiguous phrasing, low-confidence interpretations, and boundary ambiguities. All such findings are written to the ambiguity report; neither layer silently resolves them. |

---

## Compiler Analogy

A useful analogy is a compiler:

- **Deterministic parsing ≈ syntax tree** — The backbone is like the lexical and syntactic phases: it produces a well-defined structure (topic tree, reference list, entity mentions) from the document text using fixed rules. That structure is the “syntax tree” of the document.

- **LLM enrichment ≈ semantic analysis** — The LLM layer is like semantic analysis: it attaches meaning (e.g. “this reference likely points here”, “this entity has this role”) to nodes and spans that already exist. It does not change the parse tree; it only adds typed annotations that can be validated and later used for analysis or reporting.

The pipeline order reflects this: structure is fixed first; then semantic enrichment runs on that structure.

---

## System Design Principles (Summary)

- **Deterministic Backbone** — All structural elements (topics, hierarchy, IDs) are built using deterministic logic.
- **LLM as Constrained Semantic Parser** — We use **Google Gemini** (model **gemini-3-flash**) via the **google-generativeai** Python SDK for semantic enrichment. LLM outputs must be structured, schema-constrained, grounded in text spans, and validated before acceptance.
- **No Silent Corrections** — Inconsistencies and ambiguities are recorded in the ambiguity report and never auto-fixed without traceability.
- **Auditable Knowledge Graph** — All extracted knowledge is traceable to source topic, source text span, and extraction method (deterministic vs LLM).
