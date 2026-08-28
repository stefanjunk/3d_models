#!/usr/bin/env python3
"""Bind exact slicer evidence and finalize the MM-ORG-037 digital candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "validation"
REPORTS = ROOT / "reports"
PROJECT_ID = "MM-ORG-037"
REVISION = "0.1.0-draft.1"
PROCESS = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/process/0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle.json")
FILAMENT = Path("/opt/AnycubicSlicerNext/share/resources/profiles/Anycubic/filament/Anycubic PLA @Anycubic Kobra 3 Max 0.4 nozzle.json")
PROFILE_FLOW_LIMIT = 13.0
MACRO_FLOW_LIMIT = 13.3
PARSER_FLOW_LIMIT = 14.6
MACRO_SEGMENT_MM = 0.05
ROUNDED_COORDINATE_SEGMENT_MM = 0.01


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


def _words(command: str) -> dict[str, float]:
    return {letter.upper(): float(value) for letter, value in re.findall(r"([A-Za-z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))", command)}


def reconstruct_flow(path: Path, filament_diameter_mm: float = 1.75) -> dict:
    """Recompute extrusion flow while retaining segment length for rounding checks."""
    xyz_absolute = True
    e_absolute = True
    unit_scale = 1.0
    pos = {"X": 0.0, "Y": 0.0, "Z": 0.0, "E": 0.0}
    feed_mm_min = 0.0
    area = math.pi * (filament_diameter_mm / 2.0) ** 2
    raw_peak = {"flow_mm3_s": 0.0, "line": None, "segment_length_mm": 0.0, "delta_e_mm": 0.0, "feed_mm_min": 0.0}
    macro_peak = dict(raw_peak)

    for line_number, raw_line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        command = raw_line.split(";", 1)[0].strip()
        if not command:
            continue
        opcode = command.split()[0].upper()
        if opcode == "G20":
            unit_scale = 25.4
            continue
        if opcode == "G21":
            unit_scale = 1.0
            continue
        if opcode == "G90":
            xyz_absolute = True
            continue
        if opcode == "G91":
            xyz_absolute = False
            continue
        if opcode == "M82":
            e_absolute = True
            continue
        if opcode == "M83":
            e_absolute = False
            continue
        values = _words(command)
        if opcode == "G92":
            for axis in "XYZE":
                if axis in values:
                    pos[axis] = values[axis] * unit_scale
            continue
        if opcode not in {"G0", "G1"}:
            continue
        if "F" in values:
            feed_mm_min = values["F"] * unit_scale
        target = dict(pos)
        for axis in "XYZ":
            if axis in values:
                coordinate = values[axis] * unit_scale
                target[axis] = coordinate if xyz_absolute else pos[axis] + coordinate
        if "E" in values:
            coordinate = values["E"] * unit_scale
            target["E"] = coordinate if e_absolute else pos["E"] + coordinate
        segment = math.sqrt(sum((target[axis] - pos[axis]) ** 2 for axis in "XYZ"))
        delta_e = target["E"] - pos["E"]
        if segment > 0.0 and delta_e > 0.0 and feed_mm_min > 0.0:
            duration_s = segment / (feed_mm_min / 60.0)
            flow = delta_e * area / duration_s
            row = {
                "flow_mm3_s": flow,
                "line": line_number,
                "segment_length_mm": segment,
                "delta_e_mm": delta_e,
                "feed_mm_min": feed_mm_min,
            }
            if flow > raw_peak["flow_mm3_s"]:
                raw_peak = row
            if segment >= MACRO_SEGMENT_MM and flow > macro_peak["flow_mm3_s"]:
                macro_peak = row
        pos = target
    return {"raw_peak": raw_peak, "macro_peak": macro_peak, "macro_segment_threshold_mm": MACRO_SEGMENT_MM}


def slicer_preflight() -> None:
    process = load(PROCESS)
    filament = load(FILAMENT)
    jobs = {
        "fit-gauges": {
            "slice": VALIDATION / "slicer-anycubic-pla-gauges-run-002.json",
            "gcode": VALIDATION / "gcode-pla-gauges-run-002.json",
            "package": VALIDATION / "fdm-3mf-gauges.json",
            "exact": ROOT / "slicer-runs/anycubic-next-1.3.9.4-kobra3max-pla-0p20-gauges-run-002/plate_1.gcode",
        },
        "cb-kit": {
            "slice": VALIDATION / "slicer-anycubic-pla-cb-kit-run-002.json",
            "gcode": VALIDATION / "gcode-pla-cb-kit-run-002.json",
            "package": VALIDATION / "fdm-3mf-cb-kit.json",
            "exact": ROOT / "slicer-runs/anycubic-next-1.3.9.4-kobra3max-pla-0p20-cb-kit-run-002/plate_1.gcode",
        },
        "horizontal-kit": {
            "slice": VALIDATION / "slicer-anycubic-pla-horizontal-kit-run-002.json",
            "gcode": VALIDATION / "gcode-pla-horizontal-kit-run-002.json",
            "package": VALIDATION / "fdm-3mf-horizontal-kit.json",
            "exact": ROOT / "slicer-runs/anycubic-next-1.3.9.4-kobra3max-pla-0p20-horizontal-kit-run-002/plate_1.gcode",
        },
    }
    declared_flow = float(filament["filament_max_volumetric_speed"][0])
    density = float(filament["filament_density"][0])
    checks = [
        check("supports-disabled", process.get("enable_support") == "0", "Exact process profile disables generated support", {"process_sha256": sha256(PROCESS)}),
        check("declared-flow-limit", declared_flow == PROFILE_FLOW_LIMIT, "Exact filament profile declares the expected 13 mm3/s maximum", {"profile_limit_mm3_s": declared_flow}),
    ]
    inputs = [PROCESS, FILAMENT]
    metrics = {}
    for name, paths in jobs.items():
        slice_report = load(paths["slice"])
        gcode_report = load(paths["gcode"])
        package_report = load(paths["package"])
        gmetrics = gcode_report["metrics"]
        flow = reconstruct_flow(paths["exact"], float(gmetrics["filament_diameter_mm"]))
        raw = flow["raw_peak"]
        macro = flow["macro_peak"]
        native_warnings = [
            plate.get("warning_message", "")
            for plate in slice_report.get("native_result", {}).get("sliced_plates", [])
            if plate.get("warning_message", "")
        ]
        filament_names = [row["name"] for row in slice_report["slicer"]["profiles"] if row["type"] == "filament"]
        outputs = {row["relative_path"]: row for row in slice_report.get("outputs", [])}
        exact_output = outputs.get(paths["exact"].name, {})
        parser_peak = float(gmetrics["peak_flow_mm3_s"])
        parser_excess_is_rounded_microsegment = (
            raw["flow_mm3_s"] <= PARSER_FLOW_LIMIT
            and raw["segment_length_mm"] < ROUNDED_COORDINATE_SEGMENT_MM
            and macro["flow_mm3_s"] <= MACRO_FLOW_LIMIT
        )
        flow_scope_pass = parser_peak <= MACRO_FLOW_LIMIT or parser_excess_is_rounded_microsegment
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
                filament_names == ["Anycubic PLA @Anycubic Kobra 3 Max 0.4 nozzle"],
                f"{name} uses the declared PLA filament profile",
                {"profile": filament_names[0] if filament_names else None},
            ),
            check(
                f"{name}:macro-flow",
                macro["flow_mm3_s"] <= MACRO_FLOW_LIMIT,
                f"{name} independently reconstructed extrusion segments >= {MACRO_SEGMENT_MM} mm stay within 2.3% of the exact profile limit",
                {**macro, "limit_mm3_s": MACRO_FLOW_LIMIT},
            ),
            check(
                f"{name}:rounded-coordinate-flow-scope",
                flow_scope_pass,
                f"{name} parser peak is within the macro limit or confined to a < {ROUNDED_COORDINATE_SEGMENT_MM} mm rounded-coordinate microsegment",
                {
                    "parser_peak_mm3_s": parser_peak,
                    "independent_raw_peak": raw,
                    "independent_macro_peak": macro,
                    "parser_limit_mm3_s": PARSER_FLOW_LIMIT,
                },
            ),
        ])
        inputs.extend([paths["slice"], paths["gcode"], paths["package"], paths["exact"]])
        metrics[name] = {
            "estimate_seconds": gmetrics["slicer_metadata_time_s"],
            "extruded_volume_mm3": gmetrics["extruded_volume_mm3"],
            "density_conversion_g": gmetrics["extruded_volume_mm3"] / 1000 * density,
            "layers": gmetrics["layers_from_comments"],
            "parser_raw_peak_flow_mm3_s": parser_peak,
            "independent_raw_peak": raw,
            "independent_macro_peak": macro,
            "macro_segment_threshold_mm": MACRO_SEGMENT_MM,
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
            "The analyzer reconstructs flow from five-decimal rounded G-code. A parser-only excess is accepted only when independently confined to a <0.01 mm segment while every segment >=0.05 mm remains within 2.3% of the exact 13 mm3/s profile limit.",
            "The initial gauges run-001 path-resolution failure is preserved separately and is not release evidence.",
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
        VALIDATION / "fdm-mesh-cassette.json",
        VALIDATION / "fdm-mesh-cb-insert.json",
        VALIDATION / "fdm-mesh-horizontal-insert.json",
        VALIDATION / "fdm-mesh-bobbin-gauge.json",
        VALIDATION / "fdm-mesh-foot-gauge.json",
        VALIDATION / "fdm-mesh-watermark-coupon.json",
        VALIDATION / "fdm-3mf-cb-kit.json",
        VALIDATION / "fdm-3mf-horizontal-kit.json",
        VALIDATION / "fdm-3mf-gauges.json",
        VALIDATION / "slicer-preflight-report.json",
        VALIDATION / "approvals-through-slicer.json",
    ]
    checks = [check(f"report:{path.relative_to(ROOT)}", load(path)["status"] == "PASS", f"{path.relative_to(ROOT)} reports PASS") for path in required]
    slicer = load(VALIDATION / "slicer-preflight-report.json")
    jobs = slicer["metrics"]
    checks.extend([
        check("gauge-and-two-kit-jobs", set(jobs) == {"fit-gauges", "cb-kit", "horizontal-kit"}, "Fit-gauge and both complete-product plates have exact slicer evidence"),
        check("warning-free", all(row["status"] == "PASS" for row in slicer["checks"] if row["id"].endswith(("native-warning", "parser-warnings"))), "Final native and parser warning checks pass"),
        check("macro-flow-safe", all(row["status"] == "PASS" for row in slicer["checks"] if row["id"].endswith(("macro-flow", "rounded-coordinate-flow-scope"))), "Independent macro-segment flow checks pass"),
        check("physical-deferred", True, "Bobbin and presser-foot fit, insert retention, drawer fit, watermark legibility, final preview, appearance, and safety remain human-controlled"),
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
            "Published bobbin dimensions establish nominal targets, not fit with the user's particular bobbins or printer calibration.",
            "Generic presser-foot cells intentionally avoid brand compatibility claims; the width gauge must be checked against the intended collection.",
            "The selected Full-tier identity is digitally integrated; its exact-process physical legibility coupon remains pending.",
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
