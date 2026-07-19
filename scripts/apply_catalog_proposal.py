#!/usr/bin/env python3
"""Apply source binding updates from a drift report proposal."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def apply_proposal(root: Path, report_path: Path) -> int:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    
    if report.get("kind") != "system_catalog_drift_report":
        print("Invalid drift report: incorrect kind")
        return 1

    bindings_path = root / "registry/ecosystem/source-bindings.v1.json"
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))

    systems_by_name = {b["system"]: b for b in bindings["systems"]}
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    updated_count = 0
    for change in report.get("changes", []):
        if change["kind"] == "primary_source_changed":
            system = change["system"]
            if system in systems_by_name:
                b = systems_by_name[system]
                if b["source"]["locator"]["kind"] == change["locatorKind"] and b["source"]["locator"].get("path") == change.get("path"):
                    b["source"]["commit"] = change["observedCommit"]
                    b["source"]["locator"]["contentSha256"] = change["observedSha256"]
                    b["reviewedAt"] = now
                    updated_count += 1
                else:
                    print(f"Locator mismatch for {system}, skipping.")

    if updated_count > 0:
        encoded = json.dumps(bindings, indent=2) + "\n"
        bindings_path.write_text(encoded, encoding="utf-8")
        print(f"Successfully applied {updated_count} source binding updates.")
    else:
        print("No source binding updates applied.")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    return apply_proposal(args.root, args.report)

if __name__ == "__main__":
    sys.exit(main())
