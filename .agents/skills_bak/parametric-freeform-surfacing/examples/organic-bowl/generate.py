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
    mesh_metrics,
    orient_faces_positive_volume,
    pchip_profile,
    smootherstep,
    write_ascii_stl,
    write_csv_points,
    write_json,
    write_obj,
)


def base_radius_profile(u: np.ndarray, p: dict) -> np.ndarray:
    knots = p["vertical_profile"]["u"]
    values = [
        float(p["base_radius_mm"]),
        0.62 * float(p["base_radius_mm"]) + 0.38 * float(p["belly_radius_mm"]),
        float(p["belly_radius_mm"]),
        float(p["shoulder_radius_mm"]),
        float(p["rim_radius_mm"]),
    ]
    return pchip_profile(u, knots, values)


def radial_field(theta: np.ndarray, u: float | np.ndarray, p: dict) -> np.ndarray:
    base = base_radius_profile(np.asarray(u), p)
    amplitude = float(p["lobe_amplitude_mm"]) * smootherstep(u, 0.05, 0.58)
    phase = np.deg2rad(float(p["twist_deg"])) * smootherstep(u, 0.08, 1.0)
    lobes = int(p["lobes"])
    primary = np.cos(lobes * theta + phase)
    secondary = float(p["secondary_harmonic_ratio"]) * np.cos(2 * lobes * theta - 0.55 * phase)
    return base + amplitude * (primary + secondary)


def make_svg(path: Path, rim: np.ndarray, profile: np.ndarray, height: float) -> None:
    rim_xy = rim[:, :2]
    max_r = float(np.linalg.norm(rim_xy, axis=1).max())
    rim_points = " ".join(f"{250 + 190*x/max_r:.2f},{220 - 190*y/max_r:.2f}" for x, y in rim_xy)
    r_max = float(profile[:, 0].max())
    side_points = " ".join(f"{570 + 170*r/r_max:.2f},{390 - 330*z/height:.2f}" for r, z in profile)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="440" viewBox="0 0 900 440">
