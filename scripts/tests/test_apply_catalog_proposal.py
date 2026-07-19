import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from apply_catalog_proposal import apply_proposal

class TestApplyCatalogProposal(unittest.TestCase):
    def test_apply_proposal_updates_bindings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry_dir = root / "registry/ecosystem"
            registry_dir.mkdir(parents=True)
            
            bindings_path = registry_dir / "source-bindings.v1.json"
            initial_bindings = {
                "systems": [
                    {
                        "system": "repo:test",
                        "source": {
                            "commit": "oldcommit",
                            "locator": {
                                "kind": "file",
                                "path": "README.md",
                                "contentSha256": "oldsha"
                            }
                        },
                        "reviewedAt": "2026-07-01T00:00:00Z"
                    }
                ]
            }
            bindings_path.write_text(json.dumps(initial_bindings), encoding="utf-8")
            
            report_path = root / "report.json"
            report_content = {
                "kind": "system_catalog_drift_report",
                "changes": [
                    {
                        "kind": "primary_source_changed",
                        "system": "repo:test",
                        "locatorKind": "file",
                        "path": "README.md",
                        "observedCommit": "newcommit",
                        "observedSha256": "newsha"
                    }
                ]
            }
            report_path.write_text(json.dumps(report_content), encoding="utf-8")
            
            result = apply_proposal(root, report_path)
            self.assertEqual(result, 0)
            
            updated_bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
            system = updated_bindings["systems"][0]
            self.assertEqual(system["source"]["commit"], "newcommit")
            self.assertEqual(system["source"]["locator"]["contentSha256"], "newsha")
            self.assertNotEqual(system["reviewedAt"], "2026-07-01T00:00:00Z")

if __name__ == "__main__":
    unittest.main()
