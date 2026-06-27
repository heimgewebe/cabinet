#!/usr/bin/env python3
"""Validate the first explicitly approved repository against its tracked Reference."""

from __future__ import annotations

import argparse
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import repository_inventory

APPROVED_REPOSITORY = "infra"
MARKER = Path("policy/approved-repositories/infra")


class ApprovalError(RuntimeError):
    """Raised when the canary approval cannot be trusted."""


@dataclass(frozen=True)
class ApprovedRepository:
    repository: str
    origin: str
    reference: str


def _marker_bytes(repo_root: Path) -> bytes:
    repo_root = Path(os.path.abspath(repo_root.expanduser()))
    marker = repo_root / MARKER
    try:
        metadata = os.lstat(marker)
    except FileNotFoundError as exc:
        raise ApprovalError(f"approval marker is missing: {MARKER}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ApprovalError("approval marker must be a regular file, not a symlink")

    try:
        raw = repository_inventory._run_git(
            repo_root,
            "ls-files",
            "-s",
            "-z",
            "--error-unmatch",
            "--",
            f":(literal){MARKER.as_posix()}",
        )
    except repository_inventory.InventoryError as exc:
        raise ApprovalError(str(exc)) from exc
    entries = [entry for entry in raw.split(b"\0") if entry]
    if len(entries) != 1:
        raise ApprovalError("approval marker must have exactly one Git index entry")
    try:
        index_metadata, encoded_path = entries[0].split(b"\t", 1)
        mode, object_id, stage = index_metadata.split(b" ", 2)
        indexed_path = encoded_path.decode("utf-8")
        object_id_text = object_id.decode("ascii")
    except (UnicodeDecodeError, ValueError) as exc:
        raise ApprovalError("approval marker has malformed Git index metadata") from exc
    if indexed_path != MARKER.as_posix() or mode != b"100644" or stage != b"0":
        raise ApprovalError("approval marker must be a regular stage-0 Git file")

    working = marker.read_bytes()
    indexed = repository_inventory.read_index_blob(repo_root, object_id_text)
    if working != indexed:
        raise ApprovalError("approval marker differs from the Git index")
    if working:
        raise ApprovalError("approval marker must be empty")
    return working


def validate_canary(repo_root: Path) -> ApprovedRepository:
    repo_root = Path(os.path.abspath(repo_root.expanduser()))
    _marker_bytes(repo_root)
    try:
        records, _warnings = repository_inventory.load_records(
            repo_root,
            verify_index_match=True,
        )
    except repository_inventory.InventoryError as exc:
        raise ApprovalError(str(exc)) from exc
    matches = [record for record in records if record.repository == APPROVED_REPOSITORY]
    if len(matches) != 1:
        raise ApprovalError(
            f"approval marker must resolve to exactly one {APPROVED_REPOSITORY!r} Reference"
        )
    record = matches[0]
    return ApprovedRepository(
        repository=record.repository,
        origin=record.origin,
        reference=record.source_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        approved = validate_canary(args.repo_root)
    except (ApprovalError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("APPROVED-REPOSITORY-CANARY: PASS")
    print(f"Repository: {approved.repository}")
    print(f"Reference: {approved.reference}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
