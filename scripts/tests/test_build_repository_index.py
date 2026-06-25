#!/usr/bin/env python3

import unittest
import tempfile
from pathlib import Path
import os
import sys

# Add scripts directory to path to import build_repository_index
sys.path.insert(0, str(Path(__file__).parent.parent))
import importlib
build_repository_index = importlib.import_module('build-repository-index')

class TestBuildRepositoryIndex(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_parse_valid_reference(self):
        content = """# Vibe-Lab — Repository Reference

## Geprüfter Review-Snapshot

| Feld | Wert |
|---|---|
| Repository | `vibe-lab` |
| HEAD | `869abfb` |

## Live-Snapshot beim Import

| Feld | Wert |
|---|---|
| HEAD | `869abfb` |
| Beziehung zum Review | **identisch** |
| Working Tree | `clean:0` |

## Identität

| Feld | Wert |
|---|---|
| Kanonischer Pfad | `/home/alex/repos/vibe-lab` |
| Remote | `github.com:heimgewebe/vibe-lab.git` |
| Default-Branch | `main` |

## Kanonische Systemrolle

> **Exekutierbarer Erkenntnisraum für Vibe-Coding-Praktiken.**
"""
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f:
            f.write(content)
            f.close()
            try:
                data = build_repository_index.parse_repo_reference(Path(f.name))
                self.assertEqual(data['repo_name'], 'vibe-lab')
                self.assertEqual(data['review_commit'], '`869abfb`')
                self.assertEqual(data['live_commit'], '`869abfb`')
                self.assertEqual(data['relationship'], '**identisch**')
                self.assertEqual(data['working_tree'], '`clean:0`')
                self.assertEqual(data['role'], 'Exekutierbarer Erkenntnisraum für Vibe-Coding-Praktiken.')
                self.assertEqual(data['remote'], '`github.com:heimgewebe/vibe-lab.git`')
                self.assertEqual(data['default_branch'], '`main`')
            finally:
                os.remove(f.name)

    def test_generate_index_deterministic(self):
        repos = [
            {'repo_name': 'b', 'path': 'path/b', 'role': 'Role B', 'review_commit': '`2`', 'live_commit': '`2`', 'relationship': 'rel', 'working_tree': 'wt'},
            {'repo_name': 'a', 'path': 'path/a', 'role': 'Role A', 'review_commit': '`1`', 'live_commit': '`1`', 'relationship': 'rel', 'working_tree': 'wt'},
            {'repo_name': 'c', 'path': 'path/c', 'role': 'Role C', 'review_commit': '`3`', 'live_commit': '`3`', 'relationship': 'rel', 'working_tree': 'wt'}
        ]

        index1 = build_repository_index.generate_index(repos.copy())
        index2 = build_repository_index.generate_index(repos.copy())

        self.assertEqual(index1, index2)

        # Check sorting
        lines = index1.splitlines()
        table_lines = [l for l in lines if l.startswith('| **')]
        self.assertEqual(len(table_lines), 3)
        self.assertIn('**a**', table_lines[0])
        self.assertIn('**b**', table_lines[1])
        self.assertIn('**c**', table_lines[2])

    def test_missing_mandatory_field(self):
        content = """# Invalid
## Identität
| Feld | Wert |
|---|---|
"""
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f:
            f.write(content)
            f.close()
            try:
                # Need to mock sys.stderr or capture it to prevent test pollution
                import io
                stderr = sys.stderr
                sys.stderr = io.StringIO()
                try:
                    with self.assertRaises(SystemExit):
                        build_repository_index.parse_repo_reference(Path(f.name))
                finally:
                    sys.stderr = stderr
            finally:
                os.remove(f.name)


    def test_unicode_and_spaces(self):
        content = """# Unicode ÄÖÜ — Repository Reference
## Identität
| Feld | Wert |
|---|---|
| Kanonischer Pfad | `/home/alex/repos/unicode äöü` |
| Remote | `github.com:heimgewebe/unicode äöü.git` |
| Default-Branch | `main` |
"""
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False, prefix="space test ") as f:
            f.write(content)
            f.close()
            try:
                data = build_repository_index.parse_repo_reference(Path(f.name))
                self.assertEqual(data['repo_name'], 'unicode äöü')
            finally:
                os.remove(f.name)

    def test_missing_optional_field(self):
        content = """# Optional Test
## Identität
| Feld | Wert |
|---|---|
| Kanonischer Pfad | `/home/alex/repos/test` |
"""
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as f:
            f.write(content)
            f.close()
            try:
                data = build_repository_index.parse_repo_reference(Path(f.name))
                self.assertEqual(data['repo_name'], 'test')
                self.assertNotIn('role', data)
            finally:
                os.remove(f.name)

if __name__ == '__main__':
    unittest.main()
