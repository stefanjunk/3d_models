from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL / "scripts" / "validate_preflight.py"
EXAMPLE = SKILL / "examples" / "preflight-result.example.json"


def run_validator(path: Path, *args: str, expected: int = 0) -> dict:
    process = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != expected:
        raise AssertionError(
            f"validator returned {process.returncode}\n"
            f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )
    return json.loads(process.stdout)


class ValidatePreflightTests(unittest.TestCase):
    def test_example_is_schema_valid_and_reports_hold(self) -> None:
        report = run_validator(
            EXAMPLE,
            "--project-id",
            "MM-CAL-001",
            "--project-revision",
            "1.0.0",
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["decision"]["design_release"], "HOLD")
        self.assertTrue(any("blocks production design" in item for item in report["warnings"]))

    def test_initial_retrospective_backfill_requires_explicit_trigger(self) -> None:
        document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        document["traceability"].update(
            {
                "mode": "RETROSPECTIVE",
                "change_triggers": ["initial_design"],
                "previous_assessment_id": None,
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preflight-result.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            report = run_validator(path, expected=1)
        self.assertFalse(report["passed"])
        self.assertTrue(any("backfill_missing_preflight" in item for item in report["errors"]))

    def test_cross_project_link_is_rejected(self) -> None:
        report = run_validator(EXAMPLE, "--project-id", "MM-WRONG-001", expected=1)
        self.assertFalse(report["passed"])
        self.assertTrue(any("project_id" in item for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
