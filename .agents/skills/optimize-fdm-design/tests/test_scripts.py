from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_json(script: str, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(f"{script} returned {proc.returncode}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


class OptimizeFdmScriptTests(unittest.TestCase):
    def test_shell_planner_uses_constant_width_spacing(self) -> None:
        data = run_json(
            "plan_shell_ribs.py",
            "--nozzle-mm", "0.6",
            "--line-width-mm", "0.68",
            "--layer-height-mm", "0.30",
            "--shell-lines", "3",
            "--rib-lines", "2",
            "--sealed-lines", "4",
            "--floor-layers", "4",
            "--plate-thickness-mm", "2.72",
            "--wall-lines-per-side", "2",
            "--speed-mm-s", "45",
            "--max-flow-mm3-s", "12",
        )
        spacing = 0.68 - 0.30 * (1.0 - math.pi / 4.0)
        self.assertAlmostEqual(data["process"]["constant_width_path_spacing_mm"], spacing)
        self.assertAlmostEqual(data["sections"]["functional_shell"]["nominal_thickness_mm"], 0.68 + 2 * spacing)
        self.assertAlmostEqual(data["sections"]["floor_or_skin"]["nominal_thickness_mm"], 1.2)
        self.assertAlmostEqual(data["process"]["requested_flow_mm3_s"], 9.18)
        self.assertEqual(data["opposing_wall_core_check"]["status"], "SUB_LINE_WIDTH_CORE")
        self.assertFalse(data["opposing_wall_core_check"]["infill_percentage_can_change_bulk"])

    def test_thin_plate_can_be_fully_consumed_by_opposing_wall_paths(self) -> None:
        data = run_json(
            "plan_shell_ribs.py",
            "--nozzle-mm", "0.6", "--line-width-mm", "0.68",
            "--layer-height-mm", "0.30", "--shell-lines", "3",
            "--plate-thickness-mm", "3.0", "--wall-lines-per-side", "3",
        )
        self.assertEqual(data["opposing_wall_core_check"]["status"], "NO_INFILL_CORE")
        self.assertLess(data["opposing_wall_core_check"]["estimated_remaining_infill_core_mm"], 0)

    def test_variant_comparison_rejects_constraint_and_finds_pareto(self) -> None:
        payload = {
            "baseline": "base",
            "objectives": [
                {"metric": "time", "goal": "min"},
                {"metric": "mass", "goal": "min"},
            ],
            "constraints": [{"metric": "stiffness", "op": ">=", "value": 40}],
            "variants": [
                {"name": "base", "metrics": {"time": 100, "mass": 100, "stiffness": 50}},
                {"name": "fast", "metrics": {"time": 60, "mass": 85, "stiffness": 45}},
                {"name": "light", "metrics": {"time": 75, "mass": 55, "stiffness": 42}},
                {"name": "weak", "metrics": {"time": 50, "mass": 45, "stiffness": 30}},
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "variants.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            data = run_json("compare_variants.py", str(path))
        self.assertEqual(set(data["pareto_variants"]), {"fast", "light"})
        weak = next(item for item in data["results"] if item["name"] == "weak")
        self.assertFalse(weak["feasible"])
        self.assertEqual(weak["failed_constraints"][0]["metric"], "stiffness")

    def test_bundled_example_is_valid_and_combined_is_pareto(self) -> None:
        data = run_json("compare_variants.py", str(ROOT / "examples" / "desk-organizer-variants.json"))
        self.assertIn("combined-06", data["pareto_variants"])
        aggressive = next(item for item in data["results"] if item["name"] == "aggressive-windows-06")
        self.assertFalse(aggressive["feasible"])

    def test_desk_organizer_example_records_protected_geometry_and_large_cells(self) -> None:
        example = json.loads((ROOT / "examples" / "desk-organizer-variants.json").read_text(encoding="utf-8"))
        self.assertIn("drawer guide runners and rear stops", example["protected_geometry"])
        self.assertIn("large", example["cell_strategy"]["preferred"])
        self.assertEqual(example["thin_plate_checks"][0]["expected_status"], "SUB_LINE_WIDTH_CORE")


if __name__ == "__main__":
    unittest.main()
