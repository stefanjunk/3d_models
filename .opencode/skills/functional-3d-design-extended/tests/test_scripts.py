from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"


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


class ScriptTests(unittest.TestCase):
    def test_tool_selection(self) -> None:
        organic = run_json(
            "select_tool.py",
            "--input-kind", "stl",
            "--geometry", "organic",
            "--precision", "medium",
            "--json",
        )
        self.assertEqual(organic["primary"], "blender")

        precise = run_json(
            "select_tool.py",
            "--geometry", "prismatic",
            "--precision", "high",
            "--needs-step",
            "--json",
        )
        self.assertIn(precise["primary"], {"cadquery", "freecad"})
        self.assertGreater(precise["scores"]["cadquery"], precise["scores"]["openscad"])

    def test_material_and_print_profile(self) -> None:
        result = run_json(
            "select_material.py",
            "--outdoor",
            "--impact",
            "--no-enclosure",
            "--max-printability", "3",
            "--json",
        )
        self.assertGreater(len(result["recommendations"]), 0)
        self.assertNotIn("pei", [m["id"] for m in result["recommendations"]])

        profile = run_json("recommend_print_profile.py", "--material", "petg", "--nozzle", "0.6", "--json")
        self.assertEqual(profile["nozzle_mm"], 0.6)
        self.assertLessEqual(profile["layer_height_mm"], 0.45)
        self.assertGreaterEqual(profile["perimeters"], 3)

    def test_print_buy_fit_snap_gear(self) -> None:
        bearing = run_json("print_vs_buy.py", "--component", "bearing", "--json")
        self.assertEqual(bearing["recommendation"], "buy")

        fit = run_json(
            "fit_clearance.py",
            "--nominal", "6",
            "--fit", "slide",
            "--nozzle", "0.6",
            "--material", "petg",
            "--json",
        )
        self.assertGreater(fit["modeled_hole_diameter_mm_if_shaft_is_nominal"], 6.0)

        snap = run_json(
            "snapfit_calculator.py",
            "--length", "30",
            "--width", "8",
            "--thickness", "1.2",
            "--deflection", "2",
            "--modulus", "1800",
            "--allowable-strain", "1.5",
            "--json",
        )
        self.assertTrue(snap["passed_preliminary_strain"])

        gear = run_json(
            "gear_pair.py",
            "--module", "1.5",
            "--teeth1", "20",
            "--teeth2", "40",
            "--nozzle", "0.6",
            "--json",
        )
        self.assertAlmostEqual(gear["standard_center_distance_mm"], 45.0)
        self.assertAlmostEqual(gear["ratio_driven_over_driver"], 2.0)

    def test_design_specs_validate(self) -> None:
        for spec in sorted((SKILL / "examples").glob("*/design-spec.yaml")):
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_design_spec.py"), str(spec)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, f"{spec}\n{proc.stdout}\n{proc.stderr}")

    def test_parts_library_qualification_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            library = Path(td) / "parts.json"
            entry = Path(td) / "entry.json"
            entry.write_text(json.dumps({
                "part_id": "test-spacer",
                "revision": "0.1.0",
                "status": "experimental",
                "source_type": "printed",
                "category": "spacer",
                "validation": [],
                "test_evidence": [],
            }), encoding="utf-8")
            run_json("parts_library.py", "--library", str(library), "init") if False else None
            # init emits a path rather than JSON
            proc = subprocess.run([sys.executable, str(SCRIPTS / "parts_library.py"), "--library", str(library), "init"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            added = run_json("parts_library.py", "--library", str(library), "add", "--entry", str(entry))
            self.assertTrue(added["passed"])
            failed = run_json(
                "parts_library.py",
                "--library", str(library),
                "promote", "--part-id", "test-spacer", "--status", "qualified-local",
                expected=1,
            )
            self.assertFalse(failed["passed"])


if __name__ == "__main__":
    unittest.main()
