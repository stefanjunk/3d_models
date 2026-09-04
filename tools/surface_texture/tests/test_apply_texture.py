from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import texture_lib as tl  # noqa: E402
import apply_texture_patch as atp  # noqa: E402

SHELF_DIR = (
    REPO_ROOT
    / "products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf"
    / "setzkasten/honeycomb-wood-wall-shelf"
)
MASTER = REPO_ROOT / "libraries/surface-textures/wood-001/master/wood-001-tile-16bit.png"
RECIPE = REPO_ROOT / "libraries/surface-textures/wood-001/recipe.json"


class ReferenceCouponRegression(unittest.TestCase):
    def test_coupon_stl_is_byte_identical_to_fresh_shelf_generation(self) -> None:
        """The committed shelf coupon STL drifts from its parameters.json, so
        regression compares against a fresh run of the shelf generator."""
        params = json.loads((SHELF_DIR / "parameters.json").read_text(encoding="utf-8"))
        texture = params["texture"]
        sampler = tl.TileSampler(MASTER)
        mesh = tl.MeshBuilder()
        tl.build_reference_coupon(
            mesh,
            sampler,
            width=70.0,
            height=45.0,
            thickness=2.4,
            depth=float(texture["depth"]),
            edge_taper=float(texture["edge_taper"]),
            pitch=float(texture["mesh_pitch"]),
            tile_width=float(texture["front_tile_width"]),
            tile_height=float(texture["front_tile_height"]),
        )
        vertices, faces, report = mesh.finalized()
        tl.require_valid(report, "regression coupon")
        with tempfile.TemporaryDirectory() as tmp:
            mine = Path(tmp) / "mine.stl"
            tl.write_binary_stl(
                mine, vertices, faces, "Honeycomb wood wall shelf - generated mesh"
            )
            shelf_out = Path(tmp) / "shelf"
            result = subprocess.run(
                [sys.executable, str(SHELF_DIR / "scripts/generate_textured_mesh.py"), "--output-dir", str(shelf_out)],
                capture_output=True,
                text=True,
                cwd=str(SHELF_DIR),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            reference = (shelf_out / "wood-texture-coupon.stl").read_bytes()
            self.assertEqual(mine.read_bytes(), reference)


class ApplicatorSolids(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
        cls.recipe["_path"] = str(RECIPE)
        cls.sampler = tl.TileSampler(MASTER)

    def _build(self, solid: dict) -> dict:
        _v, _f, report = atp.build_solid(self.sampler, self.recipe, solid)
        tl.require_valid(report, solid.get("name", "solid"))
        return report

    def test_textured_prism_is_watertight_single_body(self) -> None:
        report = self._build(
            {
                "name": "prism",
                "kind": "rect",
                "x_range": [-50.0, 50.0],
                "y_range": [-20.0, 20.0],
                "z_range": [0.0, 30.0],
                "walls": {"textured": True, "v_period_mm": 300.0, "pitch_mm": 0.9},
            }
        )
        self.assertAlmostEqual(report["bounds_size_mm"][2], 30.0, places=5)

    def test_mixed_smooth_and_textured_faces_stay_watertight(self) -> None:
        report = self._build(
            {
                "name": "mixed",
                "kind": "rect",
                "x_range": [-40.0, 40.0],
                "y_range": [-15.0, 15.0],
                "z_range": [0.0, 24.0],
                "walls": {"textured": True, "v_period_mm": 260.0, "pitch_mm": 0.8},
                "top": {"textured": False},
                "bottom": {"textured": False},
            }
        )
        self.assertTrue(report["watertight"])

    def test_prism_with_hole_is_watertight(self) -> None:
        polygon = [[-40.0, -25.0], [40.0, -25.0], [40.0, 25.0], [-40.0, 25.0]]
        hole = [[-10.0, -8.0], [10.0, -8.0], [10.0, 8.0], [-10.0, 8.0]]
        report = self._build(
            {
                "name": "with_hole",
                "kind": "prism",
                "polygon": polygon,
                "holes": [hole],
                "z_range": [0.0, 20.0],
                "walls": {"textured": True, "v_period_mm": 300.0, "pitch_mm": 1.0},
            }
        )
        self.assertEqual(report["oriented_components"], 1)

    def test_concave_letter_like_prism_stays_watertight(self) -> None:
        # Stylized 'M' footprint: two vertical strokes with a center V notch.
        polygon = [
            [-30.0, 0.0], [-30.0, 40.0], [-18.0, 40.0], [0.0, 16.0],
            [18.0, 40.0], [30.0, 40.0], [30.0, 0.0],
        ]
        report = self._build(
            {
                "name": "letter_m",
                "kind": "prism",
                "polygon": polygon,
                "z_range": [0.0, 60.0],
                "walls": {"textured": True, "v_period_mm": 220.0, "pitch_mm": 0.9},
            }
        )
        self.assertEqual(report["boundary_edges"], 0)
        self.assertEqual(report["oriented_components"], 1)
        self.assertGreater(report["signed_volume_mm3"], 0.0)

    def test_smooth_faces_keep_exact_envelope(self) -> None:
        vertices, _faces, _report = atp.build_solid(
            self.sampler,
            self.recipe,
            {
                "name": "smooth",
                "kind": "rect",
                "x_range": [-30.0, 30.0],
                "y_range": [-10.0, 10.0],
                "z_range": [0.0, 15.0],
                "walls": {"textured": False},
            },
        )
        self.assertAlmostEqual(float(vertices[:, 0].max()), 30.0, places=6)
        self.assertAlmostEqual(float(vertices[:, 0].min()), -30.0, places=6)

    def test_union_of_two_textured_solids_is_single_watertight_body(self) -> None:
        solids = [
            {
                "name": "base",
                "kind": "rect",
                "x_range": [-60.0, 60.0],
                "y_range": [-30.0, 30.0],
                "z_range": [0.0, 20.0],
                "walls": {"textured": True, "v_period_mm": 360.0, "pitch_mm": 1.2},
            },
            {
                "name": "letter",
                "kind": "rect",
                "x_range": [-20.0, 20.0],
                "y_range": [-10.0, 10.0],
                "z_range": [18.0, 80.0],
                "walls": {"textured": True, "v_period_mm": 120.0, "pitch_mm": 1.2},
            },
        ]
        parts = []
        for solid in solids:
            vertices, faces, report = atp.build_solid(self.sampler, self.recipe, solid)
            tl.require_valid(report, solid["name"])
            parts.append((vertices, faces))
        vertices, faces = atp.union_vertices_faces(parts)
        faces, _orientation = tl.orient_mesh(vertices, faces)
        report = tl.mesh_report(vertices, faces)
        self.assertTrue(report["watertight"])
        self.assertGreater(report["signed_volume_mm3"], 0.0)
        self.assertLessEqual(report["triangles"], 1_000_000)


class CliEndToEnd(unittest.TestCase):
    def test_cli_writes_stl_report_and_enforces_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            spec = {
                "recipe": str(RECIPE),
                "solids": [
                    {
                        "name": "box",
                        "kind": "rect",
                        "x_range": [-25.0, 25.0],
                        "y_range": [-15.0, 15.0],
                        "z_range": [0.0, 12.0],
                        "walls": {"textured": True, "v_period_mm": 160.0, "pitch_mm": 1.0},
                    }
                ],
            }
            spec_path = tmp_path / "spec.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            out_dir = tmp_path / "out"
            result = subprocess.run(
                [sys.executable, str(HERE / "apply_texture_patch.py"), str(spec_path), "--output-dir", str(out_dir)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((out_dir / "textured-part-report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["budget"]["passed"])
            self.assertEqual(report["final"]["boundary_edges"], 0)

            spec["solids"][0]["walls"]["pitch_mm"] = 0.05
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(HERE / "apply_texture_patch.py"), str(spec_path), "--output-dir", str(out_dir / "fine")],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("triangle budget exceeded", result.stderr)


if __name__ == "__main__":
    unittest.main()