<rect width="900" height="440" fill="white"/>
<text x="30" y="34" font-family="sans-serif" font-size="22">Organic bowl — top outline and side profile</text>
<polygon points="{rim_points}" fill="none" stroke="black" stroke-width="2"/>
<polyline points="{side_points}" fill="none" stroke="black" stroke-width="2"/>
<line x1="570" y1="390" x2="570" y2="60" stroke="#999" stroke-dasharray="6 6"/>
</svg>\n'''
    path.write_text(svg, encoding="utf-8")


def build(p: dict, quality: str) -> tuple[np.ndarray, np.ndarray, dict]:
    height = float(p["height_mm"])
    wall = float(p["wall_mm"])
    bottom = float(p["bottom_thickness_mm"])
    rings = int(p[f"rings_{quality}"])
    segments = int(p[f"segments_{quality}"])
    theta = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=False)
    outer_z = np.linspace(0.0, height, rings)
    inner_z = np.linspace(bottom, height, rings)

    vertices: list[list[float]] = []
    outer_indices = np.empty((rings, segments), dtype=np.int64)
    inner_indices = np.empty((rings, segments), dtype=np.int64)

    for i, z in enumerate(outer_z):
        u = z / height
        radius = radial_field(theta, u, p)
        for j in range(segments):
            outer_indices[i, j] = len(vertices)
            vertices.append([radius[j] * np.cos(theta[j]), radius[j] * np.sin(theta[j]), z])
    minimum_inner_radius = float("inf")
    for i, z in enumerate(inner_z):
        u = z / height
        radius = radial_field(theta, u, p) - wall
        minimum_inner_radius = min(minimum_inner_radius, float(radius.min()))
        if np.any(radius <= 0):
            raise ValueError("Wall/bottom parameters collapse the inner cavity")
        for j in range(segments):
            inner_indices[i, j] = len(vertices)
            vertices.append([radius[j] * np.cos(theta[j]), radius[j] * np.sin(theta[j]), z])

    outer_center = len(vertices)
    vertices.append([0.0, 0.0, 0.0])
    inner_center = len(vertices)
    vertices.append([0.0, 0.0, bottom])
    faces: list[tuple[int, int, int]] = []
    for i in range(rings - 1):
        for j in range(segments):
            jn = (j + 1) % segments
            a, b = int(outer_indices[i, j]), int(outer_indices[i, jn])
            c, d = int(outer_indices[i + 1, j]), int(outer_indices[i + 1, jn])
            faces.extend([(a, b, d), (a, d, c)])
            ia, ib = int(inner_indices[i, j]), int(inner_indices[i, jn])
            ic, id_ = int(inner_indices[i + 1, j]), int(inner_indices[i + 1, jn])
            faces.extend([(ia, id_, ib), (ia, ic, id_)])
    for j in range(segments):
        jn = (j + 1) % segments
        faces.append((outer_center, int(outer_indices[0, jn]), int(outer_indices[0, j])))
        faces.append((inner_center, int(inner_indices[0, j]), int(inner_indices[0, jn])))
        outer_a, outer_b = int(outer_indices[-1, j]), int(outer_indices[-1, jn])
        inner_a, inner_b = int(inner_indices[-1, j]), int(inner_indices[-1, jn])
        faces.extend([(outer_a, outer_b, inner_b), (outer_a, inner_b, inner_a)])

    v = np.asarray(vertices, dtype=float)
    f = orient_faces_positive_volume(v, np.asarray(faces, dtype=np.int64))
    metrics = mesh_metrics(v, f)
    profile_u = np.linspace(0.0, 1.0, 160)
    profile = np.column_stack([base_radius_profile(profile_u, p), profile_u * height])
    rim_radius = radial_field(theta, 1.0, p)
    rim = np.column_stack([rim_radius * np.cos(theta), rim_radius * np.sin(theta), np.full(segments, height)])
    report = {
        "example": "organic-bowl",
        "quality": quality,
        "architecture": "smooth vertical profile + periodic Fourier lobes/twist -> outer/inner shell",
        "mesh": metrics,
        "parameters_summary": {
            "height_mm": height,
            "wall_mm_nominal_radial": wall,
            "bottom_thickness_mm": bottom,
            "lobes": int(p["lobes"]),
            "twist_deg": float(p["twist_deg"]),
            "rings": rings,
            "segments": segments,
            "minimum_inner_radius_mm": minimum_inner_radius,
        },
        "curves": {
            "base_radius_profile": curve_metrics(profile, closed=False),
            "rim_outline": curve_metrics(rim[:, :2], closed=True),
        },
        "limitations": [
            "Wall is a nominal radial offset rather than an exact normal offset.",
            "Food-contact, watertightness, heat, and cleanability are not certified by this geometry example.",
        ],
    }
    acceptance = p["acceptance"]
    report["acceptance"] = {
        "watertight": metrics["watertight_edge_incidence"] is bool(acceptance["watertight"]),
        "connected_components": metrics["connected_components"] == int(acceptance["connected_components"]),
        "degenerate_faces": metrics["degenerate_face_count"] <= int(acceptance["maximum_degenerate_faces"]),
        "minimum_volume": metrics["absolute_volume"] >= float(acceptance["minimum_volume_mm3"]),
        "minimum_inner_radius": minimum_inner_radius >= float(acceptance["minimum_inner_radius_mm"]),
    }
    report["success"] = all(report["acceptance"].values())
    return v, f, {"report": report, "rim": rim, "profile": profile}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--quality", choices=("draft", "print"), default="draft")
    args = parser.parse_args()
    p = yaml.safe_load(args.parameters.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    vertices, faces, data = build(p, args.quality)
    write_obj(args.output / "organic-bowl.obj", vertices, faces, object_name="organic_bowl")
    write_ascii_stl(args.output / "organic-bowl.stl", vertices, faces, solid_name="organic_bowl")
    write_csv_points(args.output / "vertical-profile.csv", data["profile"])
    write_csv_points(args.output / "rim-outline.csv", data["rim"])
    make_svg(args.output / "preview.svg", data["rim"], data["profile"], float(p["height_mm"]))
    shutil.copy2(args.parameters, args.output / "parameters.yaml")
    write_json(args.output / "validation.json", data["report"])
    print(f"Built organic-bowl -> {args.output} (success={data['report']['success']})")
    return 0 if data["report"]["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
