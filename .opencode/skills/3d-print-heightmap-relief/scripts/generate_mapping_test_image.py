#!/usr/bin/env python3
"""Create an asymmetric mapping/orientation test height map."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from heightmap_common import save_png

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output",type=Path)
    p.add_argument("--width",type=int,default=1200)
    p.add_argument("--height",type=int,default=600)
    args=p.parse_args()
    im=Image.new("L",(args.width,args.height),24)
    d=ImageDraw.Draw(im)
    font=ImageFont.load_default(size=max(12,args.height//24))
    d.rectangle((0,0,args.width-1,args.height-1),outline=220,width=max(3,args.width//300))
    d.rectangle((0,0,args.width//18,args.height-1),fill=80)
    d.rectangle((args.width-args.width//18,0,args.width-1,args.height-1),fill=180)
    d.rectangle((0,0,args.width-1,args.height//14),fill=230)
    d.rectangle((0,args.height-args.height//14,args.width-1,args.height-1),fill=50)
    labels=[("TOP",(args.width//2,args.height//18),230),("BOTTOM",(args.width//2,args.height*13//14),230),
            ("LEFT",(args.width//12,args.height//2),230),("RIGHT",(args.width*11//12,args.height//2),230)]
    for text,center,fill in labels:
        box=d.textbbox((0,0),text,font=font); tw=box[2]-box[0]; th=box[3]-box[1]
        d.text((center[0]-tw//2,center[1]-th//2),text,font=font,fill=fill)
    # Unequal corner markers and a rising ramp make flips immediately visible.
    for idx,r in enumerate([20,35,50,70]):
        cx=[90,args.width-90,args.width-90,90][idx]
        cy=[90,90,args.height-90,args.height-90][idx]
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=80+idx*50)
    arr=np.asarray(im,dtype=np.float32)/255.0
    arr=np.clip(arr+np.linspace(0,0.18,args.width,dtype=np.float32)[None,:],0,1)
    save_png(arr,args.output,16)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
