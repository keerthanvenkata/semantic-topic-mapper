# References and Subclauses: Design Rules

## Architectural Rule (v1)

- **Graph edges always connect TopicNodes.** The topic graph has no nodes for subclauses.
- **In v1, subclauses (a), (b), (c) are NOT topics and do NOT become TopicNodes.** They are local structural elements inside a TopicBlock. Future versions may add optional, LLM-based subclause promotion (see [System Architecture](../system_architecture.md#future-enhancements)).
- **References and entities are attached to text spans within a topic**, not to artificial subtopic IDs. We do not promote subclauses into topic IDs like `2.2.a`.

---

## Subclause Model

Subclauses live inside `TopicBlock.subclauses`. They are not part of the topic hierarchy.

| Field        | Type | Description |
|-------------|------|-------------|
| `label`     | `str` | e.g. `"a"`, `"b"` |
| `text`      | `str` | The subclause text |
| `start_char`| `int` | Start offset in source document |
| `end_char`  | `int` | End offset in source document |

---

## TopicReference Model

References link topics and record where in the source the reference text appears.

| Field                | Type     | Description |
|----------------------|----------|-------------|
| `source_topic_id`    | `TopicID` | Topic where the reference text appears (always a real TopicNode) |
| `target_topic_id`    | `TopicID` | Topic (or start of range) being referred to |
| `relation_type`      | `str`     | e.g. `"explicit"`, `"implicit"`, `"range"` |
| `start_char`         | `int`     | Start of reference span in source document |
| `end_char`           | `int`     | End of reference span |
| `source_region_type` | `"paragraph" \| "subclause" \| "title"` | Where within the topic the reference appears |
| `source_region_label`| `str \| None` | Optional; e.g. `"b"` when inside subclause (b) |

---

## Explicit Reference Detection (v1)

Deterministic detection of **explicit** "Topic &lt;ID&gt;" references is implemented in `references/reference_detector.py`. This module does not use LLMs and does not build graphs; implicit or semantic references are handled in later LLM enrichment.

- **`detect_references(blocks: list[TopicBlock]) -> list[TopicReference]`** — For each block with a non-null `topic_id`, scans three regions separately: **(a)** block title (if present), **(b)** paragraph text (`block.raw_text`), **(c)** each subclause’s text.
- **Pattern:** Looks for the word "Topic" (case-insensitive) followed by a token that is validated with the topic ID parser. Trailing punctuation (e.g. `.`, `,`, `;`, `)`) is stripped before validation. Only valid topic IDs produce a TopicReference; bare numbers without the word "Topic" are not detected.
- **TopicReference fields:** `source_topic_id` = block’s topic; `target_topic_id` = parsed ID; `relation_type` = `"explicit"`; `start_char` / `end_char` = absolute positions in the document; `source_region_type` = `"title"` | `"paragraph"` | `"subclause"`; `source_region_label` = subclause label (e.g. `"b"`) when in a subclause, else `None`.
- **v1 limitation:** Title reference spans are **approximate**. Header detection and segmentation do not track exact title offsets within the block, so spans for references found in the title use the block start; they do not point to the exact header line. Paragraph and subclause spans use block/subclause offsets and are accurate.
- No deduplication is performed in the detector; callers may deduplicate if needed.

---

## Reference Graph and Issues (v1)

The module `references/reference_graph_builder.py` builds a directed reference graph and detects structural reference issues. It does not use LLMs or modify the hierarchy.

- **Inputs:** TopicNode dict (real + synthetic nodes) and list of TopicReference (e.g. from explicit detection).
- **Outputs:** (1) A directed adjacency list `dict[str, set[str]]` (topic_id.raw → set of referenced raw IDs). (2) A list of **ReferenceIssue** objects for references whose target is missing or is a synthetic (placeholder) node. Issue types in v1: `"missing_topic"`, `"synthetic_target"`. One issue per problematic reference occurrence; no aggressive deduplication.
- **ReferenceIssue:** `source_topic_id`, `target_topic_id`, `issue_type`, `start_char`, `end_char`. Used for ambiguity reporting and exports.

**Optional future enhancements (not in v1):** Additional issue types (e.g. `"self_reference"`, `"circular_reference"`), per-edge reference counts, or storing a reverse graph for backward lookups. v1 is intentionally minimal and correct.

---

## Relationship to Topic Modeling

- **TopicBlock** includes `subclauses: list[Subclause]`. In v1, subclauses remain inside the block and are not promoted to the topic hierarchy.
- **Hierarchy logic (v1):** we do not create TopicNodes for subclauses or parse labels like `(a)` as topic IDs (e.g. `2.2.a`). The topic ID grammar stays strict; list markers are content. Future enhancements may add optional LLM-based subclause promotion.

See [Topic Modeling Foundations](topic_modeling.md) for TopicID, TopicBlock, TopicNode.
