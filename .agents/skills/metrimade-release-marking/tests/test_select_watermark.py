from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
WORKSPACE_WATERMARK = SKILL.parents[2] / "tools" / "metrimade-watermark"
WATERMARK_EXAMPLE = (
    WORKSPACE_WATERMARK
    / "exports"
    / "examples"
    / "MM-ORG-001_v0.1.0"
    / "metrimade-watermark-MM-ORG-001-v0.1.0.json"
)
WATERMARK_R2_EXAMPLES = WORKSPACE_WATERMARK / "exports" / "examples-r2"


def run_json(script: str, *args: str, expected: int = 0) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != expected:
        raise AssertionError(f"{script} return {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return json.loads(proc.stdout)


class WatermarkSelectorTests(unittest.TestCase):
    def test_watermark_selector_exact_rotated_and_block(self) -> None:
        exact = run_json(
            "select_watermark.py",
            "--metadata", str(WATERMARK_EXAMPLE),
            "--surface-width", "120",
            "--surface-height", "80",
            "--host-wall", "2.0",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
        )
        self.assertEqual(exact["status"], "PASS")
        self.assertEqual(exact["asset_id"], "MM-WM-001-R1")
        self.assertEqual(exact["domain"], "metriMade.com")
        self.assertEqual(exact["selection"]["uniform_scale"], 1.0)
        self.assertEqual(exact["selection"]["rotation_deg"], 0)

        rotated = run_json(
            "select_watermark.py",
            "--metadata", str(WATERMARK_EXAMPLE),
            "--surface-width", "30",
            "--surface-height", "80",
            "--host-wall", "1.2",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
        )
        self.assertEqual(rotated["status"], "PASS")
        self.assertEqual(rotated["selection"]["rotation_deg"], 90)

        blocked = run_json(
            "select_watermark.py",
            "--metadata", str(WATERMARK_EXAMPLE),
            "--surface-width", "50",
            "--surface-height", "30",
            "--host-wall", "1.2",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
            expected=1,
        )
        self.assertEqual(blocked["status"], "BLOCK")
        self.assertIsNone(blocked["selection"])

    def test_watermark_selector_r2_prefers_full_then_compact_then_micro(self) -> None:
        cases = (
            (80, 30, "full", 0),
            (48, 20, "compact", 0),
            (42, 16, "micro", 0),
        )
        for width, height, expected_tier, expected_rotation in cases:
            result = run_json(
                "select_watermark.py",
                "--metadata", str(WATERMARK_R2_EXAMPLES),
                "--surface-width", str(width),
                "--surface-height", str(height),
                "--host-wall", "1.2",
                "--nozzle", "0.4",
                "--layer-height", "0.2",
            )
            self.assertEqual(result["asset_id"], "MM-WM-001-R2")
            self.assertEqual(result["selection"]["layout_tier"], expected_tier)
            self.assertEqual(result["selection"]["rotation_deg"], expected_rotation)
            self.assertEqual(result["selection"]["uniform_scale"], 1.0)
        self.assertFalse(result["selection"]["domain_visible"])

        blocked = run_json(
            "select_watermark.py",
            "--metadata", str(WATERMARK_R2_EXAMPLES),
            "--surface-width", "38",
            "--surface-height", "16",
            "--host-wall", "1.2",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
            expected=1,
        )
        self.assertEqual(blocked["status"], "BLOCK")
        self.assertIsNone(blocked["selection"])


if __name__ == "__main__":
    unittest.main()
