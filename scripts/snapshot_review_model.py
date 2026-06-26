from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SnapshotAssessment:
    repository: str
    relationship_class: str
    worktree_class: str
    evidence_class: str
    priority: int
    reason_code: str
    review_head: str
    import_head: str
    relationship: str
    import_worktree: str
    imported_at: str
    source_path: str


def relationship_kind(record: Any) -> tuple[str, str]:
    normalized = record.relationship.casefold()
    if record.review_head == record.import_head:
        return "snapshot-identical", "direct-head-equality"
    if any(word in normalized for word in ("divergent", "rewritten", "amended")):
        return "snapshot-divergence-claimed", "reference-claim"
    if "enthält" in normalized or "contains" in normalized:
        return "snapshot-review-contained", "reference-claim"
    return "snapshot-relationship-claimed", "reference-claim"
