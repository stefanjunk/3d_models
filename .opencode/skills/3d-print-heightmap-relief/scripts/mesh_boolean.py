#!/usr/bin/env python3
"""Apply mesh Booleans with Manifold/Blender when available and OpenSCAD fallback."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable

import trimesh

from heightmap_common import write_json
from validate_mesh import load_mesh, report_for


def _quote_scad(path: Path) -> str:
    return '"' + str(path.resolve()).replace("\\", "/").replace('"', '\\"') + '"'


def openscad_boolean(
    base: Path,
    tools: list[Path],
    output: Path,
    operation: str,
    executable: str = "openscad",
) -> dict:
    exe = shutil.which(executable) or (executable if Path(executable).is_file() else None)
    if not exe:
        raise RuntimeError(f"OpenSCAD executable not found: {executable}")
    output.parent.mkdir(parents=True, exist_ok=True)
    imports = [f"import({_quote_scad(base)}, convexity=20);"] + [
        f"import({_quote_scad(path)}, convexity=20);" for path in tools
    ]
    if operation == "difference":
        tool_union = "\n".join(imports[1:])
        scad = (
            "$fn=96;\n"
            "render(convexity=20) difference() {\n"
            f"  {imports[0]}\n"
            "  union() {\n    " + tool_union.replace("\n", "\n    ") + "\n  }\n}\n"
        )
    elif operation == "union":
        scad = "$fn=96;\nrender(convexity=20) union() {\n  " + "\n  ".join(imports) + "\n}\n"
    elif operation == "intersection":
        scad = "$fn=96;\nrender(convexity=20) intersection() {\n  " + "\n  ".join(imports) + "\n}\n"
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    with tempfile.TemporaryDirectory(prefix="heightmap-boolean-") as td:
        scad_path = Path(td) / "boolean.scad"
        scad_path.write_text(scad, encoding="utf-8")
        command = [str(exe), "-o", str(output.resolve()), str(scad_path)]
        completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0 or not output.is_file():
        raise RuntimeError(
            "OpenSCAD Boolean failed\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return {
        "engine": "openscad",
        "command": command,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def trimesh_boolean(
    base: Path,
    tools: list[Path],
    output: Path,
    operation: str,
    engine: str,
) -> dict:
    meshes = [load_mesh(base)] + [load_mesh(path) for path in tools]
    function = {
        "difference": trimesh.boolean.difference,
        "union": trimesh.boolean.union,
        "intersection": trimesh.boolean.intersection,
    }[operation]
    result = function(meshes, engine=engine, check_volume=True)
    if result is None:
        raise RuntimeError(f"{engine} returned no mesh")
    if isinstance(result, trimesh.Scene):
        result = trimesh.util.concatenate(tuple(result.geometry.values()))
    output.parent.mkdir(parents=True, exist_ok=True)
    result.export(output)
    return {"engine": engine}


def run_boolean(
    base: Path,
    tools: list[Path],
    output: Path,
    operation: str,
    requested_engine: str,
    openscad_executable: str,
) -> dict:
    if not tools:
        raise ValueError("At least one tool mesh is required")
    attempts: list[dict] = []
    if requested_engine == "auto":
        candidates = ["manifold", "blender", "openscad"]
    else:
        candidates = [requested_engine]
    for engine in candidates:
        try:
            if engine == "openscad":
                detail = openscad_boolean(base, tools, output, operation, openscad_executable)
            else:
                detail = trimesh_boolean(base, tools, output, operation, engine)
            detail["attempts"] = attempts
            return detail
        except Exception as exc:
            attempts.append({"engine": engine, "error": str(exc)})
    raise RuntimeError("All Boolean engines failed:\n" + "\n".join(f"- {a['engine']}: {a['error']}" for a in attempts))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("operation", choices=("difference", "union", "intersection"))
    p.add_argument("base", type=Path)
    p.add_argument("tools", nargs="+", type=Path)
    p.add_argument("-o", "--output", required=True, type=Path)
    p.add_argument("--engine", choices=("auto", "manifold", "blender", "openscad"), default="auto")
    p.add_argument("--openscad", default=os.environ.get("OPENSCAD", "openscad"))
    p.add_argument("--report", type=Path)
    p.add_argument("--require-watertight", action="store_true")
    p.add_argument("--require-single-body", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    detail = run_boolean(args.base, args.tools, args.output, args.operation, args.engine, args.openscad)
    mesh = load_mesh(args.output)
    validation = report_for(mesh, str(args.output))
    failures = []
    if args.require_watertight and not validation["watertight"]:
        failures.append("output is not watertight")
    if args.require_single_body and validation["body_count"] != 1:
        failures.append(f"output has {validation['body_count']} bodies")
    report = {
        "operation": args.operation,
        "base": str(args.base),
        "tools": [str(p) for p in args.tools],
        "output": str(args.output),
        "engine_detail": detail,
        "validation": validation,
        "failures": failures,
    }
    if args.report:
        write_json(report, args.report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
