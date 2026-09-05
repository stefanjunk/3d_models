#!/usr/bin/env python3
"""Select the intended Step1X shell and register it to millimetres without touching the raw GLB."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def facts(mesh: trimesh.Trimesh) -> dict[str, object]:
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume": float(mesh.volume),
        "bounds": np.asarray(mesh.bounds).tolist(),
        "extents": np.asarray(mesh.extents).tolist(),
        "centroid": np.asarray(mesh.centroid).tolist(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--target-longest-mm", type=float, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    source_path = args.input.resolve()
    target = float(args.target_longest_mm)
    if target <= 0 or not math.isfinite(target):
        raise SystemExit("--target-longest-mm must be finite and positive")

    loaded = trimesh.load(source_path, force="scene", process=False)
    if not isinstance(loaded, trimesh.Scene):
        raise SystemExit("input must load as a GLB scene")
    flattened = trimesh.util.concatenate(tuple(loaded.geometry.values()))
    components = sorted(
        flattened.split(only_watertight=False),
        key=lambda mesh: len(mesh.faces),
        reverse=True,
    )
    if not components:
        raise SystemExit("input contains no mesh component")
    selected = components[0].copy()
    if not selected.is_watertight or selected.volume <= 0:
        raise SystemExit("largest component is not a positive watertight solid")

    selected.apply_transform(
        trimesh.transformations.rotation_matrix(math.pi / 2.0, [1.0, 0.0, 0.0])
    )
    scale = target / float(selected.extents.max())
    selected.apply_scale(scale)
    selected.apply_translation([0.0, 0.0, -float(selected.bounds[0, 2])])

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected.export(output_path)
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "operation": "largest intended shell selection plus uniform metric registration",
        "input": {"path": str(source_path), "sha256": sha256(source_path), **facts(flattened)},
        "component_count": len(components),
        "components_by_face_count": [facts(component) for component in components],
        "selection_rule": "largest component by face count; smaller components are rejected floaters and remain only in the immutable raw GLB",
        "transform": {
            "orientation": "glTF +Y up rotated +90 degrees about X to slicer/CAD +Z up",
            "uniform_scale_factor_to_mm": scale,
            "target_longest_mm": target,
            "place_min_z_at_zero": True,
        },
        "output": {"path": str(output_path), "sha256": sha256(output_path), **facts(selected)},
        "release_status": "organic draft only; cavity, base, water path, wall and physical tests are not complete",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
