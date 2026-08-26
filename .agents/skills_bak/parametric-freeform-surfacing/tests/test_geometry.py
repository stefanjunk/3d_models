from __future__ import annotations

import unittest

import numpy as np

from surface_geometry import (
    curve_metrics,
    extrude_closed_profile,
    ffd_deform_vertices,
    fourier_smooth_closed,
    loft_closed_sections,
    mesh_metrics,
    regularized_smooth,
    weld_vertices,
)


class CurveTests(unittest.TestCase):
    def test_regularized_smoothing_reduces_curvature_variation_and_preserves_ends(self) -> None:
        x = np.linspace(0.0, 100.0, 80)
        y = 8.0 * np.sin(x / 28.0) + 0.8 * np.sin(x * 1.7)
        points = np.column_stack([x, y])
        before = curve_metrics(points)
        after_points = regularized_smooth(points, strength=35.0, preserve_ends=True)
        after = curve_metrics(after_points)
        self.assertTrue(np.allclose(points[[0, -1]], after_points[[0, -1]], atol=1e-5))
        self.assertLess(after["curvature_total_variation"], before["curvature_total_variation"])

    def test_fourier_smoothing_removes_high_frequency_closed_noise(self) -> None:
        theta = np.linspace(0.0, 2.0 * np.pi, 160, endpoint=False)
        radius = 40.0 + 4.0 * np.cos(5 * theta) + 0.7 * np.cos(31 * theta)
        points = np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])
        before = curve_metrics(points, closed=True)
        faired = fourier_smooth_closed(points, harmonics=8)
        after = curve_metrics(faired, closed=True)
        self.assertEqual(faired.shape, points.shape)
        self.assertLess(after["curvature_total_variation"], before["curvature_total_variation"])


class MeshTests(unittest.TestCase):
    def test_loft_is_watertight(self) -> None:
        sections = []
        theta = np.linspace(0.0, 2.0 * np.pi, 48, endpoint=False)
        for x, radius in ((0.0, 8.0), (20.0, 13.0), (50.0, 9.0)):
            sections.append(np.column_stack([np.full_like(theta, x), radius * np.cos(theta), radius * np.sin(theta)]))
        vertices, faces, _ = loft_closed_sections(sections, point_count=48)
        metrics = mesh_metrics(vertices, faces)
        self.assertTrue(metrics["watertight_edge_incidence"])
        self.assertEqual(metrics["connected_components"], 1)
        self.assertEqual(metrics["degenerate_face_count"], 0)
        self.assertGreater(metrics["absolute_volume"], 1.0)

    def test_profile_extrusion_is_watertight(self) -> None:
        profile = np.array([[-20.0, -10.0], [25.0, -8.0], [30.0, 8.0], [-15.0, 14.0]])
        vertices, faces = extrude_closed_profile(profile, 0.0, 4.0)
        metrics = mesh_metrics(vertices, faces)
        self.assertTrue(metrics["watertight_edge_incidence"])
        self.assertEqual(metrics["degenerate_face_count"], 0)

    def test_welded_patch_mesh_recovers_shared_edges(self) -> None:
        vertices = np.array([
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0],
        ])
        faces = np.array([[0, 1, 2], [3, 4, 5]])
        welded_vertices, welded_faces = weld_vertices(vertices, faces, tolerance=1e-9)
        self.assertEqual(len(welded_vertices), 4)
        self.assertEqual(len(welded_faces), 2)



class FFDTests(unittest.TestCase):
    def test_identity_ffd_reproduces_vertices(self) -> None:
        vertices = np.array([
            [-1.0, -2.0, -3.0],
            [2.0, -2.0, -3.0],
            [-1.0, 4.0, -3.0],
            [-1.0, -2.0, 5.0],
            [2.0, 4.0, 5.0],
        ])
        deformed, report = ffd_deform_vertices(vertices, {"lattice": [3, 3, 3], "displacements": []})
        self.assertTrue(np.allclose(vertices, deformed, atol=1e-10))
        self.assertLess(report["maximum_displacement_mm"], 1e-9)

    def test_fixed_box_prevents_deformation_inside_region(self) -> None:
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [0.0, 10.0, 0.0],
            [0.0, 0.0, 10.0],
            [10.0, 10.0, 10.0],
        ])
        config = {
            "lattice": [2, 2, 2],
            "displacements": [{"index": [1, 1, 1], "delta_mm": [3.0, 4.0, 5.0]}],
            "fixed_boxes": [{"minimum_mm": [-0.1, -0.1, -0.1], "maximum_mm": [0.1, 0.1, 0.1], "falloff_mm": 0.0}],
        }
        deformed, report = ffd_deform_vertices(vertices, config)
        self.assertTrue(np.allclose(deformed[0], vertices[0]))
        self.assertGreater(np.linalg.norm(deformed[-1] - vertices[-1]), 0.1)
        self.assertEqual(report["fixed_vertex_count"], 1)


if __name__ == "__main__":
    unittest.main()
