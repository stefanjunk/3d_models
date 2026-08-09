from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import trimesh
import yaml

SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
from common import roi_contains  # noqa: E402
from fit_landmarks import umeyama  # noqa: E402


class ScriptTests(unittest.TestCase):
    def test_roi_masks(self) -> None:
        points = np.array([[0, 0, 0], [2, 0, 0], [0, 0, 3]], dtype=float)
        mask = roi_contains(points, {"type": "sphere", "center_mm": [0, 0, 0], "radius_mm": 1})
        self.assertEqual(mask.tolist(), [True, False, False])
        mask = roi_contains(points, {"type": "box", "center_mm": [0, 0, 0], "size_mm": [2, 2, 2]}, margin=1)
        self.assertEqual(mask.tolist(), [True, True, False])

    def test_landmark_fit(self) -> None:
        src = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
        target = src + np.array([5, -2, 3])
        matrix, rms = umeyama(src, target, False)
        self.assertLess(rms, 1e-10)
        self.assertTrue(np.allclose(matrix[:3, 3], [5, -2, 3]))

    def test_inspect_and_validate_identical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mesh_path = root / "box.stl"
            trimesh.creation.box(extents=[10, 10, 10]).export(mesh_path)
            inspect_out = root / "inspect.json"
            proc = subprocess.run([sys.executable, str(SCRIPTS / "inspect_mesh.py"), str(mesh_path), "--require-watertight", "--json-out", str(inspect_out)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json.loads(inspect_out.read_text())["passed"])

            plan = yaml.safe_load((SKILL / "templates" / "operation-plan.yaml").read_text())
            plan["functional_roi"] = {"type": "sphere", "center_mm": [0, 0, 0], "radius_mm": 1.0}
            plan["transition_band_mm"] = 0.0
            plan["protected_region"]["max_surface_deviation_mm"] = 0.001
            plan["protected_region"]["p95_surface_deviation_mm"] = 0.001
            plan_path = root / "plan.yaml"
            plan_path.write_text(yaml.safe_dump(plan), encoding="utf-8")
            report = root / "edit.json"
            proc = subprocess.run([sys.executable, str(SCRIPTS / "validate_edit.py"), str(mesh_path), str(mesh_path), "--plan", str(plan_path), "--samples", "1000", "--json-out", str(report)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue(json.loads(report.read_text())["passed"])


    def test_openscad_boolean_when_available(self) -> None:
        if shutil.which("openscad") is None:
            self.skipTest("OpenSCAD not installed")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "target.stl"
            cutter = root / "cutter.stl"
            output = root / "result.stl"
            trimesh.creation.box(extents=[20, 20, 20]).export(target)
            trimesh.creation.cylinder(radius=3, height=30, sections=48).export(cutter)
            proc = subprocess.run([sys.executable, str(SCRIPTS / "openscad_boolean.py"), "difference", str(target), str(cutter), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = trimesh.load_mesh(output, process=True)
            self.assertTrue(result.is_watertight)
            self.assertLess(result.volume, 20**3)

    def test_section_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mesh = root / "cylinder.stl"
            trimesh.creation.cylinder(radius=5, height=20, sections=64).export(mesh)
            out = root / "sections.json"
            proc = subprocess.run([sys.executable, str(SCRIPTS / "section_report.py"), str(mesh), "--axis", "z", "--positions", "0", "--json-out", str(out)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(out.read_text())
            self.assertGreater(data["sections"][0]["approx_area_mm2"], 70)


if __name__ == "__main__":
    unittest.main()
