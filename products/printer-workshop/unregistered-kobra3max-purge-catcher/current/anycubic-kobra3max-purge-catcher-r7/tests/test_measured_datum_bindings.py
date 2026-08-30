#!/usr/bin/env python3
"""Regression test: every user measurement must drive a named CAD feature."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = PROJECT_ROOT / "src" / "generate_r7_z_rider.py"


class MeasuredDatumBindingTest(unittest.TestCase):
    def test_all_four_measured_datums_are_bound(self) -> None:
        with tempfile.TemporaryDirectory(prefix="r7-datum-eval-") as temp_dir:
            output = Path(temp_dir) / "build"
            run = subprocess.run(
                [sys.executable, str(GENERATOR), "--output-dir", str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, msg=run.stdout + run.stderr)
            report = json.loads((output / "reports" / "geometry-validation.json").read_text())

        expected = {
            "M-R7-001-screw-pitch-z": (17.0, "lower round hole center to upper slot center"),
            "M-R7-002-lower-screw-to-purge-z": (10.0, "purge deposition datum inside closed capture zone"),
            "M-R7-003-screw-to-throw-x": (37.0, "catcher capture center plane"),
            "M-R7-004-rear-wiper-keepout-y": (
                40.0,
                "reference-only rear keep-out; added geometry stays at y >= 0",
            ),
        }
        bindings = report["metrics"]["measured_datum_bindings"]
        self.assertEqual(set(bindings), set(expected))
        for binding_id, (value, feature) in expected.items():
            binding = bindings[binding_id]
            self.assertEqual(binding["expected_mm"], value)
            self.assertEqual(binding["actual_mm"], value)
            self.assertEqual(binding["deviation_mm"], 0.0)
            self.assertEqual(binding["bound_feature"], feature)

        checks = report["checks"]
        self.assertTrue(checks["screw_pitch_bound_to_hole_centers"])
        self.assertTrue(checks["purge_z_bound_inside_closed_capture_zone"])
        self.assertTrue(checks["throw_x_bound_to_capture_center"])
        self.assertTrue(checks["rear_keepout_bound_and_respected"])


if __name__ == "__main__":
    unittest.main()
