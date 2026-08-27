from dataclasses import replace
import importlib
import importlib.util
import io
import json
from pathlib import Path
from unittest import mock
import sys
import tempfile
import unittest

from generate_labyrinth_box import main
from labyrinth_box.config import BoxConfig
from labyrinth_box.preflight import validate_and_derive


class ImageReliefTests(unittest.TestCase):
    def _module(self):
        self.assertIsNotNone(
            importlib.util.find_spec("labyrinth_box.image_relief"),
            "missing labyrinth_box.image_relief",
        )
        return importlib.import_module("labyrinth_box.image_relief")

    def _write_test_image(self, path: Path) -> None:
        from PIL import Image

        image = Image.new("L", (8, 8), color=255)
        pixels = image.load()
        for y in range(8):
            for x in range(8):
                pixels[x, y] = 0 if (x + y) % 3 == 0 else 180
        image.save(path)

    def test_vertical_mapping_splits_proportionally_and_zero_grip_uses_full_image(self) -> None:
        module = self._module()
        rows = tuple(tuple([index]) for index in range(10))

        grip, sleeve = module.split_vertical_samples(rows, 3.0, 7.0)
        no_grip, full_sleeve = module.split_vertical_samples(rows, 0.0, 7.0)

        self.assertEqual(len(grip), 3)
        self.assertEqual(len(sleeve), 7)
        self.assertEqual(grip + sleeve, rows)
        self.assertEqual(no_grip, ())
        self.assertEqual(full_sleeve, rows)

    def test_missing_optional_dependencies_have_actionable_error(self) -> None:
        module = self._module()
        with mock.patch.object(
            module.importlib,
            "import_module",
            side_effect=ModuleNotFoundError("simulated missing dependency"),
        ):
            with self.assertRaisesRegex(
                module.ImageReliefDependencyError,
                r"pip install '.\[image-relief\]'",
            ):
                module.load_optional_dependencies()

    def test_missing_image_path_fails_before_export_with_clear_message(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            stderr = io.StringIO()
            with mock.patch("sys.stderr", stderr):
                exit_code = main(
                    [
                        "--cavity-diameter", "30",
                        "--cavity-length", "45",
                        "--difficulty", "1",
                        "--image-relief", str(Path(temporary_directory) / "missing.png"),
                        "--output-dir", str(Path(temporary_directory) / "out"),
                    ]
                )
        self.assertEqual(exit_code, 2)
        self.assertIn("image relief", stderr.getvalue().lower())
        self.assertIn("does not exist", stderr.getvalue().lower())

    def test_no_image_does_not_import_image_relief_module(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with mock.patch.dict(sys.modules, {"labyrinth_box.image_relief": None}):
                exit_code = main(
                    [
                        "--cavity-diameter", "30",
                        "--cavity-length", "45",
                        "--difficulty", "1",
                        "--seed", "17",
                        "--angular-facets", "64",
                        "--output-dir", temporary_directory,
                    ]
                )
        self.assertEqual(exit_code, 0)

    def test_image_relief_emboss_and_engrave_export_valid_single_body_meshes(self) -> None:
        trimesh = importlib.import_module("trimesh")
        for mode in ("emboss", "engrave"):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    root = Path(temporary_directory)
                    image = root / "relief.png"
                    output = root / mode
                    self._write_test_image(image)
                    exit_code = main(
                        [
                            "--cavity-diameter", "30",
                            "--cavity-length", "45",
                            "--difficulty", "1",
                            "--seed", "17",
                            "--angular-facets", "64",
                            "--decoration-mode", mode,
                            "--decoration-depth", "0.4",
                            "--image-relief", str(image),
                            "--image-relief-resolution", "32",
                            "--output-dir", str(output),
                        ]
                    )
                    self.assertEqual(exit_code, 0)
                    for filename in ("inner.stl", "outer.stl"):
                        mesh = trimesh.load_mesh(
                            output / filename, force="mesh", process=True
                        )
                        self.assertTrue(mesh.is_watertight)
                        self.assertTrue(mesh.is_winding_consistent)
                        self.assertGreater(mesh.volume, 0.0)
                        self.assertEqual(len(mesh.split(only_watertight=False)), 1)
                        self.assertAlmostEqual(mesh.bounds[0][2], 0.0, places=4)


    def test_zero_grip_applies_full_image_to_sleeve_and_records_basename(self) -> None:
        trimesh = importlib.import_module("trimesh")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image = root / "relief.png"
            output = root / "out"
            self._write_test_image(image)

            exit_code = main(
                [
                    "--cavity-diameter", "30",
                    "--cavity-length", "45",
                    "--difficulty", "1",
                    "--seed", "17",
                    "--angular-facets", "64",
                    "--grip-length", "0",
                    "--decoration-depth", "0.4",
                    "--image-relief", str(image),
                    "--image-relief-resolution", "32",
                    "--output-dir", str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            mesh = trimesh.load_mesh(output / "outer.stl", force="mesh", process=True)
            self.assertTrue(mesh.is_watertight)
            self.assertTrue(mesh.is_winding_consistent)
            self.assertGreater(mesh.volume, 0.0)
            self.assertEqual(len(mesh.split(only_watertight=False)), 1)
            self.assertAlmostEqual(mesh.bounds[0][2], 0.0, places=4)

            manifest = json.loads((output / "maze.json").read_text())
            self.assertEqual(manifest["config"]["grip_length"], 0.0)
            self.assertEqual(manifest["config"]["image_relief_path"], "relief.png")

    def test_inverted_engrave_relief_still_exports_a_valid_single_body(self) -> None:
        trimesh = importlib.import_module("trimesh")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image = root / "relief.png"
            output = root / "out"
            self._write_test_image(image)

            exit_code = main(
                [
                    "--cavity-diameter", "30",
                    "--cavity-length", "45",
                    "--difficulty", "1",
                    "--seed", "17",
                    "--angular-facets", "64",
                    "--decoration-depth", "0.4",
                    "--image-relief", str(image),
                    "--image-relief-resolution", "32",
                    "--image-relief-invert",
                    "--output-dir", str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            mesh = trimesh.load_mesh(output / "inner.stl", force="mesh", process=True)
            self.assertTrue(mesh.is_watertight)
            self.assertEqual(len(mesh.split(only_watertight=False)), 1)

    def test_relief_failure_leaves_output_directory_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            corrupt = root / "corrupt.png"
            corrupt.write_bytes(b"definitely not an image")
            output = root / "out"
            output.mkdir()
            (output / "sentinel.txt").write_text("keep")

            stderr = io.StringIO()
            with mock.patch("sys.stderr", stderr):
                exit_code = main(
                    [
                        "--cavity-diameter", "30",
                        "--cavity-length", "45",
                        "--difficulty", "1",
                        "--seed", "17",
                        "--angular-facets", "64",
                        "--image-relief", str(corrupt),
                        "--image-relief-resolution", "32",
                        "--output-dir", str(output),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("image relief", stderr.getvalue().lower())
            self.assertEqual(
                sorted(path.name for path in output.iterdir()), ["sentinel.txt"]
            )

    def test_step_exports_are_unchanged_when_image_relief_is_applied(self) -> None:
        cadquery = importlib.import_module("cadquery")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            image = root / "relief.png"
            plain = root / "plain"
            decorated = root / "decorated"
            self._write_test_image(image)
            common_args = [
                "--cavity-diameter", "30",
                "--cavity-length", "45",
                "--difficulty", "1",
                "--seed", "17",
                "--angular-facets", "64",
            ]

            self.assertEqual(main(common_args + ["--output-dir", str(plain)]), 0)
            self.assertEqual(
                main(
                    common_args
                    + [
                        "--image-relief", str(image),
                        "--image-relief-resolution", "32",
                        "--output-dir", str(decorated),
                    ]
                ),
                0,
            )

            for filename in ("inner.step", "outer.step"):
                with self.subTest(filename=filename):
                    plain_volume = (
                        cadquery.importers.importStep(str(plain / filename))
                        .val()
                        .Volume()
                    )
                    decorated_volume = (
                        cadquery.importers.importStep(str(decorated / filename))
                        .val()
                        .Volume()
                    )
                    self.assertAlmostEqual(
                        plain_volume,
                        decorated_volume,
                        delta=1e-6 * max(plain_volume, 1.0),
                    )


if __name__ == "__main__":
    unittest.main()
