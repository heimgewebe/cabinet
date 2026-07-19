from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "repo:systemkatalog": {
        "repository": "heimgewebe/systemkatalog",
        "commit": "3cecde159552a7e0eff94fca94add0051017d9cc",
        "sha256": "26adf42dc6a00347ad3ae38878fe35ba20b2cbef6601d4ba08caffb7916f7175",
        "path": "README.md",
    },
    "repo:bureau": {
        "repository": "heimgewebe/bureau",
        "commit": "1fca33a9945cb25dac9eb5ef0d5b29619eb6d2a7",
        "sha256": "94b9241d6ebb0a8c0ff9b308965967825dcd5fbad285354a546ad705fa912b6d",
        "path": "README.md",
    },
    "repo:weltgewebe": {
        "repository": "heimgewebe/weltgewebe",
        "commit": "b5a9383fc36b381bf5a68fd2e9a287d13f2caa82",
        "sha256": "4ada1c4578942f620098c7b7317b040200e720c69625bf2f57cafabebe59ae33",
        "path": "README.md",
    },
    "repo:repoground": {
        "repository": "heimgewebe/repoground",
        "commit": "04f346dfcbff4513344709b4204ff9d820a91d48",
        "sha256": "de79925b48f536bf88aa1d5f6bf678a1a6461027d0a42f89d99d35c987d0f6bf",
        "path": "README.md",
    },
    "repo:semantAH": {
        "repository": "heimgewebe/semantAH",
        "commit": "d53000a909946a0381a8b365c4af7abd2456e8f6",
        "sha256": "c982af6c37a5fb316403724f7ce74ad7111e8f6b98f79d8dedadc49af55a4a2e",
        "path": "README.md",
    },
    "repo:sichter": {
        "repository": "heimgewebe/sichter",
        "commit": "f4359f0817d7db6b3f821bcdce7be12c18e561cc",
        "sha256": "4c2e3f51ef816373968b8857023446a0f7422615d22a9090cd7eeb608446f260",
        "path": "README.md",
    },
    "repo:heim-pc": {
        "repository": "heimgewebe/heim-pc",
        "commit": "686fc485f1af971ce336486ef5b10037284e626a",
        "sha256": "9e1bbe5060a3c6aa47155ac2299fc3dbc25d7aabac3ba6e498cd8667e4ca2eb6",
        "path": "manifest/operator-entry.v1.json",
    },
    "repo:commonworld": {
        "repository": "heimgewebe/commonworld",
        "commit": "3b33b4a566ab4cd5487a8a99e3f99b211347a6bc",
        "sha256": "90f94b50c7ed43bbd225e1ef52e3449858063d154f16741389f8f20f8db46880",
        "path": "README.md",
    },
}


class SourceBindingDriftCloseoutTests(unittest.TestCase):
    def test_reviewed_primary_sources_are_commit_and_content_bound(self) -> None:
        document = json.loads(
            (ROOT / "registry/ecosystem/source-bindings.v1.json").read_text(
                encoding="utf-8"
            )
        )
        systems = {item["system"]: item for item in document["systems"]}

        for system, expected in EXPECTED.items():
            with self.subTest(system=system):
                binding = systems[system]
                source = binding["source"]
                self.assertEqual(source["repository"], expected["repository"])
                self.assertEqual(source["commit"], expected["commit"])
                self.assertEqual(source["defaultBranch"], "main")
                self.assertEqual(source["locator"]["kind"], "file")
                self.assertEqual(source["locator"]["path"], expected["path"])
                self.assertEqual(
                    source["locator"]["contentSha256"], expected["sha256"]
                )
                self.assertIsInstance(binding["reviewedAt"], str)


if __name__ == "__main__":
    unittest.main()
