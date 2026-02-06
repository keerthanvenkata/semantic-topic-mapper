# Topic Modeling Foundations

The system represents document structure using core models in the shared `models/` package (`topic_models.py`), produced by the deterministic backbone.

**Architectural rule (v1):** Subclauses like (a), (b), (c) are **NOT** separate topics and do **not** become TopicNodes; they are local structural elements inside a TopicBlock. Graph edges always connect TopicNodes only. See [References and Subclauses](references_and_subclauses.md) for Subclause and TopicReference design. Future enhancements may add optional, LLM-based subclause promotion (see [System Architecture](../system_architecture.md#future-enhancements)).

---

## 1. TopicID Model

Structured identity of a topic.

| Field   | Type            | Description                          |
|---------|-----------------|--------------------------------------|
| `raw`   | `str`           | Original string form (e.g. `"2.1.a"`) |
| `parts` | `tuple[str, ...]` | Parsed hierarchical parts (e.g. `("2", "1", "a")`) |
| `level` | `int`           | Depth; equals `len(parts)`           |

**Planned behavior (methods, not yet implemented):** `parent()` → immediate parent ID candidate; `ancestors()` → list of higher-level IDs; `is_parent_of(other)`; `same_branch_as(other)`. For now, only the structure is stored.

---

## 2. TopicBlock Model

Chunk of document text associated with a topic.

| Field        | Type           | Description |
|-------------|----------------|--------------|
| `topic_id`  | `TopicID \| None` | Topic identifier, or `None` for orphan content |
| `title`     | `str \| None`  | Title if available |
| `raw_text`  | `str`          | Raw text kept intact for LLM grounding, reference span tracking, exports |
| `start_char`| `int`          | Start character offset in source document |
| `end_char`  | `int`          | End character offset in source document |
| `subclauses`| `list[Subclause]` | Local elements (a), (b), (c) inside this block; in v1 **remain inside TopicBlock**, do not become TopicNodes |

**Design choices:** `topic_id=None` allows orphan content. No hierarchy info here; hierarchy is in TopicNode. Subclauses are stored only here; they do not appear in the topic graph.

### 2b. Subclause Model (inside TopicBlock)

| Field        | Type | Description |
|-------------|------|--------------|
| `label`     | `str` | e.g. `"a"`, `"b"` |
| `text`      | `str` | Subclause text |
| `start_char`| `int` | Start offset in source document |
| `end_char`  | `int` | End offset in source document |

Subclauses are **not** topics and must **not** become TopicNodes.

---

## 3. TopicNode Model

Node in the topic hierarchy graph.

| Field          | Type               | Description |
|----------------|--------------------|-------------|
| `topic_id`    | `TopicID`          | This node’s topic identifier |
| `parent_id`   | `TopicID \| None`  | Immediate parent (e.g. root has `None`) |
| `children_ids`| `list[TopicID]`    | Immediate children |
| `block`       | `TopicBlock \| None` | Associated text block; `None` for synthetic nodes |
| `synthetic`   | `bool`             | `True` when node was created for a missing topic number (gap placeholder) |

**Why `synthetic`:** For gaps (e.g. 18.1 and 18.3 exist, 18.2 missing), we create a placeholder node for 18.2 with `synthetic=True` and `block=None`. Structural correctness is maintained without pretending content exists.

---

## 4. Topic ID Parser Design

The parser (`structure/topic_id_parser.py`) is pure, deterministic, and strict.

**Accepted grammar (v1):** Letter allowed only once, at the end.

```text
<number> ( "." <number> )* [ "." <letter> ]?
```

**Valid examples:** `2`, `2.1`, `2.1.a`, `10.4.b`

**Invalid examples:** `.2`, `2.`, `2..1`, `Topic 2`, `2.a.1` (letter before number at same depth)

**Parser responsibilities:**

- Given a string candidate: trim whitespace, validate format, split into parts, normalize letters to lowercase.
- Return a `TopicID` or `None` if invalid.

**Parser does not:** detect headers, infer hierarchy, or handle missing numbers. It only parses structure.

---

## 5. What Topic Modeling Does NOT Do

This layer does **not**:

- Detect whether a line is a header
- Build parent–child relationships
- Decide if a topic is missing
- Use LLMs
- Interpret bullets (a), (b) as structure

It only provides:

- A structured way to represent topic identity (TopicID) and text blocks (TopicBlock, TopicNode)

**Next step:** The module `hierarchy_builder.py` will compare TopicID levels, determine parent–child links, insert synthetic nodes, and detect gaps. That logic depends on these models being stable first.

**List markers:** (a), (b), (i), etc. may be stored as **Subclauses** inside TopicBlock (local structure). In v1 they do **not** form TopicNodes or topic IDs like `2.2.a`; the topic graph has no nodes for subclauses. Future enhancements may add optional LLM-based subclause promotion (see system architecture).

---

## Relationship to Pipeline

1. **Ingestion** produces normalized text.
2. **Structure** (header detection + topic ID parser) identifies candidate topic lines and parses TopicIDs.
3. **TopicBlock** extraction assigns spans and optional titles to each block.
4. **Hierarchy builder** creates **TopicNodes** from TopicBlocks, infers parent–child from TopicIDs, and inserts synthetic nodes for gaps.
5. **Graph** layer holds the TopicNode tree and TopicBlock references for downstream reference detection, entities, and export.

See [System Architecture](../system_architecture.md) for the high-level pipeline and [Two-Layer Architecture](two_layer_architecture.md) for the role of the deterministic backbone.
