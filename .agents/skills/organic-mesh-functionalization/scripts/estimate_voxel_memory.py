#!/usr/bin/env python3
"""Estimate dense voxel/SDF memory before allocating a volume."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import trimesh


def load_extents(path: Path) -> np.ndarray:
    obj = trimesh.load(path, force=None, process=True)
    if isinstance(obj, trimesh.Scene):
        meshes = [g for g in obj.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError("Scene contains no mesh")
        obj = trimesh.util.concatenate(meshes)
    return np.asarray(obj.extents, dtype=float)


def human_bytes(n: float) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024
        i += 1
    return f"{n:.2f} {units[i]}"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--mesh", type=Path)
    src.add_argument("--extents", type=float, nargs=3, metavar=("X", "Y", "Z"))
    p.add_argument("--voxel", type=float, required=True, help="Voxel size in the same units as the mesh")
    p.add_argument("--padding", type=int, default=6, help="Padding voxels added to each axis")
    p.add_argument("--dtype", choices=["bool", "uint8", "float16", "float32", "float64"], default="float32")
    p.add_argument("--buffers", type=float, default=5.0, help="Estimated simultaneous full-grid buffers")
    p.add_argument("--available-gib", type=float, help="Optional available RAM for warning threshold")
    p.add_argument("--json", dest="json_path", type=Path)
    return p


def main() -> int:
    args = parser().parse_args()
    if args.voxel <= 0:
        raise SystemExit("--voxel must be > 0")
    extents = load_extents(args.mesh) if args.mesh else np.asarray(args.extents, dtype=float)
    dims = np.ceil(extents / args.voxel).astype(np.int64) + 2 * args.padding
    voxels = int(np.prod(dims, dtype=np.int64))
    itemsize = np.dtype(args.dtype).itemsize
    one = voxels * itemsize
    projected = one * args.buffers

    chunk_axis = int(np.argmax(dims))
    chunk_slices_1gib = max(1, int((1024**3) / (itemsize * args.buffers * np.prod(np.delete(dims, chunk_axis)))))

    report = {
        "extents": extents.tolist(),
        "voxel_size": args.voxel,
        "dimensions": dims.tolist(),
        "voxels": voxels,
        "dtype": args.dtype,
        "itemsize_bytes": itemsize,
        "one_grid_bytes": one,
        "one_grid_human": human_bytes(one),
        "buffer_multiplier": args.buffers,
        "projected_peak_bytes": projected,
        "projected_peak_human": human_bytes(projected),
        "suggested_chunk_axis": ["X", "Y", "Z"][chunk_axis],
        "approx_slices_per_1gib_chunk": chunk_slices_1gib,
        "recommendation": "dense is plausible",
    }
    if args.available_gib:
        available = args.available_gib * 1024**3
        report["available_bytes"] = available
        report["fraction_of_available"] = projected / available
        if projected > 0.60 * available:
            report["recommendation"] = "change plan: crop ROI, use sparse/narrow-band volume, chunk, or increase voxel size"
    elif projected > 8 * 1024**3:
        report["recommendation"] = "high projected peak: prefer ROI/sparse/narrow-band processing"

    text = json.dumps(report, indent=2)
    print(text)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
