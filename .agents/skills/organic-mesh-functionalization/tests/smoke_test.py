#!/usr/bin/env python3
"""Portable smoke test for the non-Blender/non-FreeCAD parts of the skill."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="organic-mesh-skill-") as td:
        tmp = Path(td)
        mesh = trimesh.creation.icosphere(subdivisions=2, radius=10)
        source = tmp / "source.stl"
        result = tmp / "result.stl"
        mesh.export(source)
        mesh.export(result)
        run("scripts/inspect_mesh.py", str(source), "--require-watertight", "--max-components", "1")
        run("scripts/estimate_voxel_memory.py", "--mesh", str(source), "--voxel", "0.5", "--buffers", "4")
        run("scripts/validate_edit.py", str(source), str(result), "--samples", "500", "--max-outside-p95", "0.001")

        try:
            import cadquery  # noqa: F401
        except Exception:
            print("CadQuery not installed; core mesh tests passed")
            return 0
        cfg = tmp / "parts.json"
        cfg.write_text(json.dumps({
            "output_dir": str(tmp / "parts"),
            "parts": [{"name": "test-cylinder", "type": "cylinder", "radius": 3, "height": 8}],
        }))
        run("scripts/cadquery_primitives.py", str(cfg))
        run("scripts/inspect_mesh.py", str(tmp / "parts/test-cylinder.stl"), "--require-watertight", "--max-components", "1")
        print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
