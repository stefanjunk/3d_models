#!/usr/bin/env python3
"""Generate a product-specific metriMade FDM engraving profile and test geometry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import trimesh


DOMAIN = "metriMade.com"
ASSET_REVISION = "MM-WM-001-R2"
DEFAULT_FONT = Path("/usr/share/fonts/inter/InterVariable.ttf")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "exports" / "examples"
LAYOUT_ORDER = ("full", "compact", "micro")
LAYOUT_PRIORITY = {layout: index + 1 for index, layout in enumerate(LAYOUT_ORDER)}
PRODUCT_ID_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)+$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)

# Production mark outline. The color-only aqua edge is intentionally omitted
# from the one-color engraving because it falls below the qualified small-size
# feature limit. The central negative-space M and fitted floor remain intact.
MARK_PATHS = (
    "M8 221C2 213 0 202 0 190V62C0 27 27 0 61 0H157C168 0 177 4 184 11L91 71V174L8 221Z",
    "M132 70L195 36V191C195 207 191 217 182 226L132 193V70Z",
    "M18 230L92 184L174 231C164 237 154 238 142 238H44C33 238 24 235 18 230Z",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_inputs(product_id: str, version: str, depth: float) -> None:
    if not (3 <= len(product_id) <= 32 and PRODUCT_ID_RE.fullmatch(product_id)):
        raise ValueError(
            "Product ID must be 3-32 uppercase letters/digits with at least one hyphen, "
            "for example MM-ORG-001"
        )
    if not SEMVER_RE.fullmatch(version):
        raise ValueError("Version must be Semantic Versioning, for example 1.0.0 or 1.0.0-rc.1")
    if not 0.4 <= depth <= 0.8:
        raise ValueError("Engraving depth must be between 0.40 and 0.80 mm")


def load_font(path: Path, weight: int = 800) -> TTFont:
    font = TTFont(path)
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": weight}, inplace=False)
    return font


def raw_text(font: TTFont, text: str, tracking: float = 4.0):
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    placements: list[tuple[str, float]] = []
    cursor = 0.0
    bounds: list[tuple[float, float, float, float]] = []

    for character in text:
        glyph_name = cmap.get(ord(character))
        if glyph_name is None:
            raise ValueError(f"Font has no glyph for {character!r}")
        glyph = glyph_set[glyph_name]
        pen = BoundsPen(glyph_set)
        glyph.draw(pen)
        if pen.bounds:
            x_min, y_min, x_max, y_max = pen.bounds
            bounds.append((cursor + x_min, y_min, cursor + x_max, y_max))
        placements.append((glyph_name, cursor))
        cursor += glyph.width + tracking

    if not bounds:
        raise ValueError("Text produced no outlines")
    return placements, (
        min(item[0] for item in bounds),
        min(item[1] for item in bounds),
        max(item[2] for item in bounds),
        max(item[3] for item in bounds),
    )


def text_width_by_height(font: TTFont, text: str, visual_height_mm: float) -> float:
    _, (x_min, y_min, x_max, y_max) = raw_text(font, text)
    return (x_max - x_min) * visual_height_mm / (y_max - y_min)


def layout_metrics(font: TTFont, product_id: str, version: str, layout: str) -> dict[str, object]:
    if layout not in LAYOUT_PRIORITY:
        raise ValueError(f"Layout must be one of {', '.join(LAYOUT_ORDER)}")

    if layout == "full":
        profile_height = 12.8
        right_margin = 1.0
        icon = {"x_mm": 0.8, "y_mm": 0.8, "height_mm": 11.2}
        text_x = 11.2
        text_lines = [
            {"value": DOMAIN, "x_mm": text_x, "y_mm": 7.4, "height_mm": 4.4},
            {
                "value": f"{product_id} · v{version}",
                "x_mm": text_x,
                "y_mm": 1.8,
                "height_mm": 3.6,
            },
        ]
    elif layout == "compact":
        profile_height = 11.2
        right_margin = 0.8
        icon = {"x_mm": 0.8, "y_mm": 0.8, "height_mm": 9.6}
        text_x = 9.6
        text_lines = [
            {"value": DOMAIN, "x_mm": text_x, "y_mm": 7.4, "height_mm": 3.0},
            {"value": product_id, "x_mm": text_x, "y_mm": 4.0, "height_mm": 2.8},
            {"value": f"v{version}", "x_mm": text_x, "y_mm": 0.8, "height_mm": 2.8},
        ]
    else:
        profile_height = 9.6
        right_margin = 0.8
        icon = {"x_mm": 0.8, "y_mm": 0.8, "height_mm": 8.0}
        text_x = 8.2
        text_lines = [
            {"value": product_id, "x_mm": text_x, "y_mm": 5.0, "height_mm": 3.0},
            {"value": f"v{version}", "x_mm": text_x, "y_mm": 1.0, "height_mm": 2.8},
        ]

    for line in text_lines:
        line["width_mm"] = text_width_by_height(
            font,
            str(line["value"]),
            float(line["height_mm"]),
        )
    profile_width = round(
        max(float(line["x_mm"]) + float(line["width_mm"]) for line in text_lines)
        + right_margin,
        3,
    )
    return {
        "tier": layout,
        "priority": LAYOUT_PRIORITY[layout],
        "profile_width_mm": profile_width,
        "profile_height_mm": profile_height,
        "icon": icon,
        "text_lines": text_lines,
        "domain_visible": layout != "micro",
    }


def icon_svg() -> str:
    mark_paths = "\n    ".join(
        f'<path d="{path}" fill="#000000"/>' for path in MARK_PATHS
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="195mm" height="238mm" viewBox="0 0 195 238">
  <g>
    {mark_paths}
  </g>
</svg>
'''


def scad_wrapper(
    icon_filename: str,
    layout: dict[str, object],
    depth: float,
) -> str:
    width = float(layout["profile_width_mm"])
    height = float(layout["profile_height_mm"])
    icon = layout["icon"]
    if not isinstance(icon, dict):
        raise ValueError("Layout icon definition must be an object")
    text_lines = layout["text_lines"]
    if not isinstance(text_lines, list):
        raise ValueError("Layout text_lines must be a list")
    text_geometry = "\n".join(
        "        translate([{x:.5f}, {y:.5f}])\n"
        "            fitted_text(\"{value}\", {width:.5f}, {height:.5f});".format(
            x=float(line["x_mm"]),
            y=float(line["y_mm"]),
            value=line["value"],
            width=float(line["width_mm"]),
            height=float(line["height_mm"]),
        )
        for line in text_lines
    )
    return f'''// Generated by tools/generate_watermark.py — {ASSET_REVISION}
// Layout tier: {layout["tier"]}
mode = "cutter"; // [profile,cutter,coupon]
engraving_depth = {depth:.2f};
profile_width = {width:.3f};
profile_height = {height:.3f};
coupon_margin = 3.0;
coupon_thickness = 2.4;
font_name = "Inter:style=ExtraBold";

module fitted_text(value, target_width, target_height) {{
    resize([target_width, target_height])
        text(
            value,
            size = 10,
            font = font_name,
            halign = "left",
            valign = "bottom"
        );
}}

module watermark_profile_core() {{
    union() {{
        translate([{float(icon["x_mm"]):.5f}, {float(icon["y_mm"]):.5f}])
            scale({float(icon["height_mm"]):.5f} / 238)
            import("{icon_filename}", center = false);
{text_geometry}
    }}
}}

module watermark_profile(underside_readable = false) {{
    if (underside_readable)
        translate([profile_width, 0]) mirror([1, 0, 0])
            watermark_profile_core();
    else
        watermark_profile_core();
}}

module watermark_cutter(depth = engraving_depth, underside_readable = true) {{
    linear_extrude(height = depth)
        watermark_profile(underside_readable);
}}

module watermark_coupon() {{
    difference() {{
        translate([-coupon_margin, -coupon_margin, 0])
            cube([
                profile_width + 2 * coupon_margin,
                profile_height + 2 * coupon_margin,
                coupon_thickness
            ]);
        translate([0, 0, -0.01])
            linear_extrude(height = engraving_depth + 0.02)
                watermark_profile(true);
    }}
}}

if (mode == "profile") watermark_profile(false);
else if (mode == "coupon") watermark_coupon();
else watermark_cutter();
'''


def run_export(scad: Path, output: Path, mode: str) -> None:
    subprocess.run(
        ["openscad", "-o", str(output), "-D", f'mode="{mode}"', str(scad)],
        check=True,
        capture_output=True,
        text=True,
    )


def render_png(svg_path: Path, png_path: Path) -> None:
    subprocess.run(
        ["magick", "-background", "white", str(svg_path), "-resize", "1800x", str(png_path)],
        check=True,
    )


def normalize_svg_style(svg_path: Path) -> None:
    data = svg_path.read_text(encoding="utf-8")
    data = data.replace(
        'stroke="black" fill="lightgray" stroke-width="0.5"',
        'stroke="none" fill="#000000"',
    )
    svg_path.write_text(data, encoding="utf-8")


def validate_mesh(path: Path) -> dict[str, object]:
    mesh = trimesh.load_mesh(path, process=True)
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise RuntimeError(f"Generated mesh failed topology validation: {path}")
    return {
        "watertight": True,
        "winding_consistent": True,
        "positive_volume": True,
        "body_count": int(mesh.body_count),
        "extents_mm": [round(float(value), 5) for value in mesh.extents],
        "volume_mm3": round(float(mesh.volume), 5),
    }


def build(
    product_id: str,
    version: str,
    depth: float,
    font_path: Path,
    output_root: Path,
    layout: str = "full",
) -> Path:
    validate_inputs(product_id, version, depth)
    font = load_font(font_path)
    metrics = layout_metrics(font, product_id, version, layout)
    suffix = "" if layout == "full" else f"-{layout}"
    slug = f"{product_id}_v{version}{suffix.replace('-', '_')}"
    output_dir = output_root / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"metrimade-watermark-{product_id}-v{version}{suffix}"

    width = float(metrics["profile_width_mm"])
    height = float(metrics["profile_height_mm"])
    svg_path = output_dir / f"{stem}.svg"
    icon_path = output_dir / f"{stem}-icon-source.svg"
    scad_path = output_dir / f"{stem}.scad"
    png_path = output_dir / f"{stem}.png"
    dxf_path = output_dir / f"{stem}.dxf"
    cutter_path = output_dir / f"{stem}-cutter-d{int(round(depth * 100)):03d}.stl"
    coupon_path = output_dir / f"{stem}-coupon-d{int(round(depth * 100)):03d}.stl"

    icon_path.write_text(icon_svg(), encoding="utf-8")
    scad_path.write_text(
        scad_wrapper(
            icon_path.name,
            metrics,
            depth,
        ),
        encoding="utf-8",
    )
    if not shutil.which("openscad"):
        raise RuntimeError("OpenSCAD is required to generate manufacturing outlines and meshes")
    run_export(scad_path, svg_path, "profile")
    run_export(scad_path, dxf_path, "profile")
    run_export(scad_path, cutter_path, "cutter")
    run_export(scad_path, coupon_path, "coupon")
    normalize_svg_style(svg_path)
    render_png(svg_path, png_path)
    cutter_validation = validate_mesh(cutter_path)
    coupon_validation = validate_mesh(coupon_path)

    metadata = {
        "asset_revision": ASSET_REVISION,
        "status": "digital-production-candidate-physical-test-pending",
        "domain": DOMAIN,
        "domain_visible": metrics["domain_visible"],
        "product_id": product_id,
        "version": version,
        "layout_tier": layout,
        "layout_priority": metrics["priority"],
        "visible_text": [str(line["value"]) for line in metrics["text_lines"]],
        "layout_envelope_mm": [width, height, depth],
        "layout_policy": {
            "selection_order": list(LAYOUT_ORDER),
            "rotation_degrees": [0, 90],
            "uniform_scale": 1.0,
            "micro_domain_omission": "allowed only after full and compact do not fit the measured safe region",
        },
        "text_visual_heights_mm": [
            float(line["height_mm"]) for line in metrics["text_lines"]
        ],
        "minimum_reliable_stroke_target_mm": 0.6,
        "digital_validation": {
            "result": "PASS",
            "cutter": cutter_validation,
            "coupon": coupon_validation,
            "physical_test": "PENDING",
        },
        "process_reference": {"technology": "FDM/FFF", "nozzle_mm": 0.4, "layer_height_mm": 0.2},
        "integration": {
            "operation": "subtractive engraving",
            "default_surface": "nonfunctional low-stress underside",
            "cutter_orientation": "mirrored in X so it reads normally from the finished underside",
            "profile_scaling": "prohibited",
            "minimum_host_wall_mm": 1.2,
            "minimum_remaining_wall_mm": 0.8,
        },
        "font": {
            "family": "Inter Variable",
            "weight": 800,
            "sha256": sha256(font_path),
            "license": "SIL Open Font License 1.1",
            "runtime_dependency_in_exports": False,
            "source_regeneration_dependency": "Inter ExtraBold installed for OpenSCAD",
        },
        "release_note": "This generated example is not itself a product-release approval.",
    }
    metadata_path = output_dir / f"{stem}.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_files = sorted(path for path in output_dir.iterdir() if path.is_file() and path.name != "manifest.sha256")
    manifest = "\n".join(f"{sha256(path)}  {path.name}" for path in output_files) + "\n"
    (output_dir / "manifest.sha256").write_text(manifest, encoding="utf-8")
    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate full, compact, or micro metriMade product watermark geometry."
    )
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--depth", type=float, default=0.4)
    parser.add_argument(
        "--layout",
        choices=(*LAYOUT_ORDER, "all"),
        default="full",
        help="Generate one tier, or all tiers for automatic safe-region selection.",
    )
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    if not args.font.is_file():
        raise SystemExit(f"Inter font not found: {args.font}")
    try:
        layouts = LAYOUT_ORDER if args.layout == "all" else (args.layout,)
        outputs = [
            build(
                args.product_id,
                args.version,
                args.depth,
                args.font.resolve(),
                args.output_root.resolve(),
                layout,
            )
            for layout in layouts
        ]
    except ValueError as error:
        raise SystemExit(str(error)) from error
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
