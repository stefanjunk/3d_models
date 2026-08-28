#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
import build


class GemStageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads((ROOT / "config/model-parameters.json").read_text())
        cls.shape, cls.metrics = build.make_rack(cls.p)

    def test_supported_station_count(self):
        self.assertEqual(self.p["rack"]["tray_stations"], 6)

    def test_portfolio_envelope(self):
        self.assertLessEqual(self.p["rack"]["outer_width_mm"], 220)
        self.assertLessEqual(self.p["rack"]["outer_depth_mm"], 160)
        self.assertLessEqual(self.p["rack"]["outer_height_mm"], 140)

    def test_side_clearance(self):
        self.assertGreaterEqual(self.metrics["side_clearance_each_mm"] + 1e-9, self.p["tray"]["minimum_side_clearance_each_mm"])

    def test_vertical_clearance(self):
        self.assertGreaterEqual(self.metrics["vertical_clearance_mm"], self.p["tray"]["minimum_vertical_clearance_mm"])

    def test_rearward_fall(self):
        self.assertTrue(all(level["rearward_fall_mm"] > 0 for level in self.metrics["levels"]))

    def test_center_opening(self):
        self.assertGreaterEqual(self.p["rack"]["center_front_opening_mm"], 40)

    def test_single_solid(self):
        self.assertEqual(len(self.shape.solids().vals()), 1)

    def test_oriented_height(self):
        oriented = build.manufacturing_orientation(self.shape)
        self.assertLessEqual(oriented.val().BoundingBox().zlen, self.p["rack"]["outer_width_mm"] + 0.01)


if __name__ == "__main__":
    unittest.main()
