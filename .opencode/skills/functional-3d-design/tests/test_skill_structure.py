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

    def test_just_innovation_watermark_assets(self) -> None:
        root = SKILL / "assets" / "just-innovation-watermark"
        expected = [
            "manifest.yaml",
            "RIGHTS-NOTICE.md",
            "source/just-innovation-watermark.scad",
            "exports/dxf/just-innovation-standard.dxf",
            "exports/dxf/just-innovation-compact.dxf",
            "exports/svg/just-innovation-standard.svg",
            "exports/svg/just-innovation-compact.svg",
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

    def test_no_placeholder_tokens_in_core(self) -> None:
        pattern = re.compile(r"\b(TODO|FIXME|REPLACE_ME)\b")
        for path in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
            with self.subTest(path=path):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
