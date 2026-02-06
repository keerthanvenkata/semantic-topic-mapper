# Disambiguation Logics

This document describes how the Semantic Topic Mapper handles ambiguous or underspecified cases: entity references, implicit references, undefined terms, and structural ambiguities. The approach is **detect, classify, and report**; the system does not silently resolve ambiguity by choosing a single interpretation.

---

## Relation to System Architecture

The system has a **deterministic backbone** and an **LLM semantic layer**. Disambiguation behavior follows that split:

- **Deterministic backbone** — Detects structural and explicit anomalies (missing topic IDs, broken references, orphan text, undefined entity names). It does not guess; it flags.
- **LLM layer** — May propose interpretations (e.g. “this phrase likely refers to Topic 8”) as structured, schema-bound annotations. Such proposals are not treated as resolutions; they are inputs to the ambiguity report when confidence is low or multiple interpretations exist.

Any uncertainty or ambiguity detected by either layer is **surfaced in the ambiguity report**, never silently resolved. See **System Architecture** (`docs/system_architecture.md`) for the full description of the two-layer design and the “Deterministic Backbone vs LLM Layer” table.

---

## Core Principle: Surface, Do Not Silently Resolve

- **Do:** Detect ambiguous or underspecified cases, classify them (e.g. undefined entity, implicit reference, boundary ambiguity), attach optional LLM-suggested interpretations as annotations, and record every such case in the ambiguity report with resolution strategies.
- **Do not:** Automatically pick one interpretation (e.g. “Zone-C” = one specific entity) or alter the knowledge graph structure to “fix” ambiguity. The graph reflects what was deterministically extracted plus validated LLM annotations; the report reflects what remains uncertain.

---

## Entity Reference Disambiguation

**Problem:** The same entity may appear under different names (“Zone-C Advisors”, “advisors in Zone-C”, “hereinafter the Advisors”). Some names may never be formally defined (“Zone-C” in the assignment trap).

**Logic:**

1. **Deterministic:** Detect entity mentions (surface forms) and “hereinafter referred to as” definitions. Link definitions to canonical entity IDs where the pattern is clear. Build a set of “defined” vs “mentioned but not defined” entities.
2. **LLM (optional):** Propose alias–canonical links or role/obligation annotations for ambiguous mentions. Output is schema-bound and span-grounded; it is not used to create or delete entities in the graph.
3. **Audit:** Every mention that cannot be tied to a defined entity (or that ties to multiple candidates) is listed in the ambiguity report. Undefined or partially defined entities (e.g. “Zone-C”) are flagged with a resolution strategy (e.g. “Request clarification from document owner”).
4. **No silent resolution:** The system does not choose a single canonical entity for ambiguous mentions; it records the ambiguity and, if present, the LLM-suggested options as annotations for human or downstream review.

---

## Implicit Reference Disambiguation

**Problem:** Phrases like “as described above”, “the foregoing”, “that section” do not name a topic ID. The LLM can suggest likely targets; the document may still be ambiguous.

**Logic:**

1. **Deterministic:** Extract only explicit references (e.g. “See Topic 8”, “per Topic 12”). No guessing of referents for implicit phrasing.
2. **LLM (optional):** For given spans, produce structured annotations: suggested topic ID(s), confidence, and span. If confidence is low or multiple targets are plausible, the annotation can indicate multiple candidates.
3. **Audit:** Implicit references with no LLM suggestion, or with low confidence or multiple candidates, are recorded in the ambiguity report. Resolution strategy may be “Manual review” or “Confirm with document context”.
4. **No silent resolution:** The reference graph does not add edges for implicit references unless a validated, single-target annotation exists and policy allows it; otherwise the ambiguity is reported.

---

## Structural and Boundary Ambiguity

**Problem:** Topic numbering gaps (e.g. 18.2 missing), orphan text, sentences that could belong to more than one topic, and **missed topic boundaries** (false negatives from conservative header detection).

**Logic:**

1. **Deterministic:** Detect missing topic IDs, orphan spans, and references to non-existent topics. Create placeholder nodes only when configured; do not infer content. All findings go into the ambiguity report. When a header is missed, text merges into the previous TopicBlock; refs and entities are still extracted at the topic level.
2. **Ambiguity layer:** Unusually **long or semantically heterogeneous blocks** may be flagged as potential boundary issues (e.g. possible missed header). This does not change structure; it surfaces a candidate for review.
3. **LLM (optional):** Flag boundary ambiguities (e.g. “this sentence could belong to 5.1 or 5.2”) as annotations tied to spans. These do not move or redefine topic boundaries; they inform the report.
4. **Audit:** Missing topics, broken references, orphan content, suspected merged-boundary blocks, and LLM-flagged boundary ambiguities are listed with resolution strategies (e.g. “Registrants should request clarification from IFOC” for missing 18.2).
5. **No silent resolution:** Structure is not reorganized to “fix” gaps or boundaries; the backbone’s structure is the source of truth, and ambiguities are documented.

---

## Summary Table (Who Does What)

| Disambiguation concern      | Deterministic backbone role        | LLM layer role                         | How ambiguity is handled                    |
|----------------------------|-------------------------------------|----------------------------------------|--------------------------------------------|
| Entity identity / aliasing | Detect mentions and definitions; flag undefined | Propose alias/role annotations          | Undefined and ambiguous entities in report |
| Implicit references        | No interpretation                   | Propose suggested topic ID(s) + confidence | Low confidence / multi-candidate in report |
| Missing topic IDs          | Detect gaps; optional placeholders  | —                                      | Missing IDs and refs to them in report     |
| Boundary ambiguity         | —                                   | Flag “could belong to A or B”           | Boundary ambiguity rows in report          |
| Orphan text                | Detect and list orphan spans        | —                                      | Orphan regions in report                   |

---

## Resolution Strategies (Report Only)

The ambiguity report includes resolution strategies for each issue type. These are **recommendations for humans or downstream systems**, not automatic actions:

- **Undefined entity:** Request definition from document owner; or add to glossary with “undefined” flag.
- **Implicit reference with multiple candidates:** Manual review of context; optionally confirm with domain expert.
- **Missing topic (e.g. 18.2):** Request clarification from issuing body; do not infer content.
- **Boundary ambiguity:** Manual assignment or document owner decision.
- **Orphan content:** Review for misnumbered section or annex; do not auto-assign to a topic.

This keeps the system’s behavior predictable and auditable: the deterministic backbone and validated LLM annotations define what is in the graph; the ambiguity report defines what remains unresolved and how to handle it.
