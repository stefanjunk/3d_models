#!/usr/bin/env python3
"""Reapply CAD-owned base and channel cutters to the licence-qualified mesh."""

from __future__ import annotations

import argparse
import hashlib
import json
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
        "components": int(len(mesh.split(only_watertight=False))),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "bounds_mm": np.asarray(mesh.bounds).tolist(),
        "extents_mm": np.asarray(mesh.extents).tolist(),
        "volume_mm3": float(mesh.volume),
    }


def load_single(path: Path, role: str) -> trimesh.Trimesh:
    # STL repeats vertices per triangle; merge equivalent vertices before topology tests.
    loaded = trimesh.load_mesh(path, process=True)
    if isinstance(loaded, trimesh.Scene):
        loaded = loaded.to_geometry()
    if not isinstance(loaded, trimesh.Trimesh):
        raise RuntimeError(f"{role} is not a triangle mesh: {path}")
    if role == "source" and (
        not loaded.is_watertight or len(loaded.split(only_watertight=False)) != 1
    ):
        raise RuntimeError("source must be one watertight component")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("channels", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--base-cut-mm", type=float, default=4.0)
    parser.add_argument("--candidate-id", default="channels-parametric")
    args = parser.parse_args()

    source = load_single(args.source.resolve(), "source")
    channels = load_single(args.channels.resolve(), "channels")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cut_z = float(args.base_cut_mm)
    lower = float(source.bounds[0, 2]) - 20.0
    cutter_height = cut_z - lower
    base_cutter = trimesh.creation.box(
        extents=[400.0, 400.0, cutter_height],
        transform=trimesh.transformations.translation_matrix(
            [0.0, 0.0, lower + cutter_height / 2.0]
        ),
    )
    flat = trimesh.boolean.difference([source, base_cutter], engine="manifold")
    if not isinstance(flat, trimesh.Trimesh):
        raise RuntimeError("base Boolean did not return one mesh")
    flat.apply_translation([0.0, 0.0, -float(flat.bounds[0, 2])])
    flat_path = output_dir / "02-flat-base.stl"
    flat.export(flat_path)

    final = trimesh.boolean.difference([flat, channels], engine="manifold")
    if not isinstance(final, trimesh.Trimesh):
        raise RuntimeError("channel Boolean did not return one mesh")
    final_path = output_dir / f"03-{args.candidate_id}.stl"
    final.export(final_path)

    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "design-candidate",
        "authority": {
            "organic_surface": str(args.source),
            "flat_base": "parametric half-space cut at registered z=4.0 mm",
            "channels": str(args.channels),
            "channel_note": (
                "CAD-owned parametric cutter; acceptance still requires visual, wall, "
                "slicer and physical checks on the regenerated mesh."
            ),
        },
        "inputs": {
            "source": {"path": str(args.source), "sha256": sha256(args.source)},
            "channels": {"path": str(args.channels), "sha256": sha256(args.channels)},
        },
        "base_cut_mm": cut_z,
        "source_facts": facts(source),
        "flat_base": {"path": str(flat_path), "sha256": sha256(flat_path), **facts(flat)},
        "channel_candidate": {
            "path": str(final_path),
            "sha256": sha256(final_path),
            **facts(final),
        },
        "release_blockers": [
            "channel placement on the regenerated organic surface is not physically qualified",
            "real cable diameters and jacket hardness remain unmeasured",
            "retention, cycle and stability tests are NOT_RUN",
        ],
    }
    report_path = output_dir / f"functionalization-{args.candidate_id}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
