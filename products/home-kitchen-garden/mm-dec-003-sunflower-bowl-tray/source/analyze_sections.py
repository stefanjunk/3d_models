#!/usr/bin/env python3
"""Create deterministic vertical section evidence without modifying the mesh."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="mesh", process=True)
    if not isinstance(loaded, trimesh.Trimesh) or len(loaded.faces) == 0:
        raise ValueError("input does not contain a triangle mesh")
    return loaded


def svg_for_polylines(polylines: list[np.ndarray], horizontal_axis: int, output: Path) -> None:
    points_2d = [np.column_stack((line[:, horizontal_axis], line[:, 2])) for line in polylines]
    all_points = np.vstack(points_2d)
    lo = all_points.min(axis=0)
    hi = all_points.max(axis=0)
    span = np.maximum(hi - lo, 1e-9)
    width, height, pad = 1200.0, 500.0, 25.0

    def convert(points: np.ndarray) -> str:
        x = pad + (points[:, 0] - lo[0]) / span[0] * (width - 2 * pad)
        y = height - pad - (points[:, 1] - lo[1]) / span[1] * (height - 2 * pad)
        return " ".join(f"{px:.3f},{py:.3f}" for px, py in zip(x, y))

    paths = "\n".join(
        f'  <polyline points="{convert(points)}" fill="none" stroke="#214f78" stroke-width="2" />'
        for points in points_2d
    )
    text = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(width)}" height="{int(height)}" '
        f'viewBox="0 0 {int(width)} {int(height)}">\n'
        '  <rect width="100%" height="100%" fill="white"/>\n'
        f'{paths}\n'
        '</svg>\n'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def analyze_plane(mesh: trimesh.Trimesh, axis: str, svg_path: Path) -> dict:
    normal = np.array([1.0, 0.0, 0.0]) if axis == "x" else np.array([0.0, 1.0, 0.0])
    horizontal_axis = 1 if axis == "x" else 0
    section = mesh.section(plane_origin=[0.0, 0.0, 0.0], plane_normal=normal)
    if section is None:
        raise ValueError(f"no section at {axis}=0")
    polylines = [np.asarray(line, dtype=float) for line in section.discrete if len(line) >= 2]
    if not polylines:
        raise ValueError(f"empty section at {axis}=0")
    svg_for_polylines(polylines, horizontal_axis, svg_path)
    points = np.vstack(polylines)
    horizontal = points[:, horizontal_axis]
    z = points[:, 2]
    near_center = np.abs(horizontal) <= 2.0
    center_top = float(np.max(z[near_center])) if np.any(near_center) else None
    overall_top = float(np.max(z))
    closed = [bool(np.linalg.norm(line[0] - line[-1]) <= 1e-5) for line in polylines]
    return {
        "plane": f"{axis}=0",
        "polyline_count": len(polylines),
        "all_polylines_closed": all(closed),
        "horizontal_bounds_mm": [float(horizontal.min()), float(horizontal.max())],
        "z_bounds_mm": [float(z.min()), overall_top],
        "center_top_z_mm_within_2mm": center_top,
        "rim_minus_center_mm": None if center_top is None else overall_top - center_top,
        "open_depression_screen": bool(center_top is not None and overall_top - center_top >= 2.0),
        "svg": str(svg_path),
        "svg_sha256": sha256(svg_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--x-svg", type=Path, required=True)
    parser.add_argument("--y-svg", type=Path, required=True)
    parser.add_argument("--json", dest="json_path", type=Path, required=True)
    args = parser.parse_args()

    mesh = load_mesh(args.mesh)
    sections = [analyze_plane(mesh, "x", args.x_svg), analyze_plane(mesh, "y", args.y_svg)]
    failures = []
    if not all(item["all_polylines_closed"] for item in sections):
        failures.append("one or more vertical section polylines are open")
    if not all(item["open_depression_screen"] for item in sections):
        failures.append("central open-depression screen did not pass in both orthogonal sections")
    report = {
        "schema_version": "1.0",
        "status": "PASS" if not failures else "FAIL",
        "operation": "read-only orthogonal vertical-section screen",
        "input": {"path": str(args.mesh), "sha256": sha256(args.mesh)},
        "sections": sections,
        "failures": failures,
        "limitations": [
            "Two vertical planes do not prove the absence of every off-axis hidden pocket.",
            "The open-depression screen compares sampled section vertices within 2 mm of centre to the highest section point.",
            "Physical access and cleaning still require a prototype test."
        ]
    }
    args.json_path.parent.mkdir(parents=True, exist_ok=True)
    args.json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.json_path)
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
