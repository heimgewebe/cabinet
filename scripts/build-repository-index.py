#!/usr/bin/env python3

import argparse
import sys
import os
import re
import subprocess
from pathlib import Path

def get_tracked_files():
    root = Path(__file__).parent.parent
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "-z", "--", "*Repository Reference.md"],
            cwd=str(root),
            stderr=subprocess.DEVNULL
        )
        return [Path(f) for f in output.decode('utf-8').split('\0') if f]
    except subprocess.CalledProcessError:
        # Fallback for tar exports / non-git environments
        files = []
        for path in root.rglob("*Repository Reference.md"):
            # Exclude files in .git or other ignored dirs if we are doing rglob
            if '.git' not in path.parts:
                files.append(path.relative_to(root))
        return files

def parse_repo_reference(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    sections = re.split(r'^## ', content, flags=re.MULTILINE)

    data = {"path": str(path)}
    ident_sec = next((sec for sec in sections if sec.startswith('Identität\n') or sec.startswith('Identität\r\n')), None)

    if ident_sec:
        lines = ident_sec.splitlines()
        for line in lines:
            if '|' in line and not line.startswith('| Feld') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) == 2:
                    k, v = parts[0], parts[1]
                    if k == 'Kanonischer Pfad':
                        name = v.split('/')[-1]
                        if v.startswith('`') and v.endswith('`'):
                            name = v[1:-1].split('/')[-1]
                        data['repo_name'] = name
                    elif k == 'Remote':
                        data['remote'] = v
                    elif k == 'Default-Branch':
                        data['default_branch'] = v

    role_sec = next((sec for sec in sections if sec.startswith('Kanonische Systemrolle\n') or sec.startswith('Kanonische Systemrolle\r\n')), None)
    if role_sec:
        lines = role_sec.splitlines()
        for line in lines:
            if line.startswith('>'):
                role = line[1:].strip()
                # remove bold markdown if present
                if role.startswith('**') and role.endswith('**'):
                    role = role[2:-2]
                # remove list item hyphen
                if role.startswith('- '):
                    role = role[2:]
                data['role'] = role
                break

    review_sec = next((sec for sec in sections if sec.startswith('Geprüfter Review-Snapshot\n') or sec.startswith('Geprüfter Review-Snapshot\r\n')), None)
    if review_sec:
        for line in review_sec.splitlines():
            if '|' in line and not line.startswith('| Feld') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) == 2:
                    if parts[0] == 'HEAD':
                        data['review_commit'] = parts[1]
                    elif parts[0] == 'Repository' and 'repo_name' not in data:
                        name = parts[1]
                        if name.startswith('`') and name.endswith('`'):
                            name = name[1:-1]
                        data['repo_name'] = name

    live_sec = next((sec for sec in sections if sec.startswith('Live-Snapshot beim Import\n') or sec.startswith('Live-Snapshot beim Import\r\n')), None)
    if live_sec:
        for line in live_sec.splitlines():
            if '|' in line and not line.startswith('| Feld') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) == 2:
                    if parts[0] == 'HEAD':
                        data['live_commit'] = parts[1]
                    elif parts[0] == 'Beziehung zum Review':
                        data['relationship'] = parts[1]
                    elif parts[0] == 'Working Tree':
                        data['working_tree'] = parts[1]

    if 'repo_name' not in data:
        print(f"Fehler: Kanonische Repositoryidentität oder expliziter Repositoryname fehlt in {path}", file=sys.stderr)
        sys.exit(1)

    return data

def generate_index(repos: list) -> str:
    lines = [
        "<!-- Generated file. Do not edit manually. -->",
        "<!-- Source: tracked Repository Reference.md files. -->",
        "# Repositories",
        "",
        "Repositorykarten mit Identität, Rolle, Quellen, Beziehungen, Commit und Frische.",
        "",
        "Bestehende Repository References werden weiterverwendet statt dupliziert.",
        "",
        "| Repository | Rolle | Review | Live | Beziehung | Working Tree | Referenz |",
        "| ---------- | ----- | ------ | ---- | --------- | ------------ | -------- |"
    ]

    # Sort repos deterministically
    repos.sort(key=lambda x: x['repo_name'].lower())

    for r in repos:
        repo = r.get('repo_name', 'unbekannt')
        role = r.get('role', 'unbekannt')
        # Limit role length for table if too long
        if len(role) > 50:
            role = role[:47] + '...'

        review = r.get('review_commit', 'unbekannt')
        if review != 'unbekannt' and review.startswith('`') and review.endswith('`'):
            review = review[1:-1]
        if review != 'unbekannt':
            review = f"`{review[:7]}`"

        live = r.get('live_commit', 'unbekannt')
        if live != 'unbekannt' and live.startswith('`') and live.endswith('`'):
            live = live[1:-1]
        if live != 'unbekannt':
            live = f"`{live[:7]}`"

        rel = r.get('relationship', 'unbekannt')
        wt = r.get('working_tree', 'unbekannt')

        path = r['path']

        lines.append(f"| **{repo}** | {role} | {review} | {live} | {rel} | {wt} | [{path}](../../{path}) |")

    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    files = get_tracked_files()
    repos = []
    names = set()
    warnings = 0

    for f in files:
        data = parse_repo_reference(f)
        repo_name = data.get('repo_name')

        if not repo_name:
            print(f"Fehler: Repositoryname fehlt in {f}", file=sys.stderr)
            sys.exit(1)

        if repo_name in names:
            print(f"Fehler: Doppelte kanonische Repositoryidentität '{repo_name}' in {f}", file=sys.stderr)
            sys.exit(1)

        names.add(repo_name)

        # Check warnings
        if 'role' not in data:
            print(f"Warnung: Fehlende Rolle in {f}", file=sys.stderr)
            warnings += 1
        if 'working_tree' not in data:
            print(f"Warnung: Fehlender Working-Tree-Zustand in {f}", file=sys.stderr)
            warnings += 1

        repos.append(data)

    index_content = generate_index(repos)
    target_file = Path("bestand/10 Repositories/index.md")

    if args.check:
        if not target_file.exists():
            print("Fehler: index.md existiert nicht", file=sys.stderr)
            sys.exit(1)

        existing_content = target_file.read_text(encoding="utf-8")
        if existing_content != index_content:
            import difflib
            diff = difflib.unified_diff(
                existing_content.splitlines(keepends=True),
                index_content.splitlines(keepends=True),
                fromfile='bestand/10 Repositories/index.md (current)',
                tofile='bestand/10 Repositories/index.md (expected)'
            )
            print("".join(diff), file=sys.stderr)
            print("Fehler: index.md ist nicht aktuell", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Erfolg: index.md ist aktuell ({len(repos)} Repositories, {warnings} Warnungen)")
            sys.exit(0)
    else:
        # standard mode
        if target_file.exists():
            existing_content = target_file.read_text(encoding="utf-8")
            if existing_content == index_content:
                print(f"Keine Änderung notwendig ({len(repos)} Repositories, {warnings} Warnungen)")
                sys.exit(0)

        # atomic write
        temp_file = target_file.with_suffix('.tmp')
        temp_file.write_text(index_content, encoding="utf-8")
        temp_file.replace(target_file)
        print(f"Erfolg: index.md generiert ({len(repos)} Repositories, {warnings} Warnungen)")

if __name__ == '__main__':
    main()
