#!/usr/bin/env python3
"""Modern rounded desk organizer with two drawers and divided upper tray.

The assembled object is intentionally divided into a lower carcass, an upper
tray, two drawers, and alignment pins. A nominal one-piece body would create
large inaccessible bridges above the drawer cavities. The split retains low
assembly while making every major part support-light and replaceable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq


def rounded_prism(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    part = cq.Workplane("XY").rect(width, depth).extrude(height)
    if radius > 0:
        try:
            part = part.edges("|Z").fillet(radius)
        except Exception:
            pass
    return part


def rounded_cutter(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    return rounded_prism(width, depth, height, radius)


def build_lower(p: dict[str, float]) -> cq.Workplane:
    w, d, h = p["width"], p["depth"], p["lower_height"]
    outer = rounded_prism(w, d, h, p["outer_radius"])

    usable_w = w - 2 * p["side_wall"] - p["divider"]
    cavity_w = usable_w / 2
    cavity_h = h - p["bottom"] - p["roof"]
    cavity_d = d - p["back"] + 1.2
    y_center = -(p["back"] + 1.2) / 2
    z_center = p["bottom"] + cavity_h / 2
    x_offset = p["divider"] / 2 + cavity_w / 2

    for x in (-x_offset, x_offset):
        cutter = (
            rounded_cutter(cavity_w, cavity_d, cavity_h, p["drawer_corner_radius"])
            .translate((x, y_center, p["bottom"]))
        )
        outer = outer.cut(cutter)

    # Four vertical alignment holes accept loose printed or purchased pins.
    hole_x = w / 2 - p["side_wall"] - 6
    hole_y = d / 2 - p["back"] - 7
    for x in (-hole_x, hole_x):
        for y in (-hole_y, hole_y):
            outer = outer.cut(
                cq.Workplane("XY")
                .center(x, y)
                .circle(p["pin_hole_d"] / 2)
                .extrude(p["pin_engagement"] + 0.3)
                .translate((0, 0, h - p["pin_engagement"]))
            )
    return outer


def build_upper(p: dict[str, float]) -> cq.Workplane:
    w, d, h = p["width"], p["depth"], p["upper_height"]
    tray = rounded_prism(w, d, h, p["outer_radius"])
    base = p["tray_base"]
    wall = p["tray_wall"]
    divider = p["tray_divider"]

    # Rear full-width compartment and two front compartments.
    rear_d = d * 0.38
    front_d = d - rear_d - divider
    inner_w = w - 2 * wall
    front_w = (inner_w - divider) / 2
    pocket_h = h - base + 0.4

    rear = (
        rounded_cutter(inner_w, rear_d - wall, pocket_h, 4.0)
        .translate((0, d / 2 - wall - (rear_d - wall) / 2, base))
    )
    tray = tray.cut(rear)

    y_front = -d / 2 + wall + front_d / 2
    xoff = divider / 2 + front_w / 2
    for x in (-xoff, xoff):
        pocket = (
            rounded_cutter(front_w, front_d - wall, pocket_h, 4.0)
            .translate((x, y_front, base))
        )
        tray = tray.cut(pocket)

    # Matching alignment holes from the underside; loose pins make either part replaceable.
    hole_x = w / 2 - p["side_wall"] - 6
    hole_y = d / 2 - p["back"] - 7
    for x in (-hole_x, hole_x):
        for y in (-hole_y, hole_y):
            hole = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(p["pin_hole_d"] / 2)
                .extrude(p["pin_engagement"] + 0.3)
            )
            tray = tray.cut(hole)
    return tray


def build_drawer(p: dict[str, float], side: str) -> cq.Workplane:
    w, d, h = p["width"], p["depth"], p["lower_height"]
    usable_w = w - 2 * p["side_wall"] - p["divider"]
    cavity_w = usable_w / 2
    cavity_h = h - p["bottom"] - p["roof"]
    clear = p["drawer_clearance"]

    dw = cavity_w - 2 * clear
    dd = d - p["back"] - p["drawer_front_gap"]
    dh = cavity_h - 2 * clear
    wall = p["drawer_wall"]
    base = p["drawer_base"]

    drawer = rounded_prism(dw, dd, dh, p["drawer_corner_radius"])
    inner = (
        rounded_cutter(dw - 2 * wall, dd - 2 * wall, dh - base + 0.6, max(0.8, p["drawer_corner_radius"] - wall / 2))
        .translate((0, 0, base))
    )
    drawer = drawer.cut(inner)

    # Integrated front panel overlaps the carcass opening slightly.
    panel = (
        rounded_prism(dw + 2.2, p["front_panel_thickness"], dh + 1.2, 2.5)
        .translate((0, -dd / 2 - p["front_panel_thickness"] / 2 + 0.2, -0.6))
    )
    drawer = drawer.union(panel)

    # Finger scoop cut through the top of the front panel and drawer lip.
    scoop = (
        cq.Workplane("XZ")
        .center(0, dh + 0.2)
        .circle(p["scoop_d"] / 2)
        .extrude(p["front_panel_thickness"] + wall + 3, both=True)
        .translate((0, -dd / 2, 0))
    )
    drawer = drawer.cut(scoop)
    return drawer


def build_pin(p: dict[str, float]) -> cq.Workplane:
    # Diameter includes nominal diametral clearance relative to the two holes.
    d = p["pin_hole_d"] - p["pin_diametral_clearance"]
    length = 2 * p["pin_engagement"] - p["pin_center_gap"]
    return (
        cq.Workplane("XY")
        .circle(d / 2)
        .extrude(length)
        .edges("%CIRCLE")
        .chamfer(min(0.5, d / 8))
    )


def place_on_bed(shape: cq.Workplane) -> cq.Workplane:
    bb = shape.val().BoundingBox()
    return shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def lower_print_orientation(shape: cq.Workplane) -> cq.Workplane:
    # Back panel on the bed: drawer cavities point upward during printing.
    rotated = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    return place_on_bed(rotated)


def export(shape: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".step":
        cq.exporters.export(shape, str(path), exportType="STEP")
    elif path.suffix.lower() == ".stl":
        cq.exporters.export(shape, str(path), exportType="STL", tolerance=0.08, angularTolerance=0.12)
    else:
        raise ValueError(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("generated"))
    ap.add_argument("--width", type=float, default=188.0)
    ap.add_argument("--depth", type=float, default=126.0)
    ap.add_argument("--lower-height", type=float, default=60.0)
    ap.add_argument("--upper-height", type=float, default=48.0)
    ap.add_argument("--drawer-clearance", type=float, default=0.35, help="per side")
    args = ap.parse_args()

    p = {
        "width": args.width,
        "depth": args.depth,
        "lower_height": args.lower_height,
        "upper_height": args.upper_height,
        "outer_radius": 8.0,
        "side_wall": 4.0,
        "divider": 4.0,
        "bottom": 4.0,
        "roof": 5.0,
        "back": 4.0,
        "drawer_corner_radius": 3.0,
        "drawer_clearance": args.drawer_clearance,
        "drawer_front_gap": 5.0,
        "drawer_wall": 2.0,
        "drawer_base": 2.4,
        "front_panel_thickness": 3.0,
        "scoop_d": 25.0,
        "tray_base": 3.0,
        "tray_wall": 4.0,
        "tray_divider": 4.0,
        "pin_hole_d": 4.4,
        "pin_diametral_clearance": 0.35,
        "pin_engagement": 3.5,
        "pin_center_gap": 0.4,
    }

    lower = build_lower(p)
    upper = build_upper(p)
    drawer_l = build_drawer(p, "left")
    drawer_r = build_drawer(p, "right")
    pin = build_pin(p)

    out = args.out
    # Editable assembled-orientation masters.
    export(lower, out / "lower-carcass.step")
    export(upper, out / "upper-tray.step")
    export(drawer_l, out / "drawer-left.step")
    export(drawer_r, out / "drawer-right.step")
    export(pin, out / "alignment-pin.step")

    # Manufacturing STLs are placed on the bed intentionally.
    export(lower_print_orientation(lower), out / "lower-carcass-print.stl")
    export(place_on_bed(upper), out / "upper-tray-print.stl")
    export(place_on_bed(drawer_l), out / "drawer-left-print.stl")
    export(place_on_bed(drawer_r), out / "drawer-right-print.stl")
    export(place_on_bed(pin), out / "alignment-pin-print.stl")

    # Assembly STEP for visual/clearance review.
    assembly = cq.Assembly(name="rounded-desk-organizer")
    assembly.add(lower, name="lower")
    assembly.add(upper, name="upper", loc=cq.Location(cq.Vector(0, 0, p["lower_height"])))

    usable_w = p["width"] - 2 * p["side_wall"] - p["divider"]
    cavity_w = usable_w / 2
    xoff = p["divider"] / 2 + cavity_w / 2
    drawer_z = p["bottom"] + p["drawer_clearance"]
    drawer_y = -p["drawer_front_gap"] / 2
    assembly.add(drawer_l, name="drawer-left", loc=cq.Location(cq.Vector(-xoff, drawer_y, drawer_z)))
    assembly.add(drawer_r, name="drawer-right", loc=cq.Location(cq.Vector(xoff, drawer_y, drawer_z)))
    cq.exporters.export(assembly.toCompound(), str(out / "organizer-assembly.step"), exportType="STEP")

    report = {
        "parameters": p,
        "printed_part_count": 5,
        "alignment_pin_quantity": 4,
        "design_decision": "Split lower carcass and upper tray to remove long inaccessible bridges while keeping assembly low.",
        "drawer_clearance_per_side_mm": p["drawer_clearance"],
        "warning": "Clearance is only a starting value; print a drawer fit coupon on the exact process.",
    }
    (out / "build-metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
