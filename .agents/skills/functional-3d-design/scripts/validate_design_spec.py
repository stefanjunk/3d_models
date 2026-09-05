#!/usr/bin/env python3
"""Perform structural checks on a design-spec YAML/JSON file."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from common import load_structured

REQUIRED_TOP = ["project", "workflow", "branding", "function", "risk", "fabrication", "printer", "manufacturing", "optimization", "acceptance"]
VALID_RISK = {"decorative", "normal-functional", "structural", "safety-critical"}
VALID_MODE = {"integrated-print", "balanced-hybrid", "standard-hardware"}
VALID_REQUIREMENTS_APPROVAL = {"pending", "approved", "changes-requested"}
VALID_CONCEPT_APPROVAL = {"blocked", "pending", "approved", "changes-requested"}
VALID_WATERMARK_APPROVAL = {"blocked", "pending", "approved", "changes-requested"}
SUPPORTED_WATERMARK_ASSETS = {"MM-WM-001-R1", "MM-WM-001-R2"}
RECOMMENDED_WATERMARK_ASSET = "MM-WM-001-R2"
EXPECTED_WATERMARK_BRAND = "metriMade"
EXPECTED_WATERMARK_DOMAIN = "metriMade.com"
PRODUCT_ID_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)+$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
CONCEPT_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".svg", ".webp"}
VALID_OPTIMIZATION_STATUS = {"pending", "applied", "not-beneficial", "not-applicable"}
VALID_PREFLIGHT_STATUS = {"pending", "current", "stale"}
VALID_PREFLIGHT_MODE = {"prospective", "retrospective"}
PREFLIGHT_ARTIFACT = "preflight/preflight-result.json"
PREFLIGHT_VALIDATOR = (
    Path(__file__).resolve().parents[2]
    / "3d-design-preflight"
    / "scripts"
    / "validate_preflight.py"
)


def is_supported_concept_image(path: Path) -> bool:
    if path.suffix.lower() not in CONCEPT_IMAGE_SUFFIXES or not path.is_file():
        return False
    with path.open("rb") as handle:
        prefix = handle.read(512)
    suffix = path.suffix.lower()
    if suffix == ".png":
        return prefix.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return prefix.startswith(b"\xff\xd8\xff")
    if suffix == ".webp":
        return prefix.startswith(b"RIFF") and prefix[8:12] == b"WEBP"
    return b"<svg" in prefix.lower()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("spec")
    p.add_argument("--json-out")
    p.add_argument(
        "--require-final-approval",
        action="store_true",
        help="Fail unless requirements, concept, and the current watermarked geometry are approved.",
    )
    p.add_argument(
        "--require-current-preflight",
        action="store_true",
        help="Fail unless a schema-valid preflight for the current project revision is linked.",
    )
    args = p.parse_args()
    spec_path = Path(args.spec).resolve()

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
        errors.append(
            "workflow must contain preflight, requirements_approval, concept_approval, and watermark_approval"
        )
        preflight = {}
        requirements_approval = {}
        concept_approval = {}
        watermark_approval = {}
    else:
        preflight = workflow.get("preflight", {})
        requirements_approval = workflow.get("requirements_approval", {})
        concept_approval = workflow.get("concept_approval", {})
        watermark_approval = workflow.get("watermark_approval", {})

    require_current_preflight = args.require_current_preflight or args.require_final_approval
    preflight_status = None
    preflight_decision: dict = {}
    if not isinstance(preflight, dict):
        errors.append("workflow.preflight must be an object")
        preflight = {}
    else:
        preflight_status = preflight.get("status")
        if preflight_status not in VALID_PREFLIGHT_STATUS:
            errors.append(f"workflow.preflight.status must be one of {sorted(VALID_PREFLIGHT_STATUS)}")

        artifact = preflight.get("artifact")
        if artifact != PREFLIGHT_ARTIFACT:
            errors.append(f"workflow.preflight.artifact must be {PREFLIGHT_ARTIFACT}")

        change_triggers = preflight.get("change_triggers")
        if not isinstance(change_triggers, list):
            errors.append("workflow.preflight.change_triggers must be a list")
            change_triggers = []
        elif preflight_status in {"current", "stale"} and not change_triggers:
            errors.append(f"{preflight_status} preflight needs at least one change trigger")

        if preflight_status == "current":
            for field in (
                "mode",
                "assessment_id",
                "assessment_version",
                "assessed_project_revision",
                "updated_at",
            ):
                if not preflight.get(field):
                    errors.append(f"current preflight needs workflow.preflight.{field}")
            if preflight.get("mode") not in VALID_PREFLIGHT_MODE:
                errors.append(f"workflow.preflight.mode must be one of {sorted(VALID_PREFLIGHT_MODE)} when current")
            if preflight.get("assessed_project_revision") != project_revision:
                errors.append("current preflight must assess the current project revision")

            artifact_path = (spec_path.parent / str(artifact)).resolve()
            try:
                artifact_path.relative_to(spec_path.parent)
            except ValueError:
                errors.append("workflow.preflight.artifact must remain inside the owning product directory")
            else:
                if not PREFLIGHT_VALIDATOR.is_file():
                    errors.append(f"required sibling preflight validator is missing: {PREFLIGHT_VALIDATOR}")
                elif not artifact_path.is_file():
                    errors.append(f"linked preflight artifact does not exist: {artifact_path}")
                else:
                    process = subprocess.run(
                        [
                            sys.executable,
                            str(PREFLIGHT_VALIDATOR),
                            str(artifact_path),
                            "--project-id",
                            str(project_id),
                            "--project-revision",
                            str(project_revision),
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    try:
                        preflight_report = json.loads(process.stdout)
                    except json.JSONDecodeError:
                        errors.append(
                            "preflight validator did not return JSON: "
                            + (process.stderr.strip() or process.stdout.strip() or "no output")
                        )
                        preflight_report = {}
                    for item in preflight_report.get("errors", []):
                        errors.append(f"preflight artifact: {item}")
                    for item in preflight_report.get("warnings", []):
                        warnings.append(f"preflight artifact: {item}")
                    if process.returncode != 0 and not preflight_report.get("errors"):
                        errors.append("preflight validator failed without a structured error")

                    try:
                        preflight_document = load_structured(artifact_path)
                    except (OSError, ValueError, json.JSONDecodeError) as exc:
                        errors.append(f"cannot read linked preflight artifact: {exc}")
                        preflight_document = {}
                    if isinstance(preflight_document, dict):
                        if preflight.get("assessment_id") != preflight_document.get("assessment_id"):
                            errors.append("workflow.preflight.assessment_id must match the linked artifact")
                        if preflight.get("assessment_version") != preflight_document.get("assessment_version"):
                            errors.append("workflow.preflight.assessment_version must match the linked artifact")
                        traceability = preflight_document.get("traceability", {})
                        if isinstance(traceability, dict):
                            linked_mode = str(traceability.get("mode", "")).lower()
                            if preflight.get("mode") != linked_mode:
                                errors.append("workflow.preflight.mode must match artifact traceability.mode")
                            if preflight.get("updated_at") != traceability.get("updated_at"):
                                errors.append("workflow.preflight.updated_at must match artifact traceability.updated_at")
                            if change_triggers != traceability.get("change_triggers"):
                                errors.append(
                                    "workflow.preflight.change_triggers must match artifact traceability.change_triggers"
                                )
                        decision = preflight_document.get("decision")
                        if isinstance(decision, dict):
                            preflight_decision = decision

        elif preflight_status == "stale":
            warnings.append("preflight is stale; update and validate it before the next affected design action")
        elif preflight_status == "pending":
            warnings.append("preflight is pending; complete it before requirements approval or design generation")

    if require_current_preflight and preflight_status != "current":
        errors.append("a current validated preflight is required")

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

    if requirements_status == "approved" and preflight_status != "current":
        errors.append("requirements approval requires a current validated preflight")
    if concept_status == "approved" and preflight_status != "current":
        errors.append("concept approval requires a current validated preflight")

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

    if concept_status in {"pending", "approved", "changes-requested"}:
        concept_asset = concept_approval.get("asset")
        expected_concept_sha256 = concept_approval.get("asset_sha256")
        concept_record = concept_approval.get("asset_sha256_record")
        resolved_concept_asset: Path | None = None

        if not isinstance(concept_asset, str) or not concept_asset.strip():
            errors.append("active concept gate needs a product concept image asset")
        else:
            resolved_concept_asset = (spec_path.parent / concept_asset).resolve()
            try:
                resolved_concept_asset.relative_to(spec_path.parent)
            except ValueError:
                errors.append("workflow.concept_approval.asset must remain inside the owning product directory")
            else:
                if not resolved_concept_asset.is_file():
                    errors.append(f"linked product concept image does not exist: {resolved_concept_asset}")
                elif not is_supported_concept_image(resolved_concept_asset):
                    errors.append("workflow.concept_approval.asset must be a supported image file with matching image content")

        if not isinstance(expected_concept_sha256, str) or HEX64_RE.fullmatch(expected_concept_sha256) is None:
            errors.append("active concept gate needs a lowercase SHA-256 in workflow.concept_approval.asset_sha256")
        elif resolved_concept_asset is not None and resolved_concept_asset.is_file():
            digest = hashlib.sha256(resolved_concept_asset.read_bytes()).hexdigest()
            if digest != expected_concept_sha256:
                errors.append("workflow.concept_approval.asset_sha256 does not match the linked concept image")

        if not isinstance(concept_record, str) or not concept_record.strip():
            errors.append("active concept gate needs workflow.concept_approval.asset_sha256_record")
        else:
            record_path = (spec_path.parent / concept_record).resolve()
            try:
                record_path.relative_to(spec_path.parent)
            except ValueError:
                errors.append("workflow.concept_approval.asset_sha256_record must remain inside the owning product directory")
            else:
                if not record_path.is_file():
                    errors.append(f"linked concept provenance record does not exist: {record_path}")
                else:
                    try:
                        record_data = load_structured(record_path)
                    except (OSError, ValueError, json.JSONDecodeError) as exc:
                        errors.append(f"cannot read linked concept provenance record: {exc}")
                    else:
                        record_text = json.dumps(record_data, sort_keys=True)
                        if isinstance(concept_asset, str) and concept_asset not in record_text:
                            errors.append("concept provenance record does not reference workflow.concept_approval.asset")
                        if isinstance(expected_concept_sha256, str) and expected_concept_sha256 not in record_text:
                            errors.append("concept provenance record does not contain workflow.concept_approval.asset_sha256")

    watermark_asset = watermark_approval.get("asset_id")
    if watermark_asset not in SUPPORTED_WATERMARK_ASSETS:
        errors.append(f"watermark approval asset_id must be one of {sorted(SUPPORTED_WATERMARK_ASSETS)}")
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
        if watermark_asset == RECOMMENDED_WATERMARK_ASSET:
            tier = watermark_approval.get("layout_tier")
            if tier not in {"full", "compact", "micro"}:
                errors.append(f"{watermark_status} R2 watermark needs layout_tier full, compact, or micro")
            expected_domain_visible = tier != "micro"
            if watermark_approval.get("domain_visible") is not expected_domain_visible:
                errors.append(
                    f"{watermark_status} R2 watermark domain_visible must be {expected_domain_visible} for {tier}"
                )
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
    branding_asset = branding.get("asset_id")
    if branding_asset not in SUPPORTED_WATERMARK_ASSETS:
        errors.append(f"branding.asset_id must be one of {sorted(SUPPORTED_WATERMARK_ASSETS)}")
    if branding_asset != watermark_asset:
        errors.append("branding.asset_id must equal workflow.watermark_approval.asset_id")
    if branding_asset == "MM-WM-001-R1":
        warnings.append("MM-WM-001-R1 is legacy-compatible; use MM-WM-001-R2 for new product revisions")
    if branding_asset == RECOMMENDED_WATERMARK_ASSET and branding.get("layout_tier") not in {
        "auto",
        "full",
        "compact",
        "micro",
    }:
        errors.append("branding.layout_tier must be auto, full, compact, or micro for MM-WM-001-R2")
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
        if preflight_decision.get("design_release") not in {"GO", "GO_WITH_CONTROLS"}:
            errors.append("final release requires a preflight design decision of GO or GO_WITH_CONTROLS")
        if preflight_decision.get("confidence") == "NOT_AUTONOMOUSLY_RELEASABLE":
            errors.append("preflight prohibits autonomous final release")

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
