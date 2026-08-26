#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import yaml

SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from surface_geometry import (  # noqa: E402
    curve_metrics,
    extrude_closed_profile,
    loft_closed_sections,
    mesh_metrics,
    pchip_profile,
    write_ascii_stl,
    write_csv_points,
    write_json,
    write_obj,
)


def make_svg(path: Path, plan_left: np.ndarray, plan_right: np.ndarray, roofline: np.ndarray, chassis: np.ndarray) -> None:
    length = float(max(plan_left[:, 0].max(), chassis[:, 0].max()))
    max_width = float(max(np.abs(plan_left[:, 1]).max(), np.abs(chassis[:, 1]).max()))

    def plan_map(points: np.ndarray) -> str:
        return " ".join(f"{50 + 820*x/length:.2f},{180 - 130*y/max_width:.2f}" for x, y in points[:, :2])

    max_z = float(roofline[:, 1].max())
    side = " ".join(f"{50 + 820*x/length:.2f},{415 - 180*z/max_z:.2f}" for x, z in roofline)
    body_outline = np.vstack([plan_left, plan_right[::-1], plan_left[:1]])
    chassis_outline = np.vstack([chassis, chassis[:1]])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="460" viewBox="0 0 920 460">
<rect width="920" height="460" fill="white"/>
<text x="30" y="30" font-family="sans-serif" font-size="22">RC car freeform envelope — top and side</text>
<polyline points="{plan_map(body_outline)}" fill="none" stroke="black" stroke-width="2"/>
<polyline points="{plan_map(chassis_outline)}" fill="none" stroke="#777" stroke-width="1.5" stroke-dasharray="5 4"/>
<polyline points="{side}" fill="none" stroke="black" stroke-width="2"/>
</svg>\n'''
    path.write_text(svg, encoding="utf-8")


def build_body(p: dict, quality: str) -> tuple[np.ndarray, np.ndarray, dict]:
    length = float(p["length_mm"])
    ground = float(p["body_ground_mm"])
    base_stations = np.asarray(p["station_s"], dtype=float)
    stations = np.unique(np.r_[base_stations, (base_stations[:-1] + base_stations[1:]) / 2.0]) if quality == "print" else base_stations
    count = int(p[f"body_section_points_{quality}"])
    half = max(16, count // 2)
    width_profile = p["half_width_profile"]
    roof_profile = p["roof_height_profile"]
    sections: list[np.ndarray] = []
    plan_left: list[list[float]] = []
    plan_right: list[list[float]] = []
    roofline: list[list[float]] = []

    for s in stations:
        x = length * s
        width = float(pchip_profile(s, width_profile["s"], width_profile["mm"]))
        roof_height = float(pchip_profile(s, roof_profile["s"], roof_profile["mm_above_ground"]))
        side_height = roof_height * float(p["side_height_ratio"])
        u_top = np.linspace(-1.0, 1.0, half)
        y_top = width * u_top
        normalized = np.clip(1.0 - np.abs(u_top) ** float(p["roof_cross_exponent"]), 0.0, 1.0)
        crown = normalized ** float(p["roof_roundness_exponent"])
        shoulder = float(p["shoulder_bulge_mm"]) * np.exp(-0.5 * ((np.abs(u_top) - 0.70) / 0.17) ** 2)
        z_top = ground + side_height + (roof_height - side_height) * crown + shoulder
        u_bottom = np.linspace(1.0, -1.0, half)[1:-1]
        y_bottom = width * u_bottom
        z_bottom = ground + float(p["underbody_camber_mm"]) * (1.0 - u_bottom**2)
        section = np.vstack([
            np.column_stack([np.full_like(u_top, x), y_top, z_top]),
            np.column_stack([np.full_like(u_bottom, x), y_bottom, z_bottom]),
        ])
        sections.append(section)
        plan_left.append([x, width, 0.0])
        plan_right.append([x, -width, 0.0])
        roofline.append([x, ground + roof_height + float(p["shoulder_bulge_mm"]) * np.exp(-0.5 * (0.70 / 0.17) ** 2)])

    vertices, faces, alignment = loft_closed_sections(sections, point_count=count)
    return vertices, faces, {
        "alignment": alignment,
        "plan_left": np.asarray(plan_left),
        "plan_right": np.asarray(plan_right),
        "roofline": np.asarray(roofline),
    }


def build_chassis(p: dict, quality: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    chassis = p["chassis"]
    samples = int(chassis[f"outline_samples_{quality}"])
    x_knots = np.asarray(chassis["half_width_profile"]["x_mm"], dtype=float)
    widths = np.asarray(chassis["half_width_profile"]["mm"], dtype=float)
    x = np.linspace(x_knots[0], x_knots[-1], samples)
    w = pchip_profile(x, x_knots, widths)
    left = np.column_stack([x, w])
    right = np.column_stack([x[::-1], -w[::-1]])
    profile = np.vstack([left, right])
    vertices, faces = extrude_closed_profile(profile, 0.0, float(chassis["thickness_mm"]))
    return vertices, faces, profile


def hardpoints_from_parameters(p: dict) -> dict:
    h = p["hardpoints"]
    front = float(h["front_axle_x_mm"])
    rear = float(h["rear_axle_x_mm"])
    z = float(h["axle_z_mm"])
    half = float(h["axle_axis_half_length_mm"])
    return {
        "coordinate_system": {"x": "front-to-rear", "y": "left-to-right", "z": "up", "units": "mm"},
        "wheelbase_mm": rear - front,
        "axes": [
            {"name": "front_axle", "start": [front, -half, z], "end": [front, half, z]},
            {"name": "rear_axle", "start": [rear, -half, z], "end": [rear, half, z]},
        ],
        "points": [{"name": f"chassis_mount_{i+1}", "position": point} for i, point in enumerate(h["chassis_mounts"])],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quality", choices=("draft", "print"), default="draft")
    args = parser.parse_args()
    p = yaml.safe_load(args.parameters.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)

    body_v, body_f, body_data = build_body(p, args.quality)
    chassis_v, chassis_f, chassis_profile = build_chassis(p, args.quality)
    hardpoints = hardpoints_from_parameters(p)
    write_obj(args.output / "rc-body-envelope.obj", body_v, body_f, object_name="rc_body_envelope")
    write_ascii_stl(args.output / "rc-body-envelope.stl", body_v, body_f, solid_name="rc_body_envelope")
    write_obj(args.output / "rc-chassis.obj", chassis_v, chassis_f, object_name="rc_chassis")
    write_ascii_stl(args.output / "rc-chassis.stl", chassis_v, chassis_f, solid_name="rc_chassis")
    write_csv_points(args.output / "body-plan-left.csv", body_data["plan_left"])
    write_csv_points(args.output / "body-plan-right.csv", body_data["plan_right"])
    write_csv_points(args.output / "body-roofline.csv", body_data["roofline"])
    write_json(args.output / "hardpoints.json", hardpoints)
    shutil.copy2(args.parameters, args.output / "parameters.yaml")
    make_svg(args.output / "preview.svg", body_data["plan_left"], body_data["plan_right"], body_data["roofline"], chassis_profile)

    body_metrics = mesh_metrics(body_v, body_f)
    chassis_metrics = mesh_metrics(chassis_v, chassis_f)
    acceptance = p["acceptance"]
    hardpoint_drift = 0.0  # hardpoints are authoritative inputs, not derived from/deformed with the shell
    report = {
        "example": "rc-car-sporty-envelope",
        "quality": args.quality,
        "architecture": "immutable hardpoints -> fair body-section loft + independent smooth chassis",
        "hardpoints": hardpoints,
        "hardpoint_drift_mm": hardpoint_drift,
        "body": {
            "mesh": body_metrics,
            "alignment": body_data["alignment"],
            "curves": {
                "left_plan": curve_metrics(body_data["plan_left"][:, :2], closed=False),
                "right_plan": curve_metrics(body_data["plan_right"][:, :2], closed=False),
                "roofline": curve_metrics(body_data["roofline"], closed=False),
            },
        },
        "chassis": {"mesh": chassis_metrics, "outline": curve_metrics(chassis_profile, closed=True)},
        "limitations": [
            "Reference envelope only; no suspension, motor, drivetrain, battery, steering, wheel-arch, or crash validation.",
            "Exact functional features must be generated after the aesthetic envelope using the functional design skill.",
        ],
    }
    report["acceptance"] = {
        "body_watertight": body_metrics["watertight_edge_incidence"] is bool(acceptance["watertight"]),
        "chassis_watertight": chassis_metrics["watertight_edge_incidence"] is bool(acceptance["watertight"]),
        "body_components": body_metrics["connected_components"] == int(acceptance["connected_components_each"]),
        "chassis_components": chassis_metrics["connected_components"] == int(acceptance["connected_components_each"]),
        "body_degenerate_faces": body_metrics["degenerate_face_count"] <= int(acceptance["maximum_degenerate_faces"]),
        "chassis_degenerate_faces": chassis_metrics["degenerate_face_count"] <= int(acceptance["maximum_degenerate_faces"]),
        "body_volume": body_metrics["absolute_volume"] >= float(acceptance["minimum_body_volume_mm3"]),
        "chassis_volume": chassis_metrics["absolute_volume"] >= float(acceptance["minimum_chassis_volume_mm3"]),
        "hardpoint_drift": hardpoint_drift <= float(acceptance["hardpoint_drift_mm_max"]),
    }
    report["success"] = all(report["acceptance"].values())
    write_json(args.output / "validation.json", report)
    print(f"Built rc-car-sporty-envelope -> {args.output} (success={report['success']})")
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
