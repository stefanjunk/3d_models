#!/usr/bin/env python3
"""Cut-list calculator for the Kobra 3 Max hybrid enclosure."""
from __future__ import annotations
import argparse
import math

RAIL_REACH = 16.0
RAIL_SLOT_DEPTH = 11.0
RAIL_SEGMENT = 286.0


def mm(v: float) -> str:
    return f"{v:.0f} mm" if abs(v-round(v)) < 1e-9 else f"{v:.1f} mm"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--width', type=float, default=900, help='outer width in mm')
    p.add_argument('--depth', type=float, default=1050, help='outer depth in mm')
    p.add_argument('--height', type=float, default=900, help='outer height in mm')
    p.add_argument('--batten', type=float, default=20, help='square timber size in mm')
    p.add_argument('--panel-clearance', type=float, default=1.0,
                   help='total clearance for panel dimension captured by two rails')
    p.add_argument('--vertical-clearance', type=float, default=4.0,
                   help='clearance between bottom and top timber')
    args = p.parse_args()

    w,d,h,b = args.width,args.depth,args.height,args.batten
    if min(w,d,h,b) <= 0 or w <= 2*b or d <= 2*b or h <= 2*b:
        raise SystemExit('Invalid dimensions: enclosure must be larger than twice the batten size.')

    iw,id_,ih = w-2*b,d-2*b,h-2*b
    captured_loss = 2*(RAIL_REACH-RAIL_SLOT_DEPTH) + args.panel_clearance
    side_d = id_ - captured_loss
    back_w = iw - captured_loss
    fixed_h = ih - args.vertical_clearance

    print('FREIER INNENRAUM')
    print(f'  {mm(iw)} B x {mm(id_)} T x {mm(ih)} H')
    print('\nHOLZZUSCHNITT (standardmäßig 20x20 mm)')
    print(f'  4 x {mm(h)} senkrechte Pfosten')
    print(f'  4 x {mm(iw)} Querleisten')
    print(f'  5 x {mm(id_)} Tiefenleisten (einschließlich mittlerer Dachleiste)')
    print('\nPLEXIGLAS-ZUSCHNITT')
    print(f'  2 x {mm(side_d)} T x {mm(fixed_h)} H, Seitenwände')
    print(f'  1 x {mm(back_w)} B x {mm(fixed_h)} H, Rückwand')
    print(f'  1 x {mm(w-20)} B x {mm(h-20)} H, abnehmbare Frontplatte')
    print(f'  2 x {mm(w/2)} B x {mm(d-10)} T, Dachplatten')
    print('\nSCHIENEN')
    run = ih - 2
    full = int(run // RAIL_SEGMENT)
    rem = run - full*RAIL_SEGMENT
    print(f'  6 senkrechte Läufe, Ziellänge jeweils {mm(run)}')
    if rem < 0.5:
        print(f'  Je Lauf: {full} x {mm(RAIL_SEGMENT)}')
    else:
        print(f'  Je Lauf: {full} x {mm(RAIL_SEGMENT)} + 1 x Sonderlänge {mm(rem)}')
    total_joints = 6*max(0, math.ceil(run/RAIL_SEGMENT)-1)
    print(f'  Mindestens {total_joints} Verbindungsstifte; zwei Ersatzteile zusätzlich drucken')

if __name__ == '__main__':
    main()
