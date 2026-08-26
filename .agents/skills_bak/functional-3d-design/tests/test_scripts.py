from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"


def run_json(script: str, *args: str, expected: int = 0) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != expected:
        raise AssertionError(f"{script} return {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return json.loads(proc.stdout)


def completed_optimization_fixture() -> dict:
    return {
        "status": "not-applicable",
        "baseline_slicer_report": None,
        "selected_variant": None,
        "comparison_report": None,
        "rationale": "Unit-test fixture has no manufacturing optimization scope.",
        "mesh_simplification": {
            "status": "not-applicable",
            "master_mesh": None,
            "manufacturing_mesh": None,
            "method": None,
            "tolerance_mm": None,
            "protected_regions": [],
            "comparison_report": None,
            "rationale": "Unit-test fixture has no manufacturing mesh.",
        },
    }


class ScriptTests(unittest.TestCase):
    def test_tool_selection(self) -> None:
        organic = run_json(
            "select_tool.py",
            "--input-kind", "stl",
            "--geometry", "organic",
            "--precision", "medium",
            "--json",
        )
        self.assertEqual(organic["primary"], "blender")

        precise = run_json(
            "select_tool.py",
            "--geometry", "prismatic",
            "--precision", "high",
            "--needs-step",
            "--json",
        )
        self.assertIn(precise["primary"], {"cadquery", "freecad"})
        self.assertGreater(precise["scores"]["cadquery"], precise["scores"]["openscad"])

    def test_material_and_print_profile(self) -> None:
        result = run_json(
            "select_material.py",
            "--outdoor",
            "--impact",
            "--no-enclosure",
            "--max-printability", "3",
            "--json",
        )
        self.assertGreater(len(result["recommendations"]), 0)
        self.assertNotIn("pei", [m["id"] for m in result["recommendations"]])

        profile = run_json("recommend_print_profile.py", "--material", "petg", "--nozzle", "0.6", "--json")
        self.assertEqual(profile["nozzle_mm"], 0.6)
        self.assertLessEqual(profile["layer_height_mm"], 0.45)
        self.assertGreaterEqual(profile["perimeters"], 3)

    def test_print_buy_fit_snap_gear(self) -> None:
        bearing = run_json("print_vs_buy.py", "--component", "bearing", "--json")
        self.assertEqual(bearing["recommendation"], "buy")

        fit = run_json(
            "fit_clearance.py",
            "--nominal", "6",
            "--fit", "slide",
            "--nozzle", "0.6",
            "--material", "petg",
            "--json",
        )
        self.assertGreater(fit["modeled_hole_diameter_mm_if_shaft_is_nominal"], 6.0)

        snap = run_json(
            "snapfit_calculator.py",
            "--length", "30",
            "--width", "8",
            "--thickness", "1.2",
            "--deflection", "2",
            "--modulus", "1800",
            "--allowable-strain", "1.5",
            "--json",
        )
        self.assertTrue(snap["passed_preliminary_strain"])

        gear = run_json(
            "gear_pair.py",
            "--module", "1.5",
            "--teeth1", "20",
            "--teeth2", "40",
            "--nozzle", "0.6",
            "--json",
        )
        self.assertAlmostEqual(gear["standard_center_distance_mm"], 45.0)
        self.assertAlmostEqual(gear["ratio_driven_over_driver"], 2.0)

    def test_design_specs_validate(self) -> None:
        for spec in sorted((SKILL / "examples").glob("*/design-spec.yaml")):
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_design_spec.py"), str(spec)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, f"{spec}\n{proc.stdout}\n{proc.stderr}")

    def test_watermark_selector_standard_compact_and_block(self) -> None:
        standard = run_json(
            "select_watermark.py",
            "--surface-width", "120",
            "--surface-height", "80",
            "--host-wall", "2.0",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
        )
        self.assertEqual(standard["status"], "PASS")
        self.assertEqual(standard["selection"]["variant"], "standard")
        self.assertGreaterEqual(standard["selection"]["actual_envelope_mm"][0], 32.0)

        compact = run_json(
            "select_watermark.py",
            "--surface-width", "30",
            "--surface-height", "24",
            "--host-wall", "1.4",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
        )
        self.assertEqual(compact["selection"]["variant"], "compact")
        self.assertGreaterEqual(compact["selection"]["compact_across_flats_mm"], 10.0)

        blocked = run_json(
            "select_watermark.py",
            "--surface-width", "12",
            "--surface-height", "12",
            "--host-wall", "1.2",
            "--nozzle", "0.4",
            "--layer-height", "0.2",
            expected=1,
        )
        self.assertEqual(blocked["status"], "BLOCK")
        self.assertIsNone(blocked["selection"])

    def test_design_spec_rejects_concept_before_requirements_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "gate-test", "revision": "0.1.0"},
                "workflow": {
                    "requirements_approval": {"status": "pending", "spec_revision": None},
                    "concept_approval": {
                        "status": "approved",
                        "spec_revision": "0.1.0",
                        "asset": "concept.png",
                        "approved_by": "test-user",
                    },
                    "watermark_approval": {
                        "status": "blocked",
                        "spec_revision": None,
                        "geometry_revision": None,
                        "asset_id": "JSI-WM-001-R1",
                        "variant": None,
                        "placement": None,
                        "preview_asset": None,
                        "validation_asset": None,
                    },
                },
                "branding": {
                    "required": True,
                    "brand": "JuSt Innovation",
                    "asset_id": "JSI-WM-001-R1",
                    "operation": "recessed",
                    "preferred_surface": "print-bed-facing-underside",
                    "depth_mm": 0.4,
                },
                "function": {"summary": "Exercise approval ordering."},
                "risk": {"class": "normal-functional"},
                "fabrication": {"preference": "balanced-hybrid"},
                "printer": {"build_volume_mm": [250, 250, 250]},
                "manufacturing": {"material": "petg", "nozzle_mm": 0.6},
                "optimization": completed_optimization_fixture(),
                "acceptance": [{"id": "gate-order", "criterion": "Requirements precede concept."}],
            }), encoding="utf-8")
            result = run_json("validate_design_spec.py", str(spec), expected=1)
            self.assertFalse(result["passed"])
            self.assertTrue(any("concept" in error for error in result["errors"]))

    def test_final_release_requires_approved_watermark(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "release-gate-test", "revision": "1.0.0"},
                "workflow": {
                    "requirements_approval": {
                        "status": "approved",
                        "spec_revision": "1.0.0",
                        "approved_by": "test-user",
                    },
                    "concept_approval": {
                        "status": "approved",
                        "spec_revision": "1.0.0",
                        "asset": "concept.png",
                        "approved_by": "test-user",
                    },
                    "watermark_approval": {
                        "status": "pending",
                        "spec_revision": "1.0.0",
                        "geometry_revision": "sha256:draft",
                        "asset_id": "JSI-WM-001-R1",
                        "variant": "standard",
                        "placement": "main-body underside",
                        "preview_asset": "watermark-preview.png",
                        "validation_asset": "watermark-validation.json",
                        "approved_by": None,
                    },
                },
                "branding": {
                    "required": True,
                    "brand": "JuSt Innovation",
                    "asset_id": "JSI-WM-001-R1",
                    "operation": "recessed",
                    "preferred_surface": "print-bed-facing-underside",
                    "depth_mm": 0.4,
                },
                "function": {"summary": "Exercise the final watermark gate."},
                "risk": {"class": "normal-functional"},
                "fabrication": {"preference": "balanced-hybrid"},
                "printer": {"build_volume_mm": [250, 250, 250]},
                "manufacturing": {"material": "petg", "nozzle_mm": 0.4},
                "optimization": completed_optimization_fixture(),
                "acceptance": [{"id": "release-gate", "criterion": "Watermark approval precedes release."}],
            }), encoding="utf-8")
            pending = run_json(
                "validate_design_spec.py",
                str(spec),
                "--require-final-approval",
                expected=1,
            )
            self.assertTrue(any("watermarked geometry" in error for error in pending["errors"]))

            data = json.loads(spec.read_text(encoding="utf-8"))
            data["workflow"]["watermark_approval"].update({
                "status": "approved",
                "approved_by": "test-user",
            })
            spec.write_text(json.dumps(data), encoding="utf-8")
            approved = run_json("validate_design_spec.py", str(spec), "--require-final-approval")
            self.assertTrue(approved["passed"])

    def test_final_release_rejects_pending_optimization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "optimization-gate", "revision": "1.0.0"},
                "workflow": {
                    "requirements_approval": {"status": "approved", "spec_revision": "1.0.0", "approved_by": "test"},
                    "concept_approval": {"status": "approved", "spec_revision": "1.0.0", "asset": "concept.png", "approved_by": "test"},
                    "watermark_approval": {
                        "status": "approved", "spec_revision": "1.0.0", "geometry_revision": "sha256:test",
                        "asset_id": "JSI-WM-001-R1", "variant": "compact", "placement": "underside",
                        "preview_asset": "preview.png", "validation_asset": "validation.json", "approved_by": "test",
                    },
                },
                "branding": {
                    "required": True, "brand": "JuSt Innovation", "asset_id": "JSI-WM-001-R1",
                    "operation": "recessed", "preferred_surface": "print-bed-facing-underside", "depth_mm": 0.4,
                },
                "function": {"summary": "Exercise optimization gate."},
                "risk": {"class": "normal-functional"},
                "fabrication": {"preference": "balanced-hybrid"},
                "printer": {"build_volume_mm": [250, 250, 250]},
                "manufacturing": {"material": "petg", "nozzle_mm": 0.6},
                "optimization": {
                    "status": "pending",
                    "mesh_simplification": {"status": "pending", "protected_regions": []},
                },
                "acceptance": [{"id": "optimization", "criterion": "Optimization decision completed."}],
            }), encoding="utf-8")
            result = run_json("validate_design_spec.py", str(spec), "--require-final-approval", expected=1)
            self.assertTrue(any("optimization decision" in error for error in result["errors"]))
            self.assertTrue(any("mesh simplification decision" in error for error in result["errors"]))

    def test_mesh_simplification_gate_accepts_and_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            payload = {
                "relief_validation": True,
                "process": {"nozzle_mm": 0.6},
                "reference": {
                    "faces": 1000000, "body_count": 1, "watertight": True,
                    "winding_consistent": True, "volume_mm3": 100000.0,
                    "bed_contact_area_mm2": 5000.0, "relief_span_mm": 0.32,
                },
                "candidate": {
                    "faces": 500000, "body_count": 1, "watertight": True,
                    "winding_consistent": True, "volume_mm3": 99950.0,
                    "bed_contact_area_mm2": 4990.0, "relief_span_mm": 0.31,
                },
                "comparison": {
                    "max_surface_error_mm": 0.02, "rms_surface_error_mm": 0.005,
                    "max_protected_error_mm": 0.0,
                    "relief_correlation": 0.992,
                    "relief_contrast_loss_pct": 3.0,
                },
                "limits": {
                    "max_surface_error_mm": 0.025, "max_rms_surface_error_mm": 0.01,
                    "max_protected_error_mm": 0.001, "max_abs_volume_delta_pct": 0.1,
                    "min_triangle_reduction_pct": 25.0, "max_bed_contact_loss_pct": 1.0,
                    "max_relief_amplitude_loss_pct": 5.0,
                    "min_relief_correlation": 0.98,
                    "max_relief_contrast_loss_pct": 5.0,
                    "max_rms_nozzle_fraction": 0.05,
                },
            }
            path = td / "gate.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            accepted = run_json("mesh_simplification_gate.py", str(path))
            self.assertTrue(accepted["passed"])
            self.assertAlmostEqual(accepted["metrics"]["triangle_reduction_pct"], 50.0)
            self.assertAlmostEqual(accepted["metrics"]["effective_rms_limit_mm"], 0.01)

            payload["candidate"]["relief_span_mm"] = 0.28
            path.write_text(json.dumps(payload), encoding="utf-8")
            rejected = run_json("mesh_simplification_gate.py", str(path), expected=0)
            self.assertFalse(rejected["passed"])
            self.assertFalse(rejected["checks"]["relief_amplitude_loss_pct"]["passed"])

            payload["candidate"]["relief_span_mm"] = 0.31
            payload["comparison"]["relief_correlation"] = 0.97
            path.write_text(json.dumps(payload), encoding="utf-8")
            rejected = run_json("mesh_simplification_gate.py", str(path), expected=0)
            self.assertFalse(rejected["checks"]["relief_correlation"]["passed"])

            payload["comparison"]["relief_correlation"] = 0.99
            payload["comparison"]["relief_contrast_loss_pct"] = 5.0
            path.write_text(json.dumps(payload), encoding="utf-8")
            boundary = run_json("mesh_simplification_gate.py", str(path), expected=0)
            self.assertFalse(boundary["checks"]["relief_contrast_loss_pct"]["passed"])

    def test_applied_mesh_requires_resource_and_separate_slicer_gates(self) -> None:
        source = SKILL / "examples" / "rounded-desk-organizer" / "design-spec.yaml"
        payload = yaml.safe_load(source.read_text(encoding="utf-8"))
        payload["optimization"].update({
            "status": "not-applicable",
            "rationale": "This test exercises only the manufacturing-mesh gate.",
        })
        mesh = payload["optimization"]["mesh_simplification"]
        mesh.update({
            "status": "applied",
            "method": "protected quadric simplification",
            "tolerance_mm": 0.025,
            "comparison_report": "validation/geometry-comparison.json",
        })
        mesh["resource_budget"]["max_slicer_seconds"] = None

        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "design-spec.json"
            spec.write_text(json.dumps(payload), encoding="utf-8")
            blocked = run_json("validate_design_spec.py", str(spec), expected=1)
            self.assertTrue(any("max_slicer_seconds" in error for error in blocked["errors"]))
            self.assertTrue(any("separate passed slicer_resolution_check" in error for error in blocked["errors"]))

            mesh["resource_budget"]["max_slicer_seconds"] = 120
            mesh["slicer_resolution_check"] = {
                "status": "passed",
                "report": "validation/exact-slicer-resolution.json",
            }
            spec.write_text(json.dumps(payload), encoding="utf-8")
            accepted = run_json("validate_design_spec.py", str(spec))
            self.assertTrue(accepted["passed"])

    def test_bundled_organizer_relief_gate_example_passes(self) -> None:
        example = SKILL / "examples" / "rounded-desk-organizer" / "mesh-simplification-metrics.json"
        result = run_json("mesh_simplification_gate.py", str(example))
        self.assertTrue(result["passed"])
        self.assertAlmostEqual(result["metrics"]["effective_rms_limit_mm"], 0.03)

    def test_parts_library_qualification_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            library = Path(td) / "parts.json"
            entry = Path(td) / "entry.json"
            entry.write_text(json.dumps({
                "part_id": "test-spacer",
                "revision": "0.1.0",
                "status": "experimental",
                "source_type": "printed",
                "category": "spacer",
                "validation": [],
                "test_evidence": [],
            }), encoding="utf-8")
            run_json("parts_library.py", "--library", str(library), "init") if False else None
            # init emits a path rather than JSON
            proc = subprocess.run([sys.executable, str(SCRIPTS / "parts_library.py"), "--library", str(library), "init"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0)
            added = run_json("parts_library.py", "--library", str(library), "add", "--entry", str(entry))
            self.assertTrue(added["passed"])
            failed = run_json(
                "parts_library.py",
                "--library", str(library),
                "promote", "--part-id", "test-spacer", "--status", "qualified-local",
                expected=1,
            )
            self.assertFalse(failed["passed"])


if __name__ == "__main__":
    unittest.main()
