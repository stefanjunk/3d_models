from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
PACKAGE = SKILL.parents[2]


class SkillStructureTests(unittest.TestCase):
    def test_skill_frontmatter(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        parts = text.split("---", 2)
        self.assertGreaterEqual(len(parts), 3)
        meta = yaml.safe_load(parts[1])
        self.assertEqual(meta["name"], "functional-3d-design")
        self.assertEqual(meta["compatibility"], "opencode")
        self.assertRegex(meta["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        for key in ["name", "description", "license", "compatibility", "metadata"]:
            self.assertIn(key, meta)

    def test_expected_directories_and_examples(self) -> None:
        for directory in ["references", "scripts", "data", "schemas", "templates", "examples", "tests"]:
            self.assertTrue((SKILL / directory).is_dir(), directory)
        for example in ["honeycomb-wall-shelf", "rounded-desk-organizer", "unicorn-dice-tower", "calibration-coupons"]:
            self.assertTrue((SKILL / "examples" / example).is_dir(), example)
            self.assertTrue((SKILL / "examples" / example / "design-spec.yaml").exists())

    def test_yaml_and_json_are_parseable(self) -> None:
        for path in SKILL.rglob("*.yaml"):
            with self.subTest(path=path):
                yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in SKILL.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_opencode_agent_and_command_files(self) -> None:
        for folder in [PACKAGE / ".opencode" / "agents", PACKAGE / ".opencode" / "commands"]:
            files = list(folder.glob("*.md"))
            self.assertGreater(len(files), 0)
            for path in files:
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), path)
                self.assertIn("description:", text, path)

    def test_no_placeholder_tokens_in_core(self) -> None:
        pattern = re.compile(r"\b(TODO|FIXME|REPLACE_ME)\b")
        for path in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
            with self.subTest(path=path):
                self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
