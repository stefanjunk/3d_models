#!/usr/bin/env python3
"""Create immutable triangle-budget candidates for slicer/quality comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import trimesh


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load_mesh(source, process=True)
    if not isinstance(mesh, trimesh.Trimesh) or not mesh.is_watertight:
        raise RuntimeError("source must be one watertight mesh")

    outputs = []
    for face_count in (200000, 100000):
        path = output_dir / f"octopus-{face_count // 1000}k.stl"
        command = [
            "blender",
            "--background",
            "--python",
            str(Path(__file__).with_name("blender_decimate.py")),
            "--",
            str(source),
            str(path),
            str(face_count),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not path.is_file():
            raise RuntimeError(
                f"Blender decimation failed for {face_count} faces: "
                f"{completed.stdout}\n{completed.stderr}"
            )
        candidate = trimesh.load_mesh(path, process=True)
        if not isinstance(candidate, trimesh.Trimesh):
            raise RuntimeError(f"Blender did not export one mesh: {path}")
        outputs.append(
            {
                "path": str(path),
                "sha256": sha256(path),
                "faces": int(len(candidate.faces)),
                "watertight": bool(candidate.is_watertight),
                "winding_consistent": bool(candidate.is_winding_consistent),
                "volume_mm3": float(candidate.volume),
                "extents_mm": candidate.extents.tolist(),
            }
        )
    report = {
        "schema_version": "1.0",
        "source": {
            "path": str(source),
            "sha256": sha256(source),
            "faces": int(len(mesh.faces)),
        },
        "method": "Blender 5.2 collapse decimation; independently reloaded with Trimesh",
        "outputs": outputs,
        "selection_rule": "accept only after surface regression, mesh audit and exact-profile slicer comparison",
    }
    report_path = output_dir / "mesh-variants.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
