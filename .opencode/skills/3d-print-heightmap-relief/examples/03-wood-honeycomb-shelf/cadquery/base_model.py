#!/usr/bin/env python3
"""Parametric CadQuery honeycomb wall shelf."""
from __future__ import annotations
import argparse, math
from pathlib import Path
import cadquery as cq

def points(radius,sides=6,start_deg=30.0):
    return [(radius*math.cos(math.radians(start_deg+i*360/sides)),
             radius*math.sin(math.radians(start_deg+i*360/sides))) for i in range(sides)]

def prism(radius,depth,z0=0.0):
    pts=points(radius)
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(depth)

def build(outer_radius=60.0,inner_radius=51.0,depth=35.0):
    outer=prism(outer_radius,depth)
    inner=prism(inner_radius,depth+2.0,-1.0)
    return outer.cut(inner)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--quality",choices=("draft","print"),default="draft")
    args=p.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    model=build()
    tol,ang=((0.18,0.25) if args.quality=="draft" else (0.06,0.10))
    cq.exporters.export(model,str(args.output_dir/"honeycomb-shelf.stl"),tolerance=tol,angularTolerance=ang)
    cq.exporters.export(model,str(args.output_dir/"honeycomb-shelf.step"))
if __name__=="__main__":
    main()
