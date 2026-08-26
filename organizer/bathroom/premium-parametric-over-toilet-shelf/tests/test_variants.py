from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.over_toilet_shelf import build_model, validate_config  # noqa: E402
from src.image_relief import _prepare_field  # noqa: E402


class VariantBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.default = json.loads((ROOT / "parameters.json").read_text(encoding="utf-8"))

    def test_parameters_identify_floor_standing_revision(self) -> None:
        self.assertEqual(self.default["project"]["revision"], "0.2.0")
        self.assertEqual(
            self.default["installation"]["mode"],
            "floor_standing_with_wall_restraint",
        )

    def test_default_validation_derived_values(self) -> None:
        derived = validate_config(deepcopy(self.default))

        self.assertEqual(derived["clear_width"], 620.0)
        self.assertEqual(derived["shelf_z_values"], [1050.0, 1400.0])
        self.assertEqual(derived["tile_count"], 3)
        self.assertEqual(derived["side_segment_count"], 7)
        self.assertEqual(derived["floor_contact_count"], 4)
        self.assertEqual(derived["wall_restraint_count"], 2)
        self.assertLessEqual(derived["side_segment_print_height"], 256.0)
        self.assertEqual(derived["overall_envelope_mm"], [680.0, 300.0, 1650.0])
        self.assertEqual(derived["module_seam_joiner_quantity"], 6)
        self.assertEqual(derived["module_seam_plate_boss_contact_gap_mm"], 0.0)

    def test_default_build_inventory(self) -> None:
        # Keep this as the suite's only full geometry build.
        result = build_model(deepcopy(self.default))

        self.assertEqual(len(result.print_parts), 42)
        self.assertEqual(result.derived["print_part_file_count"], 42)
        self.assertEqual(len(result.assembly_parts), 63)
        self.assertEqual(result.derived["assembly_body_count"], 63)
        self.assertEqual(result.derived["module_seam_plate_boss_contact_gap_mm"], 0.0)

        assembly_names = {part.name for part in result.assembly_parts}
        self.assertTrue(
            {
                "left_rear_floor_foot",
                "left_front_floor_foot",
                "right_rear_floor_foot",
                "right_front_floor_foot",
                "left_wall_restraint_spacer",
                "right_wall_restraint_spacer",
            }.issubset(assembly_names)
        )

        print_names = {part.name for part in result.print_parts}
        self.assertTrue(
            {
                "level_01_module_01_drawer_housing_left_print",
                "level_01_module_01_drawer_housing_right_print",
                "level_01_module_01_drawer_left_print",
                "level_01_module_01_drawer_right_print",
                "level_01_module_02_bin_left_print",
                "level_01_module_02_bin_right_print",
                "wide_module_m3_seam_coupon_print",
                "floor_foot_tpu_lock_coupon_print",
            }.issubset(print_names)
        )

        seam = self.default["module_grid"]["wide_module_seam"]
        boss_height = float(seam["boss_height"])
        bodies = {part.name: part.solid for part in result.assembly_parts}
        contact_cases = {
            "level_1_drawer_housing_1_seam_joiner_1": 1050.0 + 92.0 + boss_height,
            "level_1_drawer_1_seam_joiner_1": (
                1050.0
                + float(self.default["module_grid"]["wall"])
                + float(self.default["module_grid"]["drawer_clearance_vertical"]) / 2.0
                + boss_height
            ),
            "level_1_bin_2_seam_joiner_1": 1050.0 + boss_height,
        }
        for name, expected_zmin in contact_cases.items():
            self.assertAlmostEqual(
                bodies[name].val().BoundingBox().zmin,
                expected_zmin,
                places=6,
                msg=f"{name} must sit directly on its two module bosses",
            )

    def test_valid_alternate_floor_standing_configuration(self) -> None:
        config = deepcopy(self.default)
        config["installation"].update(
            {
                "overall_width": 700.0,
                "overall_depth": 320.0,
                "overall_height": 1700.0,
                "wall_gap": 30.0,
            }
        )

        derived = validate_config(config)

        self.assertEqual(derived["overall_envelope_mm"], [700.0, 320.0, 1700.0])
        self.assertLessEqual(derived["side_segment_print_height"], 256.0)

    def test_rejects_legacy_installation_mode(self) -> None:
        config = deepcopy(self.default)
        config["installation"]["mode"] = "cistern_top_supported"
        with self.assertRaisesRegex(ValueError, "floor-standing installation"):
            validate_config(config)

    def test_rejects_insufficient_clear_wall_width(self) -> None:
        config = deepcopy(self.default)
        config["installation"]["clear_wall_width"] = (
            config["installation"]["overall_width"] - 1.0
        )
        with self.assertRaisesRegex(ValueError, "measured clear wall width"):
            validate_config(config)

    def test_rejects_shelf_level_off_grid(self) -> None:
        config = deepcopy(self.default)
        config["levels"][0]["shelf_top_z"] += 1.0
        with self.assertRaisesRegex(ValueError, "not aligned to the frame grid"):
            validate_config(config)

    def test_rejects_foot_footprint_beyond_overall_width(self) -> None:
        config = deepcopy(self.default)
        config["frame"]["foot_width"] += 1.0
        with self.assertRaisesRegex(ValueError, "Four-foot footprint"):
            validate_config(config)

    def test_rejects_side_segment_extent_beyond_256_mm_bed(self) -> None:
        config = deepcopy(self.default)
        config["frame"]["connector_pin_height"] = config["printer"]["build_volume"][0]
        with self.assertRaisesRegex(ValueError, "Side segment does not fit"):
            validate_config(config)

    def test_rejects_wide_module_seam_plate_air_gap(self) -> None:
        config = deepcopy(self.default)
        config["module_grid"]["wide_module_seam"]["plate_boss_contact_gap"] = 0.10
        with self.assertRaisesRegex(ValueError, "must contact their boss tops"):
            validate_config(config)

    def test_cover_fit_preserves_physical_scale(self) -> None:
        source = np.linspace(0.0, 1.0, 300 * 100, dtype=np.float64).reshape(100, 300)
        field, metadata = _prepare_field(source, 180.0, 70.0, 0.60, "cover")
        self.assertEqual(field.shape, (118, 301))
        placed_aspect = metadata["placed_width_mm"] / metadata["placed_height_mm"]
        self.assertLess(abs(placed_aspect / 3.0 - 1.0), 0.0075)

        tall = source.T
        field, metadata = _prepare_field(tall, 180.0, 70.0, 0.60, "cover")
        self.assertEqual(field.shape, (118, 301))
        placed_aspect = metadata["placed_width_mm"] / metadata["placed_height_mm"]
        self.assertLess(abs(placed_aspect / (1.0 / 3.0) - 1.0), 0.0075)


if __name__ == "__main__":
    unittest.main()
