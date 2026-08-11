#!/usr/bin/env python3
"""Perform structural checks on a design-spec YAML/JSON file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_structured

REQUIRED_TOP = ["project", "workflow", "branding", "function", "risk", "fabrication", "printer", "manufacturing", "acceptance"]
VALID_RISK = {"decorative", "normal-functional", "structural", "safety-critical"}
VALID_MODE = {"integrated-print", "balanced-hybrid", "standard-hardware"}
VALID_REQUIREMENTS_APPROVAL = {"pending", "approved", "changes-requested"}
VALID_CONCEPT_APPROVAL = {"blocked", "pending", "approved", "changes-requested"}
VALID_WATERMARK_APPROVAL = {"blocked", "pending", "approved", "changes-requested"}
EXPECTED_WATERMARK_ASSET = "JSI-WM-001-R1"


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

    project_revision = data.get("project", {}).get("revision") if isinstance(data.get("project"), dict) else None
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
    if watermark_status == "approved":
        if concept_status != "approved":
            errors.append("watermark cannot be approved before concept approval")
        if watermark_approval.get("spec_revision") != project_revision:
            errors.append("watermark approval must reference the current project revision")
        if not watermark_approval.get("geometry_revision"):
            errors.append("approved watermark needs an immutable geometry_revision or hash")
        if watermark_approval.get("variant") not in {"standard", "compact"}:
            errors.append("approved watermark variant must be standard or compact")
        for field in ("placement", "preview_asset", "validation_asset", "approved_by"):
            if not watermark_approval.get(field):
                errors.append(f"approved watermark needs {field}")
    elif concept_status == "approved":
        warnings.append("final release remains gated until watermark approval")

    branding = data.get("branding")
    if not isinstance(branding, dict):
        errors.append("branding must define the mandatory JuSt Innovation watermark")
        branding = {}
    if branding.get("required") is not True:
        errors.append("branding.required must be true")
    if branding.get("brand") != "JuSt Innovation":
        errors.append("branding.brand must be JuSt Innovation")
    if branding.get("asset_id") != EXPECTED_WATERMARK_ASSET:
        errors.append(f"branding.asset_id must be {EXPECTED_WATERMARK_ASSET}")
    if branding.get("operation") != "recessed":
        errors.append("branding.operation must be recessed")
    if branding.get("preferred_surface") != "print-bed-facing-underside":
        errors.append("branding.preferred_surface must be print-bed-facing-underside")
    depth = branding.get("depth_mm")
    if not isinstance(depth, (int, float)) or not 0.2 <= depth <= 0.8:
        errors.append("branding.depth_mm must be between 0.2 and 0.8 mm")
    elif abs(depth - 0.4) > 1e-9:
        warnings.append("non-default watermark depth requires project-specific validation and approval")

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
