#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL_REPO="$(cd "$SCRIPT_DIR/../.." && pwd)"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "Copying repository to temp directory..."
cp -r "$REAL_REPO"/. "$TEMP_DIR/"
cd "$TEMP_DIR"
git config user.email "test@example.com"
git config user.name "Test User"

# Ensure we have a clean git state in the temp repo
git add -A
git commit -m "temp test commit" --allow-empty >/dev/null

echo "=== Test 1: Sauberer Tree besteht ==="
if ! ./scripts/ci/validate-repository.sh >/dev/null; then
    echo "FAIL: Clean tree failed validation."
    exit 1
fi
echo "PASS"

echo "=== Test 2: Versionierte .agents/.runtime/daemon-token wird erkannt ==="
mkdir -p .agents/.runtime
echo "token" > .agents/.runtime/daemon-token
git add -f .agents/.runtime/daemon-token
git commit -m "add bad file" >/dev/null
if ./scripts/ci/validate-repository.sh >/dev/null 2>&1; then
    echo "FAIL: Did not catch forbidden versioned file."
    exit 1
fi
git reset --hard HEAD~1 >/dev/null
echo "PASS"

echo "=== Test 3: Ungültiges ops/manifest.json wird erkannt ==="
sed -i 's/"cabinet.local-runtime.v1"/"cabinet.wrong"/g' ops/manifest.json
git commit -am "break manifest" >/dev/null
if ./scripts/ci/validate-repository.sh >/dev/null 2>&1; then
    echo "FAIL: Did not catch invalid manifest schema."
    exit 1
fi
git reset --hard HEAD~1 >/dev/null
echo "PASS"

echo "=== Test 4: Ausführbares ops/bin-Artefakt mit Git-Modus 100644 wird erkannt ==="
git update-index --chmod=-x ops/bin/cabinet
git commit -m "break executable permission" >/dev/null
if ./scripts/ci/validate-repository.sh >/dev/null 2>&1; then
    echo "FAIL: Did not catch bad git mode 100644 for executable."
    exit 1
fi
git reset --hard HEAD~1 >/dev/null
echo "PASS"

echo "=== Test 5: --mode repository besteht ohne lokale .agents/.config und .global-agents ==="
rm -rf .agents/.config .global-agents
# These are unversioned, so removing them doesn't affect git.
# Wait, the current temp repo has them because `cp -r` copied them over.
if ! python3 scripts/check-cabinet-layout.py --mode repository "$TEMP_DIR" >/dev/null; then
    echo "FAIL: --mode repository failed without local files."
    exit 1
fi
echo "PASS"

echo "=== Test 6: --mode local verlangt lokale Dateien ==="
if python3 scripts/check-cabinet-layout.py --mode local "$TEMP_DIR" >/dev/null 2>&1; then
    echo "FAIL: --mode local succeeded despite missing local files."
    exit 1
fi
echo "PASS"

echo "TARGET-PROOF: CABINET REPOSITORY VALIDATOR TESTS PASS"
