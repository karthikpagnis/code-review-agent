"""
Aggregator agent.
Merges findings from all three analysis agents, deduplicates overlapping
issues, applies severity ordering, and builds the final ReviewReport.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from collections import Counter

from app.schemas.models import Finding, ReviewReport


_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _deduplicate(findings: list[dict]) -> list[dict]:
    """
    Remove near-duplicate findings by checking if two findings share
    the same (category, type, line_hint) triple.  Keep the one with
    higher severity when duplicates exist.
    """
    seen: dict[tuple, dict] = {}
    for f in findings:
        key = (f["category"], f["type"].lower(), f["line_hint"][:60].lower())
        if key not in seen:
            seen[key] = f
        else:
            # Keep whichever has higher severity
            if _SEVERITY_RANK[f["severity"]] < _SEVERITY_RANK[seen[key]["severity"]]:
                seen[key] = f
    return list(seen.values())


def _tag_category(issues: list[dict], category: str) -> list[dict]:
    """Attach the source category to each issue dict."""
    for i in issues:
        i["category"] = category
    return issues


def build_report(
    security_issues: list[dict],
    logic_issues: list[dict],
    quality_issues: list[dict],
    repo_url: str | None,
    language: str,
    chunks_analysed: int,
) -> ReviewReport:
    """
    Combine findings from all three agents into a single deduplicated,
    severity-sorted ReviewReport.
    """
    tagged: list[dict] = (
        _tag_category(security_issues, "security")
        + _tag_category(logic_issues,  "logic")
        + _tag_category(quality_issues, "quality")
    )

    deduped = _deduplicate(tagged)
    deduped.sort(key=lambda f: _SEVERITY_RANK[f["severity"]])

    counts = Counter(f["severity"] for f in deduped)

    findings = [Finding(**f) for f in deduped]

    return ReviewReport(
        review_id=str(uuid.uuid4()),
        repo_url=repo_url,
        language=language,
        files_analysed=1,
        chunks_analysed=chunks_analysed,
        total_issues=len(findings),
        high_count=counts.get("high", 0),
        medium_count=counts.get("medium", 0),
        low_count=counts.get("low", 0),
        findings=findings,
        blob_url=None,          # filled in by the router after Blob upload
        reviewed_at=datetime.now(timezone.utc),
    )
