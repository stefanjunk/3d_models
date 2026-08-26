from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ValidationIntegrationTests(unittest.TestCase):
    def test_fail_closed_profile_is_self_consistent(self) -> None:
        profile = json.loads((ROOT / "assets" / "validation-profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["skill"], ROOT.name)
        roles = {item["id"] for item in profile["artifact_roles"]}
        self.assertEqual(len(roles), len(profile["artifact_roles"]))
        for declared in profile["checks"]:
            self.assertTrue(set(declared["artifact_roles"]) <= roles)
        self.assertEqual(set(profile["release_policy"]["block_statuses"]), {"FAIL", "NOT_RUN", "REVIEW_REQUIRED"})
        self.assertIn("validate-printable-3d-projects", (ROOT / "SKILL.md").read_text(encoding="utf-8"))

    def test_python_sources_parse_without_bytecode(self) -> None:
        for path in sorted(ROOT.rglob("*.py")):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


if __name__ == "__main__":
    unittest.main()
