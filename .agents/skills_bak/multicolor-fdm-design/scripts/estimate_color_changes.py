#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from common import load_yaml, resolve_manifest_path, save_json


def load_part_bodies(manifest_path: Path) -> tuple[list[dict[str, Any]], dict[str, list[tuple[float, float]]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parts = manifest.get("parts", [])
    ranges: dict[str, list[tuple[float, float]]] = {}
    for part in parts:
        part_id = str(part["id"])
        mesh_path = resolve_manifest_path(manifest_path.resolve(), str(part["path"]))
        loaded = trimesh.load(mesh_path, force="scene", process=False)
        scene = loaded if isinstance(loaded, trimesh.Scene) else trimesh.Scene(loaded)
        meshes = [g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)]
        combined = trimesh.util.concatenate(meshes)
        bodies = combined.split(only_watertight=False)
        ranges[part_id] = [(float(body.bounds[0, 2]), float(body.bounds[1, 2])) for body in bodies]
    return parts, ranges


def load_purge_matrix(path: Path | None) -> tuple[dict[str, dict[str, float]], list[str]]:
    if path is None:
        return {}, []
    data = load_yaml(path)
    values = data.get("values", {})
    ids = list(data.get("filament_ids", []))
    matrix = {
        str(src): {str(dst): float(volume) for dst, volume in row.items()}
        for src, row in values.items()
    }
    return matrix, ids


def transition_cost(matrix: dict[str, dict[str, float]], src: str | None, dst: str) -> float:
    if src is None or src == dst:
        return 0.0
    return float(matrix.get(src, {}).get(dst, 0.0))


def greedy_order(active: list[str], previous: str | None, matrix: dict[str, dict[str, float]]) -> list[str]:
    remaining = set(active)
    order: list[str] = []
    current = previous
    while remaining:
        if current in remaining:
            chosen = current
        else:
            chosen = min(remaining, key=lambda candidate: (transition_cost(matrix, current, candidate), candidate))
        order.append(chosen)
        remaining.remove(chosen)
        current = chosen
    return order


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate active colors, transitions and directed purge from aligned part Z occupancy.")
    parser.add_argument("--parts-manifest", required=True, type=Path)
    parser.add_argument("--layer-height", required=True, type=float)
    parser.add_argument("--purge-matrix", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    if args.layer_height <= 0:
        raise SystemExit("Layer height must be positive")

    parts, ranges = load_part_bodies(args.parts_manifest)
    matrix, matrix_ids = load_purge_matrix(args.purge_matrix)
    color_ids = sorted(ranges)
    matrix_missing_ids = sorted(set(color_ids) - set(matrix_ids)) if args.purge_matrix else []
    matrix_complete = bool(args.purge_matrix) and not matrix_missing_ids
    all_ranges = [interval for intervals in ranges.values() for interval in intervals]
    z_min = min(interval[0] for interval in all_ranges)
    z_max = max(interval[1] for interval in all_ranges)
    layer_count = max(1, int(math.ceil((z_max - z_min) / args.layer_height)))

    previous: str | None = None
    transitions: list[dict[str, Any]] = []
    active_counts: list[int] = []
    layer_records: list[dict[str, Any]] = []
    purge_total = 0.0
    color_active_layers = {part["id"]: 0 for part in parts}
    for layer in range(layer_count):
        z = z_min + (layer + 0.5) * args.layer_height
        active = sorted(
            color
            for color, intervals in ranges.items()
            if any(low - 1e-9 <= z <= high + 1e-9 for low, high in intervals)
        )
        for color in active:
            color_active_layers[color] += 1
        order = greedy_order(active, previous, matrix)
        layer_transitions = []
        current = previous
        for color in order:
            if current is not None and color != current:
                volume = transition_cost(matrix, current, color)
                item = {"layer": layer, "z_mm": z, "from": current, "to": color, "purge_mm3": volume}
                transitions.append(item)
                layer_transitions.append(item)
                purge_total += volume
            current = color
        if order:
            previous = order[-1]
        active_counts.append(len(active))
        if len(active) > 1 or layer_transitions:
            layer_records.append({"layer": layer, "z_mm": z, "active": active, "estimated_order": order, "transitions": layer_transitions})

    histogram = {str(count): int(active_counts.count(count)) for count in sorted(set(active_counts))}
    report = {
        "manifest": str(args.parts_manifest.resolve()),
        "layer_height_mm": args.layer_height,
        "z_range_mm": [z_min, z_max],
        "layer_count": layer_count,
        "color_active_layers": color_active_layers,
        "active_color_count_histogram": histogram,
        "layers_with_multiple_colors": int(sum(count > 1 for count in active_counts)),
        "estimated_transition_count": len(transitions),
        "estimated_directed_purge_mm3": purge_total if matrix_complete else None,
        "purge_matrix": str(args.purge_matrix.resolve()) if args.purge_matrix else None,
        "purge_matrix_ids": matrix_ids,
        "purge_matrix_missing_ids": matrix_missing_ids,
        "method_note": "Greedy estimate from connected-body Z ranges; final slicer path order can differ.",
        "complex_layers": sorted(layer_records, key=lambda item: (-len(item["active"]), item["layer"]))[:200],
        "transitions": transitions[:5000],
    }
    if args.json_out:
        save_json(args.json_out, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
