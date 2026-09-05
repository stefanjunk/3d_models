from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
WATERMARK_EXAMPLE = (
    SKILL.parents[2]
    / "tools"
    / "metrimade-watermark"
    / "exports"
    / "examples"
    / "MM-ORG-001_v0.1.0"
    / "metrimade-watermark-MM-ORG-001-v0.1.0.json"
)
WATERMARK_R2_EXAMPLES = (
    SKILL.parents[2]
    / "tools"
    / "metrimade-watermark"
    / "exports"
    / "examples-r2"
)
PREFLIGHT_EXAMPLE = SKILL.parent / "3d-design-preflight" / "examples" / "preflight-result.example.json"


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


def watermark_approval_fixture(product_id: str, version: str, status: str = "blocked") -> dict:
    populated = status in {"pending", "approved"}
    return {
        "status": status,
        "spec_revision": version if populated else None,
        "geometry_revision": "sha256:test" if populated else None,
        "asset_id": "MM-WM-001-R2",
        "product_id": product_id,
        "version": version,
        "generated_profile": "assets/watermark/profile.json" if populated else None,
        "manifest_asset": "assets/watermark/manifest.sha256" if populated else None,
        "placement": "main-body underside" if populated else None,
        "preview_asset": "validation/watermark-preview.png" if populated else None,
        "validation_asset": "validation/watermark-validation.json" if populated else None,
        "physical_test_asset": "tests/watermark-coupon.json" if populated else None,
        "layout_tier": "full" if populated else None,
        "domain_visible": True if populated else None,
        "approved_by": "test-user" if status == "approved" else None,
    }


def branding_fixture(product_id: str, version: str) -> dict:
    return {
        "required": True,
        "brand": "metriMade",
        "domain": "metriMade.com",
        "asset_id": "MM-WM-001-R2",
        "layout_tier": "auto",
        "product_id": product_id,
        "version": version,
        "operation": "recessed",
        "preferred_surface": "flat-nonfunctional-low-stress-underside",
        "depth_mm": 0.4,
        "minimum_host_wall_mm": 1.2,
        "minimum_remaining_wall_mm": 0.8,
    }


def pending_preflight_fixture() -> dict:
    return {
        "status": "pending",
        "mode": None,
        "artifact": "preflight/preflight-result.json",
        "assessment_id": None,
        "assessment_version": None,
        "assessed_project_revision": None,
        "updated_at": None,
        "change_triggers": [],
    }


def write_concept_fixture(project_root: Path) -> dict:
    concept = project_root / "concept" / "concept-product-v1.0.0-r1.png"
    concept.parent.mkdir(parents=True, exist_ok=True)
    concept.write_bytes(b"\x89PNG\r\n\x1a\nunit-test-concept")
    digest = hashlib.sha256(concept.read_bytes()).hexdigest()
    record = project_root / "evidence" / "concept-image-record.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        json.dumps({"image": {"file": "concept/concept-product-v1.0.0-r1.png", "sha256": digest}}),
        encoding="utf-8",
    )
    return {
        "asset": "concept/concept-product-v1.0.0-r1.png",
        "asset_sha256": digest,
        "asset_sha256_record": "evidence/concept-image-record.json",
    }


