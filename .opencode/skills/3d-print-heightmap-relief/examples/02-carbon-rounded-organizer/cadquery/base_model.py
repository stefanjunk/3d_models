#!/usr/bin/env python3
"""Parametric CadQuery base for a rounded rectangular desk organizer."""
from __future__ import annotations
import argparse
from pathlib import Path
import cadquery as cq

def rounded_box(width,depth,height,radius,z0=0.0):
    box=(cq.Workplane("XY").workplane(offset=z0)
         .box(width,depth,height,centered=(True,True,False)))
    if radius>0:
        box=box.edges("|Z").fillet(radius)
    return box

def build(width=90.0,depth=65.0,height=95.0,radius=8.0,wall=2.4,bottom=3.0):
    outer=rounded_box(width,depth,height,radius)
    inner=rounded_box(width-2*wall,depth-2*wall,height-bottom+1.0,max(0.8,radius-wall),bottom)
    shell=outer.cut(inner)
    divider=(cq.Workplane("XY").workplane(offset=bottom)
             .box(wall,depth-2*wall-1.0,48.0,centered=(True,True,False)))
    return shell.union(divider)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--quality",choices=("draft","print"),default="draft")
    args=p.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    model=build()
    tol,ang=((0.18,0.25) if args.quality=="draft" else (0.06,0.10))
    cq.exporters.export(model,str(args.output_dir/"desk-organizer.stl"),tolerance=tol,angularTolerance=ang)
    cq.exporters.export(model,str(args.output_dir/"desk-organizer.step"))
if __name__=="__main__":
    main()
