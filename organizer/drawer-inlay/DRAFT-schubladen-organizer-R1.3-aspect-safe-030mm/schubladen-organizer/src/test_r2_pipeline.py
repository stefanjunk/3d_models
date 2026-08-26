#!/usr/bin/env python3
"""Unit tests for bounded R2 routing, freshness, budgets, and 3MF inspection."""

from __future__ import annotations

import json
import copy
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

import rebuild
from src import build_pipeline
from src import validate_r2_procedural_wood as validator


class R2RouteAndFilenamesTests(unittest.TestCase):
    def test_route_selection_defaults_r2_only_for_r2_revision(self) -> None:
        self.assertEqual(build_pipeline.select_pipeline_route("R2-procedural-wood"), "r2-procedural-wood-draft")
        self.assertEqual(build_pipeline.select_pipeline_route("R2-procedural-wood-test"), "r2-procedural-wood-draft")
        self.assertEqual(build_pipeline.select_pipeline_route("R1.3"), "legacy-r1-relief")
        self.assertEqual(rebuild.select_rebuild_route("R2-procedural-wood"), "r2-procedural-wood-draft")
        self.assertEqual(rebuild.select_rebuild_route("R1.3"), "legacy-r1-relief")

    def test_exact_r2_filename_set_has_nine_stls(self) -> None:
        names = validator.r2_stl_names()
        self.assertEqual(len(names), 9)
        self.assertEqual(len(set(names)), 9)
        self.assertEqual(
            set(names),
            {
                "DRAFT-R2-driver-front-procedural-wood-unmarked.stl",
                "DRAFT-R2-driver-back-procedural-wood-unmarked.stl",
                "DRAFT-R2-hardware-front-procedural-wood-unmarked.stl",
                "DRAFT-R2-hardware-back-procedural-wood-unmarked.stl",
                "DRAFT-R2-screwdriver-comb-procedural-wood-unmarked.stl",
                "DRAFT-R2-drawer-fit-corner-coupon.stl",
                "DRAFT-R2-connector-coupon-male.stl",
                "DRAFT-R2-connector-coupon-female.stl",
                "DRAFT-R2-procedural-wood-coupon.stl",
            },
        )

    def test_r2_rebuild_rejects_image_and_prepare_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "no raster/heightmap"):
            rebuild.validate_r2_arguments(Path("texture.png"), False)
        with self.assertRaisesRegex(ValueError, "no raster/heightmap"):
            rebuild.validate_r2_arguments(None, True)
        rebuild.validate_r2_arguments(None, False)


