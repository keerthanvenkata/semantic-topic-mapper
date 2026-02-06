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

## Relationship to Topic Modeling

- **TopicBlock** includes `subclauses: list[Subclause]`. In v1, subclauses remain inside the block and are not promoted to the topic hierarchy.
- **Hierarchy logic (v1):** we do not create TopicNodes for subclauses or parse labels like `(a)` as topic IDs (e.g. `2.2.a`). The topic ID grammar stays strict; list markers are content. Future enhancements may add optional LLM-based subclause promotion.

See [Topic Modeling Foundations](topic_modeling.md) for TopicID, TopicBlock, TopicNode.
