from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_root = Path(__file__).resolve().parents[1]

    def test_all_examples_build_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "examples"
            completed = subprocess.run(
                [sys.executable, str(self.skill_root / "scripts" / "run_examples.py"), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertTrue(summary["success"])
            for name in ("barefoot-shoe", "organic-bowl", "rc-car-sporty-envelope"):
                validation = json.loads((output / name / "validation.json").read_text(encoding="utf-8"))
                self.assertTrue(validation["success"], name)
                self.assertTrue(any((output / name).glob("*.obj")), name)
                self.assertTrue(any((output / name).glob("*.stl")), name)


if __name__ == "__main__":
    unittest.main()
