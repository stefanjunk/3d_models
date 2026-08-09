import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "power-transmission-design"
    / "scripts"
    / "screen_transmission.py"
)


def screen(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    payload["returncode"] = result.returncode
    return payload


class PowerTransmissionTests(unittest.TestCase):
    def test_belt_is_bought_as_standard_component(self) -> None:
        result = screen(
            "--type", "belt",
            "--speed-class", "low",
            "--load-class", "low",
            "--life-class", "prototype",
            "--scale", "large",
        )

        self.assertEqual(result["decision"], "BUY_STANDARD_COMPONENT")

    def test_large_low_duty_gear_is_only_a_print_candidate(self) -> None:
        result = screen(
            "--type", "gear",
            "--speed-class", "low",
            "--load-class", "low",
            "--life-class", "prototype",
            "--scale", "large",
        )

        self.assertEqual(result["decision"], "PRINT_CANDIDATE_NEEDS_TEST")
        self.assertIn("wear_test", result["required_tests"])
        self.assertNotEqual(result["returncode"], 0)

    def test_high_speed_gear_is_bought(self) -> None:
        result = screen(
            "--type", "gear",
            "--speed-class", "high",
            "--load-class", "low",
            "--life-class", "continuous",
            "--scale", "small",
        )

        self.assertEqual(result["decision"], "BUY_STANDARD_COMPONENT")


if __name__ == "__main__":
    unittest.main()
