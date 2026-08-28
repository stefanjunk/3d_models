#!/usr/bin/env python3
"""Validate the exact MM-BOAT-003 Anycubic 3MF and sliced G-code candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "1.1.0-draft.1"
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PRODUCTION_NS = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
PROFILE_FLOW_LIMIT_MM3_S = 18.0
MACRO_SEGMENT_MM = 0.05
MACRO_FLOW_LIMIT_MM3_S = 18.45
ROUNDED_RAW_FLOW_LIMIT_MM3_S = 23.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def record(path: Path) -> dict:
    return {
        "path": relative(path),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


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


def validate_3mf(path: Path) -> tuple[list[dict], dict]:
    checks: list[dict] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        components = root.findall(f".//{{{CORE_NS}}}component")
        build_items = root.findall(f".//{{{CORE_NS}}}build/{{{CORE_NS}}}item")
        external_results = []
        for component in components:
            target = component.attrib.get(f"{{{PRODUCTION_NS}}}path", "").lstrip("/")
            target_id = component.attrib.get("objectid")
            exists = target in names
            has_object = False
            if exists:
                object_root = ET.fromstring(archive.read(target))
                has_object = any(
                    item.attrib.get("id") == target_id
                    for item in object_root.findall(f".//{{{CORE_NS}}}object")
                )
            external_results.append(
                {"path": target, "object_id": target_id, "exists": exists, "object_found": has_object}
            )

        hinge_pin_count = sum("hinge_pin" in row["path"] for row in external_results)
        distributed_ok = (
            len(components) == 21
            and len(build_items) == 21
            and all(row["exists"] and row["object_found"] for row in external_results)
        )
        checks.append(
            check(
                "anycubic-production-extension",
                distributed_ok,
                "All 21 build components resolve through the 3MF production extension",
                {
                    "build_items": len(build_items),
                    "distributed_components": len(components),
                    "resolved_components": sum(
                        row["exists"] and row["object_found"] for row in external_results
                    ),
                },
            )
        )
        checks.append(
            check(
                "complete-part-count",
                hinge_pin_count == 5,
                "The consolidated plate contains five hinge pins and 16 other parts",
                {"hinge_pins": hinge_pin_count, "other_parts": len(build_items) - hinge_pin_count},
            )
        )

        expected_settings = {
            "printer_settings_id": "Anycubic Kobra 3 Max 0.4 hardened steel nozzle",
            "print_settings_id": "MM-BOAT-003 0.20mm PETG Watertight @AC K3 Max 0.4",
            "layer_height": "0.2",
            "wall_loops": "6",
            "sparse_infill_density": "25%",
            "enable_support": "1",
            "support_on_build_plate_only": "1",
            "brim_type": "outer_only",
        }
        actual_settings = {key: settings.get(key) for key in expected_settings}
        filament_ids = settings.get("filament_settings_id", [])
        embedded_flow = float(settings.get("filament_max_volumetric_speed", ["nan"])[0])
        profile_ok = (
            actual_settings == expected_settings
            and filament_ids == ["ELEGOO PETG Rapid @Anycubic Kobra 3 Max 0.4 nozzle"]
            and embedded_flow == PROFILE_FLOW_LIMIT_MM3_S
        )
        checks.append(
            check(
                "embedded-profile-set",
                profile_ok,
                "3MF embeds the selected Kobra 3 Max, watertight PETG and ELEGOO Rapid PETG profiles",
                {
                    **actual_settings,
                    "filament_settings_id": filament_ids,
                    "filament_max_volumetric_speed_mm3_s": embedded_flow,
                },
            )
        )

    metrics = {
        "build_items": len(build_items),
        "hinge_pin_count": hinge_pin_count,
        "embedded_profiles": {
            "machine": settings.get("printer_settings_id"),
            "process": settings.get("print_settings_id"),
            "filament": filament_ids,
        },
    }
    return checks, metrics


def _words(command: str) -> dict[str, float]:
    return {
        letter.upper(): float(value)
        for letter, value in re.findall(r"([A-Za-z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))", command)
    }


def reconstruct_flow(path: Path, filament_diameter_mm: float = 1.75) -> dict:
    """Reconstruct endpoint flow and preserve the segment length of every excess."""
    xyz_absolute = True
    e_absolute = True
    unit_scale = 1.0
    position = {axis: 0.0 for axis in "XYZE"}
    feed_mm_min = 0.0
    filament_area = math.pi * (filament_diameter_mm / 2.0) ** 2
    empty_peak = {
        "flow_mm3_s": 0.0,
        "line": None,
        "segment_length_mm": 0.0,
        "delta_e_mm": 0.0,
        "feed_mm_min": 0.0,
    }
    raw_peak = dict(empty_peak)
    macro_peak = dict(empty_peak)
    excess_count = 0
    max_excess_segment_mm = 0.0

    with path.open(errors="replace") as stream:
        for line_number, raw_line in enumerate(stream, 1):
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
                        position[axis] = values[axis] * unit_scale
                continue
            if opcode not in {"G0", "G1"}:
                continue
            if "F" in values:
                feed_mm_min = values["F"] * unit_scale
            target = dict(position)
            for axis in "XYZ":
                if axis in values:
                    value = values[axis] * unit_scale
                    target[axis] = value if xyz_absolute else position[axis] + value
            if "E" in values:
                value = values["E"] * unit_scale
                target["E"] = value if e_absolute else position["E"] + value
            segment_mm = math.sqrt(
                sum((target[axis] - position[axis]) ** 2 for axis in "XYZ")
            )
            delta_e_mm = target["E"] - position["E"]
            if segment_mm > 0.0 and delta_e_mm > 0.0 and feed_mm_min > 0.0:
                duration_s = segment_mm / (feed_mm_min / 60.0)
                flow_mm3_s = delta_e_mm * filament_area / duration_s
                row = {
                    "flow_mm3_s": flow_mm3_s,
                    "line": line_number,
                    "segment_length_mm": segment_mm,
                    "delta_e_mm": delta_e_mm,
                    "feed_mm_min": feed_mm_min,
                }
                if flow_mm3_s > raw_peak["flow_mm3_s"]:
                    raw_peak = row
                if segment_mm >= MACRO_SEGMENT_MM and flow_mm3_s > macro_peak["flow_mm3_s"]:
                    macro_peak = row
                if flow_mm3_s > MACRO_FLOW_LIMIT_MM3_S:
                    excess_count += 1
                    max_excess_segment_mm = max(max_excess_segment_mm, segment_mm)
            position = target

    return {
        "raw_peak": raw_peak,
        "macro_peak": macro_peak,
        "macro_segment_threshold_mm": MACRO_SEGMENT_MM,
        "macro_flow_limit_mm3_s": MACRO_FLOW_LIMIT_MM3_S,
        "raw_flow_limit_mm3_s": ROUNDED_RAW_FLOW_LIMIT_MM3_S,
        "segments_above_macro_limit": excess_count,
        "max_segment_above_macro_limit_mm": max_excess_segment_mm,
    }


def parse_footer(path: Path) -> dict:
    patterns = {
        "filament_mm": re.compile(r"^; filament used \[mm\] = ([0-9.]+)$"),
        "filament_cm3": re.compile(r"^; filament used \[cm3\] = ([0-9.]+)$"),
        "filament_g": re.compile(r"^; filament used \[g\] = ([0-9.]+)$"),
        "layers": re.compile(r"^; total layers count = (\d+)$"),
        "normal_time": re.compile(r"^; estimated printing time \(normal mode\) = (.+)$"),
    }
    result: dict[str, float | int | str] = {}
    with path.open(errors="replace") as stream:
        for raw_line in stream:
            line = raw_line.rstrip("\n")
            for key, pattern in patterns.items():
                match = pattern.match(line)
                if match:
                    value = match.group(1)
                    result[key] = int(value) if key == "layers" else float(value) if key.startswith("filament_") else value
    return result


def validate_slice(slicer_report_path: Path, gcode_path: Path) -> tuple[list[dict], dict]:
    report = load(slicer_report_path)
    gcode_hash = sha256(gcode_path)
    output = next(
        (item for item in report.get("outputs", []) if item.get("relative_path") == gcode_path.name),
        {},
    )
    native_warnings = [
        plate.get("warning_message", "")
        for plate in report.get("native_result", {}).get("sliced_plates", [])
        if plate.get("warning_message", "")
    ]
    gcode_report = report.get("gcode_reports", {}).get(gcode_path.name, {})
    gcode_metrics = gcode_report.get("metrics", {})
    checks = [
        check(
            "native-anycubic-slice",
            report.get("status") == "PASS"
            and report.get("slicer", {}).get("version") == "1.3.9.4"
            and report.get("native_result", {}).get("error_string") == "Success."
            and not native_warnings,
            "Anycubic Slicer Next 1.3.9.4 completed locally without native warnings",
            {
                "slicer_version": report.get("slicer", {}).get("version"),
                "native_warnings": native_warnings,
                "triangle_count": report.get("native_result", {})
                .get("sliced_plates", [{}])[0]
                .get("triangle_count"),
            },
        ),
        check(
            "exact-gcode-preserved",
            output.get("sha256") == gcode_hash
            and output.get("size_bytes") == gcode_path.stat().st_size,
            "Exact G-code hash and byte size match the native slicer report",
            {"sha256": gcode_hash, "size_bytes": gcode_path.stat().st_size},
        ),
        check(
            "single-tool-layer-consistency",
            gcode_report.get("status") == "PASS"
            and gcode_metrics.get("tools_seen") == [0]
            and gcode_metrics.get("tool_changes") == 0
            and gcode_metrics.get("layers_from_comments") == 1179,
            "G-code uses one tool, no tool changes and 1179 consistent layers",
            {
                "tools_seen": gcode_metrics.get("tools_seen"),
                "tool_changes": gcode_metrics.get("tool_changes"),
                "layers": gcode_metrics.get("layers_from_comments"),
                "motion_bounds_mm": gcode_metrics.get("motion_bounds_mm"),
            },
        ),
    ]

    flow = reconstruct_flow(gcode_path, float(gcode_metrics.get("filament_diameter_mm", 1.75)))
    raw = flow["raw_peak"]
    macro = flow["macro_peak"]
    flow_ok = (
        raw["flow_mm3_s"] <= ROUNDED_RAW_FLOW_LIMIT_MM3_S
        and macro["flow_mm3_s"] <= MACRO_FLOW_LIMIT_MM3_S
        and flow["max_segment_above_macro_limit_mm"] < MACRO_SEGMENT_MM
    )
    checks.append(
        check(
            "rounded-coordinate-flow-scope",
            flow_ok,
            "Any reconstructed excess above 18.45 mm3/s is confined below 0.05 mm while the >=0.05 mm domain remains bounded",
            flow,
        )
    )
    footer = parse_footer(gcode_path)
    checks.append(
        check(
            "slicer-footer-metrics",
            footer.get("layers") == 1179
            and footer.get("normal_time") == "21h 4m 16s"
            and footer.get("filament_g") == 376.41,
            "Slicer footer exposes the expected time, layer and material planning values",
            footer,
        )
    )
    return checks, {"flow": flow, "slicer_footer": footer, "gcode": gcode_metrics}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--three-mf", type=Path, required=True)
    parser.add_argument("--slicer-report", type=Path, required=True)
    parser.add_argument("--gcode", type=Path, required=True)
    parser.add_argument("--machine-profile", type=Path, required=True)
    parser.add_argument("--process-profile", type=Path, required=True)
    parser.add_argument("--filament-profile", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    paths = [
        args.three_mf.resolve(),
        args.slicer_report.resolve(),
        args.gcode.resolve(),
        args.machine_profile.resolve(),
        args.process_profile.resolve(),
        args.filament_profile.resolve(),
    ]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        parser.error(f"missing input files: {missing}")

    three_mf_checks, three_mf_metrics = validate_3mf(paths[0])
    slice_checks, slice_metrics = validate_slice(paths[1], paths[2])
    checks = three_mf_checks + slice_checks
    report = {
        "schema_version": "1.0",
        "tool": "MM-BOAT-003 Anycubic print-candidate validator",
        "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft-print-candidate",
        "inputs": [record(path) for path in paths],
        "checks": checks,
        "metrics": {"three_mf": three_mf_metrics, "slice": slice_metrics},
        "limitations": [
            "The generic repository 3MF validator does not traverse Anycubic's production-extension distributed object resources; native Anycubic import and exact slicing are the authoritative compatibility evidence here.",
            "The flow audit reconstructs ratios from rounded emitted coordinates. Its bounded allowance is arithmetic evidence, not a physical hotend-flow measurement and must not excuse a sustained excess.",
            "Headless slicing does not replace final human GUI review of layers, supports, seams and bed placement.",
            "No printer upload or print-start action was performed.",
            "Watertightness, fit, trim, flotation and powered swimming still require the documented physical coupons and prototype tests.",
        ],
        "required_capabilities": [],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "report": str(args.json_out), "checks": len(checks)}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
