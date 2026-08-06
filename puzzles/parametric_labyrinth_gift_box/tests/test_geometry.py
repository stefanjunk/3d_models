from dataclasses import replace
import unittest

from labyrinth_box.config import BoxConfig
from labyrinth_box.geometry import (
    _cell_z,
    _follower_at,
    _shortest_column_delta,
    build_labyrinth_box,
)


class GeometryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BoxConfig(
            cavity_diameter=30.0,
            cavity_length=45.0,
            difficulty=1,
            seed=17,
            angular_facets=64,
        )

    def _assert_solution_clear(self, result) -> None:
        maze_part = (
            result.inner if result.config.maze_location == "inner" else result.outer
        )
        angle_step = 360.0 / result.maze.columns
        poses: list[tuple[float, float]] = []

        for cell in result.maze.solution:
            poses.append(
                (
                    cell[1] * angle_step,
                    _cell_z(cell[0], result.config, result.dimensions),
                )
            )
        for first, second in zip(result.maze.solution, result.maze.solution[1:]):
            first_angle = first[1] * angle_step
            column_delta = _shortest_column_delta(
                first[1], second[1], result.maze.columns
            )
            second_angle = first_angle + column_delta * angle_step
            first_z = _cell_z(first[0], result.config, result.dimensions)
            second_z = _cell_z(second[0], result.config, result.dimensions)
            poses.append(
                ((first_angle + second_angle) / 2.0, (first_z + second_z) / 2.0)
            )

        for angle, center_z in poses:
            follower = _follower_at(
                result.config, result.dimensions, angle, center_z
            )
            overlap = follower.val().intersect(maze_part.val()).Volume()
            self.assertLess(overlap, 1e-5)

    def test_inner_maze_builds_two_valid_single_solids(self) -> None:
        result = build_labyrinth_box(replace(self.config, maze_location="inner"))

        self.assertTrue(result.inner.val().isValid())
        self.assertTrue(result.outer.val().isValid())
        self.assertEqual(len(result.inner.solids().vals()), 1)
        self.assertEqual(len(result.outer.solids().vals()), 1)
        self.assertGreater(result.inner.val().Volume(), 0)
        self.assertGreater(result.outer.val().Volume(), 0)

    def test_outer_maze_builds_two_valid_single_solids(self) -> None:
        result = build_labyrinth_box(replace(self.config, maze_location="outer"))

        self.assertTrue(result.inner.val().isValid())
        self.assertTrue(result.outer.val().isValid())
        self.assertEqual(len(result.inner.solids().vals()), 1)
        self.assertEqual(len(result.outer.solids().vals()), 1)

    def test_critical_dimensions_match_derived_contract(self) -> None:
        result = build_labyrinth_box(self.config)
        inner_box = result.inner.val().BoundingBox()
        outer_box = result.outer.val().BoundingBox()

        self.assertAlmostEqual(inner_box.zlen, result.dimensions.inner_height, places=4)
        self.assertAlmostEqual(outer_box.zlen, result.dimensions.sleeve_height, places=4)
        self.assertAlmostEqual(
            outer_box.xlen, 2.0 * result.dimensions.sleeve_outer_radius, places=3
        )
        self.assertAlmostEqual(
            result.config.cavity_diameter,
            2.0
            * (
                result.dimensions.inner_outer_radius
                - result.config.inner_wall
            ),
            places=6,
        )

        inner_solid = result.inner.solids().val()
        cavity_radius = result.config.cavity_diameter / 2.0
        cavity_z = result.config.bottom_thickness + result.config.cavity_length / 2.0
        self.assertFalse(inner_solid.isInside((cavity_radius - 0.05, 0, cavity_z)))
        self.assertTrue(inner_solid.isInside((cavity_radius + 0.05, 0, cavity_z)))
        self.assertTrue(
            inner_solid.isInside((0, 0, result.config.bottom_thickness / 2.0))
        )
        self.assertFalse(
            inner_solid.isInside((0, 0, result.config.bottom_thickness + 0.05))
        )

    def test_assembled_parts_have_no_solid_intersection(self) -> None:
        for location in ("inner", "outer"):
            with self.subTest(location=location):
                result = build_labyrinth_box(
                    replace(self.config, maze_location=location)
                )
                overlap = result.inner.val().intersect(result.outer.val())
                self.assertLess(overlap.Volume(), 1e-5)

    def test_follower_uses_round_cross_section_for_corner_clearance(self) -> None:
        result = build_labyrinth_box(replace(self.config, maze_location="outer"))

        cylindrical_faces = result.inner.faces("%CYLINDER").vals()

        self.assertGreaterEqual(len(cylindrical_faces), 3)

    def test_round_follower_clears_solution_nodes_and_edge_midpoints(self) -> None:
        for location in ("inner", "outer"):
            with self.subTest(location=location):
                result = build_labyrinth_box(
                    replace(self.config, maze_location=location)
                )
                self._assert_solution_clear(result)

    def test_large_radius_auto_faceting_preserves_solution_clearance(self) -> None:
        large = BoxConfig(
            cavity_diameter=200.0,
            cavity_length=45.0,
            difficulty=1,
            seed=17,
            angular_facets=48,
        )
        for location in ("inner", "outer"):
            with self.subTest(location=location):
                result = build_labyrinth_box(replace(large, maze_location=location))
                self._assert_solution_clear(result)


if __name__ == "__main__":
    unittest.main()
