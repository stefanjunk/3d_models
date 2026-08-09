from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_generators(self) -> None:
        if importlib.util.find_spec("cadquery") is None:
            self.skipTest("CadQuery is an optional dependency")
        mapping = {
            "dice-tower": "functional_parts.py",
            "barefoot-shoe": "sole_generator.py",
            "unicorn-compartment": "compartment_parts.py",
        }
        with tempfile.TemporaryDirectory() as td:
            for name, script_name in mapping.items():
                with self.subTest(example=name):
                    out = Path(td) / name
                    proc = subprocess.run([sys.executable, str(SKILL / "examples" / name / script_name), "--out", str(out)], capture_output=True, text=True)
                    self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                    self.assertGreater(len(list(out.glob("*.stl"))), 0)
                    self.assertGreater(len(list(out.glob("*.step"))), 0)


if __name__ == "__main__":
    unittest.main()
