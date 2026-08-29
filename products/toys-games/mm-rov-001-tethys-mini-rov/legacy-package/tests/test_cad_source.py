import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))

from generate_parts import make_parts  # noqa: E402


class CadSourceTests(unittest.TestCase):
    def test_unique_names_and_positive_quantities(self):
        parts = make_parts()
        names = [part.name for part in parts]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(part.quantity > 0 for part in parts))

    def test_critical_guard_clearance_is_documented(self):
        nozzle = next(part for part in make_parts() if part.name == "thruster_nozzle_60mm")
        self.assertIn("68 mm clear bore", nozzle.note)


if __name__ == "__main__":
    unittest.main()
