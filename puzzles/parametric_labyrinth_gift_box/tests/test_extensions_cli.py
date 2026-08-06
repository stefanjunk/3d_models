import json
from pathlib import Path
import tempfile
import unittest

from generate_labyrinth_box import _build_parser, main


class ExtensionCliTests(unittest.TestCase):
    def test_help_lists_grip_ornament_and_image_relief_flags(self) -> None:
        help_text = _build_parser().format_help()
        for flag in (
            "--grip-length",
            "--ornament-type",
            "--decoration-mode",
            "--decoration-depth",
            "--decoration-count",
            "--decoration-margin",
            "--image-relief",
            "--image-relief-resolution",
            "--image-relief-invert",
        ):
            with self.subTest(flag=flag):
                self.assertIn(flag, help_text)

    def test_manifest_records_grip_decorations_orientation_and_hybrid_fidelity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            exit_code = main(
                [
                    "--cavity-diameter", "30",
                    "--cavity-length", "45",
                    "--difficulty", "1",
                    "--seed", "17",
                    "--angular-facets", "64",
                    "--grip-length", "12",
                    "--ornament-type", "flutes",
                    "--decoration-mode", "emboss",
                    "--decoration-count", "6",
                    "--output-dir", str(output),
                ]
            )

            self.assertEqual(exit_code, 0)
            manifest = json.loads((output / "maze.json").read_text())
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(manifest["config"]["grip_length"], 12.0)
            self.assertEqual(manifest["config"]["ornament_type"], "flutes")
            self.assertEqual(manifest["print_orientation"]["inner"], "grip_down")
            self.assertFalse(manifest["image_relief"]["requested"])
            self.assertFalse(manifest["image_relief"]["step_includes_raster_relief"])
            self.assertTrue(manifest["exact_brep"]["includes_built_in_ornaments"])


if __name__ == "__main__":
    unittest.main()