class R2IdentityAndBudgetTests(unittest.TestCase):
    def test_hash_and_freshness_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.txt"
            artifact = root / "artifact.bin"
            report_path = root / "report.json"
            source.write_text("source-v1", encoding="utf-8")
            artifact.write_bytes(b"artifact-v1")
            report = {
                "identities": {
                    "inputs": {"source": validator.file_identity(root, source)},
                    "artifacts": {"artifact": validator.file_identity(root, artifact)},
                }
            }
            report_path.write_text(json.dumps(report), encoding="utf-8")
            self.assertEqual(
                validator.verify_identity_bundle(
                    root,
                    report_path,
                    report,
                    {"source": "source.txt"},
                    {"artifact": "artifact.bin"},
                ),
                [],
            )

            source.write_text("source-v2", encoding="utf-8")
            errors = validator.verify_identity_bundle(
                root,
                report_path,
                report,
                {"source": "source.txt"},
                {"artifact": "artifact.bin"},
            )
            self.assertTrue(any("SHA-256 mismatch" in error for error in errors))
            self.assertTrue(any("stale artifact" in error for error in errors))

            newer = source.stat().st_mtime_ns + 10_000_000
            os.utime(source, ns=(newer, newer))
            errors = validator.verify_identity_bundle(
                root,
                report_path,
                report,
                {"source": "source.txt"},
                {"artifact": "artifact.bin"},
            )
            self.assertTrue(any("stale report" in error for error in errors))

    def test_budget_arithmetic_at_seventy_percent_boundary(self) -> None:
        budget = {
            "r1_3_baseline_triangles": 1000,
            "r1_3_baseline_stl_bytes": 10_000,
            "triangle_target_total": 300,
            "triangle_stop_total": 400,
            "max_stl_bytes_total": 3000,
            "max_peak_rss_mib_per_module": 100.0,
            "minimum_triangle_and_byte_reduction_fraction": 0.7,
        }
        rows = [
            {"id": "a", "triangles": 100, "file_bytes": 1000, "peak_rss_mib": 90.0},
            {"id": "b", "triangles": 200, "file_bytes": 2000, "peak_rss_mib": 100.0},
        ]
        metrics = validator.budget_metrics(rows, budget)
        self.assertAlmostEqual(metrics["triangle_reduction_fraction"], 0.7)
        self.assertAlmostEqual(metrics["byte_reduction_fraction"], 0.7)
        self.assertTrue(all(metrics["checks"].values()))
        rows[1]["triangles"] = 201
        self.assertFalse(validator.budget_metrics(rows, budget)["checks"]["triangle_reduction"])

    def test_texture_plan_rejects_non_engrave_and_wrong_dimensions(self) -> None:
        good = {
            "policy": {"operation": "engrave-only"},
            "groove": {"width_mm": 0.9, "depth_mm": 0.2},
            "paths": [{"width_mm": 0.9, "depth_mm": 0.2}],
            "knots": [{"contours": [{"width_mm": 0.9, "depth_mm": 0.2}]}],
        }
        self.assertEqual(validator.texture_plan_errors("fixture", good, 0.9, 0.2), [])
        bad = json.loads(json.dumps(good))
        bad["policy"]["operation"] = "emboss"
        bad["paths"][0]["width_mm"] = 0.8
        errors = validator.texture_plan_errors("fixture", bad, 0.9, 0.2)
        self.assertTrue(any("non-engrave" in error for error in errors))
        self.assertTrue(any("wrong path/knot" in error for error in errors))

    @staticmethod
    def coherent_plan_fixture(source_rectangle: dict, targets: list[dict]) -> dict:
        clips = []
        for target in targets:
            rectangle = target["rectangle_mm"]
            clips.append({
                "id": target["region_id"],
                "rectangle_mm": rectangle,
                "inset_centerline_rectangle_mm": {
                    "min": [value + 0.45 for value in rectangle["min"]],
                    "max": [value - 0.45 for value in rectangle["max"]],
                },
            })
        first_clip = clips[0]
        inset = first_clip["inset_centerline_rectangle_mm"]
        path = {
            "id": "parent-01-fragment-001",
            "parent_path_id": "parent-01",
            "clip_rectangle_id": first_clip["id"],
            "width_mm": 0.9,
            "depth_mm": 0.2,
            "points_mm": [
                [inset["min"][0], inset["min"][1]],
                [inset["max"][0], inset["min"][1]],
            ],
        }
        return {
            "seed": 7,
            "region": {
                "id": validator.ASSEMBLY_FLOOR_SOURCE_ID,
                "surface": "floor",
                "rectangle_mm": source_rectangle,
            },
            "policy": {"operation": "engrave-only", "coherence_policy": "plan-once-then-clip"},
            "coherence": {
                "coherence_policy": "plan-once-then-clip",
                "source_field_id": validator.ASSEMBLY_FLOOR_SOURCE_ID,
                "source_rectangle_mm": source_rectangle,
                "clip_rectangles": clips,
                "parent_path_ids": ["parent-01"],
            },
            "groove": {"width_mm": 0.9, "depth_mm": 0.2},
            "paths": [path],
            "knots": [],
        }

    def test_coherence_validator_requires_policy_insets_and_parent_ids(self) -> None:
        source = {"min": [0.0, 0.0], "max": [20.0, 20.0]}
        targets = [{
            "region_id": "allowed-01",
            "source_id": validator.ASSEMBLY_FLOOR_SOURCE_ID,
            "rectangle_mm": {"min": [1.0, 1.0], "max": [10.0, 10.0]},
        }]
        good = self.coherent_plan_fixture(source, targets)
        self.assertEqual(
            validator.coherence_plan_errors("fixture", good, targets, 0.9, 2, source, "driver-back"),
            [],
        )
        bad = copy.deepcopy(good)
        bad["policy"].pop("coherence_policy")
        bad["coherence"]["clip_rectangles"][0]["inset_centerline_rectangle_mm"]["min"][0] -= 0.1
        bad["paths"][0].pop("parent_path_id")
        errors = validator.coherence_plan_errors("fixture", bad, targets, 0.9, 2, source, "driver-back")
        self.assertTrue(any("coherence policy" in error for error in errors))
        self.assertTrue(any("half-width inset" in error for error in errors))
        self.assertTrue(any("parent path ID" in error for error in errors))

    def test_module_validator_rejects_independent_floor_replanning(self) -> None:
        params = {
            "organizer": {
                "base_wall_thickness": 3.2,
                "outer_wall_thickness_override": None,
                "width_x": 227.0,
                "depth_y": 357.0,
            }
        }
        wood = {
            "seed": 7,
            "grain": {"groove_width_mm": 0.9, "floor_margin_mm": 2.0},
            "knots": {"nested_contours": 2},
        }
        source = validator.assembly_floor_source_rectangle(params, wood)
        targets = [
            {
                "region_id": "driver-back-floor-01",
                "source_id": validator.ASSEMBLY_FLOOR_SOURCE_ID,
                "rectangle_mm": {"min": [6.0, 190.0], "max": [40.0, 250.0]},
                "plane": {"axis": "z", "coordinate_mm": 2.6, "normal": 1},
                "long_axis": 1,
            },
            {
                "region_id": "driver-back-floor-02",
                "source_id": validator.ASSEMBLY_FLOOR_SOURCE_ID,
                "rectangle_mm": {"min": [50.0, 190.0], "max": [85.0, 250.0]},
                "plane": {"axis": "z", "coordinate_mm": 2.6, "normal": 1},
                "long_axis": 1,
            },
        ]
        plan = self.coherent_plan_fixture(source, targets)
        groups = [{"id": "floor", "targets": targets, "plans": [plan, copy.deepcopy(plan)]}]
        errors = validator.module_coherence_errors("driver-back", groups, params, wood)
        self.assertTrue(any("independently replanned" in error for error in errors))
        self.assertTrue(any("not one assembly-global source plan" in error for error in errors))


