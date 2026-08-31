from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_skill_frontmatter(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        parts = text.split("---", 2)
        self.assertGreaterEqual(len(parts), 3)
        meta = yaml.safe_load(parts[1])
        self.assertEqual(meta["name"], "functional-3d-design")
        self.assertRegex(meta["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertEqual(set(meta), {"name", "description"})

    def test_expected_directories_and_examples(self) -> None:
        for directory in ["references", "scripts", "data", "schemas", "templates", "examples", "tests"]:
            self.assertTrue((SKILL / directory).is_dir(), directory)
        for example in ["honeycomb-wall-shelf", "rounded-desk-organizer", "unicorn-dice-tower", "calibration-coupons"]:
            self.assertTrue((SKILL / "examples" / example).is_dir(), example)
            self.assertTrue((SKILL / "examples" / example / "design-spec.yaml").exists())

    def test_metrimade_watermark_package(self) -> None:
        root = SKILL.parents[2] / "tools" / "metrimade-watermark"
        expected = [
            "design-spec.yaml",
            "RIGHTS-NOTICE.md",
            "THIRD-PARTY-NOTICES.md",
            "provenance.json",
            "source/metrimade-watermark.scad",
            "tools/generate_watermark.py",
            "exports/examples/MM-ORG-001_v0.1.0/metrimade-watermark-MM-ORG-001-v0.1.0.json",
            "exports/examples/MM-ORG-001_v0.1.0/manifest.sha256",
        ]
        for relative in expected:
            self.assertTrue((root / relative).is_file(), relative)

    def test_yaml_and_json_are_parseable(self) -> None:
        for path in SKILL.rglob("*.yaml"):
            with self.subTest(path=path):
                yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in SKILL.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_openai_agent_metadata(self) -> None:
        metadata_path = SKILL / "agents" / "openai.yaml"
        self.assertTrue(metadata_path.exists())
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        interface = metadata.get("interface", {})
        self.assertTrue(interface.get("display_name"))
        self.assertTrue(interface.get("short_description"))

    def test_final_handoff_keeps_model_primary(self) -> None:
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        report_path = SKILL / "references" / "final-model-result-report.md"
        self.assertTrue(report_path.is_file())
        report = report_path.read_text(encoding="utf-8")

        self.assertIn("## Mandatory final model result report", skill_text)
        self.assertLess(
            skill_text.index("**Watermark integration**"),
            skill_text.index("**Final model result report**"),
        )
        required_sections = [
            "**Design outcome**",
            "**Model result**",
            "**Verification and print readiness**",
            "**Deliverables**",
            "**Open items and limitations**",
            "**Kennzeichnung**",
            "**Next model action or readiness**",
        ]
        positions = [report.index(section) for section in required_sections]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("one compact sidebar-style bullet or at most two short lines", report)
        self.assertIn("Never title the final response after the watermark", report)
        self.assertIn("Never make watermark status the final sentence", report)

    def test_efficiency_and_mesh_simplification_are_mandatory_gates(self) -> None:
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        mesh_reference = SKILL / "references" / "mesh-simplification.md"
        gate_script = SKILL / "scripts" / "mesh_simplification_gate.py"
        self.assertTrue(mesh_reference.is_file())
        self.assertTrue(gate_script.is_file())
        organizer_metrics = SKILL / "examples" / "rounded-desk-organizer" / "mesh-simplification-metrics.json"
        self.assertTrue(organizer_metrics.is_file())
        self.assertIn("optimize-fdm-design", skill_text)
        self.assertIn("Every manufacturing model must pass an efficiency and mesh-complexity decision", skill_text)
        self.assertIn("master_mesh", skill_text)
        self.assertIn("slicer_resolution_check", skill_text)
        self.assertLess(
            skill_text.index("**Efficiency and mesh-simplification gate**"),
            skill_text.index("**Watermark integration**"),
        )
        self.assertLess(
            skill_text.index("**Watermark integration**"),
            skill_text.index("**Final derived mesh export and release regression checks**"),
        )

    def test_preflight_is_the_first_design_gate_and_has_deterministic_handoff(self) -> None:
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        integration = SKILL / "references" / "preflight-integration.md"
        preflight_skill = SKILL.parent / "3d-design-preflight"
        self.assertTrue(integration.is_file())
        self.assertTrue((preflight_skill / "SKILL.md").is_file())
        self.assertTrue((preflight_skill / "scripts" / "validate_preflight.py").is_file())
        self.assertLess(
            skill_text.index("## Start every design with the mandatory preflight"),
            skill_text.index("## Start every design with an explicit contract"),
        )
        self.assertLess(
            skill_text.index("**3D design preflight**"),
            skill_text.index("**Requirements and risk review**"),
        )
        self.assertIn("RETROSPECTIVE", skill_text)
        self.assertIn("preflight/preflight-result.json", skill_text)

        schema = json.loads((SKILL / "schemas" / "design-spec.schema.json").read_text(encoding="utf-8"))
        self.assertIn("preflight", schema["properties"]["workflow"]["required"])
        profile = json.loads((SKILL / "assets" / "validation-profile.json").read_text(encoding="utf-8"))
        roles = {item["id"]: item for item in profile["artifact_roles"]}
        self.assertTrue(roles["preflight-result"]["required"])

    def test_no_placeholder_tokens_in_core(self) -> None:
        pattern = re.compile(r"\b(TODO|FIXME|REPLACE_ME)\b")
        for path in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
            with self.subTest(path=path):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
