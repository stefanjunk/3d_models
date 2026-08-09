#!/usr/bin/env python3
"""Parametric CadQuery base and lid for the cylindrical gift box."""
from __future__ import annotations
import argparse
from pathlib import Path
import cadquery as cq

def build_body(radius=40.0,height=90.0,wall=2.4,bottom=2.8):
    outer=cq.Workplane("XY").circle(radius).extrude(height)
    cavity=(cq.Workplane("XY").workplane(offset=bottom)
            .circle(radius-wall).extrude(height-bottom+1.0))
    return outer.cut(cavity)

def build_lid(radius=40.0,wall=2.4,clearance=0.35,top=2.6,skirt=9.0):
    lip_radius=radius+1.2
    disk=cq.Workplane("XY").circle(lip_radius).extrude(top)
    plug_outer=radius-clearance
    plug_inner=max(1.0,plug_outer-wall)
    ring=(cq.Workplane("XY").workplane(offset=-skirt)
          .circle(plug_outer).circle(plug_inner).extrude(skirt))
    knob=(cq.Workplane("XY").workplane(offset=top)
          .circle(8.0).extrude(5.0)
          .faces(">Z").workplane().circle(5.5).extrude(5.0))
    return disk.union(ring).union(knob)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--quality",choices=("draft","print"),default="draft")
    args=p.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    body=build_body(); lid=build_lid()
    tol,ang=((0.18,0.25) if args.quality=="draft" else (0.06,0.10))
    cq.exporters.export(body,str(args.output_dir/"gift-box-body.stl"),tolerance=tol,angularTolerance=ang)
    cq.exporters.export(lid,str(args.output_dir/"gift-box-lid.stl"),tolerance=tol,angularTolerance=ang)
    cq.exporters.export(body,str(args.output_dir/"gift-box-body.step"))
    cq.exporters.export(lid,str(args.output_dir/"gift-box-lid.step"))
if __name__=="__main__":
    main()
