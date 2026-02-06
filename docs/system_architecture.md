# Semantic Topic Mapper — System Architecture

## Purpose

Semantic Topic Mapper is a deterministic + LLM-assisted system that extracts
structured knowledge from long, complex regulatory-style documents.

The system produces:

- Topic hierarchies
- Cross-references between topics
- Entity inventories and relationships
- Structural and semantic ambiguity reports

This is **not** a chatbot, summarizer, or RAG system.  
It is a **document structure intelligence engine**.

---

## Input Assumptions

- Input is **normalized plain text**
- PDFs are converted to text *before* entering the system
- Layout artifacts may exist (line breaks, headers, footers) and are handled in preprocessing
- The document may contain:
  - Inconsistent numbering
  - Missing sections
  - Implicit references
  - Undefined entities

The system must detect and report issues rather than silently fixing them.

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

## Two-Layer Architecture: Deterministic Backbone and LLM Semantic Layer

The system is built as two distinct layers:

1. **Deterministic backbone** — The source of structural truth. It parses the document, detects topic boundaries and IDs, builds the topic hierarchy, and extracts explicit references and entity mentions using rules, grammars, and regex. Its outputs are reproducible and fully controlled by the implementation.

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
| **Topic boundary detection** | Yes. Identifies where topics start and end using header patterns and topic ID grammar. | No. May flag *candidate* boundary ambiguities (e.g. “this sentence could belong to 5.1 or 5.2”) as annotations; does not move or redefine boundaries. |
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

### 1. Deterministic Backbone
All structural elements (topics, hierarchy, IDs) are built using deterministic logic.

### 2. LLM as Constrained Semantic Parser
We use **Google Gemini** (model **gemini-3-flash**) via the **google-generativeai** Python SDK for semantic enrichment. LLMs are used only to interpret language-heavy signals such as:
- Implicit references
- Entity roles
- Obligation semantics
- Ambiguity indicators

LLM outputs must be:
- Structured
- Schema-constrained
- Grounded to text spans
- Validated before acceptance

### 3. No Silent Corrections
If something is inconsistent, missing, or ambiguous:
→ It is recorded in the ambiguity report  
→ It is never auto-fixed without traceability

### 4. Auditable Knowledge Graph
All extracted knowledge must be traceable back to:
- Source topic
- Source text span
- Extraction method (deterministic vs LLM)

---

## Core Subsystems

| Subsystem | Responsibility |
|----------|----------------|
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

- PDF layout parsing
- Legal reasoning or interpretation
- Summarization or Q&A interfaces
- UI or visualization dashboards
