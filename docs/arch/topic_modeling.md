# Topic Modeling Foundations

The system represents document structure using three core models. These live in the shared `models/` package (`topic_models.py`) and are produced by the deterministic backbone.

---

## Core Models

### TopicID

A structured representation of a topic identifier (e.g. `2.1.a`). Topic IDs are parsed into hierarchical parts and used to determine structural relationships between topics.

- Parsed by the deterministic **topic ID grammar** (see below).
- Used to infer parent–child relationships (e.g. `2.1` is parent of `2.1.a`).
- No semantic meaning is attached at parse time; hierarchy is purely structural.

### TopicBlock

A container for the raw text associated with a topic. It stores:

- The topic identifier (if present)
- Title (if available)
- Character span within the source document

**TopicBlocks do not encode hierarchy.** They are flat “blocks” of text with an optional ID and span. Hierarchy is built separately via TopicNodes.

### TopicNode

A node in the topic hierarchy graph. TopicNodes:

- Reference TopicBlocks (one node may wrap one block’s content)
- Define parent–child relationships between topics
- May be **synthetic**: created when structural gaps are detected (e.g. missing intermediate topic numbers such as 18.2)

The graph of TopicNodes is the structural backbone’s representation of the document outline. Placeholder/synthetic nodes are marked as such and reported in the ambiguity report.

---

## Topic ID Grammar

Topic identifiers follow a strict grammar:

```text
<number> ( "." <number_or_letter> )*
```

**Examples:**

| Input   | Parsed as |
|--------|-----------|
| `2`     | Top-level topic 2 |
| `2.1`   | Child of 2 |
| `2.1.a` | Child of 2.1 (letter suffix) |

The grammar is implemented deterministically (e.g. in `structure/topic_id_parser.py`). Non-matching headings are not treated as topic IDs by the backbone; they may be used as secondary signals or left to semantic enrichment.

---

## List Markers and Substructure

List markers such as **(a)**, **(b)**, **(i)**, etc. are treated as **content within a topic**, not as automatic structural elements.

- They do not automatically form new TopicNodes.
- They may be explicitly promoted to structural elements by later semantic analysis (e.g. LLM or rules that interpret “5.1.a” as both a topic header and a list item). Until then, the backbone does not create nodes for list markers alone.
- This keeps the default hierarchy strict and numbering-driven; list-derived substructure is an optional, explicit enhancement.

---

## Relationship to Pipeline

1. **Ingestion** produces normalized text.
2. **Structure** (header detection + topic ID parser) identifies candidate topic lines and parses TopicIDs.
3. **TopicBlock** extraction assigns spans and optional titles to each block.
4. **Hierarchy builder** creates **TopicNodes** from TopicBlocks, infers parent–child from TopicIDs, and inserts synthetic nodes for gaps.
5. **Graph** layer holds the TopicNode tree and TopicBlock references for downstream reference detection, entities, and export.

See [System Architecture](../system_architecture.md) for the high-level pipeline and [Two-Layer Architecture](two_layer_architecture.md) for the role of the deterministic backbone.
