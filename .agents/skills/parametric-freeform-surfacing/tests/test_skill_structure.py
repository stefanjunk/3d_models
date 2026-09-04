from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


class SkillStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_root = Path(__file__).resolve().parents[1]
        cls.scripts = cls.skill_root / "scripts"

    def test_frontmatter_name_matches_directory(self) -> None:
        text = (self.skill_root / "SKILL.md").read_text(encoding="utf-8")
        end = text.find("\n---\n", 4)
        frontmatter = yaml.safe_load(text[4:end])
        self.assertEqual(frontmatter["name"], self.skill_root.name)
        compatibility = frontmatter.get(
            "compatibility", frontmatter.get("metadata", {}).get("compatibility", "")
        )
        self.assertIn("OpenCode", compatibility)

    def test_opencode_command_is_portable(self) -> None:
        command = self.skill_root / "opencode" / "commands" / "design-freeform-surface.md"
        self.assertTrue(command.is_file())
        text = command.read_text(encoding="utf-8")
        self.assertIn("$ARGUMENTS", text)
        self.assertNotIn("model:", text)


    def test_validate_skill_cli(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(self.scripts / "validate_skill.py"), "--root", str(self.skill_root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads(completed.stdout)
        self.assertTrue(report["valid"])

    def test_validate_template_spec_cli(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(self.scripts / "validate_spec.py"), str(self.skill_root / "assets" / "templates" / "surfacing-spec.yaml")],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["valid"])

    def test_project_init(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            completed = subprocess.run(
                [sys.executable, str(self.scripts / "project_init.py"), str(target)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue((target / "surfacing-spec.yaml").is_file())
            self.assertTrue((target / "hardpoints.json").is_file())


if __name__ == "__main__":
    unittest.main()
