from dataclasses import replace
import unittest

from labyrinth_box.config import BoxConfig
from labyrinth_box.preflight import (
    PrintabilityWarning,
    UnsafeParametersError,
    requested_grid,
    validate_and_derive,
)


class PreflightTests(unittest.TestCase):
    def test_default_configuration_is_printable(self) -> None:
        config = BoxConfig()

        derived = validate_and_derive(config)

        self.assertGreater(derived.inner_outer_radius, config.cavity_diameter / 2)
        self.assertGreater(derived.sleeve_outer_radius, derived.sleeve_inner_radius)
        self.assertGreaterEqual(derived.row_pitch, derived.minimum_pitch)
        self.assertGreaterEqual(derived.column_pitch, derived.minimum_pitch)
        self.assertEqual((derived.rows, derived.columns), requested_grid(config.difficulty))

    def test_difficulty_increases_grid_density(self) -> None:
        easy = requested_grid(1)
        hard = requested_grid(10)

        self.assertGreater(hard[0], easy[0])
        self.assertGreater(hard[1], easy[1])

    def test_small_box_warns_and_stops_before_export(self) -> None:
        config = BoxConfig(cavity_diameter=15.0, cavity_length=25.0, difficulty=10)

        with self.assertWarnsRegex(PrintabilityWarning, "difficulty 10"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_inner_maze_requires_residual_inner_wall(self) -> None:
        config = replace(
            BoxConfig(maze_location="inner"),
            inner_wall=2.0,
            channel_depth=1.0,
            minimum_wall=1.6,
        )

        with self.assertWarnsRegex(PrintabilityWarning, "inner wall"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_outer_maze_requires_residual_outer_wall(self) -> None:
        config = replace(
            BoxConfig(maze_location="outer"),
            outer_wall=2.0,
            channel_depth=1.0,
            minimum_wall=1.6,
        )

        with self.assertWarnsRegex(PrintabilityWarning, "outer wall"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_maze_margin_preserves_one_closed_end_band(self) -> None:
        config = replace(BoxConfig(), maze_margin=1.0)

        with self.assertWarnsRegex(PrintabilityWarning, "maze_margin"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_follower_clearance_must_be_positive(self) -> None:
        for clearance in (0.0, -0.25):
            with self.subTest(clearance=clearance):
                config = replace(BoxConfig(), follower_clearance=clearance)
                with self.assertWarnsRegex(PrintabilityWarning, "follower_clearance"):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(config)

    def test_inner_maze_spacing_is_checked_at_groove_floor(self) -> None:
        config = BoxConfig(
            cavity_diameter=4.0,
            cavity_length=45.0,
            difficulty=1,
            maze_location="inner",
            inner_wall=3.2,
            channel_depth=1.6,
        )

        with self.assertWarnsRegex(PrintabilityWarning, "difficulty 1"):
            with self.assertRaises(UnsafeParametersError):
                validate_and_derive(config)

    def test_bottom_and_cap_must_meet_minimum_wall(self) -> None:
        for field in ("bottom_thickness", "cap_thickness"):
            with self.subTest(field=field):
                config = replace(BoxConfig(), **{field: 0.6})
                with self.assertWarnsRegex(PrintabilityWarning, field):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(config)

    def test_nozzle_safety_thresholds_cannot_be_lowered_below_floors(self) -> None:
        unsafe_values = {
            "minimum_wall": 0.6,
            "minimum_web": 0.6,
            "minimum_feature": 0.3,
        }
        for field, value in unsafe_values.items():
            with self.subTest(field=field):
                config = replace(BoxConfig(), **{field: value})
                with self.assertWarnsRegex(PrintabilityWarning, field):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(config)

    def test_channel_facets_scale_with_large_radius(self) -> None:
        config = BoxConfig(
            cavity_diameter=200.0,
            cavity_length=45.0,
            difficulty=1,
            angular_facets=48,
        )

        derived = validate_and_derive(config)

        self.assertGreater(derived.angular_facets, config.angular_facets)

    def test_non_finite_dimensions_warn_and_stop(self) -> None:
        for field, value in (
            ("cavity_diameter", float("nan")),
            ("cavity_length", float("inf")),
        ):
            with self.subTest(field=field):
                config = replace(BoxConfig(), **{field: value})
                with self.assertWarnsRegex(PrintabilityWarning, "finite"):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(config)

    def test_stl_tolerances_must_be_positive_and_print_appropriate(self) -> None:
        unsafe_values = {
            "stl_tolerance": -0.1,
            "stl_angular_tolerance": 0.8,
        }
        for field, value in unsafe_values.items():
            with self.subTest(field=field):
                config = replace(BoxConfig(), **{field: value})
                with self.assertWarnsRegex(PrintabilityWarning, field):
                    with self.assertRaises(UnsafeParametersError):
                        validate_and_derive(config)


if __name__ == "__main__":
    unittest.main()
