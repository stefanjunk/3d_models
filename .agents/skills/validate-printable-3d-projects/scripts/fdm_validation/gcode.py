from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

from .common import check, report

TOKEN = re.compile(r"([A-Za-z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
TIME_PATTERNS = [
    re.compile(r"estimated printing time.*?=\s*(.+)", re.I),
    re.compile(r"TIME:\s*(\d+(?:\.\d+)?)", re.I),
]


def _duration(text: str) -> float | None:
    if text.replace(".", "", 1).isdigit():
        return float(text)
    values = {unit: float(value) for value, unit in re.findall(r"(\d+(?:\.\d+)?)\s*([dhms])", text.lower())}
    if not values:
        return None
    return values.get("d", 0) * 86400 + values.get("h", 0) * 3600 + values.get("m", 0) * 60 + values.get("s", 0)


def analyze(path: Path, policy: dict[str, Any] | None = None, profile: str = "release") -> dict[str, Any]:
    policy = policy or {}
    if not path.is_file():
        return report("analyze-gcode", [check("gcode-file", "FAIL", f"G-code not found: {path}")], inputs=[path], profile=profile)

    absolute_xyz = True
    absolute_e = True
    position = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    feed_mm_min = 0.0
    unit_scale_mm = 1.0
    bounds = {axis: [math.inf, -math.inf] for axis in "XYZ"}
    tools: set[int] = {0}
    current_tool = 0
    e_positions: dict[int, float] = {0: 0.0}
    tool_changes = 0
    arc_moves = 0
    volumetric_extrusion_seen = False
    layers = 0
    last_layer_marker: str | None = None
    extrusion_mm_by_tool: dict[int, float] = {0: 0.0}
    travel_mm = 0.0
    print_move_mm = 0.0
    motion_seconds = 0.0
    peak_flow_mm3_s = 0.0
    peak_flow_line = None
    filament_diameter = float(policy.get("filament_diameter_mm", 1.75))
    filament_area = math.pi * (filament_diameter / 2.0) ** 2
    metadata_time = None
    warnings: list[str] = []

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw in enumerate(handle, start=1):
            stripped = raw.strip()
            if stripped.startswith(";"):
                upper = stripped.upper()
                if upper.startswith(";LAYER:") or upper.startswith("; LAYER "):
                    marker = stripped
                    if marker != last_layer_marker:
                        layers += 1
                        last_layer_marker = marker
                for pattern in TIME_PATTERNS:
                    match = pattern.search(stripped)
                    if match:
                        metadata_time = _duration(match.group(1).strip())
                continue
            code = stripped.split(";", 1)[0].strip()
            if not code:
                continue
            words = code.split()
            command_index = 1 if words and re.fullmatch(r"N\d+", words[0], re.I) and len(words) > 1 else 0
            command = words[command_index].upper()
            values = {letter.upper(): float(value) for letter, value in TOKEN.findall(code)}
            if command == "G20":
                unit_scale_mm = 25.4
            elif command == "G21":
                unit_scale_mm = 1.0
            elif command == "G90":
                absolute_xyz = True
            elif command == "G91":
                absolute_xyz = False
            elif command == "M82":
                absolute_e = True
            elif command == "M83":
                absolute_e = False
            elif command == "G92":
                for axis in "XYZ":
                    if axis in values:
                        position[axis] = values[axis] * unit_scale_mm
                if "E" in values:
                    e_positions[current_tool] = values["E"] * unit_scale_mm
            elif command == "M200":
                volumetric_extrusion_seen = values.get("D", 1.0) != 0.0
            elif command.startswith("T") and command[1:].isdigit():
                new_tool = int(command[1:])
                tools.add(new_tool)
                extrusion_mm_by_tool.setdefault(new_tool, 0.0)
                e_positions.setdefault(new_tool, 0.0)
                if new_tool != current_tool:
                    tool_changes += 1
                    current_tool = new_tool
            elif command in {"G0", "G1", "G2", "G3"}:
                if command in {"G2", "G3"}:
                    arc_moves += 1
                old = position.copy()
                if "F" in values:
                    feed_mm_min = values["F"] * unit_scale_mm
                for axis in "XYZ":
                    if axis in values:
                        coordinate = values[axis] * unit_scale_mm
                        position[axis] = coordinate if absolute_xyz else position[axis] + coordinate
                if "E" in values:
                    coordinate = values["E"] * unit_scale_mm
                    new_e = coordinate if absolute_e else e_positions[current_tool] + coordinate
                    delta_e = new_e - e_positions[current_tool]
                    e_positions[current_tool] = new_e
                else:
                    delta_e = 0.0
                spatial = math.sqrt(sum((position[axis] - old[axis]) ** 2 for axis in "XYZ"))
                for axis in "XYZ":
                    bounds[axis][0] = min(bounds[axis][0], position[axis])
                    bounds[axis][1] = max(bounds[axis][1], position[axis])
                if feed_mm_min > 0 and spatial > 0:
                    seconds = spatial / (feed_mm_min / 60.0)
                    motion_seconds += seconds
                    if delta_e > 0:
                        flow = delta_e * filament_area / seconds
                        if flow > peak_flow_mm3_s:
                            peak_flow_mm3_s = flow
                            peak_flow_line = line_number
                if delta_e > 0:
                    extrusion_mm_by_tool[current_tool] += delta_e
                    print_move_mm += spatial
                else:
                    travel_mm += spatial

    finite_bounds = {
        axis: ([None, None] if not math.isfinite(values[0]) else values)
        for axis, values in bounds.items()
    }
    if layers == 0:
        warnings.append("No recognized layer comments were found; layer count is unknown")
    metrics = {
        "layers_from_comments": layers or None,
        "tools_seen": sorted(tools),
        "tool_changes": tool_changes,
        "arc_moves": arc_moves,
        "volumetric_extrusion_seen": volumetric_extrusion_seen,
        "positive_extrusion_mm_by_tool": {str(key): value for key, value in sorted(extrusion_mm_by_tool.items())},
        "positive_extrusion_total_mm": sum(extrusion_mm_by_tool.values()),
        "filament_diameter_mm": filament_diameter,
        "extruded_volume_mm3": sum(extrusion_mm_by_tool.values()) * filament_area,
        "motion_time_lower_bound_s": motion_seconds,
        "slicer_metadata_time_s": metadata_time,
        "travel_path_mm": travel_mm,
        "printing_move_path_mm": print_move_mm,
        "peak_flow_mm3_s": peak_flow_mm3_s,
        "peak_flow_line": peak_flow_line,
        "motion_bounds_mm": finite_bounds,
        "warnings": warnings,
    }
    checks = [check("gcode-parse", "PASS", "G-code parsed without executing or uploading it")]
    checks.append(check("filament-diameter", "PASS" if filament_diameter > 0 else "FAIL", f"Filament diameter {filament_diameter:g} mm"))
    strict_motion = bool(policy.get("require_complete_motion")) or any(key in policy for key in ("bed_mm", "max_flow_mm3_s"))
    if arc_moves:
        checks.append(check("arc-motion", "NOT_RUN" if strict_motion else "REVIEW_REQUIRED", f"{arc_moves} arc move(s) were reduced to endpoint chords; bounds, time, and flow are incomplete", required=strict_motion))
    if volumetric_extrusion_seen:
        strict_extrusion = any(key in policy for key in ("max_flow_mm3_s", "min_positive_extrusion_mm", "max_positive_extrusion_mm"))
        checks.append(check("volumetric-extrusion", "NOT_RUN" if strict_extrusion else "REVIEW_REQUIRED", "M200 volumetric extrusion was enabled; filament-length metrics are not comparable", required=strict_extrusion))
    if "max_tool_changes" in policy:
        limit = int(policy["max_tool_changes"])
        checks.append(check("tool-change-budget", "PASS" if tool_changes <= limit else "FAIL", f"Tool changes {tool_changes} / {limit}", metrics={"actual": tool_changes, "limit": limit}))
    if "max_flow_mm3_s" in policy:
        limit = float(policy["max_flow_mm3_s"])
        checks.append(check("flow-budget", "PASS" if peak_flow_mm3_s <= limit else "FAIL", f"Peak estimated flow {peak_flow_mm3_s:.6g} / {limit:g} mm³/s", metrics={"actual_mm3_s": peak_flow_mm3_s, "limit_mm3_s": limit, "line": peak_flow_line}))
    positive_extrusion = sum(extrusion_mm_by_tool.values())
    if "min_positive_extrusion_mm" in policy:
        limit = float(policy["min_positive_extrusion_mm"])
        checks.append(check("minimum-extrusion", "PASS" if positive_extrusion >= limit >= 0 else "FAIL", f"Positive extrusion {positive_extrusion:.6g} mm; minimum {limit:g} mm"))
    if "max_positive_extrusion_mm" in policy:
        limit = float(policy["max_positive_extrusion_mm"])
        checks.append(check("maximum-extrusion", "PASS" if 0 <= positive_extrusion <= limit else "FAIL", f"Positive extrusion {positive_extrusion:.6g} mm; maximum {limit:g} mm"))
    if "allowed_tools" in policy:
        allowed = {int(item) for item in policy["allowed_tools"]}
        unexpected = sorted(tools - allowed)
        checks.append(check("tool-allowlist", "PASS" if not unexpected else "FAIL", "All tools are allowed" if not unexpected else f"Unexpected tools: {unexpected}", metrics={"seen": sorted(tools), "allowed": sorted(allowed)}))
    if "max_metadata_time_s" in policy:
        limit = float(policy["max_metadata_time_s"])
        if metadata_time is None:
            checks.append(check("metadata-time", "NOT_RUN", "No recognized slicer time metadata was found"))
        else:
            checks.append(check("metadata-time", "PASS" if metadata_time <= limit else "FAIL", f"Slicer metadata time {metadata_time:.6g} s; maximum {limit:g} s"))
    if "bed_mm" in policy:
        bed = policy["bed_mm"]
        passed = isinstance(bed, list) and len(bed) == 3
        if passed:
            for index, axis in enumerate("XYZ"):
                low, high = finite_bounds[axis]
                if low is not None and (low < -1e-9 or high > float(bed[index]) + 1e-9):
                    passed = False
        checks.append(check("gcode-bed-bounds", "PASS" if passed else "FAIL", "Motion stays within declared non-negative build bounds" if passed else "Motion exceeds or cannot be compared to build bounds", metrics={"motion_bounds_mm": finite_bounds, "bed_mm": bed}))
    if policy.get("require_layer_markers"):
        checks.append(check("layer-markers", "PASS" if layers else "FAIL", f"Recognized layer markers: {layers}"))
    if "min_layers" in policy:
        minimum = int(policy["min_layers"])
        checks.append(check("minimum-layers", "PASS" if layers >= minimum else "FAIL", f"Recognized layers {layers}; minimum {minimum}"))
    return report(
        "analyze-gcode",
        checks,
        inputs=[path],
        profile=profile,
        metrics=metrics,
        limitations=[
            "Motion time ignores acceleration, cooling, dwell, firmware behavior, and many slicer-specific commands.",
            "Peak flow is derived from positive E and linear move time; pressure advance and firmware limits can differ.",
            "Arc endpoints are parsed, but curved bounds, path length, time, and flow require a slicer-native or arc-aware backend.",
            "Layer and metadata parsing depends on common comments; retain the exact slicer project and preview.",
        ],
    )
