"""Tests for the registry-derived Mermaid ecosystem projection."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from render_ecosystem_registry_map import (  # noqa: E402
    MermaidRenderer,
    ProjectionConfigLoader,
    ProjectionRunReport,
    ProjectionViewConfig,
    RegistryData,
    RegistryMapError,
    main as render_main,
    mermaid_id,
    render_mermaid,
)


class EcosystemRegistryMapRenderTests(unittest.TestCase):
    def test_mermaid_id_normalizes_registry_ids(self) -> None:
        self.assertEqual(mermaid_id("repo:cabinet"), "repo_cabinet")
        self.assertEqual(mermaid_id("runtime:heim-pc"), "runtime_heim_pc")
        self.assertEqual(mermaid_id("123:node"), "n_123_node")

    def test_render_mermaid_preserves_registry_boundary_and_edge_status(self) -> None:
        nodes = [
            {
                "id": "actor:alexander",
                "kind": "human",
                "label": "Alexander",
                "status": "active",
            },
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            },
            {
                "id": "artifact:ecosystem-map",
                "kind": "artifact",
                "label": "Ecosystem Map v0",
                "status": "draft",
            },
        ]
        edges = [
            {
                "from": "actor:alexander",
                "to": "repo:cabinet",
                "type": "steers",
                "status": "active",
            },
            {
                "from": "repo:cabinet",
                "to": "artifact:ecosystem-map",
                "type": "owns",
                "status": "draft",
            },
        ]
        rendered = render_mermaid(nodes, edges)
        self.assertTrue(rendered.startswith("flowchart TD\n"))
        self.assertIn("GENERATED: scripts/render_ecosystem_registry_map.py", rendered)
        self.assertIn("does not establish claim truth", rendered)
        self.assertIn("actor_alexander -->|steers / active| repo_cabinet", rendered)
        self.assertIn("repo_cabinet -->|owns / draft| artifact_ecosystem_map", rendered)

    def test_render_mermaid_rejects_edges_to_unknown_nodes(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            },
            {
                "id": "artifact:ecosystem-map",
                "kind": "artifact",
                "label": "Ecosystem Map v0",
                "status": "draft",
            },
        ]
        edges = [
            {
                "from": "repo:cabinet",
                "to": "repo:missing",
                "type": "owns",
                "status": "active",
            }
        ]
        with self.assertRaises(RegistryMapError):
            render_mermaid(nodes, edges)

    def test_check_mode_accepts_tracked_generated_projection(self) -> None:
        self.assertEqual(render_main(["--repo-root", str(ROOT), "--check"]), 0)

    def test_output_path_may_not_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / "ecosystem-registry-map.mmd"
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = render_main(
                    [
                        "--repo-root",
                        str(ROOT),
                        "--output",
                        str(outside),
                    ]
                )
            self.assertEqual(result, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("output path escapes repository", stderr.getvalue())

    def test_render_mermaid_includes_registry_ids_in_node_labels(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            },
            {
                "id": "artifact:ecosystem-map",
                "kind": "artifact",
                "label": "Ecosystem Map v0",
                "status": "draft",
            },
        ]
        rendered = render_mermaid(nodes, [])
        self.assertIn("Cabinet<br/>id: repo:cabinet<br/>repository<br/>status: active", rendered)
        self.assertIn("Ecosystem Map v0<br/>id: artifact:ecosystem-map<br/>artifact<br/>status: draft", rendered)

    def test_render_mermaid_uses_visual_anchor_not_canon_class(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            },
            {
                "id": "artifact:ecosystem-map",
                "kind": "artifact",
                "label": "Ecosystem Map v0",
                "status": "draft",
            },
        ]
        rendered = render_mermaid(nodes, [])
        self.assertIn("Visual anchor only; does not establish canonical truth.", rendered)
        self.assertIn("classDef mapAnchor", rendered)
        self.assertNotIn("classDef canon", rendered)

    def test_render_mermaid_rejects_non_object_nodes(self) -> None:
        with self.assertRaisesRegex(RegistryMapError, "node 1 must be an object"):
            render_mermaid(["repo:cabinet"], [])

    def test_render_mermaid_rejects_nodes_with_missing_required_fields(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
            }
        ]
        with self.assertRaisesRegex(RegistryMapError, "node 1 missing required string field: status"):
            render_mermaid(nodes, [])

    def test_render_mermaid_rejects_edges_with_missing_required_fields(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            }
        ]
        edges = [
            {
                "to": "repo:cabinet",
                "type": "owns",
                "status": "active",
            }
        ]
        with self.assertRaisesRegex(RegistryMapError, "edge 1 missing required string field: from"):
            render_mermaid(nodes, edges)

    def test_missing_visual_anchor_nodes_do_not_raise_key_error(self) -> None:
        nodes = [
            {
                "id": "repo:other",
                "kind": "repository",
                "label": "Other",
                "status": "active",
            }
        ]
        rendered = render_mermaid(nodes, [])
        self.assertNotIn("mapAnchor", rendered)
        self.assertIn("repo_other", rendered)

    def test_generated_comment_marks_manual_edit_boundary(self) -> None:
        nodes = [
            {
                "id": "repo:other",
                "kind": "repository",
                "label": "Other",
                "status": "active",
            }
        ]
        rendered = render_mermaid(nodes, [])
        self.assertIn("GENERATED FILE. Do not edit manually.", rendered)
        self.assertIn("Run: python3 scripts/render_ecosystem_registry_map.py", rendered)

    def test_view_config_can_reorder_and_rename_kind_groups(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            },
            {
                "id": "agent:local",
                "kind": "agent",
                "label": "Local agents",
                "status": "available",
            },
        ]
        config = ProjectionViewConfig(
            kind_order=("agent", "repository"),
            kind_titles={"agent": "Agent Surface", "repository": "Repo Surface"},
            visual_anchor_node_ids=(),
        )
        rendered = MermaidRenderer(config).render(RegistryData(nodes=nodes, edges=[]))
        self.assertLess(rendered.index("kind_agent[Agent Surface]"), rendered.index("kind_repository[Repo Surface]"))
        self.assertNotIn("mapAnchor", rendered)

    def test_projection_config_loader_reads_o_json_view_settings(self) -> None:
        config = ProjectionConfigLoader(ROOT, Path("docs/blueprints/o.json")).load()
        self.assertIn("repository", config.kind_order)
        self.assertEqual(config.title_for("agent"), "Agenten")
        self.assertIn("repo:cabinet", config.visual_anchor_node_ids)

    def test_json_report_preserves_non_truth_boundary(self) -> None:
        report = ProjectionRunReport(
            ok=True,
            mode="check",
            output="rendered/ecosystem-registry-map.mmd",
            node_count=2,
            edge_count=1,
            stale=False,
            message="ok",
        )
        text = report.to_json()
        self.assertIn('"ok": true', text)
        self.assertIn('"claim_truth"', text)
        self.assertIn('"merge_readiness"', text)

    def test_json_flag_returns_success_report(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            result = render_main(["--repo-root", str(ROOT), "--check", "--json"])
        self.assertEqual(result, 0)
        report = json.loads(stdout.getvalue())
        self.assertTrue(report["ok"])
        self.assertEqual(report["output"], "rendered/ecosystem-registry-map.mmd")
        self.assertFalse(report["stale"])
        self.assertIsNone(report["error"])

    def test_render_mermaid_rejects_non_object_edges_before_sorting(self) -> None:
        nodes = [
            {
                "id": "repo:cabinet",
                "kind": "repository",
                "label": "Cabinet",
                "status": "active",
            }
        ]
        with self.assertRaisesRegex(RegistryMapError, "edge 1 must be an object"):
            render_mermaid(nodes, ["not-an-edge"])

    def test_partial_kind_title_override_preserves_default_titles(self) -> None:
        config = ProjectionViewConfig(kind_titles={"agent": "Agent Surface"})
        self.assertEqual(config.title_for("agent"), "Agent Surface")
        self.assertEqual(config.title_for("repository"), "Repos und Organe")

    def test_json_error_report_for_malformed_ecosystem_map_v0_is_stable(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/tests") as temporary:
            config = Path(temporary) / "bad-config.json"
            config.write_text('{"ecosystem_map_v0": "bad"}', encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = render_main(
                    [
                        "--repo-root",
                        str(ROOT),
                        "--check",
                        "--json",
                        "--view-config",
                        str(config.relative_to(ROOT)),
                    ]
                )
            self.assertEqual(result, 2)
            self.assertEqual(stderr.getvalue(), "")
            report = json.loads(stdout.getvalue())
            self.assertFalse(report["ok"])
            self.assertEqual(report["output"], "rendered/ecosystem-registry-map.mmd")
            self.assertIsNone(report["node_count"])
            self.assertIsNone(report["edge_count"])
            self.assertIsNone(report["stale"])
            self.assertEqual(report["error"], "ecosystem_map_v0 must be an object")
            self.assertIn("claim_truth", report["does_not_establish"])

    def test_json_error_report_for_malformed_registry_projection_view_is_stable(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/tests") as temporary:
            config = Path(temporary) / "bad-view.json"
            config.write_text('{"ecosystem_map_v0": {"registry_projection_view": "bad"}}', encoding="utf-8")
            stdout = StringIO()
            with redirect_stdout(stdout), redirect_stderr(StringIO()):
                result = render_main(
                    [
                        "--repo-root",
                        str(ROOT),
                        "--check",
                        "--json",
                        "--view-config",
                        str(config.relative_to(ROOT)),
                    ]
                )
            self.assertEqual(result, 2)
            report = json.loads(stdout.getvalue())
            self.assertEqual(report["error"], "registry_projection_view must be an object")
            self.assertIn("merge_readiness", report["does_not_establish"])

    def test_explicit_missing_view_config_fails_closed(self) -> None:
        stdout = StringIO()
        missing = "scripts/tests/missing-view-config.json"
        with redirect_stdout(stdout), redirect_stderr(StringIO()):
            result = render_main(
                [
                    "--repo-root",
                    str(ROOT),
                    "--check",
                    "--json",
                    "--view-config",
                    missing,
                ]
            )
        self.assertEqual(result, 2)
        report = json.loads(stdout.getvalue())
        self.assertIn("view config file not found", report["error"])


if __name__ == "__main__":
    unittest.main()
