#!/usr/bin/env python3
"""Fast regression tests for the R1.3 physical-aspect correction."""

from __future__ import annotations

import unittest

from prepare_relief import repeat_tile_size, source_physical_size


class AspectPreservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.processing = {
            "repeat_tile": {
                "size_policy": "preserve_source_aspect",
                "anchor_axis": "width",
                "anchor_mm": 180.0,
            }
        }

    def test_steel_source_registers_as_180_by_120_mm(self) -> None:
        spec = {
            "physical_authoring": {
                "width_mm": 180.0,
                "height_mm": 120.0,
                "replacement_height_policy": "derive_from_square_pixel_source_aspect",
            }
        }
        width, height, _ = source_physical_size(spec, 1536, 1024)
        self.assertEqual(width, 180.0)
        self.assertEqual(height, 120.0)

    def test_repeat_tile_derives_second_axis_uniformly(self) -> None:
        width, height, metadata = repeat_tile_size(self.processing, 1.5, False)
        self.assertEqual((width, height), (180.0, 120.0))
        self.assertEqual(metadata["requested_aspect_error_pct"], 0.0)

    def test_square_tile_is_rejected_for_three_to_two_source(self) -> None:
        bad = {
            "repeat_tile": {
                "size_policy": "explicit",
                "anchor_axis": "width",
                "anchor_mm": 180.0,
                "size_mm": [180.0, 180.0],
            }
        }
        with self.assertRaisesRegex(ValueError, "change physical aspect"):
            repeat_tile_size(bad, 1.5, False)


if __name__ == "__main__":
    unittest.main()
