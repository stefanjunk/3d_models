import json
from pathlib import Path
import tempfile
import unittest

import trimesh

from generate_labyrinth_box import main


class CliTests(unittest.TestCase):
    def test_cli_exports_both_parts_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)

            exit_code = main(
                [
                    "--cavity-diameter",
                    "30",
                    "--cavity-length",
                    "45",
                    "--difficulty",
                    "1",
                    "--maze-location",
                    "inner",
                    "--seed",
                    "17",
                    "--angular-facets",
                    "64",
                    "--output-dir",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            expected_files = {
                "inner.stl",
                "outer.stl",
                "inner.step",
                "outer.step",
                "assembly.step",
                "maze.json",
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected_files)
            self.assertTrue(all((output / name).stat().st_size > 0 for name in expected_files))

            manifest = json.loads((output / "maze.json").read_text())
            self.assertEqual(manifest["config"]["maze_location"], "inner")
            self.assertEqual(manifest["maze"]["unique_solution_count"], 1)
            self.assertEqual(
                len(manifest["maze"]["edges"]),
                manifest["maze"]["rows"] * manifest["maze"]["columns"] - 1,
            )
            self.assertEqual(manifest["print_orientation"]["outer"], "cap_down")

            for filename in ("inner.stl", "outer.stl"):
                mesh = trimesh.load_mesh(output / filename, force="mesh", process=True)
                self.assertTrue(mesh.is_watertight)
                self.assertTrue(mesh.is_winding_consistent)
                self.assertAlmostEqual(mesh.bounds[0][2], 0.0, places=4)

            outer_mesh = trimesh.load_mesh(
                output / "outer.stl", force="mesh", process=True
            )
            minimum_z, maximum_z = outer_mesh.bounds[:, 2]
            bottom_area = sum(
                area
                for normal, center, area in zip(
                    outer_mesh.face_normals,
                    outer_mesh.triangles_center,
                    outer_mesh.area_faces,
                )
                if abs(normal[2]) > 0.99 and center[2] < minimum_z + 0.01
            )
            top_area = sum(
                area
                for normal, center, area in zip(
                    outer_mesh.face_normals,
                    outer_mesh.triangles_center,
                    outer_mesh.area_faces,
                )
                if abs(normal[2]) > 0.99 and center[2] > maximum_z - 0.01
            )
            self.assertGreater(bottom_area, 2.0 * top_area)

    def test_cli_exports_outer_maze_variant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)

            exit_code = main(
                [
                    "--cavity-diameter",
                    "30",
                    "--cavity-length",
                    "45",
                    "--difficulty",
                    "1",
                    "--maze-location",
                    "outer",
                    "--seed",
                    "17",
                    "--angular-facets",
                    "64",
                    "--output-dir",
                    str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            manifest = json.loads((output / "maze.json").read_text())
            self.assertEqual(manifest["config"]["maze_location"], "outer")
            self.assertEqual(manifest["maze"]["unique_solution_count"], 1)
            self.assertTrue(
                trimesh.load_mesh(
                    output / "outer.stl", force="mesh", process=True
                ).is_watertight
            )


if __name__ == "__main__":
    unittest.main()
