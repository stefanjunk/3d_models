import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "fdm-joints-and-fits"
    / "scripts"
    / "generate_fit_coupon.py"
)


class FitCouponTests(unittest.TestCase):
    def test_generates_bore_ladder_and_machine_readable_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "coupon.stl"
            report = Path(tmp) / "coupon.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--nominal",
                    "8.0",
                    "--offsets=-0.2,-0.1,0,0.1,0.2",
                    "--output",
                    str(output),
                    "--report",
                    str(report),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "COUPON_GENERATED")
            self.assertEqual(payload["hole_diameters_mm"], [7.8, 7.9, 8.0, 8.1, 8.2])
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 500)

    def test_rejects_nonascending_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--nominal",
                    "8.0",
                    "--offsets=0.1,0,-0.1",
                    "--output",
                    str(Path(tmp) / "coupon.stl"),
                    "--report",
                    str(Path(tmp) / "coupon.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
