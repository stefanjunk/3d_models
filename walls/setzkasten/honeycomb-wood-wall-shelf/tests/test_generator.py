from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "scripts"))

import generate_textured_mesh as generator  # noqa: E402


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.params = json.loads((PROJECT_DIR / "parameters.json").read_text(encoding="utf-8"))

    def test_draft_module_is_single_watertight_positive_volume(self) -> None:
        _vertices, _faces, report = generator.build_module(self.params, pitch_override=1.2)
        self.assertTrue(report["watertight"])
        self.assertEqual(report["boundary_edges"], 0)
        self.assertEqual(report["nonmanifold_edges"], 0)
        self.assertEqual(report["inconsistent_winding_edges"], 0)
        self.assertEqual(report["oriented_components"], 1)
        self.assertGreater(report["signed_volume_mm3"], 0)
        self.assertAlmostEqual(report["bounds_size_mm"][0], 168.0, places=5)
        self.assertFalse(report["derived"]["back_panel_enabled"])
        self.assertAlmostEqual(report["derived"]["nominal_inside_depth_mm"], 72.0)

    def test_closed_back_option_remains_watertight(self) -> None:
        params = copy.deepcopy(self.params)
        params["module"]["back_panel_enabled"] = True
        _vertices, _faces, report = generator.build_module(params, pitch_override=1.2)
        self.assertTrue(report["watertight"])
        self.assertEqual(report["oriented_components"], 1)
        self.assertTrue(report["derived"]["back_panel_enabled"])
        self.assertAlmostEqual(
            report["derived"]["nominal_inside_depth_mm"],
            params["module"]["depth"] - params["module"]["back_thickness"],
        )

    def test_impossible_wall_is_rejected(self) -> None:
        params = copy.deepcopy(self.params)
        params["module"]["wall_thickness"] = 100.0
        with self.assertRaises(ValueError):
            generator.build_module(params, pitch_override=2.0)

    def test_impossible_back_is_rejected(self) -> None:
        params = copy.deepcopy(self.params)
        params["module"]["back_thickness"] = params["module"]["depth"]
        with self.assertRaises(ValueError):
            generator.build_module(params, pitch_override=2.0)

    def test_impossible_mounting_ear_is_rejected(self) -> None:
        params = copy.deepcopy(self.params)
        params["mounting"]["ear_thickness"] = params["module"]["depth"]
        with self.assertRaises(ValueError):
            generator.build_module(params, pitch_override=2.0)


if __name__ == "__main__":
    unittest.main()
