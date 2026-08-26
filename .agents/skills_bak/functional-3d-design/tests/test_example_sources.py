from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
EXAMPLES = SKILL / "examples"
SCRIPTS = SKILL / "scripts"


class ExampleSourceTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("cadquery") is not None, "cadquery unavailable")
    def test_cadquery_examples_export_valid_meshes(self) -> None:
        for name in ["honeycomb-wall-shelf", "rounded-desk-organizer"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                example = EXAMPLES / name
                proc = subprocess.run(
                    [sys.executable, str(example / "model.py"), "--out", td],
                    cwd=example,
                    capture_output=True,
                    text=True,
                    timeout=240,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, f"{proc.stdout}\n{proc.stderr}")
                stls = list(Path(td).glob("*.stl"))
                self.assertGreater(len(stls), 0)
                for stl in stls:
                    check = subprocess.run(
                        [sys.executable, str(SCRIPTS / "validate_mesh.py"), str(stl), "--require-watertight", "--max-bodies", "1", "--quiet"],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        check=False,
                    )
                    self.assertEqual(check.returncode, 0, f"{stl}\n{check.stdout}\n{check.stderr}")

    @unittest.skipUnless(shutil.which("openscad"), "openscad unavailable")
    def test_openscad_examples_export_valid_meshes(self) -> None:
        cases = [
            ("unicorn-dice-tower", ["openscad", "-o", "{out}/tower.stl", "model.scad"], ["tower.stl"]),
            ("calibration-coupons", ["openscad", "-D", 'coupon="fit"', "-o", "{out}/fit.stl", "model.scad"], ["fit.stl"]),
        ]
        for name, template, outputs in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                example = EXAMPLES / name
                command = [part.replace("{out}", td) for part in template]
                proc = subprocess.run(command, cwd=example, capture_output=True, text=True, timeout=240, check=False)
                self.assertEqual(proc.returncode, 0, f"{proc.stdout}\n{proc.stderr}")
                for output in outputs:
                    stl = Path(td) / output
                    check = subprocess.run(
                        [sys.executable, str(SCRIPTS / "validate_mesh.py"), str(stl), "--require-watertight", "--max-bodies", "1", "--quiet"],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        check=False,
                    )
                    self.assertEqual(check.returncode, 0, f"{stl}\n{check.stdout}\n{check.stderr}")


if __name__ == "__main__":
    unittest.main()
