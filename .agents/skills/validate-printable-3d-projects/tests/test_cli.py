from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/fdm_ci.py"


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(CLI), *args], text=True, capture_output=True, check=False)

    def test_doctor_is_machine_readable(self) -> None:
        completed = self.run_cli("doctor", "--profile", "draft")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["tool"], "doctor")
        self.assertIn("capability_groups", payload["environment"])

    def test_missing_mesh_fails(self) -> None:
        completed = self.run_cli("audit-mesh", "missing.stl")
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(json.loads(completed.stdout)["status"], "FAIL")

    def test_validate_skill_from_arbitrary_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [sys.executable, "-B", str(CLI), "validate-skill", str(ROOT), "--runtime", "opencode", "--profile", "draft"],
                cwd=tmp,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertNotEqual(json.loads(completed.stdout)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
