#!/usr/bin/env python3
"""Run a simple clean-mesh Boolean through the OpenSCAD CLI and validate the export."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import dump_json, load_mesh, mesh_metrics


def scad_import(path: str | Path, convexity: int) -> str:
    # JSON string syntax is compatible with OpenSCAD string literals for paths.
    return f"import({json.dumps(str(Path(path).resolve()))}, convexity={convexity});"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("operation", choices=["difference", "union", "intersection"])
    p.add_argument("target")
    p.add_argument("tools", nargs="+")
    p.add_argument("--output", required=True)
    p.add_argument("--convexity", type=int, default=30)
    p.add_argument("--json-out")
    args = p.parse_args()

    exe = shutil.which("openscad")
    if not exe:
        raise SystemExit("OpenSCAD CLI not found")
    target = scad_import(args.target, args.convexity)
    tools = "\n".join(scad_import(x, args.convexity) for x in args.tools)
    if args.operation == "difference":
        body = f"difference() {{\n{target}\nunion() {{\n{tools}\n}}\n}}"
    elif args.operation == "union":
        body = f"union() {{\n{target}\n{tools}\n}}"
    else:
        body = f"intersection() {{\n{target}\nunion() {{\n{tools}\n}}\n}}"
    source = f"render(convexity={args.convexity}) {{\n{body}\n}}\n"
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="organic-mesh-openscad-") as td:
        scad = Path(td) / "job.scad"
        scad.write_text(source, encoding="utf-8")
        proc = subprocess.run([exe, "-o", str(out), str(scad)], capture_output=True, text=True)
    if proc.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        raise SystemExit(f"OpenSCAD Boolean failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    result = load_mesh(out, process=True)
    report = {
        "operation": args.operation,
        "engine": "openscad-cgal",
        "output": str(out),
        "result": mesh_metrics(result),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "warning": "Use only for already-clean manifold inputs and still run protected-surface and intent validation.",
    }
    print(dump_json(report, args.json_out))
    return 0 if result.is_watertight and len(result.faces) else 1


if __name__ == "__main__":
    raise SystemExit(main())
