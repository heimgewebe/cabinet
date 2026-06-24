#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "=== Git-Whitespace ==="
EMPTY_TREE="$(git hash-object -t tree /dev/null)"
git diff --check "$EMPTY_TREE" HEAD
echo "Git-Whitespace: PASS"

echo "=== JSON ==="
git ls-files -z '*.json' | while IFS= read -r -d '' f; do
    python3 -m json.tool "$f" >/dev/null
done
echo "JSON: PASS"

echo "=== Python ==="
git ls-files -z '*.py' | while IFS= read -r -d '' f; do
    python3 -c 'import sys; compile(open(sys.argv[1], encoding="utf-8").read(), sys.argv[1], "exec")' "$f"
done
echo "Python: PASS"

echo "=== Bash ==="
# Find all versioned files, check if they have a bash shebang, then run bash -n
git ls-files -z | while IFS= read -r -d '' f; do
    if [[ -f "$f" ]]; then
        # Check if the first line is a bash shebang
        line=$(head -n 1 "$f" 2>/dev/null || true)
        if [[ "$line" =~ ^#!(.*)bash ]]; then
            bash -n "$f"
        fi
    fi
done

# Ensure specific paths are bash syntax checked
for f in ops/bin/* ops/install/*.sh scripts/cabinet-safe-export.sh scripts/ci/*.sh; do
    if [[ -f "$f" ]] && git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
        bash -n "$f"
    fi
done
echo "Bash: PASS"

echo "=== Layout ==="
python3 scripts/check-cabinet-layout.py --mode repository "$REPO_ROOT"

echo "=== Runtime-Manifest ==="
python3 - <<'EOF'
import json
import sys
import os
import subprocess
from pathlib import Path

repo_root = Path(os.environ["REPO_ROOT"])
manifest_path = repo_root / "ops/manifest.json"

with open(manifest_path, encoding="utf-8") as f:
    manifest = json.load(f)

if manifest.get("schema") != "cabinet.local-runtime.v1":
    sys.exit(f"Invalid schema: {manifest.get('schema')}")

if manifest.get("cabinet_version") != "0.4.4":
    sys.exit(f"Invalid cabinet_version: {manifest.get('cabinet_version')}")

# Get git stages for files
try:
    git_stage_output = subprocess.check_output(["git", "ls-files", "--stage"], text=True)
except subprocess.CalledProcessError as e:
    sys.exit(f"Failed to get git index: {e}")

git_modes = {}
for line in git_stage_output.splitlines():
    if not line:
        continue
    parts = line.split(maxsplit=3)
    if len(parts) >= 4:
        mode = parts[0]
        path = parts[3]
        git_modes[path] = mode

for tmpl in manifest.get("templates", []):
    src = tmpl.get("source")
    if not src or ".." in src or src.startswith("/"):
        sys.exit(f"Invalid source path: {src}")
    if not (repo_root / src).is_file():
        sys.exit(f"Source file missing: {src}")
    if git_modes.get(src) != "100644":
        sys.exit(f"Invalid git mode for template {src}: {git_modes.get(src)} (expected 100644)")

for exe in manifest.get("executables", []):
    src = exe.get("source")
    if not src or ".." in src or src.startswith("/"):
        sys.exit(f"Invalid source path: {src}")
    if not (repo_root / src).is_file():
        sys.exit(f"Source file missing: {src}")
    if git_modes.get(src) != "100755":
        sys.exit(f"Invalid git mode for executable {src}: {git_modes.get(src)} (expected 100755)")

for link in manifest.get("symlinks", []):
    src = link.get("source")
    if not src or ".." in src or src.startswith("/"):
        sys.exit(f"Invalid source path: {src}")
    if not (repo_root / src).exists():
        sys.exit(f"Source file/dir missing: {src}")

local_only = manifest.get("local_only", [])
expected_local = [
    "~/.config/cabinet/runtime.env",
    "~/.local/state/cabinet/",
    "~/.cabinet/",
    ".cabinet-state/"
]
for e in expected_local:
    if e not in local_only:
        sys.exit(f"Expected path missing from local_only: {e}")

# check for no embedded secrets or absolute paths
all_items = manifest.get("templates", []) + manifest.get("executables", []) + manifest.get("symlinks", [])
for item in all_items:
    target = item.get("target")
    if target and target.startswith("/"):
        sys.exit(f"Absolute target path not allowed: {target}")

print("Runtime-Manifest: PASS")
EOF

echo "=== Verbotene versionierte Laufzeitpfade ==="
python3 - <<'EOF'
import sys
import os
import fnmatch
import subprocess

forbidden_patterns = [
    ".cabinet.db",
    ".cabinet.db-*",
    "**/.cabinet.db",
    "**/.cabinet.db-*",
    ".cabinet-state/*",
    "**/.cabinet-state/*",
    ".agents/.runtime/*",
    "**/.agents/.runtime/*",
    ".agents/.config/*",
    "**/.agents/.config/*",
    ".global-agents/*",
    ".env",
    ".env.*",
    ".cabinet.env",
    "*.pem",
    "*.key"
]

try:
    files_output = subprocess.check_output(["git", "ls-files", "-z"], text=True)
except subprocess.CalledProcessError as e:
    sys.exit(f"Failed to run git ls-files: {e}")

files = [f for f in files_output.split("\0") if f]
errors = []

for f in files:
    if f == "ops/env/runtime.env.example":
        continue

    for pattern in forbidden_patterns:
        # adjust path matching
        if fnmatch.fnmatch(f, pattern) or fnmatch.fnmatch(f, pattern.replace("/*", "")) or ("/" not in pattern and fnmatch.fnmatch(os.path.basename(f), pattern)):
            errors.append(f)
            break

if errors:
    print("Forbidden versioned paths found:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
EOF
echo "Verbotene Pfade: PASS"

echo "TARGET-PROOF: CABINET REPOSITORY CONTRACT VALID"
