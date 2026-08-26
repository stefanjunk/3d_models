#!/usr/bin/env python3
"""Perform structural checks on a design-spec YAML/JSON file."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import load_structured

REQUIRED_TOP = ["project", "workflow", "branding", "function", "risk", "fabrication", "printer", "manufacturing", "optimization", "acceptance"]
VALID_RISK = {"decorative", "normal-functional", "structural", "safety-critical"}
VALID_MODE = {"integrated-print", "balanced-hybrid", "standard-hardware"}
VALID_REQUIREMENTS_APPROVAL = {"pending", "approved", "changes-requested"}
VALID_CONCEPT_APPROVAL = {"blocked", "pending", "approved", "changes-requested"}
VALID_WATERMARK_APPROVAL = {"blocked", "pending", "approved", "changes-requested"}
EXPECTED_WATERMARK_ASSET = "MM-WM-001-R1"
EXPECTED_WATERMARK_BRAND = "metriMade"
EXPECTED_WATERMARK_DOMAIN = "metriMade.com"
PRODUCT_ID_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)+$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
VALID_OPTIMIZATION_STATUS = {"pending", "applied", "not-beneficial", "not-applicable"}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("spec")
    p.add_argument("--json-out")
    p.add_argument(
        "--require-final-approval",
        action="store_true",
        help="Fail unless requirements, concept, and the current watermarked geometry are approved.",
    )
    args = p.parse_args()

    data = load_structured(args.spec)
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing top-level field: {key}")

    project = data.get("project")
    if not isinstance(project, dict):
        errors.append("project must define an immutable product id and Semantic Versioning revision")
        project = {}
    project_id = project.get("id")
    project_revision = project.get("revision")
    if not isinstance(project_id, str) or not (3 <= len(project_id) <= 32) or not PRODUCT_ID_RE.fullmatch(project_id):
        errors.append("project.id must be 3-32 uppercase letters/digits with at least one hyphen")
    if not isinstance(project_revision, str) or not SEMVER_RE.fullmatch(project_revision):
        errors.append("project.revision must be a Semantic Versioning version")
    workflow = data.get("workflow")
    if not isinstance(workflow, dict):
        errors.append("workflow must contain requirements_approval, concept_approval, and watermark_approval")
        requirements_approval = {}
        concept_approval = {}
        watermark_approval = {}
    else:
        requirements_approval = workflow.get("requirements_approval", {})
        concept_approval = workflow.get("concept_approval", {})
        watermark_approval = workflow.get("watermark_approval", {})

    if not isinstance(requirements_approval, dict):
        errors.append("workflow.requirements_approval must be an object")
        requirements_approval = {}
    if not isinstance(concept_approval, dict):
        errors.append("workflow.concept_approval must be an object")
        concept_approval = {}
    if not isinstance(watermark_approval, dict):
        errors.append("workflow.watermark_approval must be an object")
        watermark_approval = {}

    requirements_status = requirements_approval.get("status")
    concept_status = concept_approval.get("status")
    watermark_status = watermark_approval.get("status")
    if requirements_status not in VALID_REQUIREMENTS_APPROVAL:
        errors.append(f"workflow.requirements_approval.status must be one of {sorted(VALID_REQUIREMENTS_APPROVAL)}")
    if concept_status not in VALID_CONCEPT_APPROVAL:
        errors.append(f"workflow.concept_approval.status must be one of {sorted(VALID_CONCEPT_APPROVAL)}")
    if watermark_status not in VALID_WATERMARK_APPROVAL:
        errors.append(f"workflow.watermark_approval.status must be one of {sorted(VALID_WATERMARK_APPROVAL)}")

    if requirements_status == "approved":
        if requirements_approval.get("spec_revision") != project_revision:
            errors.append("requirements approval must reference the current project revision")
        if not requirements_approval.get("approved_by"):
            errors.append("approved requirements need approved_by")
    if requirements_status != "approved" and concept_status != "blocked":
        errors.append("concept approval must be blocked until requirements are approved")
    if concept_status != "approved" and watermark_status != "blocked":
        errors.append("watermark approval must be blocked until concept approval")
    if concept_status == "approved":
        if requirements_status != "approved":
            errors.append("concept cannot be approved before requirements")
        if concept_approval.get("spec_revision") != project_revision:
            errors.append("concept approval must reference the current project revision")
        if not concept_approval.get("asset"):
            errors.append("approved concept needs an asset reference")
        if not concept_approval.get("approved_by"):
            errors.append("approved concept needs approved_by")
    elif requirements_status == "approved":
        warnings.append("production CAD remains gated until concept approval")

    if watermark_approval.get("asset_id") != EXPECTED_WATERMARK_ASSET:
        errors.append(f"watermark approval must use asset_id {EXPECTED_WATERMARK_ASSET}")
    if watermark_approval.get("product_id") != project_id:
        errors.append("watermark approval product_id must equal project.id")
    if watermark_approval.get("version") != project_revision:
        errors.append("watermark approval version must equal project.revision")
    if watermark_status in {"pending", "approved"}:
        for field in (
            "geometry_revision",
            "generated_profile",
            "manifest_asset",
            "placement",
            "preview_asset",
            "validation_asset",
            "physical_test_asset",
        ):
            if not watermark_approval.get(field):
                errors.append(f"{watermark_status} watermark needs {field}")
    if watermark_status == "approved":
        if concept_status != "approved":
            errors.append("watermark cannot be approved before concept approval")
        if watermark_approval.get("spec_revision") != project_revision:
            errors.append("watermark approval must reference the current project revision")
        if not watermark_approval.get("approved_by"):
            errors.append("approved watermark needs approved_by")
    elif concept_status == "approved":
        warnings.append("final release remains gated until watermark approval")

    branding = data.get("branding")
    if not isinstance(branding, dict):
        errors.append("branding must define the mandatory product-specific metriMade.com watermark")
        branding = {}
    if branding.get("required") is not True:
        errors.append("branding.required must be true")
    if branding.get("brand") != EXPECTED_WATERMARK_BRAND:
        errors.append(f"branding.brand must be {EXPECTED_WATERMARK_BRAND}")
    if branding.get("domain") != EXPECTED_WATERMARK_DOMAIN:
        errors.append(f"branding.domain must be {EXPECTED_WATERMARK_DOMAIN}")
    if branding.get("asset_id") != EXPECTED_WATERMARK_ASSET:
        errors.append(f"branding.asset_id must be {EXPECTED_WATERMARK_ASSET}")
    if branding.get("product_id") != project_id:
        errors.append("branding.product_id must equal project.id")
    if branding.get("version") != project_revision:
        errors.append("branding.version must equal project.revision")
    if branding.get("operation") != "recessed":
        errors.append("branding.operation must be recessed")
    if branding.get("preferred_surface") != "flat-nonfunctional-low-stress-underside":
        errors.append("branding.preferred_surface must be flat-nonfunctional-low-stress-underside")
    depth = branding.get("depth_mm")
    if not isinstance(depth, (int, float)) or not 0.4 <= depth <= 0.8:
        errors.append("branding.depth_mm must be between 0.4 and 0.8 mm")
    elif abs(depth - 0.4) > 1e-9:
        warnings.append("non-default watermark depth requires project-specific validation and approval")
    if branding.get("minimum_host_wall_mm") != 1.2:
        errors.append("branding.minimum_host_wall_mm must be 1.2")
    if branding.get("minimum_remaining_wall_mm") != 0.8:
        errors.append("branding.minimum_remaining_wall_mm must be 0.8")

    if args.require_final_approval:
        if requirements_status != "approved":
            errors.append("final release requires approved requirements")
        if concept_status != "approved":
            errors.append("final release requires approved concept")
        if watermark_status != "approved":
            errors.append("final release requires approved watermarked geometry")

    risk = data.get("risk", {}).get("class") if isinstance(data.get("risk"), dict) else None
    if risk not in VALID_RISK:
        errors.append(f"risk.class must be one of {sorted(VALID_RISK)}")

    mode = data.get("fabrication", {}).get("preference") if isinstance(data.get("fabrication"), dict) else None
    if mode not in VALID_MODE:
        errors.append(f"fabrication.preference must be one of {sorted(VALID_MODE)}")

    nozzle = data.get("manufacturing", {}).get("nozzle_mm") if isinstance(data.get("manufacturing"), dict) else None
    if nozzle is None or not isinstance(nozzle, (int, float)) or nozzle <= 0:
        errors.append("manufacturing.nozzle_mm must be positive")
    elif nozzle not in (0.4, 0.6, 0.8):
        warnings.append("nonstandard nozzle: ensure an explicit profile and feature calibration")

    optimization = data.get("optimization")
    if not isinstance(optimization, dict):
        errors.append("optimization must record the FDM efficiency and mesh-simplification decisions")
        optimization = {}
    optimization_status = optimization.get("status")
    if optimization_status not in VALID_OPTIMIZATION_STATUS:
        errors.append(f"optimization.status must be one of {sorted(VALID_OPTIMIZATION_STATUS)}")
    elif optimization_status == "pending":
        warnings.append("print-time/material optimization decision remains pending")
    elif optimization_status == "applied":
        for field in ("baseline_slicer_report", "selected_variant", "comparison_report"):
            if not optimization.get(field):
                errors.append(f"applied optimization needs {field}")
    elif optimization_status == "not-beneficial":
        if not optimization.get("baseline_slicer_report"):
            errors.append("not-beneficial optimization needs baseline_slicer_report")
        if not optimization.get("comparison_report") and not optimization.get("rationale"):
            errors.append("not-beneficial optimization needs comparison_report or rationale")
    elif optimization_status == "not-applicable" and not optimization.get("rationale"):
        errors.append("not-applicable optimization needs rationale")

    mesh_optimization = optimization.get("mesh_simplification")
    if not isinstance(mesh_optimization, dict):
        errors.append("optimization.mesh_simplification must be an object")
        mesh_optimization = {}
    mesh_status = mesh_optimization.get("status")
    if mesh_status not in VALID_OPTIMIZATION_STATUS:
        errors.append(f"optimization.mesh_simplification.status must be one of {sorted(VALID_OPTIMIZATION_STATUS)}")
    elif mesh_status == "pending":
        warnings.append("manufacturing-mesh simplification decision remains pending")
    elif mesh_status == "applied":
        for field in ("master_mesh", "manufacturing_mesh", "method", "tolerance_mm", "comparison_report"):
            if not mesh_optimization.get(field):
                errors.append(f"applied mesh simplification needs {field}")
        tolerance = mesh_optimization.get("tolerance_mm")
        if tolerance is not None and (not isinstance(tolerance, (int, float)) or tolerance <= 0):
            errors.append("mesh simplification tolerance_mm must be positive")
    elif mesh_status == "not-beneficial":
        if not mesh_optimization.get("master_mesh"):
            errors.append("not-beneficial mesh simplification needs master_mesh")
        if not mesh_optimization.get("comparison_report") and not mesh_optimization.get("rationale"):
            errors.append("not-beneficial mesh simplification needs comparison_report or rationale")
    elif mesh_status == "not-applicable" and not mesh_optimization.get("rationale"):
        errors.append("not-applicable mesh simplification needs rationale")
    protected_regions = mesh_optimization.get("protected_regions")
    if not isinstance(protected_regions, list):
        errors.append("optimization.mesh_simplification.protected_regions must be a list")

    resource_budget = mesh_optimization.get("resource_budget")
    if resource_budget is not None and not isinstance(resource_budget, dict):
        errors.append("optimization.mesh_simplification.resource_budget must be an object")
        resource_budget = {}
    if mesh_status in {"applied", "not-beneficial"}:
        if not isinstance(resource_budget, dict):
            resource_budget = {}
        for field in ("triangle_target", "triangle_stop", "peak_memory_gib", "max_mesh_mib", "max_slicer_seconds"):
            value = resource_budget.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"completed mesh simplification needs positive resource_budget.{field}")
        if (
            isinstance(resource_budget.get("triangle_target"), (int, float))
            and isinstance(resource_budget.get("triangle_stop"), (int, float))
            and resource_budget["triangle_stop"] <= resource_budget["triangle_target"]
        ):
            errors.append("resource_budget.triangle_stop must exceed triangle_target")

    slicer_check = mesh_optimization.get("slicer_resolution_check")
    if slicer_check is not None and not isinstance(slicer_check, dict):
        errors.append("optimization.mesh_simplification.slicer_resolution_check must be an object")
        slicer_check = {}
    if mesh_status == "applied":
        if not isinstance(slicer_check, dict) or slicer_check.get("status") != "passed":
            errors.append("applied mesh simplification needs a separate passed slicer_resolution_check")
        elif not slicer_check.get("report"):
            errors.append("passed slicer_resolution_check needs report")

    if args.require_final_approval:
        if optimization_status == "pending":
            errors.append("final release requires a completed print-time/material optimization decision")
        if mesh_status == "pending":
            errors.append("final release requires a completed manufacturing-mesh simplification decision")

    build = data.get("printer", {}).get("build_volume_mm") if isinstance(data.get("printer"), dict) else None
    if not isinstance(build, list) or len(build) != 3 or not all(isinstance(v, (int, float)) and v > 0 for v in build):
        errors.append("printer.build_volume_mm must contain three positive numbers")

    acceptance = data.get("acceptance")
    if not isinstance(acceptance, list) or not acceptance:
        errors.append("acceptance must be a nonempty list")
    elif not all(isinstance(item, dict) and item.get("id") and item.get("criterion") for item in acceptance):
        errors.append("every acceptance entry needs id and criterion")

    if risk in {"structural", "safety-critical"}:
        loads = data.get("loads")
        if not loads:
            errors.append("structural/safety-critical design requires loads")
        if not data.get("test_plan"):
            warnings.append("structural/safety-critical design should link a test_plan")

    report = {"spec": str(Path(args.spec).resolve()), "errors": errors, "warnings": warnings, "passed": not errors}
    text = json.dumps(report, indent=2)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
