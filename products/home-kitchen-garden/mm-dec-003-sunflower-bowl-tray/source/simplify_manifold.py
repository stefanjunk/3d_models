#!/usr/bin/env python3
"""Create a physical-tolerance-bounded Manifold mesh simplification candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path

import manifold3d
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
        "positive_volume": bool(mesh.is_volume),
        "components": int(len(mesh.split(only_watertight=False))),
        "bounds_mm": np.asarray(mesh.bounds).tolist(),
        "extents_mm": np.asarray(mesh.extents).tolist(),
        "volume_mm3": float(mesh.volume),
        "area_mm2": float(mesh.area),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tolerance-mm", type=float, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    source_path = args.input.resolve()
    output_path = args.output.resolve()
    report_path = args.report.resolve()
    tolerance = float(args.tolerance_mm)
    if not 0.0 < tolerance <= 0.1:
        raise SystemExit("--tolerance-mm must be in (0, 0.1]")
    source = trimesh.load_mesh(source_path, process=True)
    if isinstance(source, trimesh.Scene):
        source = source.to_geometry()
    if not isinstance(source, trimesh.Trimesh) or not source.is_volume:
        raise RuntimeError("input must be one positive manifold volume")

    manifold_mesh = manifold3d.Mesh(
        vert_properties=np.asarray(source.vertices, dtype=np.float32),
        tri_verts=np.asarray(source.faces, dtype=np.uint32),
    )
    simplified = manifold3d.Manifold(manifold_mesh).simplify(tolerance).to_mesh()
    candidate = trimesh.Trimesh(
        vertices=np.asarray(simplified.vert_properties)[:, :3],
        faces=np.asarray(simplified.tri_verts),
        process=True,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    candidate.export(output_path)
    failures = []
    if not candidate.is_volume or len(candidate.split(only_watertight=False)) != 1:
        failures.append("simplified candidate is not one positive watertight component")
    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "operation": "Manifold::simplify physical-tolerance candidate",
        "tool": {"name": "manifold3d", "version": importlib.metadata.version("manifold3d")},
        "tolerance_mm": tolerance,
        "guarantee_claim": "Manifold documentation: all surfaces move by less than the supplied tolerance; independent bidirectional distance validation remains required.",
        "input": {"path": str(source_path), "sha256": sha256(source_path), "bytes": source_path.stat().st_size, **facts(source)},
        "output": {"path": str(output_path), "sha256": sha256(output_path), "bytes": output_path.stat().st_size, **facts(candidate)},
        "face_reduction_fraction": 1.0 - len(candidate.faces) / len(source.faces),
        "file_reduction_fraction": 1.0 - output_path.stat().st_size / source_path.stat().st_size,
        "failures": failures,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
