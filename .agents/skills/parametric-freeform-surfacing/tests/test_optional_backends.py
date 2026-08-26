from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


class OptionalBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_root = Path(__file__).resolve().parents[1]
        cls.scripts = cls.skill_root / "scripts"

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "SciPy not installed")
    def test_scipy_bspline_fit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "curve.csv"
            output = root / "fit.csv"
            report = root / "fit.json"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["x", "y"])
                for x in np.linspace(0.0, 100.0, 50):
                    writer.writerow([x, 12.0 * np.sin(x / 35.0) + 0.3 * np.sin(x)])
            completed = subprocess.run(
                [
                    sys.executable,
                    str(self.scripts / "fit_bspline.py"),
                    str(source), str(output),
                    "--smoothing", "5.0",
                    "--report", str(report),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["degree"], 3)
            self.assertGreater(data["coefficient_count"], 3)
            self.assertTrue(output.is_file())

    @unittest.skipUnless(importlib.util.find_spec("cadquery"), "CadQuery not installed")
    def test_cadquery_loft_exports_valid_step(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sections = root / "sections"
            sections.mkdir()
            theta = np.linspace(0.0, 2.0 * np.pi, 36, endpoint=False)
            for index, (x, ry, rz) in enumerate(((0.0, 10.0, 7.0), (25.0, 16.0, 11.0), (55.0, 8.0, 6.0))):
                path = sections / f"{index:02d}.csv"
                with path.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["x", "y", "z"])
                    writer.writerows(np.column_stack([np.full_like(theta, x), ry * np.cos(theta), rz * np.sin(theta)]))
            step = root / "loft.step"
            stl = root / "loft.stl"
            report = root / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(self.scripts / "backends" / "cadquery_loft_to_step.py"),
                    str(sections), str(step),
                    "--stl", str(stl),
                    "--report", str(report),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(data["solid_valid"])
            self.assertTrue(data["mesh_welded"]["watertight_edge_incidence"])
            self.assertTrue(step.is_file())
            self.assertTrue(stl.is_file())

    @unittest.skipUnless(importlib.util.find_spec("trimesh"), "Trimesh not installed")
    def test_extract_reference_mesh_sections(self) -> None:
        import trimesh
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mesh_path = root / "sphere.stl"
            trimesh.creation.icosphere(subdivisions=2, radius=12.0).export(mesh_path)
            output = root / "sections"
            completed = subprocess.run([
                sys.executable, str(self.scripts / "extract_mesh_sections.py"),
                str(mesh_path), str(output), "--axis", "x", "--count", "5", "--points", "64",
            ], text=True, capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            report = json.loads((output / "section-extraction.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(report["extracted_sections"], 3)
            self.assertTrue(any(output.glob("*.csv")))



if __name__ == "__main__":
    unittest.main()
