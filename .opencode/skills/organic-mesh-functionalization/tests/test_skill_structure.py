from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parents[1]
PACKAGE = SKILL.parents[2]


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        meta = yaml.safe_load(text.split("---", 2)[1])
        self.assertEqual(meta["name"], "organic-mesh-functionalization")
        self.assertEqual(meta["compatibility"], "opencode")
        self.assertRegex(meta["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_expected_tree(self) -> None:
        for folder in ["references", "scripts", "data", "schemas", "templates", "examples", "tests"]:
            self.assertTrue((SKILL / folder).is_dir(), folder)
        for example in ["dice-tower", "barefoot-shoe", "unicorn-compartment"]:
            self.assertTrue((SKILL / "examples" / example / "operation-plan.yaml").exists())
        self.assertGreaterEqual(len(list((SKILL / "references").glob("*.md"))), 12)

    def test_structured_files_parse(self) -> None:
        for path in SKILL.rglob("*.yaml"):
            with self.subTest(path=path):
                yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in SKILL.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_agents_commands(self) -> None:
        for folder in [PACKAGE / ".opencode" / "agents", PACKAGE / ".opencode" / "commands"]:
            files = list(folder.glob("*.md"))
            self.assertGreater(len(files), 0)
            for path in files:
                self.assertTrue(path.read_text(encoding="utf-8").startswith("---\n"))

    def test_no_placeholders(self) -> None:
        pattern = re.compile(r"\b(TODO|FIXME|REPLACE_ME)\b")
        for path in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
            self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")), path)


if __name__ == "__main__":
    unittest.main()
