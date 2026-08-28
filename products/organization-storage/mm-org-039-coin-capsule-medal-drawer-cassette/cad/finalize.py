#!/usr/bin/env python3
"""Bind exact slicer evidence and finalize the MM-ORG-039 digital candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "validation"
REPORTS = ROOT / "reports"
PROJECT_ID = "MM-ORG-039"
REVISION = "0.1.0-draft.1"
PROCESS = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/process/0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle.json")
BASE_FILAMENT = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/filament/Anycubic PLA @Anycubic Kobra 3 Max 0.4 nozzle.json")
FILAMENT = ROOT / "slicer-profiles/MM-ORG-039 Conservative Anycubic PLA 12.8.json"
PROFILE_FLOW_LIMIT = 12.8
AUDIT_FLOW_LIMIT = 13.3
FILAMENT_PROFILE_NAME = "MM-ORG-039 Conservative Anycubic PLA 12.8"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    try:
        display = str(path.relative_to(ROOT))
    except ValueError:
        display = str(path)
    return {"path": display, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def write_report(path: Path, tool: str, checks: list[dict], inputs: list[Path], metrics: dict, limitations: list[str]) -> None:
    value = {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [record(item) for item in inputs],
        "checks": checks,
        "metrics": metrics,
        "limitations": limitations,
        "required_capabilities": [],
    }
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def slicer_preflight() -> None:
    process = load(PROCESS)
    filament = load(FILAMENT)
    base_filament = load(BASE_FILAMENT)
    jobs = {
        "fit-label-and-mark-gauges": {
            "slice": VALIDATION / "slicer-anycubic-pla-gauges-run-002.json",
            "gcode": VALIDATION / "gcode-pla-gauges-run-002.json",
            "package": VALIDATION / "fdm-3mf-gauges.json",
            "exact": ROOT / "slicer-runs/anycubic-kobra3max-pla-gauges-run-002/plate_1.gcode",
        },
        "square-50-kit": {
            "slice": VALIDATION / "slicer-anycubic-pla-square-kit-run-001.json",
            "gcode": VALIDATION / "gcode-pla-square-kit-run-001.json",
            "package": VALIDATION / "fdm-3mf-square-kit.json",
            "exact": ROOT / "slicer-runs/anycubic-kobra3max-pla-square-kit-run-001/plate_1.gcode",
        },
        "round-46-kit": {
            "slice": VALIDATION / "slicer-anycubic-pla-round-kit-run-001.json",
            "gcode": VALIDATION / "gcode-pla-round-kit-run-001.json",
            "package": VALIDATION / "fdm-3mf-round-kit.json",
            "exact": ROOT / "slicer-runs/anycubic-kobra3max-pla-round-kit-run-001/plate_1.gcode",
        },
    }
    declared_flow = float(filament["filament_max_volumetric_speed"][0])
    density = float(base_filament["filament_density"][0])
    checks = [
        check("supports-disabled", process.get("enable_support") == "0", "Exact process profile disables generated support", {"process_sha256": sha256(PROCESS)}),
        check("declared-flow-limit", declared_flow == PROFILE_FLOW_LIMIT, "Project filament profile declares the expected conservative 12.8 mm3/s maximum", {"profile_limit_mm3_s": declared_flow}),
        check("profile-inheritance", filament.get("inherits") == base_filament.get("name"), "Project filament profile inherits the exact Anycubic PLA Kobra 3 Max profile"),
    ]
    inputs = [PROCESS, BASE_FILAMENT, FILAMENT]
    metrics = {}
    for name, paths in jobs.items():
        slice_report = load(paths["slice"])
        gcode_report = load(paths["gcode"])
        package_report = load(paths["package"])
        gmetrics = gcode_report["metrics"]
        native_warnings = [
            plate.get("warning_message", "")
            for plate in slice_report.get("native_result", {}).get("sliced_plates", [])
            if plate.get("warning_message", "")
        ]
        filament_names = [row["name"] for row in slice_report["slicer"]["profiles"] if row["type"] == "filament"]
        outputs = {row["relative_path"]: row for row in slice_report.get("outputs", [])}
        exact_output = outputs.get(paths["exact"].name, {})
        peak_flow = float(gmetrics["peak_flow_mm3_s"])
        checks.extend([
            check(f"{name}:package", package_report["status"] == "PASS", f"{name} 3MF package passes strict validation"),
            check(f"{name}:slice", slice_report["status"] == "PASS", f"{name} native slice succeeds"),
            check(f"{name}:native-warning", not native_warnings, f"{name} has no native slicer warnings", {"warnings": native_warnings}),
            check(f"{name}:gcode", gcode_report["status"] == "PASS", f"{name} G-code policy passes"),
            check(
                f"{name}:preserved",
                paths["exact"].exists()
                and exact_output.get("sha256") == sha256(paths["exact"])
                and exact_output.get("size_bytes") == paths["exact"].stat().st_size,
                f"{name} exact G-code hash and size match the slicer report",
                {"sha256": sha256(paths["exact"]), "size_bytes": paths["exact"].stat().st_size},
            ),
            check(f"{name}:single-tool", gmetrics["tools_seen"] == [0] and gmetrics["tool_changes"] == 0, f"{name} uses one tool with no tool changes"),
            check(f"{name}:parser-warnings", not gmetrics["warnings"], f"{name} parser reports no warnings"),
            check(
                f"{name}:material-profile",
                filament_names == [FILAMENT_PROFILE_NAME],
                f"{name} uses the declared conservative PLA filament profile",
                {"profile": filament_names[0] if filament_names else None},
            ),
            check(
                f"{name}:declared-flow",
                peak_flow <= AUDIT_FLOW_LIMIT,
                f"{name} parsed peak flow stays within the bounded 13.3 mm3/s audit limit",
                {"estimated_mm3_s": peak_flow, "profile_limit_mm3_s": declared_flow, "audit_limit_mm3_s": AUDIT_FLOW_LIMIT},
            ),
        ])
        inputs.extend([paths["slice"], paths["gcode"], paths["package"], paths["exact"]])
        metrics[name] = {
            "estimate_seconds": gmetrics["slicer_metadata_time_s"],
            "extruded_volume_mm3": gmetrics["extruded_volume_mm3"],
            "density_conversion_g": gmetrics["extruded_volume_mm3"] / 1000 * density,
            "layers": gmetrics["layers_from_comments"],
            "peak_flow_mm3_s": peak_flow,
            "profile_max_volumetric_speed_mm3_s": declared_flow,
            "gcode_path": str(paths["exact"].relative_to(ROOT)),
            "gcode_sha256": sha256(paths["exact"]),
            "material": "PLA",
        }
    write_report(
        VALIDATION / "slicer-preflight-report.json",
        f"{PROJECT_ID}-anycubic-slicer-preflight",
        checks,
        inputs,
        metrics,
        [
            "Density conversions are planning estimates, not scale measurements.",
            "The 13.3 mm3/s audit ceiling allows only parser rounding above the project profile's 12.8 mm3/s declaration.",
            "The stock-profile gauge run-001 exceeded the audit limit and is preserved as failed diagnostic evidence; it is not release evidence.",
            "Headless slicing does not replace the human final layer, seam, support, and bed-placement preview.",
            "No printer upload or print-start action was performed.",
        ],
    )


def print_candidate() -> None:
    required = [
        VALIDATION / "parametric-source-report.json",
        VALIDATION / "mesh-generation-report.json",
        VALIDATION / "interface-report.json",
        VALIDATION / "watermark-report.json",
        REPORTS / "optimization-comparison.json",
        VALIDATION / "fdm-mesh-host.json",
        VALIDATION / "fdm-mesh-square-adapter.json",
        VALIDATION / "fdm-mesh-round-adapter.json",
        VALIDATION / "fdm-mesh-interface-gauge.json",
        VALIDATION / "fdm-mesh-full-watermark-coupon.json",
        VALIDATION / "fdm-mesh-micro-watermark-coupon.json",
        VALIDATION / "fdm-3mf-square-kit.json",
        VALIDATION / "fdm-3mf-round-kit.json",
        VALIDATION / "fdm-3mf-gauges.json",
        VALIDATION / "slicer-preflight-report.json",
        VALIDATION / "approvals-through-slicer.json",
    ]
    checks = [check(f"report:{path.relative_to(ROOT)}", load(path)["status"] == "PASS", f"{path.relative_to(ROOT)} reports PASS") for path in required]
    slicer = load(VALIDATION / "slicer-preflight-report.json")
    jobs = slicer["metrics"]
    checks.extend([
        check("gauge-and-two-kits", set(jobs) == {"fit-label-and-mark-gauges", "square-50-kit", "round-46-kit"}, "Gauge and both complete-product variants have exact slicer evidence"),
        check("warning-free", all(row["status"] == "PASS" for row in slicer["checks"] if row["id"].endswith(("native-warning", "parser-warnings"))), "Final native and parser warning checks pass"),
        check("flow-safe", all(row["status"] == "PASS" for row in slicer["checks"] if row["id"].endswith("declared-flow")), "Bounded exact-profile flow checks pass"),
        check("physical-deferred", True, "Capsule fit, extraction, abrasion, loaded handling, label retention, mark legibility, final preview, appearance, and safety remain human-controlled"),
    ])
    totals = {
        "all_jobs_estimate_seconds": sum(job["estimate_seconds"] for job in jobs.values()),
        "all_jobs_density_conversion_g": sum(job["density_conversion_g"] for job in jobs.values()),
        "digital_print_candidate": True,
        "physical_validation": "DEFERRED",
        "commercial_release": "BLOCKED",
        "support_generation": "disabled_by_exact_process_profile",
        "jobs": jobs,
    }
    write_report(
        VALIDATION / "print-candidate-report.json",
        f"{PROJECT_ID}-finalize-digital-print-candidate",
        checks,
        required,
        totals,
        [
            "Capsule sizes are measured interface targets; actual supplier dimensions and edge radii must be checked with the exact gauge before a complete kit.",
            "The product stores encapsulated collectibles only; bare coin or medal contact, archival safety, tarnish prevention, chemical compatibility, and security are not claimed.",
            "The Full- and Micro-tier identity marks are digitally integrated; exact-process physical legibility remains pending.",
            "The final slicer layer, seam, support, and bed-placement review and all physical tests remain human-controlled.",
            "No printer upload or print-start action was performed.",
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["preflight", "candidate"])
    args = parser.parse_args()
    slicer_preflight() if args.stage == "preflight" else print_candidate()


if __name__ == "__main__":
    main()
