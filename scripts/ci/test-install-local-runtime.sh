#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TEMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TEMP_HOME"' EXIT

export HOME="$TEMP_HOME"

echo "=== Setting up künstliches HOME ==="
APP_ROOT="$HOME/.cabinet/app/v0.4.4"
mkdir -p "$APP_ROOT"

# Mock package.json
cat > "$APP_ROOT/package.json" <<'EOF'
{
  "version": "0.4.4"
}
EOF

# Mock src/lib/themes.ts
mkdir -p "$APP_ROOT/src/lib"
cat > "$APP_ROOT/src/lib/themes.ts" <<'EOF'
export const themes = [
  { name: "black", type: "dark" }
];
EOF

# Mock patch targets
mkdir -p "$APP_ROOT/src/app"
cat > "$APP_ROOT/src/app/layout.tsx" <<'EOF'
defaultTheme="light"
EOF

mkdir -p "$APP_ROOT/src/components/layout"
cat > "$APP_ROOT/src/components/layout/theme-initializer.tsx" <<'EOF'
const themeName = stored || "paper";
EOF

cat > "$APP_ROOT/src/components/layout/room-theme-sync.tsx" <<'EOF'
room?.theme || getStoredThemeName() || "paper";
EOF

# Mock runtime.env
mkdir -p "$HOME/.config/cabinet"
echo "SECRET=1" > "$HOME/.config/cabinet/runtime.env"
chmod 0600 "$HOME/.config/cabinet/runtime.env"

# Mock systemctl in PATH
mkdir -p "$HOME/bin"
cat > "$HOME/bin/systemctl" <<'EOF'
#!/usr/bin/env bash
if [[ "$1" == "--user" && "$2" == "daemon-reload" && -z "${3:-}" ]]; then
    exit 0
fi
echo "systemctl stub called with invalid args: $*" >&2
exit 1
EOF
chmod +x "$HOME/bin/systemctl"
export PATH="$HOME/bin:$PATH"

echo "=== First Install Run ==="
"$REPO_ROOT/ops/install/install-local-runtime.sh"

echo "=== Capturing Managed State ==="
# Capture managed files (excluding append-only backup directories)
# ~/.local/bin/
# ~/.config/systemd/user/
find "$HOME/.local/bin" "$HOME/.config/systemd/user" -type f -o -type l | sort | xargs sha256sum > "$HOME/state1.txt"
# Also capture the dark patch files
find "$APP_ROOT/src" -type f | sort | xargs sha256sum >> "$HOME/state1.txt"

echo "=== Second Install Run (Idempotence) ==="
"$REPO_ROOT/ops/install/install-local-runtime.sh" | tee "$HOME/install2.log"

if ! grep -q "PASS  bereits gepatcht: src/app/layout.tsx" "$HOME/install2.log"; then
    echo "FAIL: Patch 1 not recognized as already patched."
    exit 1
fi
if ! grep -q "PASS  bereits gepatcht: src/components/layout/theme-initializer.tsx" "$HOME/install2.log"; then
    echo "FAIL: Patch 2 not recognized as already patched."
    exit 1
fi
if ! grep -q "PASS  bereits gepatcht: src/components/layout/room-theme-sync.tsx" "$HOME/install2.log"; then
    echo "FAIL: Patch 3 not recognized as already patched."
    exit 1
fi

echo "=== Comparing Managed State ==="
find "$HOME/.local/bin" "$HOME/.config/systemd/user" -type f -o -type l | sort | xargs sha256sum > "$HOME/state2.txt"
find "$APP_ROOT/src" -type f | sort | xargs sha256sum >> "$HOME/state2.txt"

if ! diff -u "$HOME/state1.txt" "$HOME/state2.txt"; then
    echo "FAIL: State divergence between run 1 and 2."
    exit 1
fi

# Ensure runtime.env was untouched
if [[ "$(stat -c "%a" "$HOME/.config/cabinet/runtime.env")" != "600" ]]; then
    echo "FAIL: runtime.env mode changed."
    exit 1
fi
if [[ "$(cat "$HOME/.config/cabinet/runtime.env")" != "SECRET=1" ]]; then
    echo "FAIL: runtime.env content changed."
    exit 1
fi

echo "TARGET-PROOF: CABINET INSTALLER SHADOW TEST PASS"
echo "TARGET-PROOF: SECOND INSTALL IS IDEMPOTENT"
