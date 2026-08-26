#!/usr/bin/env python3
"""Generate editable metric SVG centerlines for compact surface patterns.

The SVG is a vector source for CAD emboss/engrave, curve mapping, or an
independently validated toolpath workflow. It is deliberately not G-code.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def positive(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("value must be finite and greater than zero")
    return number


def size_mm(value: str) -> tuple[float, float]:
    try:
        left, right = value.lower().replace("×", "x").split("x", 1)
        return positive(left), positive(right)
    except (ValueError, argparse.ArgumentTypeError) as exc:
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT in millimetres") from exc


def fmt(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def add_path(group: ET.Element, data: str, **attributes: str) -> None:
    attrs = {"d": data}
    attrs.update(attributes)
    ET.SubElement(group, tag("path"), attrs)


def carbon_twill(group: ET.Element, width: float, height: float, pitch: float) -> None:
    count = int(math.ceil((width + 2 * height) / pitch)) + 2
    dash = f"{fmt(2 * pitch)} {fmt(2 * pitch)}"
    for index in range(count):
        offset = -height + index * pitch
        add_path(
            group,
            f"M {fmt(offset)} 0 L {fmt(offset + height)} {fmt(height)}",
            **{"stroke-dasharray": dash, "stroke-dashoffset": fmt((index % 4) * pitch)},
        )
        add_path(
            group,
            f"M {fmt(offset)} {fmt(height)} L {fmt(offset + height)} 0",
            **{"stroke-dasharray": dash, "stroke-dashoffset": fmt(((index + 2) % 4) * pitch)},
        )


def wood_grain(
    group: ET.Element,
    width: float,
    height: float,
    pitch: float,
    margin: float,
    rng: random.Random,
) -> None:
    samples = max(32, int(math.ceil(width / max(pitch / 4.0, 0.1))))
    y = margin + pitch / 2.0
    while y <= height - margin:
        phase = rng.uniform(0.0, 2.0 * math.pi)
        period = rng.uniform(6.0 * pitch, 12.0 * pitch)
        amplitude = rng.uniform(0.10, 0.24) * pitch
        points: list[str] = []
        for index in range(samples + 1):
            x = width * index / samples
            yy = y + amplitude * math.sin(2.0 * math.pi * x / period + phase)
            yy += 0.35 * amplitude * math.sin(4.0 * math.pi * x / period + 0.7 * phase)
            points.append(f"{fmt(x)},{fmt(yy)}")
        ET.SubElement(group, tag("polyline"), {"points": " ".join(points)})
        y += pitch

    knot_count = min(3, max(1, int(width * height / 2400.0)))
    for _ in range(knot_count):
        cx = rng.uniform(0.22 * width, 0.78 * width)
        cy = rng.uniform(0.20 * height, 0.80 * height)
        angle = rng.uniform(-18, 18)
        for ring in range(1, 4):
            ET.SubElement(
                group,
                tag("ellipse"),
                {
                    "cx": fmt(cx),
                    "cy": fmt(cy),
                    "rx": fmt(ring * 0.55 * pitch),
                    "ry": fmt(ring * 0.28 * pitch),
                    "transform": f"rotate({fmt(angle)} {fmt(cx)} {fmt(cy)})",
                },
            )


def lotus(group: ET.Element, width: float, height: float, pitch: float) -> None:
    cx, cy = width / 2.0, height / 2.0
    outer = 0.43 * min(width, height)
    inner = max(0.10 * outer, 0.6 * pitch)
    petal_count = max(8, min(16, int(round(2.0 * math.pi * outer / max(2.5 * pitch, 0.1)))))
    half_base = math.pi / petal_count * 0.58
    for index in range(petal_count):
        angle = -math.pi / 2.0 + 2.0 * math.pi * index / petal_count
        left = angle - half_base
        right = angle + half_base
        base_left = (cx + inner * math.cos(left), cy + inner * math.sin(left))
        base_right = (cx + inner * math.cos(right), cy + inner * math.sin(right))
        tip = (cx + outer * math.cos(angle), cy + outer * math.sin(angle))
        ctrl_left = (cx + 0.72 * outer * math.cos(left), cy + 0.72 * outer * math.sin(left))
        ctrl_right = (cx + 0.72 * outer * math.cos(right), cy + 0.72 * outer * math.sin(right))
        data = (
            f"M {fmt(base_left[0])} {fmt(base_left[1])} "
            f"Q {fmt(ctrl_left[0])} {fmt(ctrl_left[1])} {fmt(tip[0])} {fmt(tip[1])} "
            f"Q {fmt(ctrl_right[0])} {fmt(ctrl_right[1])} {fmt(base_right[0])} {fmt(base_right[1])}"
        )
        add_path(group, data)
    ET.SubElement(group, tag("circle"), {"cx": fmt(cx), "cy": fmt(cy), "r": fmt(inner)})


def brushed(group: ET.Element, width: float, height: float, pitch: float) -> None:
    y = -height
    while y <= 2 * height:
        add_path(group, f"M {-width} {fmt(y)} L {fmt(2 * width)} {fmt(y)}")
        y += pitch


def build_svg(args: argparse.Namespace) -> ET.ElementTree:
    width, height = args.size_mm
    if args.stroke_mm >= args.pitch_mm:
        raise ValueError("--stroke-mm must be smaller than --pitch-mm")
    if 2 * args.margin_mm >= min(width, height):
        raise ValueError("--margin-mm leaves no usable pattern area")

    root = ET.Element(
        tag("svg"),
        {
            "width": f"{fmt(width)}mm",
            "height": f"{fmt(height)}mm",
            "viewBox": f"0 0 {fmt(width)} {fmt(height)}",
        },
    )
    metadata = {
        "generator": "design-printable-surface-textures/generate_surface_pattern_svg.py",
        "pattern": args.pattern,
        "size_mm": [width, height],
        "pitch_mm": args.pitch_mm,
        "stroke_mm": args.stroke_mm,
        "seed": args.seed,
        "role": "editable-vector-source-not-machine-gcode",
    }
    ET.SubElement(root, tag("metadata")).text = json.dumps(metadata, sort_keys=True)
    defs = ET.SubElement(root, tag("defs"))
    clip = ET.SubElement(defs, tag("clipPath"), {"id": "patch"})
    ET.SubElement(
        clip,
        tag("rect"),
        {
            "x": fmt(args.margin_mm),
            "y": fmt(args.margin_mm),
            "width": fmt(width - 2 * args.margin_mm),
            "height": fmt(height - 2 * args.margin_mm),
        },
    )
    group = ET.SubElement(
        root,
        tag("g"),
        {
            "id": args.pattern,
            "fill": "none",
            "stroke": "#000000",
            "stroke-width": fmt(args.stroke_mm),
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "clip-path": "url(#patch)",
            "transform": f"rotate({fmt(args.angle_deg)} {fmt(width / 2)} {fmt(height / 2)})",
        },
    )
    rng = random.Random(args.seed)
    if args.pattern == "carbon-twill":
        carbon_twill(group, width, height, args.pitch_mm)
    elif args.pattern == "wood-grain":
        wood_grain(group, width, height, args.pitch_mm, args.margin_mm, rng)
    elif args.pattern == "lotus":
        lotus(group, width, height, args.pitch_mm)
    elif args.pattern == "brushed":
        brushed(group, width, height, args.pitch_mm)
    else:  # pragma: no cover - argparse prevents this
        raise ValueError(f"unsupported pattern: {args.pattern}")
    return ET.ElementTree(root)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--pattern", choices=("carbon-twill", "wood-grain", "lotus", "brushed"), required=True)
    result.add_argument("--size-mm", type=size_mm, required=True, metavar="WIDTHxHEIGHT")
    result.add_argument("--pitch-mm", type=positive, required=True)
    result.add_argument("--stroke-mm", type=positive, required=True)
    result.add_argument("--margin-mm", type=float, default=1.0)
    result.add_argument("--angle-deg", type=float, default=0.0)
    result.add_argument("--seed", type=int, default=1)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    if args.margin_mm < 0:
        raise SystemExit("error: --margin-mm must be non-negative")
    try:
        tree = build_svg(args)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
