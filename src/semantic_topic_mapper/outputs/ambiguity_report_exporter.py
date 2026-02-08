"""
Ambiguity report exporter: serialize audit issues to CSV.

Maps internal AuditIssue list to the assignment deliverable format (issue_type,
severity, message, topic_id, start_char, end_char). Thin serializer only;
no LLM or inference.
"""

from __future__ import annotations

import csv

from semantic_topic_mapper.audit.ambiguity_detector import AuditIssue


def export_ambiguity_report(issues: list[AuditIssue], path: str) -> None:
    """
    Write a CSV file with columns: issue_type, severity, message, topic_id,
    start_char, end_char. Optional fields are written as empty string when None.
    """
    columns = [
        "issue_type",
        "severity",
        "message",
        "topic_id",
        "start_char",
        "end_char",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for i in issues:
            w.writerow({
                "issue_type": i.issue_type,
                "severity": i.severity,
                "message": i.message,
                "topic_id": i.topic_id.raw if i.topic_id else "",
                "start_char": i.start_char if i.start_char is not None else "",
                "end_char": i.end_char if i.end_char is not None else "",
            })
