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

## System Design Principles

### 1. Deterministic Backbone
All structural elements (topics, hierarchy, IDs) are built using deterministic logic.

### 2. LLM as Constrained Semantic Parser
LLMs are used only to interpret language-heavy signals such as:
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
