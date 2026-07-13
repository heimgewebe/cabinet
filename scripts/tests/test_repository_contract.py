from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/ci/check-repository-contract.py"
SPEC = importlib.util.spec_from_file_location("systemkatalog_repository_contract", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RepositoryContractTests(unittest.TestCase):
    def test_generic_secret_and_temp_patterns_remain_allowed(self) -> None:
        MODULE.check_gitignore_text(".env\n.env.*\n*.pem\n*.log\n")

    def test_cabinet_runtime_patterns_may_not_be_hidden(self) -> None:
        with self.assertRaisesRegex(SystemExit, "must remain visible"):
            MODULE.check_gitignore_text(".cabinet.db\n.cabinet-state/\n")

    def test_agent_runtime_patterns_may_not_be_hidden(self) -> None:
        with self.assertRaisesRegex(SystemExit, "must remain visible"):
            MODULE.check_gitignore_text("**/.agents/.runtime/\n.global-agents/\n")


if __name__ == "__main__":
    unittest.main()
