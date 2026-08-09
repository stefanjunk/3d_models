#!/usr/bin/env python3
"""Coarse CadQuery-native pixel relief for logos and deliberately low-resolution art.

This is not appropriate for photographic or texture-height maps: each active
cell becomes a B-rep feature. Use the mesh-patch workflow for dense images.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
import cadquery as cq

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("image",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--width-mm",type=float,default=60)
    p.add_argument("--height-mm",type=float,default=30)
    p.add_argument("--base-mm",type=float,default=3)
    p.add_argument("--depth-mm",type=float,default=0.6)
    p.add_argument("--threshold",type=float,default=0.5)
    p.add_argument("--cells-x",type=int,default=48)
    p.add_argument("--mode",choices=("emboss","engrave"),default="engrave")
    args=p.parse_args()
    im=Image.open(args.image).convert("L").resize((args.cells_x,max(2,round(args.cells_x*args.height_mm/args.width_mm))))
    h=np.asarray(im,dtype=np.float32)/255.0
    ny,nx=h.shape; dx=args.width_mm/nx; dy=args.height_mm/ny
    base=cq.Workplane("XY").box(args.width_mm,args.height_mm,args.base_mm,centered=(True,True,False))
    active=np.argwhere(h>=args.threshold)
    for iy,ix in active:
        x=-args.width_mm/2+(ix+0.5)*dx
        y=args.height_mm/2-(iy+0.5)*dy
        cell=(cq.Workplane("XY").workplane(offset=args.base_mm if args.mode=="emboss" else args.base_mm-args.depth_mm)
              .center(x,y).box(dx*1.01,dy*1.01,args.depth_mm,centered=(True,True,False)))
        base=base.union(cell) if args.mode=="emboss" else base.cut(cell)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    cq.exporters.export(base,str(args.output))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
