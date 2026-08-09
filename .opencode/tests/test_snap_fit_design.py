import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "snap-fit-design"
    / "scripts"
    / "snapfit_calculator.py"
)


def calculate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class SnapFitDesignTests(unittest.TestCase):
    def test_reports_cantilever_strain_and_requires_coupon(self) -> None:
        result = calculate(
            "--material", "PETG",
            "--length", "28",
            "--root-thickness", "2.0",
            "--tip-thickness", "1.1",
            "--width", "8",
            "--deflection", "2.0",
            "--root-radius", "1.5",
            "--cycles", "500",
            "--allowable-strain", "0.03",
        )

        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertAlmostEqual(report["predicted_root_strain"], 0.007653, places=6)
        self.assertEqual(report["status"], "COUPON_REQUIRED")

    def test_rejects_small_root_radius(self) -> None:
        result = calculate(
            "--material", "PETG",
            "--length", "28",
            "--root-thickness", "2.0",
            "--tip-thickness", "1.1",
            "--width", "8",
            "--deflection", "2.0",
            "--root-radius", "0.8",
            "--cycles", "10",
            "--allowable-strain", "0.03",
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "REDESIGN_REQUIRED")

    def test_rejects_tip_thicker_than_root(self) -> None:
        result = calculate(
            "--material", "PLA",
            "--length", "20",
            "--root-thickness", "1.5",
            "--tip-thickness", "2.0",
            "--width", "8",
            "--deflection", "1.0",
            "--root-radius", "1.0",
            "--cycles", "1",
            "--allowable-strain", "0.03",
        )

        self.assertEqual(result.returncode, 2)

    def test_rejects_strain_above_declared_allowable(self) -> None:
        result = calculate(
            "--material", "PETG",
            "--length", "10",
            "--root-thickness", "2.0",
            "--tip-thickness", "1.0",
            "--width", "8",
            "--deflection", "8.0",
            "--root-radius", "1.0",
            "--cycles", "1",
            "--allowable-strain", "0.03",
        )

        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "REDESIGN_REQUIRED")
        self.assertIn("declared allowable strain", " ".join(report["blockers"]))


if __name__ == "__main__":
    unittest.main()
