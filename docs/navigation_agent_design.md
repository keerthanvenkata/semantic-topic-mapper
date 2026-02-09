# Navigation Agent Design

This document describes how a future **intelligent navigation agent** could use the Semantic Topic Mapper’s outputs — the topic graph, reference graph, and entity graph — to support goal-directed navigation and answer-seeking in complex documents.

---

## Available Graphs (From Pipeline Outputs)

| Graph / artefact | Content | Use for navigation |
|------------------|--------|--------------------|
| **Topic graph** | Hierarchy of topics (topic_map.json): parent–child, synthetic nodes for gaps. Each node has topic_id, title, optional block. | “Where does this section sit in the document?” “What are the siblings?” “What is the parent section?” |
| **Reference graph** | Directed edges between topics (cross_reference_graph.pdf + internal graph): “Topic A references Topic B”. | “What does this section point to?” “What sections point here?” “Follow cross-references from here.” |
| **Entity graph** | Entities (entity_catalogue.csv) and relationships (entity_relationships.json): who reports to whom, obligations, governance. | “Which roles oversee this one?” “What entities are mentioned in Topic X?” “Trace obligation chains.” |

The pipeline does not yet build a single unified “entity graph” data structure; it produces entity catalogue and relationship list. A navigation agent can construct a graph from these (nodes = entities, edges = relationships) and optionally attach topic_id (first_seen_topic, definition_topic) for “where is this entity defined or first mentioned.”

---

## How an Agent Could Use the Graphs

1. **Topic-first navigation**
   - User: “Take me to the section that defines term X.”
   - Agent: Resolve X to an entity (entity catalogue); get definition_topic; use topic graph to get section title and context; optionally follow references from that topic.

2. **Reference-guided traversal**
   - User: “What does Topic 5 refer to?”
   - Agent: Use reference graph to list targets of Topic 5; present titles (from topic graph) and optionally snippets.

3. **Entity-relationship traversal**
   - User: “Who does the Compliance Officer report to?”
   - Agent: Find “Compliance Officer” in entity catalogue; use entity_relationships to find edges with relation_type reports_to; resolve target entity and, if needed, topic_id for “where is this stated.”

4. **Combined queries**
   - “Which topics discuss entity E and also reference Topic 8?” — intersect entity mentions (by topic) with reference graph (sources that point to Topic 8).

---

## Design Principles for the Agent

- **Graphs are read-only for navigation:** the agent does not modify topic structure, references, or entities; it only traverses and presents.
- **Ambiguity report as input:** the agent can surface “entity_ambiguity” and other audit issues so the user knows when an entity or reference is uncertain.
- **Deterministic backbone as source of truth:** structural navigation (topic hierarchy, explicit references) relies on the deterministic pipeline; LLM enrichment adds types and relationship hints but does not invent structure.

---

## Future Extensions

- **Reverse reference index:** “Which topics reference this one?” for backward navigation.
- **Entity–topic index:** “All topics where entity E is mentioned” for quick jump.
- **Confidence or provenance:** tag LLM-derived relationships so the agent can show “suggested” vs “explicit” when presenting answers.

This design keeps the agent as a consumer of the pipeline’s deliverables and avoids duplicating extraction logic inside the agent.
