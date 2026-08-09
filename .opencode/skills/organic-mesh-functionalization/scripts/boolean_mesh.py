#!/usr/bin/env python3
"""Run a logged Boolean on valid closed meshes using Trimesh engines."""
from __future__ import annotations

import argparse
import importlib.util
import shutil
from pathlib import Path

from common import dump_json, load_mesh, mesh_metrics


def available_engines() -> list[str]:
    engines: list[str] = []
    if importlib.util.find_spec("manifold3d") is not None:
        engines.append("manifold")
    if shutil.which("blender"):
        engines.append("blender")
    return engines


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("operation", choices=["difference", "union", "intersection"])
    p.add_argument("target")
    p.add_argument("tools", nargs="+")
    p.add_argument("--engine", choices=["auto", "manifold", "blender"], default="auto")
    p.add_argument("--output", required=True)
    p.add_argument("--skip-volume-check", action="store_true")
    p.add_argument("--json-out")
    args = p.parse_args()

    import trimesh

    meshes = [load_mesh(args.target, process=True)] + [load_mesh(x, process=True) for x in args.tools]
    pre = [mesh_metrics(m) for m in meshes]
    invalid = [i for i, m in enumerate(meshes) if not (m.is_watertight and m.is_winding_consistent and abs(m.volume) > 0)]
    if invalid and not args.skip_volume_check:
        raise SystemExit(f"Operands {invalid} are not valid closed positive/negative volumes; repair or use --skip-volume-check only with review")

    engines = available_engines()
    engine = args.engine
    if engine == "auto":
        if not engines:
            raise SystemExit("No Boolean engine available. Install manifold3d or Blender.")
        engine = engines[0]
    if engine not in engines:
        raise SystemExit(f"Requested engine '{engine}' unavailable; available: {engines}")

    kwargs = {"engine": engine, "check_volume": not args.skip_volume_check}
    if args.operation == "difference":
        result = trimesh.boolean.difference(meshes, **kwargs)
    elif args.operation == "union":
        result = trimesh.boolean.union(meshes, **kwargs)
    else:
        result = trimesh.boolean.intersection(meshes, **kwargs)
    if result is None or not hasattr(result, "faces") or len(result.faces) == 0:
        raise SystemExit("Boolean returned no mesh")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.export(out)
    report = {
        "operation": args.operation,
        "engine": engine,
        "target": str(Path(args.target).resolve()),
        "tools": [str(Path(x).resolve()) for x in args.tools],
        "operands": pre,
        "result": mesh_metrics(result),
        "output": str(out.resolve()),
        "warning": "A valid Boolean result still requires intent, protected-surface, section, wall, and slicer validation.",
    }
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
