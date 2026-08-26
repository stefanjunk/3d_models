from __future__ import annotations

from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_name(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = yaml.safe_load(match.group(1))
        self.assertEqual(frontmatter["name"], ROOT.name)

    def test_three_examples_exist(self):
        examples = [path for path in (ROOT / "examples").iterdir() if path.is_dir()]
        self.assertEqual(len(examples), 3)
        for example in examples:
            self.assertTrue((example / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
