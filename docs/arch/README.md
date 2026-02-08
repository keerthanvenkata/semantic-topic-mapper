# Architecture (arch)

Detailed architecture documents linked from [System Architecture](../system_architecture.md).

| Document | Contents |
|---------|----------|
| [Ingestion and Output](ingestion.md) | What is ingested (normalized .txt); loader, normalizer; optional PDF→txt; output folder and per-job subfolders |
| [Two-Layer Architecture](two_layer_architecture.md) | Deterministic backbone vs LLM layer, principles, responsibility table, compiler analogy |
| [Topic Modeling Foundations](topic_modeling.md) | TopicID, TopicBlock, TopicNode, Subclause, topic ID grammar, header detection (patterns + heuristics), handling missed topic boundaries (false negatives), list markers |
| [References and Subclauses](references_and_subclauses.md) | Subclauses ≠ topics; TopicReference; explicit "Topic X" detection (reference_detector); graph edges connect TopicNodes only |