class R2ThreeMfTests(unittest.TestCase):
    @staticmethod
    def write_fixture(path: Path, namespace: str = validator.CORE_NS) -> None:
        modules = (
            (1, "driver-front", 92.0, 178.5, (0.0, 0.0, 0.0)),
            (2, "driver-back", 92.0, 178.5, (0.0, 178.5, 0.0)),
            (3, "hardware-front", 135.0, 178.5, (92.0, 0.0, 0.0)),
            (4, "hardware-back", 135.0, 178.5, (92.0, 178.5, 0.0)),
        )
        objects = []
        items = []
        for object_id, name, width, depth, translation in modules:
            objects.append(
                f'<object id="{object_id}" type="model" name="{name}"><mesh><vertices>'
                f'<vertex x="0" y="0" z="0"/><vertex x="{width}" y="{depth}" z="64"/>'
                f'<vertex x="{width}" y="0" z="0"/></vertices><triangles>'
                '<triangle v1="0" v2="1" v3="2"/></triangles></mesh></object>'
            )
            x, y, z = translation
            items.append(
                f'<item objectid="{object_id}" transform="1 0 0 0 1 0 0 0 1 {x} {y} {z}"/>'
            )
        model = (
            f'<?xml version="1.0" encoding="UTF-8"?><model xmlns="{namespace}" unit="millimeter">'
            '<metadata name="Status">DRAFT unmarked</metadata><resources>'
            + "".join(objects)
            + "</resources><build>"
            + "".join(items)
            + "</build></model>"
        )
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("[Content_Types].xml", "types")
            archive.writestr("_rels/.rels", "rels")
            archive.writestr("3D/3dmodel.model", model)

    def test_namespace_objects_build_items_and_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.3mf"
            self.write_fixture(path)
            scan = validator.scan_3mf(path)
            self.assertTrue(scan["crc_pass"])
            self.assertTrue(scan["core_namespace_pass"])
            self.assertEqual([item["name"] for item in scan["objects"]], list(validator.MODULES))
            self.assertEqual(len(scan["build_items"]), 4)
            self.assertTrue(scan["translation_only_transforms"])
            self.assertTrue(validator.exact_envelope(scan["assembly_bounds_mm"]))

    def test_wrong_namespace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong-namespace.3mf"
            self.write_fixture(path, "urn:not-the-core-namespace")
            scan = validator.scan_3mf(path)
            self.assertFalse(scan["core_namespace_pass"])


if __name__ == "__main__":
    unittest.main()
