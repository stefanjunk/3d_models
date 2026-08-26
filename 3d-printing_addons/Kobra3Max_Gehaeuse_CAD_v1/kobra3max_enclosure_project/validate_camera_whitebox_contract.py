#!/usr/bin/env python3
"""Deterministic dimensional checks for the Kobra 3 Max camera whitebox."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def simple_number(source: str, name: str) -> float:
    match = re.search(
        rf"(?m)^\s*{re.escape(name)}\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)\s*;",
        source,
    )
    if not match:
        raise ValueError(f"Cannot find simple numeric assignment for {name}")
    return float(match.group(1))


def default_number(source: str, name: str) -> float:
    match = re.search(
        rf"(?m)^\s*{re.escape(name)}\s*=\s*is_undef\({re.escape(name)}\)\s*\?\s*"
        rf"(-?[0-9]+(?:\.[0-9]+)?)\s*:\s*{re.escape(name)}\s*;",
        source,
    )
    if not match:
        raise ValueError(f"Cannot find default assignment for {name}")
    return float(match.group(1))


def check(checks: list[dict], check_id: str, passed: bool, message: str, **metrics: float) -> None:
    checks.append(
        {
            "id": check_id,
            "status": "PASS" if passed else "FAIL",
            "required": True,
            "message": message,
            "metrics": metrics,
            "evidence": [],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", required=True)
    args = parser.parse_args()

    design_spec = ROOT / "design-spec.yaml"
    parts_source = ROOT / "kobra3max_enclosure.scad"
    assembly_source = ROOT / "kobra3max_enclosure_complete.scad"
    dimensions_source = ROOT / "camera_whitebox_dimensions.py"
    inputs = [design_spec, parts_source, assembly_source, dimensions_source]

    assembly = assembly_source.read_text(encoding="utf-8")
    parts = parts_source.read_text(encoding="utf-8")

    w = simple_number(assembly, "W")
    d = simple_number(assembly, "D")
    h = simple_number(assembly, "H")
    b = simple_number(assembly, "B")
    panel = simple_number(assembly, "PANEL")
    service_bay = simple_number(assembly, "SERVICE_BAY_W")
    overlap = simple_number(assembly, "DOOR_OVERLAP")
    cassette_inset = simple_number(assembly, "LIGHT_CASSETTE_INSET")
    window_cut_w = simple_number(assembly, "WINDOW_CUT_W")
    window_cut_h = simple_number(assembly, "WINDOW_CUT_H")
    window_cx = simple_number(assembly, "WINDOW_CX")
    window_cz = simple_number(assembly, "WINDOW_CZ")

    keepout_w, keepout_d, keepout_h = 706.0, 940.0, 753.0
    clear_w = w - 2 * b - 2 * panel
    clear_d = d - 2 * b - panel
    clear_h = h - 2 * b
    side_margin = (clear_w - keepout_w) / 2
    depth_margin = (clear_d - keepout_d) / 2
    height_margin = clear_h - keepout_h

    stile_x = w - b - service_bay
    door_w = stile_x - b + 2 * overlap
    door_h = clear_h + 2 * overlap
    cassette_w = w - 2 * cassette_inset
    cassette_d = d - 2 * cassette_inset

    eye_t = default_number(parts, "CAMERA_ARM_EYE_T")
    hinge_clearance = default_number(parts, "CAMERA_HINGE_CLEARANCE")
    hinge_d = default_number(parts, "CAMERA_HINGE_D")
    baffle_depth = default_number(parts, "BAFFLE_DEPTH")
    camera_face_w = default_number(parts, "CAMERA_FACE_W")
    camera_face_h = default_number(parts, "CAMERA_FACE_H")
    camera_reference_full_h = default_number(parts, "CAMERA_REFERENCE_FULL_H")
    camera_reference_depth = default_number(parts, "CAMERA_REFERENCE_DEPTH")
    camera_protected_depth = default_number(parts, "CAMERA_PROTECTED_DEPTH")
    fit_clearance = default_number(parts, "CAMERA_FIT_CLEARANCE")
    lens_d = default_number(parts, "CAMERA_LENS_D")
    led_d = default_number(parts, "CAMERA_LED_D")
    ball_d = default_number(parts, "CAMERA_BALL_D")
    ball_clearance = default_number(parts, "CAMERA_BALL_CLEARANCE")
    window_w = default_number(parts, "CAMERA_WINDOW_W")
    window_h = default_number(parts, "CAMERA_WINDOW_H")
    window_tilt = default_number(parts, "CAMERA_WINDOW_TILT")
    fork_gap = eye_t + hinge_clearance

    service_cutout_y = 730.0
    service_cutout_z = 620.0
    service_cutout_d = 250.0
    service_cutout_h = 170.0
    rear_edge_clearance = d - (service_cutout_y + service_cutout_d)
    top_edge_clearance = h - (service_cutout_z + service_cutout_h)
    baffle_inner_width = 170.0 - 2 * 2.6
    baffle_inlet_area = baffle_inner_width * baffle_depth
    fan_open_area = math.pi * (114.0 / 2) ** 2
    baffle_area_ratio = baffle_inlet_area / fan_open_area

    service_panel_left = w - service_bay - 10.0
    service_panel_right = service_panel_left + service_bay
    window_left = window_cx - (window_w + 16.0) / 2
    window_right = window_cx + (window_w + 16.0) / 2
    window_bottom = window_cz - (window_h + 16.0) / 2
    window_top = window_cz + (window_h + 16.0) / 2

    checks: list[dict] = []
    check(checks, "body-side-clearance", side_margin >= 25,
          "Centred side margin is at least 25 mm", actual_mm=side_margin, minimum_mm=25)
    check(checks, "body-depth-clearance", depth_margin >= 25,
          "Centred front/rear margin is at least 25 mm", actual_mm=depth_margin, minimum_mm=25)
    check(checks, "body-height-clearance", height_margin >= 35,
          "Height margin is at least 35 mm", actual_mm=height_margin, minimum_mm=35)
    check(checks, "door-positive-envelope", door_w > 650 and door_h > 800,
          "Main door remains a usable positive opening", width_mm=door_w, height_mm=door_h)
    check(checks, "service-bay-range", 110 <= service_bay <= 220,
          "Fixed service bay stays within approved practical range", actual_mm=service_bay,
          minimum_mm=110, maximum_mm=220)
    check(checks, "roof-cassette-positive", cassette_w > 700 and cassette_d > 850,
          "Roof-light cassette retains useful illuminated area", width_mm=cassette_w,
          depth_mm=cassette_d)
    check(checks, "camera-fork-clearance", 0.4 <= hinge_clearance <= 0.9,
          "Camera fork has a coupon-testable FDM clearance", eye_mm=eye_t,
          gap_mm=fork_gap, total_clearance_mm=hinge_clearance)
    check(checks, "camera-hinge-hole", 4.4 <= hinge_d <= 4.7,
          "Camera hinge hole is a bounded M4 clearance feature", actual_mm=hinge_d,
          minimum_mm=4.4, maximum_mm=4.7)
    check(checks, "camera-official-interface",
          camera_face_w == 22.50 and camera_face_h == 38.50
          and camera_reference_full_h == 43.50 and camera_reference_depth == 25.00
          and lens_d == 14.30 and led_d == 5.50,
          "Camera interface constants match the recorded official reference measurements",
          face_width_mm=camera_face_w, face_height_mm=camera_face_h,
          full_reference_height_mm=camera_reference_full_h,
          full_reference_depth_mm=camera_reference_depth,
          lens_diameter_mm=lens_d, led_diameter_mm=led_d)
    check(checks, "camera-protected-depth",
          camera_protected_depth >= camera_reference_depth + 0.20,
          "Assembled shell depth exceeds the documented 25 mm reference extent",
          protected_depth_mm=camera_protected_depth,
          reference_depth_mm=camera_reference_depth,
          allowance_mm=camera_protected_depth-camera_reference_depth)
    check(checks, "camera-fit-clearance", 0.15 <= fit_clearance <= 0.60,
          "Camera body clearance is bounded and has a dedicated fit coupon",
          radial_clearance_mm=fit_clearance,
          cavity_width_mm=camera_face_w + 2 * fit_clearance,
          cavity_height_mm=camera_face_h + 2 * fit_clearance)
    check(checks, "camera-ball-interface", ball_d == 11.0 and 0.20 <= ball_clearance <= 0.40,
          "Independent ball/socket interface uses the approved coupon-tuned dimensions",
          ball_diameter_mm=ball_d, nominal_radial_clearance_mm=ball_clearance)
    check(checks, "camera-window-aperture",
          window_cut_w <= window_w - 8 and window_cut_h <= window_h - 8,
          "The service-panel cutout remains fully covered by the clear optical pane",
          cutout_width_mm=window_cut_w, cutout_height_mm=window_cut_h,
          pane_width_mm=window_w, pane_height_mm=window_h)
    check(checks, "camera-window-service-bay",
          window_left >= service_panel_left and window_right <= service_panel_right
          and window_bottom >= 20 and window_top <= h - 20,
          "Window frame fits the fixed service panel with an edge border",
          left_border_mm=window_left - service_panel_left,
          right_border_mm=service_panel_right - window_right,
          bottom_mm=window_bottom, top_mm=window_top)
    check(checks, "camera-window-tilt", 4 <= window_tilt <= 10,
          "Optical pane tilt is bounded for reflection control",
          tilt_deg=window_tilt, minimum_deg=4, maximum_deg=10)
    check(checks, "camera-source-independence", re.search(r"\bimport\s*\(", parts) is None,
          "Project CAD contains no imported mesh geometry", import_calls=0)
    check(checks, "complete-assembly-content",
          all(token in assembly for token in (
              "complete_enclosure();", "fixed_service_panel();", "camera_subsystem();",
              "roof_light_cassette();", "exhaust_system();")),
          "Complete assembly instantiates enclosure, service, camera, light and exhaust systems",
          required_subsystems=5)
    check(checks, "service-cutout-edge-distance",
          rear_edge_clearance >= 35 and top_edge_clearance >= 35,
          "Exhaust service cutout stays clear of rear and top sheet edges",
          rear_edge_mm=rear_edge_clearance, top_edge_mm=top_edge_clearance, minimum_mm=35)
    check(checks, "baffle-inlet-area", baffle_area_ratio >= 0.9,
          "Baffle bottom inlet is at least 90% of the 114 mm fan opening area",
          inlet_area_mm2=baffle_inlet_area, fan_open_area_mm2=fan_open_area,
          area_ratio=baffle_area_ratio)

    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "schema_version": "1.0",
        "tool": "validate_camera_whitebox_contract",
        "tool_version": "1.1.0",
        "status": status,
        "profile": "draft",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
            for path in inputs
        ],
        "checks": checks,
        "metrics": {
            "body_mm": [w, d, h],
            "clear_after_skins_mm": [clear_w, clear_d, clear_h],
            "printer_keepout_mm": [keepout_w, keepout_d, keepout_h],
            "door_mm": [door_w, door_h],
            "roof_cassette_mm": [cassette_w, cassette_d],
            "camera_face_mm": [camera_face_w, camera_face_h],
            "camera_depth_mm": [camera_reference_depth, camera_protected_depth],
            "camera_ball_socket_mm": [ball_d, ball_clearance],
            "camera_window_mm": [window_w, window_h, window_tilt],
        },
        "limitations": [
            "The printer keep-out remains a planning envelope rather than a physical swept-volume measurement.",
            "Camera-body fit and ball/socket friction require printed coupons and the purchased camera.",
            "Door rotation, cable sweep, camera field of view, optical reflections and thermal performance require physical tests.",
        ],
        "required_capabilities": [],
    }

    output = ROOT / args.json_out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "output": str(output), "check_count": len(checks)}))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
