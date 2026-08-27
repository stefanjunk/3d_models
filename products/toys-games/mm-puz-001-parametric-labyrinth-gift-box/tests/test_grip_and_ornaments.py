from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

import cadquery as cq
import trimesh

from generate_labyrinth_box import export_box
from labyrinth_box.config import BoxConfig
from labyrinth_box.geometry import build_labyrinth_box
from labyrinth_box.preflight import (
    PrintabilityWarning,
    UnsafeParametersError,
    validate_and_derive,
)


class GripAndOrnamentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BoxConfig(
            cavity_diameter=30.0,
            cavity_length=45.0,
            difficulty=1,
            seed=17,
            angular_facets=64,
        )

    def test_config_exposes_approved_extension_defaults(self) -> None:
        expected = {
            "grip_length": 15.0,
            "ornament_type": "none",
            "decoration_mode": "engrave",
            "decoration_depth": 0.6,
            "decoration_count": 16,
            "decoration_margin": 3.0,
            "image_relief_path": None,
            "image_relief_resolution": 256,
            "image_relief_invert": False,
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertTrue(hasattr(self.config, name), f"missing BoxConfig.{name}")
                self.assertEqual(getattr(self.config, name), value)

    def test_grip_extends_assembly_below_zero_with_closed_silhouette_radius(self) -> None:
        result = build_labyrinth_box(self.config)
        bounds = result.inner.val().BoundingBox()

        self.assertAlmostEqual(bounds.zmin, -self.config.grip_length, places=4)
        self.assertAlmostEqual(bounds.zmax, result.dimensions.inner_height, places=4)
        self.assertAlmostEqual(bounds.zlen, result.dimensions.inner_total_extent, places=4)
        self.assertAlmostEqual(
            result.dimensions.grip_radius,
            result.dimensions.sleeve_outer_radius,
            places=6,
        )
        self.assertAlmostEqual(bounds.xlen, 2.0 * result.dimensions.grip_radius, places=3)
        self.assertTrue(
            result.inner.val().isInside(
                (result.dimensions.grip_radius - 0.05, 0.0, -self.config.grip_length / 2.0)
            )
        )

    def test_zero_grip_preserves_original_assembly_z_bounds(self) -> None:
        config = replace(self.config, grip_length=0.0)
        result = build_labyrinth_box(config)
        bounds = result.inner.val().BoundingBox()

        self.assertAlmostEqual(bounds.zmin, 0.0, places=4)
        self.assertAlmostEqual(bounds.zlen, result.dimensions.inner_height, places=4)
        self.assertAlmostEqual(
            result.dimensions.inner_total_extent,
            result.dimensions.inner_height,
            places=6,
        )

    def test_grip_does_not_create_assembled_intersection(self) -> None:
        for location in ("inner", "outer"):
            with self.subTest(location=location):
                result = build_labyrinth_box(replace(self.config, maze_location=location))
                self.assertLess(
                    result.inner.val().intersect(result.outer.val()).Volume(),
                    1e-5,
                )

    def test_print_exports_put_grip_down_at_zero_for_stl_and_step(self) -> None:
        result = build_labyrinth_box(self.config)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            export_box(result, output)

            mesh = trimesh.load_mesh(output / "inner.stl", force="mesh", process=True)
            step = cq.importers.importStep(str(output / "inner.step"))

            self.assertAlmostEqual(mesh.bounds[0][2], 0.0, places=4)
            self.assertAlmostEqual(
                mesh.extents[2], result.dimensions.inner_total_extent, places=3
            )
            self.assertAlmostEqual(step.val().BoundingBox().zmin, 0.0, places=4)
            self.assertAlmostEqual(
                step.val().BoundingBox().zlen,
                result.dimensions.inner_total_extent,
                places=3,
            )

    def test_grip_length_rejects_negative_and_nonfinite_values(self) -> None:
        for value in (-0.01, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertWarnsRegex(PrintabilityWarning, "grip_length"):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(replace(self.config, grip_length=value))

    def test_decoration_parameters_reject_invalid_values(self) -> None:
        invalid = (
            ("ornament_type", "stars"),
            ("decoration_mode", "raised"),
            ("decoration_depth", float("nan")),
            ("decoration_depth", 0.0),
            ("decoration_depth", 2.1),
            ("decoration_count", 2),
            ("decoration_count", 129),
            ("decoration_margin", -0.1),
            ("image_relief_resolution", 31),
            ("image_relief_resolution", 1025),
        )
        for field, value in invalid:
            with self.subTest(field=field, value=value):
                with self.assertWarnsRegex(PrintabilityWarning, field):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(replace(self.config, **{field: value}))

    def test_decorated_grip_requires_a_usable_margin_band(self) -> None:
        config = replace(
            self.config,
            grip_length=6.0,
            ornament_type="flutes",
            decoration_margin=3.0,
        )
        with self.assertWarnsRegex(PrintabilityWarning, "grip decoration band"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_enabled_decoration_requires_a_positive_edge_and_seam_margin(self) -> None:
        config = replace(
            self.config,
            ornament_type="rings",
            decoration_margin=0.0,
        )
        with self.assertWarnsRegex(PrintabilityWarning, "decoration_margin"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_image_relief_rejects_combined_builtin_ornaments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            image = Path(temporary_directory) / "art.png"
            image.write_bytes(b"png-bytes")
            config = replace(
                self.config,
                ornament_type="flutes",
                image_relief_path=str(image),
            )
            with self.assertWarnsRegex(PrintabilityWarning, "cannot be combined"):
                with self.assertRaises(UnsafeParametersError):
                    validate_and_derive(config)

    def test_rings_reject_axial_pitch_below_minimum_feature(self) -> None:
        config = replace(
            self.config,
            ornament_type="rings",
            decoration_count=128,
        )
        with self.assertWarnsRegex(PrintabilityWarning, "rings"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_outer_maze_engraving_accounts_for_channel_and_decoration_depth(self) -> None:
        config = replace(
            self.config,
            maze_location="outer",
            ornament_type="rings",
            decoration_mode="engrave",
            outer_wall=3.4,
            channel_depth=1.2,
            decoration_depth=0.8,
            minimum_wall=1.6,
        )
        with self.assertWarnsRegex(PrintabilityWarning, "outer wall"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_every_built_in_ornament_and_mode_produces_valid_single_solids(self) -> None:
        for ornament in ("flutes", "diamonds", "rings"):
            for mode in ("engrave", "emboss"):
                with self.subTest(ornament=ornament, mode=mode):
                    config = replace(
                        self.config,
                        ornament_type=ornament,
                        decoration_mode=mode,
                        decoration_count=6,
                    )
                    result = build_labyrinth_box(config)
                    for part in (result.inner, result.outer):
                        self.assertTrue(part.val().isValid())
                        self.assertEqual(len(part.solids().vals()), 1)
                        self.assertGreater(part.val().Volume(), 0.0)
                    if mode == "emboss":
                        self.assertGreater(
                            result.outer.val().BoundingBox().xlen,
                            2.0 * result.dimensions.sleeve_outer_radius,
                        )
                    else:
                        self.assertAlmostEqual(
                            result.outer.val().BoundingBox().xlen,
                            2.0 * result.dimensions.sleeve_outer_radius,
                            places=3,
                        )


if __name__ == "__main__":
    unittest.main()
