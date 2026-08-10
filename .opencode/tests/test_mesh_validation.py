import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).parents[1] / "skills" / "mesh-validation" / "scripts" / "validate_mesh.py"


class MeshValidationTests(unittest.TestCase):
    def test_closed_cube_passes_without_processing(self) -> None:
        try:
            import trimesh
        except ImportError:
            self.skipTest("trimesh unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            mesh_path = Path(tmp) / "cube.stl"
            trimesh.creation.box(extents=(10, 20, 30)).export(mesh_path)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(mesh_path),
                    "--require-watertight",
                    "--require-volume",
                    "--require-single-body",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["load_processing"])
        self.assertTrue(report["passed"])

    def test_scene_node_transforms_affect_bounds_and_bed_fit(self) -> None:
        try:
            import trimesh
        except ImportError:
            self.skipTest("trimesh unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            mesh_path = Path(tmp) / "scene.glb"
            scene = trimesh.Scene()
            scene.add_geometry(trimesh.creation.box(extents=(10, 10, 10)), node_name="origin")
            transform = np.eye(4)
            transform[0, 3] = 100
            scene.add_geometry(
                trimesh.creation.box(extents=(10, 10, 10)),
                node_name="translated",
                transform=transform,
            )
            mesh_path.write_bytes(scene.export(file_type="glb"))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(mesh_path), "--bed", "50", "50", "50"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertGreater(report["extents_mm"][0], 100)
        self.assertFalse(report["checks"]["bed_fit_axis_aligned"])


if __name__ == "__main__":
    unittest.main()
