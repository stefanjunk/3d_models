from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_root = Path(__file__).resolve().parents[1]
        cls.scripts = cls.skill_root / "scripts"

    def test_route_method_outputs_hybrid_and_companions(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(self.scripts / "route_method.py"),
                "--input", "dense-ai-mesh",
                "--hardpoints", "exact",
                "--editability", "high",
                "--style-variants", "yes",
                "--local-blends", "yes",
                "--step-required", "yes",
                "--protected-source", "yes",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads(completed.stdout)
        self.assertIn("organic-mesh-functionalization", report["companions"])
        self.assertIn("functional-3d-design", report["companions"])

    def test_fair_curve_cli_writes_output_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_path = root / "input.csv"
            output_path = root / "output.csv"
            report_path = root / "report.json"
            with input_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["x", "y"])
                for i in range(30):
                    writer.writerow([i, 0.08 * ((-1) ** i) + i * i / 200.0])
            completed = subprocess.run(
                [
                    sys.executable,
                    str(self.scripts / "fair_curve.py"),
                    str(input_path), str(output_path),
                    "--strength", "20",
                    "--preserve-ends",
                    "--report", str(report_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue(output_path.is_file())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertLess(report["after"]["curvature_total_variation"], report["before"]["curvature_total_variation"])

    def test_compare_hardpoints_detects_pass_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = root / "baseline.json"
            current = root / "current.json"
            baseline.write_text(json.dumps({
                "points": [{"name": "mount", "position": [0, 0, 0]}],
                "axes": [{"name": "axle", "start": [0, -10, 2], "end": [0, 10, 2]}],
                "planes": [{"name": "seat", "origin": [0, 0, 0], "normal": [0, 0, 1]}],
            }), encoding="utf-8")
            current.write_text(json.dumps({
                "points": [{"name": "mount", "position": [0.02, 0, 0]}],
                "axes": [{"name": "axle", "start": [0.01, -10, 2], "end": [0.01, 10, 2]}],
                "planes": [{"name": "seat", "origin": [0, 0, 0.03], "normal": [0, 0, 1]}],
            }), encoding="utf-8")
            completed = subprocess.run([
                sys.executable, str(self.scripts / "compare_hardpoints.py"),
                str(baseline), str(current), "--point-tol", "0.05",
                "--axis-pos-tol", "0.05", "--plane-offset-tol", "0.05",
            ], text=True, capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue(json.loads(completed.stdout)["success"])



if __name__ == "__main__":
    unittest.main()
