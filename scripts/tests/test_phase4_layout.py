from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class PhaseFourLayoutTests(unittest.TestCase):
    def test_default_is_steuerung(self) -> None:
        policy = json.loads(
            (REPO_ROOT / "policy/cabinet-layout.json").read_text(encoding="utf-8")
        )
        home = json.loads(
            (REPO_ROOT / ".home/home.json").read_text(encoding="utf-8")
        )
        self.assertEqual(policy["defaultRoom"], "steuerung")
        self.assertEqual(home["defaultRoom"], "steuerung")
        self.assertEqual(home["lastActiveRoom"], "steuerung")

    def test_vorzimmer_remains_available(self) -> None:
        policy = json.loads(
            (REPO_ROOT / "policy/cabinet-layout.json").read_text(encoding="utf-8")
        )
        self.assertIn("vorzimmer", policy["rooms"])
        self.assertTrue((REPO_ROOT / "vorzimmer/.cabinet").is_file())


if __name__ == "__main__":
    unittest.main()
