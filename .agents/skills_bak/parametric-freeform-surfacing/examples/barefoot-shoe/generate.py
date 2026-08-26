#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import yaml

SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from surface_geometry import (  # noqa: E402
    curve_metrics,
    loft_closed_sections,
    mesh_metrics,
    pchip_profile,
    smootherstep,
    write_ascii_stl,
    write_csv_points,
    write_json,
    write_obj,
)


def make_svg(path: Path, left: np.ndarray, right: np.ndarray, length: float) -> None:
    all_points = np.vstack([left[:, :2], right[:, :2]])
    min_xy = all_points.min(axis=0)
    max_xy = all_points.max(axis=0)
    scale = min(900.0 / max(max_xy[0] - min_xy[0], 1.0), 360.0 / max(max_xy[1] - min_xy[1], 1.0))

    def map_points(points: np.ndarray) -> str:
        mapped = []
        for x, y in points[:, :2]:
            px = 50 + (x - min_xy[0]) * scale
            py = 210 - (y - (min_xy[1] + max_xy[1]) / 2.0) * scale
            mapped.append(f"{px:.2f},{py:.2f}")
        return " ".join(mapped)

    outline = np.vstack([left, right[::-1], left[:1]])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420">
<rect width="1000" height="420" fill="white"/>
<text x="40" y="35" font-family="sans-serif" font-size="22">Barefoot shoe plan silhouette — {length:.0f} mm</text>
<polyline points="{map_points(outline)}" fill="none" stroke="black" stroke-width="2"/>
<line x1="50" y1="210" x2="950" y2="210" stroke="#999" stroke-dasharray="6 6"/>
</svg>\n'''
    path.write_text(svg, encoding="utf-8")


def build(parameters: dict, quality: str) -> tuple[np.ndarray, np.ndarray, dict]:
    length = float(parameters["length_mm"])
    base_stations = np.asarray(parameters["station_s"], dtype=float)
    if quality == "print":
        stations = np.unique(np.r_[base_stations, (base_stations[:-1] + base_stations[1:]) / 2.0])
    else:
        stations = base_stations
    section_points = int(parameters[f"section_points_{quality}"])
    half = max(12, section_points // 2)

    width = parameters["width_profile"]
    width_s = width["s"]
    medial_values = width["medial_half_mm"]
    lateral_values = width["lateral_half_mm"]
    thickness_profile = parameters["sole_thickness_profile"]
    sections: list[np.ndarray] = []
    centerline: list[list[float]] = []
    left: list[list[float]] = []
    right: list[list[float]] = []

    for s in stations:
        x = length * s
        center_y = float(parameters["centerline_shift_mm"]) * np.sin(np.pi * s) * (0.25 + 0.75 * s)
        medial = float(pchip_profile(s, width_s, medial_values))
        lateral = float(pchip_profile(s, width_s, lateral_values))
        thickness = float(pchip_profile(s, thickness_profile["s"], thickness_profile["mm"]))
        heel = float(parameters["heel_rise_mm"]) * (1.0 - float(smootherstep(s, 0.0, 0.24)))
        toe = float(parameters["toe_spring_mm"]) * float(smootherstep(s, 0.64, 1.0))
        bottom_center = heel + toe

        u_top = np.linspace(-1.0, 1.0, half)
        y_top = center_y + np.where(u_top >= 0.0, u_top * medial, u_top * lateral)
        cross = float(parameters["cross_camber_mm"]) * (1.0 - u_top**2)
        arch = (
            float(parameters["arch_height_mm"])
            * np.exp(-0.5 * ((s - float(parameters["arch_center_s"])) / float(parameters["arch_length_sigma"])) ** 2)
            * np.exp(-0.5 * ((u_top - float(parameters["arch_medial_u"])) / float(parameters["arch_width_sigma"])) ** 2)
        )
        z_top = bottom_center + thickness + cross + arch

        u_bottom = np.linspace(1.0, -1.0, half)[1:-1]
        y_bottom = center_y + np.where(u_bottom >= 0.0, u_bottom * medial, u_bottom * lateral)
        z_bottom = bottom_center - float(parameters["bottom_camber_mm"]) * (1.0 - u_bottom**2)

        section = np.vstack([
            np.column_stack([np.full_like(u_top, x), y_top, z_top]),
            np.column_stack([np.full_like(u_bottom, x), y_bottom, z_bottom]),
        ])
        sections.append(section)
        centerline.append([x, center_y, bottom_center])
        left.append([x, center_y + medial, bottom_center + thickness])
        right.append([x, center_y - lateral, bottom_center + thickness])

    vertices, faces, alignment = loft_closed_sections(sections, point_count=section_points)
    centerline_array = np.asarray(centerline)
    left_array = np.asarray(left)
    right_array = np.asarray(right)
    metrics = mesh_metrics(vertices, faces)
    report = {
        "example": "barefoot-shoe",
        "quality": quality,
        "architecture": "semantic width/height profiles -> registered closed sections -> lofted solid envelope",
        "station_count": int(len(stations)),
        "section_points": int(section_points),
        "alignment": alignment,
        "curves": {
            "centerline": curve_metrics(centerline_array, closed=False),
            "medial_silhouette": curve_metrics(left_array[:, :2], closed=False),
            "lateral_silhouette": curve_metrics(right_array[:, :2], closed=False),
        },
        "mesh": metrics,
        "dimensions": {
            "length_mm": float(vertices[:, 0].max() - vertices[:, 0].min()),
            "width_mm": float(vertices[:, 1].max() - vertices[:, 1].min()),
            "height_mm": float(vertices[:, 2].max() - vertices[:, 2].min()),
        },
        "limitations": [
            "Reference geometry only; not a medical or production footwear fit model.",
            "Nominal shell does not include textile attachment, outsole traction, flex cuts, or material-specific compensation.",
        ],
    }
    report["acceptance"] = {
        "watertight": metrics["watertight_edge_incidence"] is bool(parameters["acceptance"]["watertight"]),
        "connected_components": metrics["connected_components"] == int(parameters["acceptance"]["connected_components"]),
        "degenerate_faces": metrics["degenerate_face_count"] <= int(parameters["acceptance"]["maximum_degenerate_faces"]),
        "minimum_volume": metrics["absolute_volume"] >= float(parameters["acceptance"]["minimum_volume_mm3"]),
    }
    report["success"] = all(report["acceptance"].values())
    return vertices, faces, {"report": report, "centerline": centerline_array, "left": left_array, "right": right_array}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quality", choices=("draft", "print"), default="draft")
    args = parser.parse_args()
    parameters = yaml.safe_load(args.parameters.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    vertices, faces, data = build(parameters, args.quality)
    write_obj(args.output / "barefoot-shoe-envelope.obj", vertices, faces, object_name="barefoot_shoe_envelope")
    write_ascii_stl(args.output / "barefoot-shoe-envelope.stl", vertices, faces, solid_name="barefoot_shoe_envelope")
    write_csv_points(args.output / "centerline.csv", data["centerline"])
    write_csv_points(args.output / "medial-silhouette.csv", data["left"])
    write_csv_points(args.output / "lateral-silhouette.csv", data["right"])
    make_svg(args.output / "preview-plan.svg", data["left"], data["right"], float(parameters["length_mm"]))
    shutil.copy2(args.parameters, args.output / "parameters.yaml")
    write_json(args.output / "validation.json", data["report"])
    print(f"Built barefoot-shoe -> {args.output} (success={data['report']['success']})")
    return 0 if data["report"]["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
