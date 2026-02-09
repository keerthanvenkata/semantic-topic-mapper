"""
LLM-based entity enrichment: entity type classification, relationship extraction,
and entity ambiguity detection.

Uses Gemini (google.genai) only. All prompts request JSON; outputs are
validated before applying. LLM never invents new entities or modifies topic structure.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from semantic_topic_mapper.audit.ambiguity_detector import AuditIssue
from semantic_topic_mapper.entities.entity_models import Entity, EntityRelationship

logger = logging.getLogger(__name__)

VALID_ENTITY_TYPES = frozenset({
    "organization",
    "role",
    "temporal",
    "legal_construct",
    "other",
})

VALID_RELATION_TYPES = frozenset({
    "reports_to",
    "oversees",
    "obligation_to",
    "advises",
    "governs",
})


def _extract_json_from_response(text: str) -> str:
    """Strip markdown code fences if present and return inner string."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text


def _call_gemini_json(prompt: str, description: str) -> dict[str, Any] | None:
    """Call Gemini with temperature 0; parse and return JSON dict or None on failure."""
    try:
        from semantic_topic_mapper.llm.client import generate_content_text

        text = generate_content_text(prompt, temperature=0.0)
        if not text:
            logger.warning("LLM %s: empty response", description)
            return None
        raw = _extract_json_from_response(text)
        return json.loads(raw)
    except ValueError as e:
        logger.warning("LLM %s: config/API key issue: %s", description, e)
        return None
    except json.JSONDecodeError as e:
        logger.warning("LLM %s: invalid JSON: %s", description, e)
        return None
    except Exception as e:
        logger.warning("LLM %s: %s", description, e)
        return None


def enrich_entity_types(entities: list[Entity], full_text: str) -> None:
    """
    Use Gemini to classify each entity into one of: organization, role, temporal,
    legal_construct, other. Only updates entity.entity_type where it is currently None.
    Ignores names not in the deterministic entity list. In-place only; no new entities.
    """
    if not entities:
        return

    names = [e.canonical_name for e in entities]
    name_set = frozenset(names)

    prompt = f"""You are a document analyst. Classify each of the following entities from the document into exactly one type.

Allowed types only: organization, role, temporal, legal_construct, other.

Document excerpt (for context, length limited):
{full_text[:12000]}

Entity names to classify (use these exact strings):
{json.dumps(names)}

Respond with ONLY a single JSON object, no other text:
{{"entities": [{{"name": "<exact name>", "type": "<one of: organization, role, temporal, legal_construct, other>"}}]}}

Every name in the list must appear exactly once. Use the exact name string from the list."""

    data = _call_gemini_json(prompt, "entity type enrichment")
    if not data or "entities" not in data or not isinstance(data["entities"], list):
        return

    by_name = {e.canonical_name: e for e in entities}
    for item in data["entities"]:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        typ = item.get("type")
        if name not in name_set or typ not in VALID_ENTITY_TYPES:
            continue
        entity = by_name.get(name)
        if entity is not None and entity.entity_type is None:
            entity.entity_type = typ


def extract_llm_entity_relationships(
    entities: list[Entity],
    full_text: str,
) -> list[EntityRelationship]:
    """
    Use Gemini to extract relationships only between the given entities.
    Returns EntityRelationship list; only (source, target) pairs where both
    names exist in entities. topic_id is set to source entity's first_seen_topic (v1).
    """
    if not entities:
        return []

    names = [e.canonical_name for e in entities]
    name_set = frozenset(names)
    by_name = {e.canonical_name: e for e in entities}

    prompt = f"""You are a document analyst. Extract relationships between the following entities only. Do not add any entity not in the list.

Allowed relation_type values only: reports_to, oversees, obligation_to, advises, governs.

Document excerpt (for context, length limited):
{full_text[:12000]}

Entity names (use these exact strings; source and target must be from this list):
{json.dumps(names)}

Respond with ONLY a single JSON object, no other text:
{{"relationships": [{{"source": "<entity name>", "target": "<entity name>", "relation_type": "<one of: reports_to, oversees, obligation_to, advises, governs>"}}]}}

Only include relationships explicitly supported by the document. Both source and target must be from the entity list above."""

    data = _call_gemini_json(prompt, "LLM relationship extraction")
    if not data or "relationships" not in data or not isinstance(data["relationships"], list):
        return []

    result: list[EntityRelationship] = []
    for item in data["relationships"]:
        if not isinstance(item, dict):
            continue
        source_name = item.get("source")
        target_name = item.get("target")
        relation_type = item.get("relation_type")
        if (
            source_name not in name_set
            or target_name not in name_set
            or relation_type not in VALID_RELATION_TYPES
        ):
            continue
        source_entity = by_name[source_name]
        target_entity = by_name[target_name]
        result.append(
            EntityRelationship(
                source_entity_id=source_entity.entity_id,
                target_entity_id=target_entity.entity_id,
                relation_type=relation_type,
                topic_id=source_entity.first_seen_topic,
            )
        )
    return result


def detect_entity_ambiguities(
    entities: list[Entity],
    full_text: str,
) -> list[AuditIssue]:
    """
    Use Gemini to identify entities that appear ambiguous: undefined modifiers,
    referenced but never clearly defined, or possibly referring to multiple concepts.
    Returns AuditIssue list with issue_type="entity_ambiguity", severity="warning".
    """
    if not entities:
        return []

    names = [e.canonical_name for e in entities]
    by_name = {e.canonical_name: e for e in entities}

    prompt = f"""You are a document analyst. Identify entities that are ambiguous in the document.

Consider: entities that appear to include undefined modifiers; are referenced but never clearly defined; or might refer to multiple concepts.

Document excerpt (for context, length limited):
{full_text[:12000]}

Entity names to consider (from our extraction):
{json.dumps(names)}

Respond with ONLY a single JSON object, no other text:
{{"ambiguous_entities": [{{"name": "<exact entity name from list>", "reason": "<short explanation>"}}]}}

Only include entities from the list above. Leave ambiguous_entities empty if none are ambiguous."""

    data = _call_gemini_json(prompt, "entity ambiguity detection")
    if not data or "ambiguous_entities" not in data or not isinstance(data["ambiguous_entities"], list):
        return []

    result: list[AuditIssue] = []
    for item in data["ambiguous_entities"]:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        reason = item.get("reason")
        if not name or not reason:
            continue
        entity = by_name.get(name)
        if entity is None:
            continue
        result.append(
            AuditIssue(
                issue_type="entity_ambiguity",
                severity="warning",
                message=reason if isinstance(reason, str) else str(reason),
                topic_id=entity.first_seen_topic,
                start_char=None,
                end_char=None,
            )
        )
    return result
