#!/usr/bin/env python3
"""Generate and mesh-check the six CAD-owned cable-channel cutters."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from cadquery import exporters


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def top_intervals(mesh: trimesh.Trimesh, points: np.ndarray) -> list[tuple[float, float]]:
    count = len(points)
    origins = np.column_stack([points, np.full(count, 100.0)])
    directions = np.tile([0.0, 0.0, -1.0], (count, 1))
    locations, ray_ids, _ = mesh.ray.intersects_location(
        origins, directions, multiple_hits=True
    )
    grouped: list[list[float]] = [[] for _ in range(count)]
    for location, ray_id in zip(locations, ray_ids):
        grouped[int(ray_id)].append(float(location[2]))
    intervals: list[tuple[float, float]] = []
    for values in grouped:
        values.sort(reverse=True)
        if len(values) < 2:
            raise RuntimeError("channel site leaves the mesh at a validation sample")
        intervals.append((values[1], values[0]))
    return intervals


def cutter_for(
    channel: dict[str, object],
    mesh: trimesh.Trimesh,
    floor_mm: float,
    lip_mm: float,
    pinch_mm: float,
    axis_samples: int,
    lateral_fractions: list[float],
) -> tuple[cq.Shape, dict[str, object]]:
    angle = math.radians(float(channel["angle_deg"]))
    radial = np.array([math.cos(angle), math.sin(angle)])
    tangent = np.array([-math.sin(angle), math.cos(angle)])
    axis = radial if channel["axis"] == "radial" else tangent
    side = np.array([-axis[1], axis[0]])
    center = float(channel["radius_mm"]) * radial
    length = float(channel["length_mm"])
    bore = float(channel["bore_diameter_mm"])
    radius = bore / 2.0
    points = np.array(
        [
            center + along * axis + fraction * bore * side
            for along in np.linspace(-length / 2.0, length / 2.0, axis_samples)
            for fraction in lateral_fractions
        ]
    )
    intervals = top_intervals(mesh, points)
    bottom_max = max(item[0] for item in intervals)
    top_min = min(item[1] for item in intervals)
    z_bore = bottom_max + floor_mm + radius
    measured_floor = z_bore - radius - bottom_max
    measured_lip = top_min - (z_bore + radius)
    if measured_floor < floor_mm - 1e-6 or measured_lip < lip_mm - 1e-6:
        raise RuntimeError(
            f"{channel['id']} lacks wall reserve: floor={measured_floor:.3f}, "
            f"top_lip={measured_lip:.3f}"
        )

    epsilon = 0.6
    direction = cq.Vector(float(axis[0]), float(axis[1]), 0.0)
    start = center - axis * (length + epsilon) / 2.0
    cylinder = cq.Solid.makeCylinder(
        radius,
        length + epsilon,
        cq.Vector(float(start[0]), float(start[1]), z_bore),
        direction,
    )
    mouth_width = bore - pinch_mm
    mouth_height = float(mesh.bounds[1, 2]) - z_bore + 5.0
    plane = cq.Plane(
        origin=(float(center[0]), float(center[1]), z_bore),
        xDir=(float(axis[0]), float(axis[1]), 0.0),
        normal=(0.0, 0.0, 1.0),
    )
    mouth = cq.Workplane(plane).box(
        length + epsilon, mouth_width, mouth_height, centered=(True, True, False)
    ).val()
    combined = cylinder.fuse(mouth)
    return combined, {
        **channel,
        "center_xy_mm": [float(center[0]), float(center[1])],
        "axis_xy": [float(axis[0]), float(axis[1])],
        "z_bore_mm": z_bore,
        "sampled_bottom_max_mm": bottom_max,
        "sampled_top_min_mm": top_min,
        "verified_floor_mm": measured_floor,
        "verified_top_lip_mm": measured_lip,
        "mouth_width_mm": mouth_width,
        "boolean_epsilon_mm": epsilon,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parameters", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    source = (args.parameters.parent.parent / parameters["source_mesh"]).resolve()
    mesh = trimesh.load_mesh(source, process=True)
    if not isinstance(mesh, trimesh.Trimesh) or not mesh.is_watertight:
        raise RuntimeError("registered flat-base source must be a watertight mesh")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    shapes: list[cq.Shape] = []
    records: list[dict[str, object]] = []
    for channel in parameters["channels"]:
        shape, record = cutter_for(
            channel,
            mesh,
            float(parameters["minimum_floor_mm"]),
            float(parameters["minimum_top_lip_mm"]),
            float(parameters["pinch_under_bore_mm"]),
            int(parameters["site_sampling"]["axis_samples"]),
            [float(v) for v in parameters["site_sampling"]["lateral_offsets_as_bore_fraction"]],
        )
        shapes.append(shape)
        records.append(record)

    compound = cq.Compound.makeCompound(shapes)
    step_path = output_dir / "cable-channels-run005.step"
    stl_path = output_dir / "cable-channels-run005.stl"
    exporters.export(compound, str(step_path))
    exporters.export(
        compound, str(stl_path), tolerance=0.05, angularTolerance=0.1
    )
    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "cad_authority": str(args.parameters),
        "source_mesh": {"path": str(source), "sha256": sha256(source)},
        "cadquery_version": cq.__version__,
        "outputs": {
            "step": {"path": str(step_path), "sha256": sha256(step_path)},
            "stl": {"path": str(stl_path), "sha256": sha256(stl_path)},
        },
        "channels": records,
        "status": "geometry-check-pass-physical-qualification-not-run",
    }
    report_path = output_dir / "cable-channels-run005-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
