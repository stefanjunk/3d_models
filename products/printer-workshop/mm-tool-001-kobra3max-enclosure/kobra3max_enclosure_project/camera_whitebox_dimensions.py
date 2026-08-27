#!/usr/bin/env python3
"""Cut-list calculator for the bottomless Kobra 3 Max camera whitebox."""
from __future__ import annotations

import argparse


def mm(value: float) -> str:
    return f"{value:.0f} mm" if abs(value - round(value)) < 1e-9 else f"{value:.1f} mm"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=float, default=900, help="body width in mm")
    parser.add_argument("--depth", type=float, default=1050, help="body depth in mm")
    parser.add_argument("--height", type=float, default=900, help="body height in mm")
    parser.add_argument("--batten", type=float, default=20, help="square timber size in mm")
    parser.add_argument("--wall", type=float, default=3, help="opaque wall-panel thickness in mm")
    parser.add_argument("--door", type=float, default=4, help="clear door thickness in mm")
    parser.add_argument("--diffuser", type=float, default=3, help="roof diffuser thickness in mm")
    parser.add_argument("--window-width", type=float, default=80,
                        help="clear camera-window width in mm")
    parser.add_argument("--window-height", type=float, default=90,
                        help="clear camera-window height in mm")
    parser.add_argument("--window", type=float, default=2,
                        help="clear camera-window thickness in mm")
    parser.add_argument("--service-bay", type=float, default=140,
                        help="fixed front-right service-bay width in mm")
    parser.add_argument("--door-overlap", type=float, default=10,
                        help="door overlap around the moving opening in mm")
    parser.add_argument("--cassette-inset", type=float, default=24,
                        help="roof-light cassette inset from body edge in mm")
    args = parser.parse_args()

    w, d, h, b = args.width, args.depth, args.height, args.batten
    if min(w, d, h, b, args.wall, args.door, args.diffuser,
           args.window_width, args.window_height, args.window) <= 0:
        raise SystemExit("All dimensions must be positive.")
    if w <= 2 * b or d <= 2 * b or h <= 2 * b:
        raise SystemExit("The enclosure must be larger than twice the batten size.")
    if not 110 <= args.service_bay <= 220:
        raise SystemExit("Service bay must stay between 110 and 220 mm.")
    if not b <= args.cassette_inset <= 80:
        raise SystemExit("Cassette inset is outside the supported range.")
    if args.window_width + 24 >= args.service_bay:
        raise SystemExit("Camera window plus fastener border does not fit the service bay.")

    iw, id_, ih = w - 2 * b, d - 2 * b, h - 2 * b
    stile_x = w - b - args.service_bay
    door_w = stile_x - b + 2 * args.door_overlap
    door_h = ih + 2 * args.door_overlap
    cassette_w = w - 2 * args.cassette_inset
    cassette_d = d - 2 * args.cassette_inset
    cassette_cross = cassette_d - 2 * b

    print("KOBRA 3 MAX CAMERA WHITEBOX – DRAFT CUT LIST")
    print("\nBODY ENVELOPE")
    print(f"  {mm(w)} W x {mm(d)} D x {mm(h)} H")
    print(f"  clear frame opening: {mm(iw)} W x {mm(id_)} D x {mm(ih)} H")
    print(f"  approximate clear space after wall skins: {mm(iw-2*args.wall)} W x "
          f"{mm(id_-args.wall)} D x {mm(ih)} H")

    print(f"\nTIMBER BODY FRAME ({mm(b)} square)")
    print(f"  4 x {mm(h)} corner posts")
    print(f"  4 x {mm(iw)} front/rear rails")
    print(f"  4 x {mm(id_)} side rails")
    print(f"  1 x {mm(id_)} roof centre rail")
    print(f"  1 x {mm(ih)} fixed camera/service stile")

    print(f"\nTIMBER ROOF-LIGHT CASSETTE ({mm(b)} square)")
    print(f"  2 x {mm(cassette_w)} front/rear rails")
    print(f"  2 x {mm(cassette_cross)} side rails between front/rear rails")
    print("  cassette adds approximately 60 mm above the 900 mm body")

    print("\nSHEET MATERIAL")
    print(f"  2 x {mm(d)} x {mm(h)} x {mm(args.wall)} white-coated hardboard, sides")
    print(f"  1 x {mm(w)} x {mm(h)} x {mm(args.wall)} white-coated hardboard, rear")
    print(f"  1 x {mm(iw)} x {mm(id_)} x {mm(args.diffuser)} opal sheet, roof diffuser")
    print(f"  1 x {mm(door_w)} x {mm(door_h)} x {mm(args.door)} clear PMMA, door")
    print(f"  1 x {mm(args.service_bay)} x {mm(door_h)} x {mm(args.wall)} white-coated hardboard, fixed service bay")
    print(f"  1 x {mm(args.window_width)} x {mm(args.window_height)} x {mm(args.window)} clear PMMA/PC, optical window")
    print(f"  1 x {mm(cassette_w)} x {mm(cassette_d)} lightweight opaque sheet, cassette lid")

    print("\nRIGHT-SIDE SERVICE CUTOUT")
    print("  250 x 170 mm opening, nominal lower-left position 730 mm from front and 620 mm above table")
    print("  verify against frame, fan hardware and the physical camera view before cutting")

    print("\nCAMERA AND LIGHTING")
    print("  1 x 500 mm 2020 T-slot extrusion, vertical camera rail")
    print("  optical-panel cutout: 72 x 82 mm, centred nominally 820 mm from the left and 590 mm above table")
    print("  fit coupons first: camera body ring plus 11 mm ball/socket clearance strip")
    print("  6 x approximately 940 mm roof LED/aluminium heat-spreader runs")
    print("  2 x approximately 610 mm opal fill-light profiles")


if __name__ == "__main__":
    main()
