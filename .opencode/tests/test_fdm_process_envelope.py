import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "fdm-process-envelope"
    / "scripts"
    / "evaluate_process_envelope.py"
)


def evaluate(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        payload = json.loads(result.stdout)
    else:
        payload = {"status": "NO_OUTPUT", "stderr": result.stderr}
    payload["returncode"] = result.returncode
    return payload


class FdmProcessEnvelopeTests(unittest.TestCase):
    def test_rejects_feature_narrower_than_nozzle(self) -> None:
        result = evaluate(
            "--nozzle", "0.8",
            "--material", "PETG",
            "--min-wall", "1.2",
            "--min-feature", "0.7",
        )

        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertNotEqual(result["returncode"], 0)

    def test_marks_press_fit_and_snap_fit_as_coupon_required(self) -> None:
        result = evaluate(
            "--nozzle", "0.4",
            "--material", "PETG",
            "--min-wall", "1.2",
            "--min-feature", "1.0",
            "--press-fit",
            "--snap-fit",
        )

        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertIn("press_fit", result["required_coupons"])
        self.assertIn("snap_fit", result["required_coupons"])

    def test_accepts_pla_as_baseline_material_without_unnecessary_upgrade(self) -> None:
        result = evaluate(
            "--nozzle", "0.6",
            "--material", "PLA",
            "--min-wall", "1.8",
            "--min-feature", "1.2",
        )

        self.assertEqual(result["status"], "SUPPORTED")

    def test_requires_hardened_nozzle_for_pa_cf(self) -> None:
        result = evaluate(
            "--nozzle", "0.6",
            "--material", "PA-CF",
            "--min-wall", "1.8",
            "--min-feature", "1.2",
        )

        self.assertEqual(result["status"], "CONDITIONAL")
        self.assertIn("hardened_nozzle", result["requirements"])


if __name__ == "__main__":
    unittest.main()
