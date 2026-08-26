#!/usr/bin/env python3
"""Generate a detail-transfer coupon and an open-face negative tray.

The coupon contains paired raised ridges and recessed grooves at several widths.
Use it through the complete print/coating/plaster/cast/glaze workflow before
committing to a full mold.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import cadquery as cq


def union_all(shapes: list[cq.Shape]) -> cq.Shape:
    if not shapes:
        raise ValueError("No shapes to union.")
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    try:
        return result.clean()
    except Exception:
        return result


def curved_base(width: float, length: float, base_thickness: float, sag: float) -> tuple[cq.Shape, float, float]:
    if sag <= 0:
        raise ValueError("Curvature sag must be positive.")
    a = width / 2.0
    radius = (a * a + sag * sag) / (2.0 * sag)
    center_z = base_thickness + sag - radius
    edge_z = center_z + math.sqrt(max(0.0, radius * radius - a * a))
    profile = (
        cq.Workplane("XZ")
        .moveTo(-a, 0.0)
        .lineTo(-a, edge_z)
        .threePointArc((0.0, center_z + radius), (a, edge_z))
        .lineTo(a, 0.0)
        .close()
    )
    return profile.extrude(length / 2.0, both=True).val(), radius, center_z


def curved_band(width: float, length: float, inner_radius: float, outer_radius: float, center_z: float) -> cq.Shape:
    if outer_radius <= inner_radius:
        raise ValueError("Outer radius must exceed inner radius.")
    a = width / 2.0
    if a >= inner_radius:
        raise ValueError("Coupon width is too large for the requested curvature.")
    zo = center_z + math.sqrt(outer_radius * outer_radius - a * a)
    zi = center_z + math.sqrt(inner_radius * inner_radius - a * a)
    profile = (
        cq.Workplane("XZ")
        .moveTo(-a, zo)
        .threePointArc((0.0, center_z + outer_radius), (a, zo))
        .lineTo(a, zi)
        .threePointArc((0.0, center_z + inner_radius), (-a, zi))
        .close()
    )
    return profile.extrude(length / 2.0, both=True).val()


def build_coupon(width: float, length: float, base_thickness: float, widths: list[float], depths: list[float], curved: bool, sag: float) -> tuple[cq.Shape, list[dict[str, float]]]:
    if width <= 0 or length <= 0 or base_thickness <= 0:
        raise ValueError("Coupon dimensions must be positive.")
    if len(widths) != len(depths) or not widths:
        raise ValueError("Feature width and depth lists must be non-empty and equal length.")
    if any(v <= 0 for v in widths + depths):
        raise ValueError("Feature widths and depths must be positive.")

    if curved:
        base, radius, center_z = curved_base(width, length, base_thickness, sag)
    else:
        base = cq.Workplane("XY").box(width, length, base_thickness, centered=(True, True, False)).val()
        radius = center_z = 0.0

    x_positions = [(-width * 0.40) + i * (width * 0.80 / max(1, len(widths) - 1)) for i in range(len(widths))]
    ridge_y0, ridge_y1 = 3.0, length / 2.0 - 4.0
    groove_y0, groove_y1 = -length / 2.0 + 4.0, -3.0
    if ridge_y1 <= ridge_y0 or groove_y1 <= groove_y0:
        raise ValueError("Coupon length is too small for paired feature strips.")

    result = base
    entries: list[dict[str, float]] = []
    for idx, (x, feature_width, depth) in enumerate(zip(x_positions, widths, depths, strict=True)):
        ridge_box = cq.Solid.makeBox(feature_width, ridge_y1 - ridge_y0, base_thickness + sag + max(depths) + 20.0,
                                      (x - feature_width / 2.0, ridge_y0, 0.0))
        groove_box = cq.Solid.makeBox(feature_width, groove_y1 - groove_y0, base_thickness + sag + max(depths) + 20.0,
                                       (x - feature_width / 2.0, groove_y0, 0.0))

        if curved:
            ridge_layer = curved_band(width, length, radius, radius + depth, center_z).intersect(ridge_box)
            groove_layer = curved_band(width, length, max(0.1, radius - depth), radius + 0.03, center_z).intersect(groove_box)
        else:
            ridge_layer = cq.Solid.makeBox(feature_width, ridge_y1 - ridge_y0, depth,
                                            (x - feature_width / 2.0, ridge_y0, base_thickness))
            groove_layer = cq.Solid.makeBox(feature_width, groove_y1 - groove_y0, depth + 0.03,
                                             (x - feature_width / 2.0, groove_y0, base_thickness - depth))

        result = result.fuse(ridge_layer).cut(groove_layer)
        entries.append({
            "index": idx,
            "x_mm": x,
            "width_mm": feature_width,
            "depth_or_height_mm": depth,
            "ridge_y_range_mm": [ridge_y0, ridge_y1],
            "groove_y_range_mm": [groove_y0, groove_y1],
        })

    # Add a broad, shallow circular recess and boss to test rounded detail.
    dot_r = min(3.5, width * 0.04)
    dot_depth = min(max(depths), 0.8)
    if curved:
        # Keep curved mode focused on line features; dots would require a local normal projection.
        pass
    else:
        boss = cq.Solid.makeCylinder(dot_r, dot_depth, (-width * 0.30, 0, base_thickness))
        pit = cq.Solid.makeCylinder(dot_r, dot_depth + 0.03, (width * 0.30, 0, base_thickness - dot_depth))
        result = result.fuse(boss).cut(pit)

    try:
        result = result.clean()
    except Exception:
        pass
    return result, entries


def make_negative_tray(master: cq.Shape, margin: float, backing: float) -> cq.Shape:
    if margin <= 0 or backing <= 0:
        raise ValueError("Tray margin and backing must be positive.")
    b = master.BoundingBox()
    height = b.zlen + backing
    block = cq.Solid.makeBox(b.xlen + 2 * margin, b.ylen + 2 * margin, height,
                             (b.xmin - margin, b.ymin - margin, 0.0))
    # Mirror around the flat bottom plane so the article's back is flush with the
    # open top and the decorated face points down into the tray.
    downward = master.mirror("XY").translate((0, 0, height))
    tray = block.cut(downward)
    try:
        return tray.clean()
    except Exception:
        return tray


def export(shape: cq.Shape, path: Path, tolerance: float) -> None:
    if shape.isNull() or not shape.isValid():
        raise ValueError(f"Invalid shape: {path.name}")
    if path.suffix == ".step":
        cq.exporters.export(shape, str(path), exportType="STEP")
    else:
        cq.exporters.export(shape, str(path), exportType="STL", tolerance=tolerance, angularTolerance=0.12)


def parse_csv_floats(value: str) -> list[float]:
    try:
        return [float(v.strip()) for v in value.split(",") if v.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected comma-separated numbers") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--width", type=float, default=100.0)
    parser.add_argument("--length", type=float, default=60.0)
    parser.add_argument("--base-thickness", type=float, default=3.0)
    parser.add_argument("--feature-widths", type=parse_csv_floats, default=parse_csv_floats("0.3,0.5,0.8,1.2,2.0"))
    parser.add_argument("--feature-depths", type=parse_csv_floats, default=parse_csv_floats("0.15,0.2,0.3,0.5,0.8"))
    parser.add_argument("--curved", action="store_true", help="Use a shallow convex cylindrical face")
    parser.add_argument("--sag", type=float, default=8.0, help="Center rise over edge for curved coupon")
    parser.add_argument("--tray-margin", type=float, default=6.0)
    parser.add_argument("--tray-backing", type=float, default=5.0)
    parser.add_argument("--stl-tolerance", type=float, default=0.04)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        out = args.output_dir.expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        master, entries = build_coupon(
            args.width, args.length, args.base_thickness,
            args.feature_widths, args.feature_depths, args.curved, args.sag
        )
        tray = make_negative_tray(master, args.tray_margin, args.tray_backing)
        for shape, stem in ((master, "detail_coupon_master"), (tray, "detail_coupon_negative_tray")):
            export(shape, out / f"{stem}.step", args.stl_tolerance)
            export(shape, out / f"{stem}.stl", args.stl_tolerance)

        manifest = {
            "units": "mm",
            "curved": args.curved,
            "coupon_dimensions_mm": [args.width, args.length, args.base_thickness],
            "sag_mm": args.sag if args.curved else 0.0,
            "features": entries,
            "tray_margin_mm": args.tray_margin,
            "tray_backing_mm": args.tray_backing,
            "instructions": [
                "Print the master and/or direct negative tray with the intended production orientation and surface finish.",
                "Carry the coupon through every transfer stage: coating/release, plaster working mold if used, cast, drying/firing, glaze, and cleaning.",
                "Record the smallest feature that remains distinct, demolds without damage, and is cleanable under the intended use.",
                "Do not infer food-contact compliance from geometric success."
            ]
        }
        (out / "detail_coupon_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output_dir": str(out), "features": len(entries), "curved": args.curved}, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
