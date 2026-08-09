#!/usr/bin/env python3
"""CadQuery base + external watertight relief patch + robust mesh Boolean."""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
import cadquery as cq

def build_base() -> cq.Workplane:
    # Replace this with the parametric B-rep model. Keep image sampling out of
    # the feature tree unless the relief is intentionally very coarse.
    outer=(cq.Workplane("XY").box(80,55,45,centered=(True,True,False))
           .edges("|Z").fillet(6))
    cavity=(cq.Workplane("XY").workplane(offset=3)
            .box(75,50,43,centered=(True,True,False))
            .edges("|Z").fillet(3.5))
    return outer.cut(cavity)

def run(command:list[str])->None:
    completed=subprocess.run(command,text=True,capture_output=True)
    if completed.returncode:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("relief_config",type=Path)
    p.add_argument("--output-dir",type=Path,default=Path("build"))
    p.add_argument("--operation",choices=("difference","union"),default="difference")
    p.add_argument("--engine",choices=("auto","manifold","blender","openscad"),default="auto")
    p.add_argument("--linear-tolerance",type=float,default=0.08)
    p.add_argument("--angular-tolerance",type=float,default=0.12)
    args=p.parse_args()
    out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    scripts=Path(__file__).resolve().parents[2]/"scripts"

    base=build_base()
    base_stl=out/"base.stl"
    cq.exporters.export(
        base,str(base_stl),
        tolerance=args.linear_tolerance,
        angularTolerance=args.angular_tolerance,
    )
    cq.exporters.export(base,str(out/"base.step"))

    patch=out/"relief-patch.stl"
    run([sys.executable,str(scripts/"relief_patch.py"),str(args.relief_config),str(patch),
         "--report",str(out/"relief-patch.report.json")])
    final=out/"base-with-relief.stl"
    op="difference" if args.operation=="difference" else "union"
    run([sys.executable,str(scripts/"mesh_boolean.py"),op,str(base_stl),str(patch),
         "-o",str(final),"--engine",args.engine,"--require-watertight",
         "--require-single-body","--report",str(out/"boolean.report.json")])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
