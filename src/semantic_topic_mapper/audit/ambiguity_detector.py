"""
Ambiguity and consistency audit layer.

Aggregates structural and semantic signals (synthetic topics, reference issues,
undefined entities, single-mention entities) into a unified list of AuditIssue
records for reporting. Surfaces structural and semantic ambiguity for human or
downstream review; does not resolve issues or use LLMs.
"""

from __future__ import annotations

from dataclasses import dataclass

from semantic_topic_mapper.entities.entity_models import Entity
from semantic_topic_mapper.models.topic_models import TopicID, TopicNode
from semantic_topic_mapper.references.reference_graph_builder import ReferenceIssue


@dataclass
class AuditIssue:
    """
    A single audit finding for reporting.

    issue_type and severity classify the finding; message is human-readable.
    topic_id and start_char/end_char optionally point to the relevant location.
    """

    issue_type: str
    severity: str  # "info", "warning", "error"
    message: str
    topic_id: TopicID | None
    start_char: int | None
    end_char: int | None


def run_audit(
    nodes: dict[str, TopicNode],
    reference_issues: list[ReferenceIssue],
    entities: list[Entity],
) -> list[AuditIssue]:
    """
    Run the ambiguity and consistency audit.

    Aggregates synthetic topic nodes, reference issues (missing/synthetic
    targets), undefined entities, and single-mention entities into a unified
    list of AuditIssue records. This layer surfaces structural and semantic
    ambiguity; it does not fix or resolve issues.
    """
    issues: list[AuditIssue] = []

    for raw, node in nodes.items():
        if not node.synthetic:
            continue
        issues.append(
            AuditIssue(
                issue_type="missing_topic_content",
                severity="warning",
                message=f"Topic {raw} has no content (placeholder for structural gap).",
                topic_id=node.topic_id,
                start_char=None,
                end_char=None,
            )
        )

    for ref_issue in reference_issues:
        if ref_issue.issue_type == "missing_topic":
            severity = "error"
            message = f"Reference from {ref_issue.source_topic_id.raw} to missing topic {ref_issue.target_topic_id.raw}."
        elif ref_issue.issue_type == "synthetic_target":
            severity = "warning"
            message = f"Reference from {ref_issue.source_topic_id.raw} to placeholder topic {ref_issue.target_topic_id.raw} (no content)."
        else:
            severity = "warning"
            message = f"Reference issue: {ref_issue.issue_type}."
        issues.append(
            AuditIssue(
                issue_type=ref_issue.issue_type,
                severity=severity,
                message=message,
                topic_id=ref_issue.source_topic_id,
                start_char=ref_issue.start_char,
                end_char=ref_issue.end_char,
            )
        )

    for entity in entities:
        if entity.definition_text is None:
            issues.append(
                AuditIssue(
                    issue_type="undefined_entity",
                    severity="warning",
                    message=f'Entity "{entity.canonical_name}" has no explicit definition.',
                    topic_id=entity.first_seen_topic,
                    start_char=None,
                    end_char=None,
                )
            )
        if len(entity.mentions) == 1:
            issues.append(
                AuditIssue(
                    issue_type="single_mention_entity",
                    severity="info",
                    message=f'Entity "{entity.canonical_name}" appears only once.',
                    topic_id=entity.first_seen_topic,
                    start_char=None,
                    end_char=None,
                )
            )

    return issues
