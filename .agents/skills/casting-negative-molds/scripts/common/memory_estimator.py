#!/usr/bin/env python3
"""Estimate voxel and height-map mesh sizes before expensive mold operations."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def human_bytes(value: float) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")
    v = float(value)
    for unit in units:
        if abs(v) < 1024.0 or unit == units[-1]:
            return f"{v:.3g} {unit}"
        v /= 1024.0
    return f"{v:.3g} PiB"


def voxel_estimate(dimensions: tuple[float, float, float], pitch: float, bytes_per_voxel: float, overhead: tuple[float, float]) -> dict[str, Any]:
    if any(v <= 0 for v in dimensions) or pitch <= 0 or bytes_per_voxel <= 0:
        raise ValueError("Voxel dimensions, pitch, and bytes per voxel must be positive.")
    grid = tuple(int(math.ceil(v / pitch)) for v in dimensions)
    count = math.prod(grid)
    raw = count * bytes_per_voxel
    return {
        "dimensions_mm": list(dimensions),
        "pitch_mm": pitch,
        "grid": list(grid),
        "voxel_count": count,
        "bytes_per_voxel": bytes_per_voxel,
        "raw_bytes": raw,
        "raw_human": human_bytes(raw),
        "working_memory_range_bytes": [raw * overhead[0], raw * overhead[1]],
        "working_memory_range_human": [human_bytes(raw * overhead[0]), human_bytes(raw * overhead[1])],
        "note": "Working range is a planning multiplier, not a guarantee; application data structures and temporary copies vary."
    }


def heightmap_estimate(width: int, height: int, bytes_per_vertex: float, bytes_per_triangle: float) -> dict[str, Any]:
    if width < 2 or height < 2:
        raise ValueError("Height-map dimensions must each be at least 2 pixels.")
    vertices = width * height
    triangles = 2 * (width - 1) * (height - 1)
    raw = vertices * bytes_per_vertex + triangles * bytes_per_triangle
    return {
        "pixels": [width, height],
        "vertices": vertices,
        "triangles": triangles,
        "planning_bytes_per_vertex": bytes_per_vertex,
        "planning_bytes_per_triangle": bytes_per_triangle,
        "raw_array_estimate_bytes": raw,
        "raw_array_estimate_human": human_bytes(raw),
        "note": "CAD/mesh application memory is normally much higher than compact raw numeric arrays."
    }


def sampled_heightmap(physical: tuple[float, float], pitch: float) -> tuple[int, int]:
    if any(v <= 0 for v in physical) or pitch <= 0:
        raise ValueError("Physical size and sample pitch must be positive.")
    return tuple(int(math.ceil(v / pitch)) + 1 for v in physical)  # include both edges


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--volume-mm", nargs=3, type=float, metavar=("X", "Y", "Z"), help="Bounding volume for dense voxel processing")
    parser.add_argument("--voxel-mm", type=float, help="Voxel pitch in millimetres")
    parser.add_argument("--bytes-per-voxel", type=float, default=4.0, help="Raw storage assumption, e.g. float32 = 4")
    parser.add_argument("--overhead-factors", nargs=2, type=float, default=(4.0, 12.0), metavar=("LOW", "HIGH"), help="Planning multipliers over raw voxel storage")
    parser.add_argument("--heightmap", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"), help="Height-map pixel dimensions")
    parser.add_argument("--physical-size-mm", nargs=2, type=float, metavar=("WIDTH", "HEIGHT"), help="Derive height-map samples from physical size")
    parser.add_argument("--sample-pitch-mm", type=float, help="Height-map sample pitch; used with --physical-size-mm")
    parser.add_argument("--bytes-per-vertex", type=float, default=32.0, help="Planning bytes per vertex in compact arrays")
    parser.add_argument("--bytes-per-triangle", type=float, default=24.0, help="Planning bytes per triangle in compact arrays")
    parser.add_argument("--json", dest="json_path", type=Path, help="Write JSON report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report: dict[str, Any] = {}
        if args.volume_mm or args.voxel_mm:
            if not (args.volume_mm and args.voxel_mm):
                raise ValueError("Use --volume-mm and --voxel-mm together.")
            low, high = args.overhead_factors
            if low <= 0 or high < low:
                raise ValueError("Overhead factors must be positive and HIGH >= LOW.")
            report["voxel"] = voxel_estimate(tuple(args.volume_mm), args.voxel_mm, args.bytes_per_voxel, (low, high))

        pixels: tuple[int, int] | None = tuple(args.heightmap) if args.heightmap else None
        if args.physical_size_mm or args.sample_pitch_mm:
            if not (args.physical_size_mm and args.sample_pitch_mm):
                raise ValueError("Use --physical-size-mm and --sample-pitch-mm together.")
            derived = sampled_heightmap(tuple(args.physical_size_mm), args.sample_pitch_mm)
            if pixels and pixels != derived:
                raise ValueError(f"Explicit height map {pixels} conflicts with derived dimensions {derived}.")
            pixels = derived
            report["heightmap_sampling"] = {
                "physical_size_mm": list(args.physical_size_mm),
                "sample_pitch_mm": args.sample_pitch_mm,
                "derived_pixels": list(derived)
            }

        if pixels:
            report["heightmap_mesh"] = heightmap_estimate(pixels[0], pixels[1], args.bytes_per_vertex, args.bytes_per_triangle)

        if not report:
            raise ValueError("Provide a voxel estimate, a height-map estimate, or both.")

        text = json.dumps(report, indent=2)
        print(text)
        if args.json_path:
            path = args.json_path.expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
