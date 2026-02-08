# Semantic Topic Mapper — Assumptions

This document defines the operational assumptions under which the Semantic Topic Mapper system is designed. These assumptions intentionally constrain scope and prevent overengineering.

---

## 1. Input Format Assumptions

- **The pipeline ingests plain text** (`.txt`, UTF-8 by default). The loader reads the file; the normalizer applies minimal cleanup. That normalized string is the start of the pipeline.
- The system does not perform PDF layout parsing or document formatting extraction inside the core pipeline. An **optional PDF→txt utility** (`ingestion/pdf_to_txt.py`) is provided to convert a PDF to .txt for later ingestion; file parsing and processing can be detailed in future considerations.
- Text has already been extracted from its original source (PDF, DOCX, etc.) before entering the system, or is produced by the PDF→txt utility.
- The input text may contain minor formatting inconsistencies, but is generally readable and structurally intact.

---

## 2. Text Normalization Scope

- The system does not perform advanced text normalization.
- No attempt is made to reconstruct layout features such as:
  - Columns
  - Tables
  - Visual indentation from PDFs
- Only minimal cleanup may be performed if strictly necessary for parsing (e.g., trimming whitespace).
- Bullet structure recovery from heavily corrupted layout is considered out of scope.

---

## 3. Structural Assumptions

- Topic hierarchy is primarily inferred from **explicit numbering patterns** (e.g., 5, 5.1, 5.1.a).
- Non-numbered headings may exist but are treated as secondary signals.
- Bullet points are treated as content within a topic, not automatically as subtopics.
- The system may create **synthetic placeholder topics** when structural gaps are detected (e.g., Topic 18.2 missing).
- **Header detection** is conservative: lines are accepted only when they match known patterns (e.g. “TOPIC X: TITLE”, “2.1 Title”) and pass simple heuristics (e.g. title does not end with a period; standalone single numbers > 50 are rejected to avoid years). Numbered sentences and in-line mentions like “Topic 12” are not treated as headers.
- **Explicit topic references** are detected by scanning for the literal "Topic &lt;ID&gt;" (case-insensitive) in each block's title, paragraph text, and subclauses; the following token is validated with the topic ID parser. **v1:** Title reference spans are approximate (header line offsets within the block are not separately tracked). Implicit or semantic references are handled later by LLM enrichment.
- **Missed topic boundaries (false negatives)** are an accepted tradeoff: some true headers may be missed, so text can merge into one TopicBlock. False positives (wrong splits) are considered more damaging than false negatives; refs and entities are still extracted at the topic level, and ambiguity detection may flag suspicious blocks.

---

## 4. Deterministic Backbone Assumptions

- The deterministic parser is the **source of structural truth**.
- LLMs do not:
  - Create or delete topic nodes
  - Modify topic hierarchy
  - Reassign text blocks to different topics
- Structural extraction must be **reproducible without LLM involvement**.

---

## 5. LLM Usage Assumptions

- LLMs are used strictly for **semantic enrichment**, including:
  - Classifying the intent of cross-references
  - Identifying implicit references
  - Interpreting entity roles
  - Flagging possible structural or semantic ambiguities
- LLM outputs are:
  - Structured
  - Schema-constrained
  - Validated before entering the knowledge graph
  - Never treated as authoritative structural edits

---

## 6. Ambiguity Handling Assumptions

- The system **prioritizes flagging ambiguity over resolving it automatically**.
- Missing topics, undefined entities, and unclear references are recorded in the ambiguity report.
- The system does not attempt legal interpretation or policy reasoning.

---

## 7. Entity Assumptions

- Entities may be referenced without formal definitions.
- The system must **record undefined entities** rather than infer missing definitions.
- Entity roles may be probabilistic when inferred by the LLM.

---

## 8. Output and Jobs

- Deliverables are written under **`output/`** (or `OUTPUT_DIR`). Each run should use a **per-document or per-job subfolder** (e.g. `output/<job_id>/`) so that topic_map.json, cross_reference_graph.pdf, entity_catalogue.csv, entity_relationships.json, and ambiguity_report.csv for that run stay together.

## 9. Out of Scope

The following are intentionally excluded from this version of the system:

- PDF visual layout reconstruction (optional PDF→txt extracts text only)
- OCR processing
- Legal reasoning or compliance judgment
- Natural language summarization
- Interactive user interfaces

---

## Guiding Principle

The system favors **deterministic structure + explicit uncertainty reporting** over heuristic guessing or silent correction.
