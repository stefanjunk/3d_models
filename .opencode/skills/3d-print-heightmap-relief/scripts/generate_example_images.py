#!/usr/bin/env python3
"""Generate redistributable procedural source images used by the three examples."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from heightmap_common import image_stats, make_preview, save_png, seam_metrics, write_json


def unicorn_heightmap(width: int = 1200, height: int = 600) -> np.ndarray:
    scale = 2
    canvas = Image.new("L", (width * scale, height * scale), 0)
    d = ImageDraw.Draw(canvas)
    S = scale
    def ellipse(box, fill=255):
        d.ellipse(tuple(int(v*S) for v in box), fill=fill)
    def polygon(points, fill=255):
        d.polygon([(int(x*S), int(y*S)) for x,y in points], fill=fill)
    def line(points, width_px, fill=255):
        d.line([(int(x*S), int(y*S)) for x,y in points], fill=fill, width=int(width_px*S), joint="curve")

    # A clean, side-view silhouette designed to survive FDM simplification.
    ellipse((385, 245, 790, 440))
    polygon([(690,300),(770,150),(835,155),(785,340)])
    ellipse((745,120,905,245))
    ellipse((850,165,930,220))
    polygon([(838,133),(876,36),(890,145)])  # horn
    polygon([(790,134),(805,77),(830,145)])  # ear
    # Legs and rounded hooves.
    polygon([(435,365),(505,365),(485,520),(430,520)])
    polygon([(615,370),(680,365),(705,520),(650,520)])
    ellipse((420,495,490,535)); ellipse((645,495,715,535))
    # Mane and tail are thick enough to print.
    polygon([(770,160),(710,178),(745,215),(685,226),(735,255),(690,300),(780,290)])
    line([(398,290),(300,230),(230,250),(170,205)], 38)
    line([(185,205),(130,165)], 24)
    # Eye and a few intentional negative details.
    ellipse((850,165,866,181), fill=0)
    line([(760,205),(805,222)], 10, fill=0)

    mask = np.asarray(canvas, dtype=np.float32) / 255.0
    mask = ndimage.zoom(mask, (height/mask.shape[0], width/mask.shape[1]), order=1)
    # A small inward bevel makes the relief read under grazing light.
    inside = ndimage.distance_transform_edt(mask > 0.5)
    bevel = np.clip(inside / max(1.0, width/240.0), 0.0, 1.0)
    result = mask * (0.60 + 0.40 * bevel)

    # Add printable stars without approaching the wrapping seam.
    yy, xx = np.mgrid[0:height, 0:width]
    for cx, cy, r in [(230,125,20),(1010,125,22),(1020,390,16),(255,430,14)]:
        ang = np.arctan2(yy-cy,xx-cx)
        rr = np.hypot(xx-cx,yy-cy)
        boundary = r * (0.45 + 0.55 * (np.cos(5*ang) > 0))
        result = np.maximum(result, (rr < boundary).astype(np.float32) * 0.8)
    return np.clip(result,0,1).astype(np.float32)


def carbon_heightmap(size: int = 1024) -> np.ndarray:
    y,x=np.mgrid[0:size,0:size].astype(np.float64)
    u=x/size; v=y/size
    strands=16
    p=np.mod((u+v)*strands,1.0)
    q=np.mod((u-v)*strands,1.0)
    dp=np.minimum(p,1-p); dq=np.minimum(q,1-q)
    warp=np.exp(-(dp/0.20)**4)
    weft=np.exp(-(dq/0.20)**4)
    checker=np.sin(2*np.pi*8*u)*np.sin(2*np.pi*8*v)
    over=0.5+0.5*np.tanh(5*checker)
    # Twill dominance alternates, while fine longitudinal ridges suggest fibre bundles.
    micro_p=0.82+0.18*np.cos(2*np.pi*64*(u-v))
    micro_q=0.82+0.18*np.cos(2*np.pi*64*(u+v))
    relief=over*warp*micro_p+(1-over)*weft*micro_q
    under=(1-over)*warp*0.33+over*weft*0.33
    values=0.12+0.70*relief+0.25*under
    values=ndimage.gaussian_filter(values,sigma=0.55,mode="wrap")
    values=(values-values.min())/(values.max()-values.min())
    return values.astype(np.float32)


def wood_heightmap(size: int = 1024) -> np.ndarray:
    y,x=np.mgrid[0:size,0:size].astype(np.float64)
    u=x/size; v=y/size
    # Long grain runs left/right. Every frequency is integral, so both axes tile.
    warp=(0.34*np.sin(2*np.pi*u)+0.16*np.sin(2*np.pi*(3*u+v))
          +0.08*np.sin(2*np.pi*(7*u-2*v)))
    phase=2*np.pi*(11*v+warp)
    grain=(0.50+0.25*np.sin(phase)+0.12*np.sin(2.0*phase+0.8)
           +0.07*np.sin(4.0*phase-0.4))
    fine=0.08*np.sin(2*np.pi*(41*v+0.7*np.sin(2*np.pi*5*u)))
    values=grain+fine

    # Toroidal elliptical knot rings preserve seamless repetition.
    for cu,cv,strength in [(0.28,0.34,0.32),(0.72,0.70,0.26)]:
        du=(u-cu+0.5)%1.0-0.5
        dv=(v-cv+0.5)%1.0-0.5
        r=np.sqrt((du/0.16)**2+(dv/0.060)**2)
        envelope=np.exp(-(r/1.45)**4)
        values += strength*envelope*np.sin(2*np.pi*(3.3*r+0.18*np.sin(2*np.pi*u)))
    values=ndimage.gaussian_filter(values,sigma=(0.55,0.35),mode="wrap")
    p1,p99=np.percentile(values,[1,99])
    return np.clip((values-p1)/(p99-p1),0,1).astype(np.float32)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--force",action="store_true")
    args=parser.parse_args()
    root=args.output_root.resolve()
    items=[
        ("examples/01-unicorn-cylinder/source/unicorn-source.png",unicorn_heightmap()),
        ("examples/02-carbon-rounded-organizer/source/carbon-fiber-source.png",carbon_heightmap()),
        ("examples/03-wood-honeycomb-shelf/source/wood-source.png",wood_heightmap()),
    ]
    report={"files":[]}
    for rel,array in items:
        path=root/rel
        if path.exists() and not args.force:
            raise FileExistsError(f"{path} exists; pass --force to replace generated fixtures")
        save_png(array,path,16)
        preview=path.with_name(path.stem+"-preview.png")
        make_preview(array,preview,1000)
        report["files"].append({
            "path":rel,"preview":str(preview.relative_to(root)),
            "shape_px":[int(array.shape[1]),int(array.shape[0])],
            "stats":image_stats(array),"seams":seam_metrics(array),
        })
    write_json(report,root/"examples/generated-image-report.json")
    print(f"Generated {len(items)} source images below {root}")
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        raise SystemExit(2)
