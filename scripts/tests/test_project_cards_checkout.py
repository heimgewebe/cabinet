from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve().parents[1] / "check-project-card-provenance.py"
SPEC = importlib.util.spec_from_file_location("project_cards_checkout", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load provenance validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ProjectCardsCheckoutTest(unittest.TestCase):
    def test_inputs_are_index_identical(self) -> None:
        paths = MODULE.verify_provenance(ROOT)
        self.assertIn(Path("bestand/20 Projekte/index.md"), paths)
        self.assertIn(Path("weltgewebe/Repository Reference.md"), paths)


if __name__ == "__main__":
    unittest.main()