def write_current_preflight(
    project_root: Path,
    product_id: str,
    version: str,
    *,
    mode: str = "prospective",
) -> dict:
    document = json.loads(PREFLIGHT_EXAMPLE.read_text(encoding="utf-8"))
    assessment_id = f"PREFLIGHT-{product_id}-001"
    updated_at = "2026-08-31T12:00:00+02:00"
    triggers = ["initial_design"] if mode == "prospective" else ["backfill_missing_preflight"]
    document.update(
        {
            "assessment_id": assessment_id,
            "product": f"{product_id} validation fixture",
            "warnings": [],
        }
    )
    document["gates"] = {f"G{index}": "PASS" for index in range(7)}
    document["decision"] = {
        "lane": "A",
        "confidence": "HIGH",
        "design_release": "GO",
        "rationale": "Deterministic unit-test fixture.",
    }
    document["readiness"].update({"level": "R4", "blocking_unknowns": []})
    document["readiness"]["component_levels"] = {
        key: "R4"
        for key in (
            "scope_variant",
            "requirements",
            "critical_interfaces",
            "manufacturing_profile",
            "verification",
        )
    }
    document["traceability"].update(
        {
            "mode": mode.upper(),
            "project_id": product_id,
            "project_revision": version,
            "basis_refs": ["design-spec.json"],
            "change_triggers": triggers,
            "previous_assessment_id": None,
            "updated_at": updated_at,
        }
    )
    artifact = project_root / "preflight" / "preflight-result.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(document), encoding="utf-8")
    return {
        "status": "current",
        "mode": mode,
        "artifact": "preflight/preflight-result.json",
        "assessment_id": assessment_id,
        "assessment_version": document["assessment_version"],
        "assessed_project_revision": version,
        "updated_at": updated_at,
        "change_triggers": triggers,
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

    def test_anycubic_slicer_preflight_routes_through_validation_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "part.stl"
            source.write_text("solid part\nendsolid part\n", encoding="utf-8")
            profiles = {}
            for kind in ("machine", "process", "filament"):
                path = root / f"{kind}.json"
                path.write_text(json.dumps({"type": kind, "name": kind}), encoding="utf-8")
                profiles[kind] = path
            result = run_json(
                "slicer_preflight.py",
                str(source),
                "--slicer", "AnycubicSlicerNext",
                "--machine-profile", str(profiles["machine"]),
                "--process-profile", str(profiles["process"]),
                "--filament-profile", str(profiles["filament"]),
                "--output-dir", str(root / "slice"),
            )
            self.assertEqual(result["backend"], "anycubic-slicer-next")
            self.assertIn("slice-anycubic-next", result["command"])
            self.assertFalse(result["execute_requested"])

            project = root / "project.3mf"
            project.write_bytes(b"fixture")
            incomplete = run_json(
                "slicer_preflight.py",
                str(project),
                "--slicer", "AnycubicSlicerNext",
                "--machine-profile", str(profiles["machine"]),
                expected=1,
            )
            self.assertIn("requires --machine-profile", incomplete["error"])

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

    def test_project_init_scaffolds_pending_preflight_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "project_init.py"),
                    "fixture",
                    "--directory",
                    directory,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            project = Path(directory) / "fixture"
            self.assertTrue((project / "preflight" / "preflight-input.yaml").is_file())
            spec = yaml.safe_load((project / "design-spec.yaml").read_text(encoding="utf-8"))
            self.assertEqual(spec["workflow"]["preflight"]["status"], "pending")

    def test_current_preflight_is_required_and_cross_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec = yaml.safe_load((SKILL / "templates" / "design-spec.yaml").read_text(encoding="utf-8"))
            spec_path = root / "design-spec.yaml"
            spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
            pending = run_json(
                "validate_design_spec.py",
                str(spec_path),
                "--require-current-preflight",
                expected=1,
            )
            self.assertTrue(any("current validated preflight" in item for item in pending["errors"]))

            spec["workflow"]["requirements_approval"].update(
                {
                    "status": "approved",
                    "spec_revision": spec["project"]["revision"],
                    "approved_by": "test-user",
                }
            )
            spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
            premature_approval = run_json("validate_design_spec.py", str(spec_path), expected=1)
            self.assertTrue(
                any("requirements approval requires" in item for item in premature_approval["errors"])
            )

            spec["workflow"]["preflight"] = write_current_preflight(
                root,
                spec["project"]["id"],
                spec["project"]["revision"],
                mode="retrospective",
            )
            spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
            current = run_json(
                "validate_design_spec.py",
                str(spec_path),
                "--require-current-preflight",
            )
            self.assertTrue(current["passed"])

    def test_packager_bundles_metrimade_watermark_core(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "functional-3d-design.zip"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "package_skill.py"),
                    "--package-root",
                    str(SKILL),
                    "--output",
                    str(package),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with zipfile.ZipFile(package) as archive:
                names = set(archive.namelist())
            prefix = "functional-3d-design/assets/metrimade-watermark/"
            for relative in (
                "README.md",
                "design-spec.yaml",
                "provenance.json",
                "source/metrimade-watermark.scad",
                "tools/generate_watermark.py",
            ):
                self.assertIn(prefix + relative, names)
            self.assertIn("3d-design-preflight/SKILL.md", names)
            self.assertIn("3d-design-preflight/scripts/validate_preflight.py", names)

    def test_design_spec_rejects_concept_before_requirements_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "MM-GATE-TEST", "revision": "0.1.0"},
                "workflow": {
                    "preflight": pending_preflight_fixture(),
                    "requirements_approval": {"status": "pending", "spec_revision": None},
                    "concept_approval": {
                        "status": "approved",
                        "spec_revision": "0.1.0",
                        "asset": "concept.png",
                        "approved_by": "test-user",
                    },
                    "watermark_approval": watermark_approval_fixture("MM-GATE-TEST", "0.1.0"),
                },
                "branding": branding_fixture("MM-GATE-TEST", "0.1.0"),
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

    def test_design_spec_rejects_approved_concept_without_image_hash_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec = root / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "MM-CONCEPT-TEST", "revision": "1.0.0"},
                "workflow": {
                    "preflight": write_current_preflight(root, "MM-CONCEPT-TEST", "1.0.0"),
                    "requirements_approval": {"status": "approved", "spec_revision": "1.0.0", "approved_by": "test"},
                    "concept_approval": {"status": "approved", "spec_revision": "1.0.0", "asset": "missing.png", "approved_by": "agent:test"},
                    "watermark_approval": watermark_approval_fixture("MM-CONCEPT-TEST", "1.0.0"),
                },
                "branding": branding_fixture("MM-CONCEPT-TEST", "1.0.0"),
                "function": {"summary": "Exercise mandatory concept-image evidence."},
                "risk": {"class": "normal-functional"},
                "fabrication": {"preference": "balanced-hybrid"},
                "printer": {"build_volume_mm": [250, 250, 250]},
                "manufacturing": {"material": "petg", "nozzle_mm": 0.4},
                "optimization": completed_optimization_fixture(),
                "acceptance": [{"id": "concept-image", "criterion": "Concept approval binds an image."}],
            }), encoding="utf-8")
            result = run_json("validate_design_spec.py", str(spec), expected=1)
            self.assertFalse(result["passed"])
            self.assertTrue(any("concept image" in error for error in result["errors"]))
            self.assertTrue(any("asset_sha256" in error for error in result["errors"]))

    def test_final_release_requires_approved_watermark(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            concept = write_concept_fixture(root)
            spec = root / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "MM-RELEASE-TEST", "revision": "1.0.0"},
                "workflow": {
                    "preflight": write_current_preflight(root, "MM-RELEASE-TEST", "1.0.0"),
                    "requirements_approval": {
                        "status": "approved",
                        "spec_revision": "1.0.0",
                        "approved_by": "test-user",
                    },
                    "concept_approval": {
                        "status": "approved",
                        "spec_revision": "1.0.0",
                        "approved_by": "test-user",
                        **concept,
                    },
                    "watermark_approval": watermark_approval_fixture(
                        "MM-RELEASE-TEST", "1.0.0", "pending"
                    ),
                },
                "branding": branding_fixture("MM-RELEASE-TEST", "1.0.0"),
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

            data["branding"]["version"] = "1.0.1"
            spec.write_text(json.dumps(data), encoding="utf-8")
            mismatched = run_json(
                "validate_design_spec.py",
                str(spec),
                "--require-final-approval",
                expected=1,
            )
            self.assertTrue(any("branding.version" in error for error in mismatched["errors"]))

    def test_final_release_rejects_pending_optimization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            concept = write_concept_fixture(root)
            spec = root / "design-spec.json"
            spec.write_text(json.dumps({
                "project": {"id": "MM-OPT-TEST", "revision": "1.0.0"},
                "workflow": {
                    "preflight": write_current_preflight(root, "MM-OPT-TEST", "1.0.0"),
                    "requirements_approval": {"status": "approved", "spec_revision": "1.0.0", "approved_by": "test"},
                    "concept_approval": {"status": "approved", "spec_revision": "1.0.0", "approved_by": "test", **concept},
                    "watermark_approval": watermark_approval_fixture(
                        "MM-OPT-TEST", "1.0.0", "approved"
                    ),
                },
                "branding": branding_fixture("MM-OPT-TEST", "1.0.0"),
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
