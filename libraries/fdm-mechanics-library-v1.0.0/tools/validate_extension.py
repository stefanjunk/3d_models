#!/usr/bin/env python3
"""Validate the approved 1.1.0-draft.1 extension contract and fresh renders."""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import csv
import hashlib
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
import yaml

from generate_sources import make_sample_records, readme_text, wrapper_text
from library_spec import FAMILIES

ROOT = Path(__file__).resolve().parents[1]
EXTENSION_FAMILIES = set(range(31, 40))
EXTENSION_IDS = {f"{sample_id:03d}" for sample_id in range(121, 157)}
SEALING_FAMILIES = {31, 32, 35, 37, 39}
LEGACY_PARAMETERS = {
    31: {"squeeze"},
    32: {"clearance", "compression"},
    33: {"clearance"},
    34: {"output_r"},
    36: {"clearance"},
    39: {"switch_l"},
}
INVALID_CASES: dict[int, tuple[str, dict[str, Any]]] = {
    31: ("radial_squeeze_below_minimum", {"radial_squeeze": 0.04}),
    32: ("running_clearance_below_minimum", {"running_clearance": 0.19}),
    33: ("axial_stop_below_minimum", {"axial_stop": 0.30}),
    34: ("pivot_offset_not_above_crank_envelope", {"pivot_offset": 11}),
    35: ("piston_clearance_below_minimum", {"clearance": 0.10}),
    36: ("head_d_insufficient", {"head_d": 3}),
    37: ("compression_length_below_minimum", {"compression_l": 2}),
    38: ("contact_keepout_too_large", {"contact_keepout": 23}),
    39: ("wall_thickness_below_minimum", {"wall_t": 0.9}),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scad_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(scad_value(item) for item in value) + "]"
    return repr(value)


def module_parameters(source: str, module: str) -> set[str]:
    match = re.search(rf"module\s+{re.escape(module)}\s*\((.*?)\)\s*\{{", source, re.DOTALL)
    if not match:
        return set()
    return set(re.findall(r"(?:^|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", match.group(1)))


def mesh_metrics(path: Path) -> dict[str, Any]:
    mesh = trimesh.load(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Could not load mesh: {path}")
    canonical_triangles = [
        tuple(sorted(tuple(round(float(coordinate), 6) for coordinate in vertex) for vertex in triangle))
        for triangle in np.asarray(mesh.triangles)
    ]
    canonical_triangles.sort()
    canonical_digest = hashlib.sha256()
    for triangle in canonical_triangles:
        canonical_digest.update(np.asarray(triangle, dtype="<f8").tobytes())
    return {
        "sha256": sha256(path),
        "canonical_triangle_sha256": canonical_digest.hexdigest(),
        "faces": int(len(mesh.faces)),
        "vertices": int(len(mesh.vertices)),
        "components": int(len(mesh.split(only_watertight=False))),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "bounds_mm": np.asarray(mesh.bounds).round(6).tolist(),
        "volume_mm3": float(abs(mesh.volume)),
        "surface_area_mm2": float(mesh.area),
    }


def compare_metrics(packaged: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    packaged_bounds = np.asarray(packaged["bounds_mm"], dtype=float)
    fresh_bounds = np.asarray(fresh["bounds_mm"], dtype=float)
    volume_scale = max(packaged["volume_mm3"], 1e-9)
    area_scale = max(packaged["surface_area_mm2"], 1e-9)
    canonical_match = packaged["canonical_triangle_sha256"] == fresh["canonical_triangle_sha256"]
    return {
        "exact_sha256_match": packaged["sha256"] == fresh["sha256"],
        "canonical_triangle_sha256_match": canonical_match,
        "bounds_max_delta_mm": float(np.max(np.abs(packaged_bounds - fresh_bounds))),
        "relative_volume_delta": abs(packaged["volume_mm3"] - fresh["volume_mm3"]) / volume_scale,
        "relative_surface_area_delta": abs(packaged["surface_area_mm2"] - fresh["surface_area_mm2"]) / area_scale,
        "face_count_delta": fresh["faces"] - packaged["faces"],
        "component_count_match": packaged["components"] == fresh["components"],
        "geometry_equivalent": canonical_match,
    }


def render_record(record: dict[str, Any], timeout: int) -> dict[str, Any]:
    args = ["view=\"plate\""] + [f"{key}={scad_value(value)}" for key, value in record["params"].items()]
    source = (
        f"use <{ROOT / 'library/fdm_mechanisms.scad'}>\n"
        "$fn=48;\n"
        f"{record['module']}({', '.join(args)});\n"
    )
    packaged_path = ROOT / record["stl_path"]
    with tempfile.TemporaryDirectory(prefix=f"fdm-extension-{record['id']}-") as tmp:
        tmp_path = Path(tmp)
        harness = tmp_path / "model.scad"
        fresh_path = tmp_path / "fresh.stl"
        harness.write_text(source, encoding="utf-8")
        command = ["openscad", "-o", str(fresh_path), str(harness)]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        output = completed.stdout + completed.stderr
        result: dict[str, Any] = {
            "id": record["id"],
            "family": record["family_number"],
            "module": record["module"],
            "returncode": completed.returncode,
            "unknown_parameter_warning": "Ignoring unknown parameter" in output,
            "render_passed": completed.returncode == 0 and fresh_path.is_file(),
        }
        if not result["render_passed"]:
            result["diagnostic_tail"] = output[-1000:]
            return result
        packaged = mesh_metrics(packaged_path)
        fresh = mesh_metrics(fresh_path)
        result["packaged"] = packaged
        result["fresh"] = fresh
        result["comparison"] = compare_metrics(packaged, fresh)
        result["passed"] = result["comparison"]["geometry_equivalent"] and not result["unknown_parameter_warning"]
        return result


def render_boundary_case(
    family: dict[str, Any], label: str, params: dict[str, Any], expect_success: bool, timeout: int
) -> dict[str, Any]:
    args = ["view=\"plate\""] + [f"{key}={scad_value(value)}" for key, value in params.items()]
    source = (
        f"use <{ROOT / 'library/fdm_mechanisms.scad'}>\n"
        "$fn=24;\n"
        f"{family['module']}({', '.join(args)});\n"
    )
    with tempfile.TemporaryDirectory(prefix=f"fdm-boundary-{family['family']}-") as tmp:
        tmp_path = Path(tmp)
        harness = tmp_path / "boundary.scad"
        output_path = tmp_path / "boundary.stl"
        harness.write_text(source, encoding="utf-8")
        completed = subprocess.run(
            ["openscad", "-o", str(output_path), str(harness)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = completed.stdout + completed.stderr
        rendered = completed.returncode == 0 and output_path.is_file() and output_path.stat().st_size > 256
        assertion_failed = "ERROR: Assertion" in output
        passed = rendered and not assertion_failed if expect_success else assertion_failed
        return {
            "family": family["family"],
            "module": family["module"],
            "case": label,
            "expect_success": expect_success,
            "returncode": completed.returncode,
            "rendered": rendered,
            "assertion_failed": assertion_failed,
            "unknown_parameter_warning": "Ignoring unknown parameter" in output,
            "passed": passed and "Ignoring unknown parameter" not in output,
        }


def validate_contract(require_fresh_build_summary: bool) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    spec = yaml.safe_load((ROOT / "design-spec.yaml").read_text(encoding="utf-8"))
    revision = spec.get("project", {}).get("revision")
    requirements = spec.get("workflow", {}).get("requirements_approval", {})
    concept = spec.get("workflow", {}).get("concept_approval", {})
    concept_path = ROOT / str(concept.get("asset", ""))
    gates = {
        "revision": revision,
        "requirements_status": requirements.get("status"),
        "requirements_revision": requirements.get("spec_revision"),
        "concept_status": concept.get("status"),
        "concept_revision": concept.get("spec_revision"),
        "concept_asset": concept.get("asset"),
        "concept_asset_exists": concept_path.is_file(),
        "concept_asset_sha256": sha256(concept_path) if concept_path.is_file() else None,
    }
    if not (
        revision == "1.1.0-draft.1"
        and requirements.get("status") == "approved"
        and requirements.get("spec_revision") == revision
        and concept.get("status") == "approved"
        and concept.get("spec_revision") == revision
        and concept_path.is_file()
    ):
        errors.append("Requirements/concept gates are not valid for 1.1.0-draft.1")

    expected = make_sample_records()
    expected_extension = [record for record in expected if record["id"] in EXTENSION_IDS]
    catalog = json.loads((ROOT / "catalog/catalog.json").read_text(encoding="utf-8"))
    catalog_by_id = {record["id"]: record for record in catalog}
    spec_families = {item["id"]: item for item in spec.get("function", {}).get("included_families", [])}
    family_by_number = {family["family"]: family for family in FAMILIES}
    scad_source = (ROOT / "library/fdm_mechanisms.scad").read_text(encoding="utf-8")
    family_checks: list[dict[str, Any]] = []

    for family_number in sorted(EXTENSION_FAMILIES):
        family = family_by_number[family_number]
        spec_family = spec_families.get(family_number, {})
        required = set(spec_family.get("required_public_parameters", []))
        signature = module_parameters(scad_source, family["module"])
        variants = [record for record in expected_extension if record["family_number"] == family_number]
        missing_by_variant = {
            record["id"]: sorted(required - set(record["params"]))
            for record in variants
            if required - set(record["params"])
        }
        legacy_by_variant = {
            record["id"]: sorted(LEGACY_PARAMETERS.get(family_number, set()) & set(record["params"]))
            for record in variants
            if LEGACY_PARAMETERS.get(family_number, set()) & set(record["params"])
        }
        check = {
            "family": family_number,
            "module": family["module"],
            "variant_count": len(variants),
            "required_parameters": sorted(required),
            "module_parameters": sorted(signature),
            "missing_module_parameters": sorted(required - signature),
            "missing_by_variant": missing_by_variant,
            "legacy_by_variant": legacy_by_variant,
        }
        check["passed"] = (
            len(variants) == 4
            and not check["missing_module_parameters"]
            and not missing_by_variant
            and not legacy_by_variant
        )
        if not check["passed"]:
            errors.append(f"Family {family_number} does not satisfy the approved public-parameter contract")
        family_checks.append(check)

    artifact_errors: list[dict[str, Any]] = []
    for record in expected_extension:
        sample_dir = ROOT / "samples" / record["relative_directory"]
        mismatches: list[str] = []
        if catalog_by_id.get(record["id"]) != record:
            mismatches.append("catalog")
        metadata_path = sample_dir / "metadata.json"
        if not metadata_path.is_file() or json.loads(metadata_path.read_text(encoding="utf-8")) != record:
            mismatches.append("metadata")
        model_path = sample_dir / "model.scad"
        if not model_path.is_file() or model_path.read_text(encoding="utf-8") != wrapper_text(record):
            mismatches.append("model")
        readme_path = sample_dir / "README.md"
        if not readme_path.is_file() or readme_path.read_text(encoding="utf-8") != readme_text(record):
            mismatches.append("README")
        if mismatches:
            artifact_errors.append({"id": record["id"], "mismatches": mismatches})
    if artifact_errors:
        errors.append(f"{len(artifact_errors)} extension samples have stale generated artifacts")

    with (ROOT / "catalog/catalog.csv").open(encoding="utf-8", newline="") as handle:
        csv_records = list(csv.DictReader(handle))
    csv_by_id = {record.get("id"): record for record in csv_records}
    catalog_html = (ROOT / "CATALOG.html").read_text(encoding="utf-8")
    catalog_md = (ROOT / "catalog/CATALOG_DE.md").read_text(encoding="utf-8")
    claims_record_errors: list[dict[str, Any]] = []
    for record in expected_extension:
        issues: list[str] = []
        if record.get("artifact_status") != "experimental-draft":
            issues.append("record_artifact_status")
        if record.get("qualification_status") != "unqualified":
            issues.append("record_qualification_status")
        if "DRAFT" not in record.get("status_de", "") or "nicht physisch qualifiziert" not in record.get("status_de", ""):
            issues.append("record_status_disclosure")
        claim = record.get("claims_de", "")
        if not claim:
            issues.append("record_claims_missing")

        csv_record = csv_by_id.get(record["id"], {})
        for field in ("artifact_status", "qualification_status", "status_de", "claims_de"):
            if csv_record.get(field) != record.get(field):
                issues.append(f"catalog_csv_{field}")

        sample_dir = ROOT / "samples" / record["relative_directory"]
        metadata = json.loads((sample_dir / "metadata.json").read_text(encoding="utf-8"))
        for field in ("artifact_status", "qualification_status", "status_de", "claims_de"):
            if metadata.get(field) != record.get(field):
                issues.append(f"metadata_{field}")

        readme = (sample_dir / "README.md").read_text(encoding="utf-8")
        for required_text in ("`experimental-draft`", "`unqualified`", record["status_de"], claim):
            if required_text not in readme:
                issues.append("README_status_or_claims")
                break
        if re.search(r"\bdruckfertig\w*\b", readme, re.IGNORECASE):
            issues.append("README_unqualified_druckfertig_claim")

        card_match = re.search(
            rf'<article class="card" data-id="{record["id"]}".*?</article>',
            catalog_html,
            re.DOTALL,
        )
        card = card_match.group(0) if card_match else ""
        for required_text in ("experimental-draft", "unqualified", html.escape(claim)):
            if required_text not in card:
                issues.append("CATALOG_html_status_or_claims")
                break
        catalog_md_line = next(
            (line for line in catalog_md.splitlines() if line.startswith(f"| {record['id']} |")),
            "",
        )
        if "`experimental-draft` / `unqualified`" not in catalog_md_line:
            issues.append("CATALOG_md_status")

        if record["family_number"] in SEALING_FAMILIES:
            for required_text in ("Konstruktionsabsicht", "Keine geprüfte Leckrate", "IP-/Wasserdichtheit"):
                if required_text not in claim:
                    issues.append("sealing_claim_boundary")
                    break
        if record["family_number"] == 39:
            for required_text in ("ununterbrochenen Wandbarriere", "ohne Sensordurchbruch"):
                if required_text not in claim:
                    issues.append("family_39_wall_intent_boundary")
                    break
            if "Dichte Schalter" in record["use_de"]:
                issues.append("family_39_unbounded_use_wording")

        if issues:
            claims_record_errors.append({"id": record["id"], "issues": sorted(set(issues))})

    catalog_header_passed = (
        "Erweiterung 121–156" in catalog_html
        and "experimental-draft" in catalog_html
        and "unqualified" in catalog_html
        and not re.search(r"\bdruckfertig\w*\b", catalog_html, re.IGNORECASE)
    )
    if not catalog_header_passed:
        errors.append("CATALOG.html does not bound the extension DRAFT/qualification claims")
    if claims_record_errors:
        errors.append(f"{len(claims_record_errors)} extension records fail claims-bounded disclosure checks")

    claims_bounded = {
        "extension_records_checked": len(expected_extension),
        "required_artifact_status": "experimental-draft",
        "required_qualification_status": "unqualified",
        "catalog_json_checked": len(expected_extension),
        "catalog_csv_checked": len(expected_extension),
        "metadata_checked": len(expected_extension),
        "readmes_checked": len(expected_extension),
        "catalog_html_cards_checked": len(expected_extension),
        "catalog_markdown_rows_checked": len(expected_extension),
        "sealing_records_checked": sum(record["family_number"] in SEALING_FAMILIES for record in expected_extension),
        "family_39_records_checked": sum(record["family_number"] == 39 for record in expected_extension),
        "catalog_header_passed": catalog_header_passed,
        "record_errors": claims_record_errors,
        "passed": catalog_header_passed and not claims_record_errors and len(expected_extension) == 36,
    }

    fresh_build: dict[str, Any] | None = None
    fresh_summary_path = ROOT / "validation/extension-build-summary.json"
    if fresh_summary_path.is_file():
        summary = json.loads(fresh_summary_path.read_text(encoding="utf-8"))
        results = summary.get("results", [])
        fresh_build = {
            "samples_requested": summary.get("samples_requested"),
            "passed": summary.get("passed"),
            "warning": summary.get("warning"),
            "failed": summary.get("failed"),
            "all_extension_ids": {item.get("id") for item in results} == EXTENSION_IDS,
            "all_forced_stl_renders": all(
                not item.get("stl_reused") and item.get("stl_render_seconds", 0) > 0 for item in results
            ),
            "all_forced_preview_renders": all(
                not item.get("preview_reused") and item.get("preview_render_seconds", 0) > 0 for item in results
            ),
            "all_previews_preserved": all(item.get("preview_preserved") is True for item in results),
        }
        fresh_build["passed_check"] = (
            fresh_build["samples_requested"] == 36
            and fresh_build["passed"] == 36
            and fresh_build["warning"] == 0
            and fresh_build["failed"] == 0
            and fresh_build["all_extension_ids"]
            and fresh_build["all_forced_stl_renders"]
            and (fresh_build["all_forced_preview_renders"] or fresh_build["all_previews_preserved"])
        )
        if require_fresh_build_summary and not fresh_build["passed_check"]:
            errors.append("Fresh extension build summary does not prove 36 forced STL renders and an explicit preview disposition")
    elif require_fresh_build_summary:
        errors.append("Fresh extension build summary is missing")

    contract = {
        "gates": gates,
        "catalog_count": len(catalog),
        "extension_record_count": len(expected_extension),
        "family_checks": family_checks,
        "generated_artifact_errors": artifact_errors,
        "claims_bounded": claims_bounded,
        "fresh_build": fresh_build,
    }
    return contract, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="validation/extension-validation.json")
    parser.add_argument("--compare-packaged", action="store_true")
    parser.add_argument("--render-boundaries", action="store_true")
    parser.add_argument("--require-fresh-build-summary", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    contract, errors = validate_contract(args.require_fresh_build_summary)
    records = [record for record in make_sample_records() if record["id"] in EXTENSION_IDS]
    geometry_regression: list[dict[str, Any]] = []
    if args.compare_packaged:
        with futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            geometry_regression = list(pool.map(lambda record: render_record(record, args.timeout), records))
        geometry_regression.sort(key=lambda item: item["id"])
        failed = [item["id"] for item in geometry_regression if not item.get("passed")]
        if failed:
            errors.append(f"Fresh source renders are not exactly equivalent for: {', '.join(failed)}")

    boundary_results: list[dict[str, Any]] = []
    if args.render_boundaries:
        families = {family["family"]: family for family in FAMILIES if family["family"] in EXTENSION_FAMILIES}
        cases: list[tuple[dict[str, Any], str, dict[str, Any], bool, int]] = []
        for family_number, family in sorted(families.items()):
            cases.append((family, "first_catalog_variant", dict(family["variants"][0]["params"]), True, args.timeout))
            cases.append((family, "last_catalog_variant", dict(family["variants"][-1]["params"]), True, args.timeout))
            label, override = INVALID_CASES[family_number]
            invalid_params = dict(family["variants"][0]["params"])
            invalid_params.update(override)
            cases.append((family, label, invalid_params, False, args.timeout))
        with futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            boundary_results = list(pool.map(lambda item: render_boundary_case(*item), cases))
        boundary_results.sort(key=lambda item: (item["family"], item["case"]))
        failed = [f"F{item['family']}:{item['case']}" for item in boundary_results if not item["passed"]]
        if failed:
            errors.append(f"Boundary render failures: {', '.join(failed)}")

    report = {
        "spec_revision": contract["gates"]["revision"],
        "status": "passed" if not errors else "failed",
        "checks": contract,
        "geometry_regression": geometry_regression,
        "boundary_results": boundary_results,
        "errors": errors,
    }
    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": report["status"],
        "contract_families": len(contract["family_checks"]),
        "stale_generated_samples": len(contract["generated_artifact_errors"]),
        "claims_bounded": contract["claims_bounded"]["passed"],
        "claims_records_checked": contract["claims_bounded"]["extension_records_checked"],
        "geometry_comparisons": len(geometry_regression),
        "geometry_equivalent": sum(item.get("passed", False) for item in geometry_regression),
        "boundary_cases": len(boundary_results),
        "boundary_passed": sum(item.get("passed", False) for item in boundary_results),
        "errors": errors,
        "report": args.report,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
