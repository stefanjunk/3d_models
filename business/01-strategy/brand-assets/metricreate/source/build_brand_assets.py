#!/usr/bin/env python3
"""Build deterministic metriCreate logo assets from selected v3 concept 01."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


PALETTE = {
    "canvas": "#0B0F12",
    "navy": "#112431",
    "teal": "#08777D",
    "aqua": "#7FD5D3",
    "offwhite": "#F2F6F5",
    "orange": "#F05A28",
}

# The original concept sheet and isolated user-selected crop are raster
# references. These paths are a deliberate, mechanically reproducible redraw of
# concept 01: two architectural planes, a fitted floor and one precision-cut
# orange edge. No bitmap tracing is used.
LEFT_PATH = (
    "M20 66C20 40 42 20 70 20L168 24L112 78V176L30 216"
    "C24 212 20 204 20 196Z"
)

RIGHT_PATH = (
    "M154 82L222 52Q228 50 228 58V198Q228 208 217 216L154 181Z"
)

FLOOR_PATH = (
    "M36 220L117 177Q120 175 123 177L210 220Q203 230 187 230"
    "H58Q43 230 36 220Z"
)

ACCENT_PATH = "M118 75L214 29L227 32L124 82Z"

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
DEFAULT_FONT = Path("/usr/share/fonts/inter/InterVariable.ttf")
SELECTION_REFERENCE = (
    ROOT / "source" / "reference" / "metricreate-v3-concept-01-user-selection.png"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_font(path: Path, weight: int = 650) -> TTFont:
    font = TTFont(path)
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": weight}, inplace=False)
    return font


def raw_text(font: TTFont, text: str, tracking: float = -12.0):
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


def outlined_text(
    font: TTFont,
    text: str,
    *,
    target_width: float,
    x: float,
    y: float,
    fill: str,
    tracking: float = -12.0,
) -> str:
    glyph_set = font.getGlyphSet()
    placements, (x_min, _y_min, x_max, y_max) = raw_text(font, text, tracking)
    scale = target_width / (x_max - x_min)
    fragments: list[str] = []

    for glyph_name, cursor in placements:
        pen = SVGPathPen(glyph_set)
        transformed = TransformPen(
            pen,
            (
                scale,
                0,
                0,
                -scale,
                x + (cursor - x_min) * scale,
                y + y_max * scale,
            ),
        )
        glyph_set[glyph_name].draw(transformed)
        commands = pen.getCommands()
        if commands:
            fragments.append(
                f'<path d="{commands}" fill="{fill}" fill-rule="nonzero"/>'
            )
    return "".join(fragments)


def svg_document(view_box: str, body: str, title: str, description: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" '
        'role="img" aria-labelledby="title desc">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <desc id="desc">{description}</desc>\n'
        f'{body}\n'
        '</svg>\n'
    )


def canvas_body(width: int, height: int) -> str:
    return f'  <rect width="{width}" height="{height}" fill="{PALETTE["canvas"]}"/>'


def mark_body(*, monochrome: bool = False, transform: str | None = None) -> str:
    navy = PALETTE["navy"]
    teal = navy if monochrome else PALETTE["teal"]
    floor = navy if monochrome else PALETTE["offwhite"]
    orange = navy if monochrome else PALETTE["orange"]

    content = "\n".join(
        (
            f'    <path d="{LEFT_PATH}" fill="{navy}"/>',
            f'    <path d="{RIGHT_PATH}" fill="{teal}"/>',
            f'    <path d="{FLOOR_PATH}" fill="{floor}"/>',
            f'    <path d="{ACCENT_PATH}" fill="{orange}"/>',
        )
    )
    if transform:
        return f'  <g transform="{transform}">\n{content}\n  </g>'
    return f'  <g>\n{content}\n  </g>'


def write_svg(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def render_png(svg_path: Path, png_path: Path, width: int) -> None:
    subprocess.run(
        [
            "magick",
            "-background",
            "none",
            str(svg_path),
            "-resize",
            f"{width}x",
            "-strip",
            str(png_path),
        ],
        check=True,
    )


def build(font_path: Path) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    if not SELECTION_REFERENCE.is_file():
        raise FileNotFoundError(f"Selection reference not found: {SELECTION_REFERENCE}")
    font = load_font(font_path)
    description = (
        "Selected metriCreate v3 concept 01: a compact spatial enclosure with a "
        "rounded navy left plane, a precise teal right plane, a fitted off-white "
        "floor and one signal-orange upper cut, carried on a fixed dark field."
    )

    assets: dict[str, str] = {}
    assets["metricreate-mark-color.svg"] = svg_document(
        "0 0 248 240",
        f'{canvas_body(248, 240)}\n{mark_body()}',
        "metriCreate color mark on fixed dark field",
        description,
    )
    assets["metricreate-mark-color-transparent.svg"] = svg_document(
        "0 0 248 240",
        mark_body(),
        "metriCreate color mark on transparent background",
        "Transparent full-color version of the selected spatial enclosure mark, "
        "intended for dark or contrast-checked backgrounds.",
    )
    assets["metricreate-mark-mono.svg"] = svg_document(
        "0 0 248 240",
        mark_body(monochrome=True),
        "metriCreate monochrome mark",
        "Single-color version of the selected spatial enclosure mark.",
    )

    stacked_word_dark = outlined_text(
        font,
        "metriCreate",
        target_width=270,
        x=45,
        y=282,
        fill=PALETTE["offwhite"],
    )
    stacked_word_mono = outlined_text(
        font,
        "metriCreate",
        target_width=270,
        x=45,
        y=282,
        fill=PALETTE["navy"],
    )
    stacked_mark = mark_body(transform="translate(56 4)")
    assets["metricreate-lockup-stacked-color-dark.svg"] = svg_document(
        "0 0 360 360",
        f'{canvas_body(360, 360)}\n{stacked_mark}\n  <g>{stacked_word_dark}</g>',
        "metriCreate stacked color logo on fixed dark field",
        description,
    )
    assets["metricreate-lockup-stacked-color-transparent.svg"] = svg_document(
        "0 0 360 360",
        f'{stacked_mark}\n  <g>{stacked_word_dark}</g>',
        "metriCreate stacked color logo on transparent background",
        "Transparent full-color stacked logo with an off-white wordmark, "
        "intended for dark or contrast-checked backgrounds.",
    )
    assets["metricreate-lockup-stacked-mono.svg"] = svg_document(
        "0 0 360 360",
        f'{mark_body(monochrome=True, transform="translate(56 4)")}\n'
        f"  <g>{stacked_word_mono}</g>",
        "metriCreate stacked monochrome logo",
        "Single-color stacked version of the selected spatial enclosure logo.",
    )

    horizontal_word_dark = outlined_text(
        font,
        "metriCreate",
        target_width=365,
        x=255,
        y=82,
        fill=PALETTE["offwhite"],
    )
    horizontal_word_mono = outlined_text(
        font,
        "metriCreate",
        target_width=365,
        x=255,
        y=82,
        fill=PALETTE["navy"],
    )
    horizontal_mark = mark_body(transform="translate(18 8) scale(0.88)")
    assets["metricreate-lockup-horizontal-color-dark.svg"] = svg_document(
        "0 0 650 230",
        f'{canvas_body(650, 230)}\n{horizontal_mark}\n  <g>{horizontal_word_dark}</g>',
        "metriCreate horizontal color logo on fixed dark field",
        description,
    )
    assets["metricreate-lockup-horizontal-color-transparent.svg"] = svg_document(
        "0 0 650 230",
        f'{horizontal_mark}\n  <g>{horizontal_word_dark}</g>',
        "metriCreate horizontal color logo on transparent background",
        "Transparent full-color horizontal logo with an off-white wordmark, "
        "intended for dark or contrast-checked backgrounds.",
    )
    assets["metricreate-lockup-horizontal-mono.svg"] = svg_document(
        "0 0 650 230",
        f'{mark_body(monochrome=True, transform="translate(18 8) scale(0.88)")}\n'
        f"  <g>{horizontal_word_mono}</g>",
        "metriCreate horizontal monochrome logo",
        "Single-color horizontal version of the selected spatial enclosure logo.",
    )

    for filename, content in assets.items():
        write_svg(EXPORTS / filename, content)

    render_png(
        EXPORTS / "metricreate-lockup-stacked-color-dark.svg",
        EXPORTS / "metricreate-lockup-stacked-color-dark.png",
        1200,
    )
    render_png(
        EXPORTS / "metricreate-lockup-horizontal-color-dark.svg",
        EXPORTS / "metricreate-lockup-horizontal-color-dark.png",
        1600,
    )
    render_png(
        EXPORTS / "metricreate-mark-color.svg",
        EXPORTS / "metricreate-mark-color.png",
        768,
    )
    render_png(
        EXPORTS / "metricreate-lockup-stacked-color-transparent.svg",
        EXPORTS / "metricreate-lockup-stacked-color-transparent.png",
        1200,
    )
    render_png(
        EXPORTS / "metricreate-lockup-horizontal-color-transparent.svg",
        EXPORTS / "metricreate-lockup-horizontal-color-transparent.png",
        1600,
    )
    render_png(
        EXPORTS / "metricreate-mark-color-transparent.svg",
        EXPORTS / "metricreate-mark-color-transparent.png",
        768,
    )

    font_hash = sha256(font_path)
    provenance = {
        "asset_family": "metriCreate production logo",
        "revision": "MC-BRAND-001-R3",
        "status": "selected-vector-redraw-clearance-pending",
        "intended_rights_owner": "Stefan Junk Holding UG (haftungsbeschränkt)",
        "ownership_status": "to be confirmed in signed BRD-001 brand risk approval",
        "selected_by": "Stefan Junk",
        "selected_at": "2026-09-04",
        "selection": "metriCreate family evolution v3 concept 01",
        "supersedes": "MC-BRAND-001-R1 (v3 concept 04)",
        "superseded_asset_archive": "archive/MC-BRAND-001-R1",
        "concept_sheet": {
            "path": "../../logo-concepts/metricreate-metrimade-sibling-concepts-v3.png",
            "sha256": "821fc7fccab16f71db2b71d17f3d404848fc9c13f8648608d54f271da7e00f5b",
            "generator": "OpenAI built-in image generation",
        },
        "selection_reference": {
            "path": "source/reference/metricreate-v3-concept-01-user-selection.png",
            "sha256": sha256(SELECTION_REFERENCE),
            "role": "user-supplied isolated crop confirming v3 concept 01 selection",
        },
        "vector_redraw": {
            "method": "deterministic original SVG geometry and outlined wordmark",
            "source": "source/build_brand_assets.py",
            "designer_operator": "OpenAI Codex under Stefan Junk's direction",
            "note": "The selected raster concept is a form reference only; no bitmap tracing is used.",
        },
        "background_policy": {
            "default_color_assets": "fixed embedded #0B0F12 field",
            "transparent_color_assets": (
                "full-color geometry with transparent canvas; off-white wordmark "
                "in lockups; use only on dark or contrast-checked backgrounds"
            ),
            "light_background_fallback": "corresponding monochrome navy SVG",
        },
        "font": {
            "family": "Inter Variable",
            "weight": 650,
            "source_path_at_build": str(font_path),
            "sha256": font_hash,
            "copyright": "Copyright 2016 The Inter Project Authors",
            "license": "SIL Open Font License 1.1",
            "runtime_dependency": False,
            "note": "All wordmark glyphs are converted to paths; the font file is not bundled.",
        },
        "palette": PALETTE,
        "clearance_limit": "Selection and source provenance do not replace name/device-mark and similarity clearance.",
    }
    (ROOT / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest_files = sorted(EXPORTS.glob("*")) + [
        ROOT / "provenance.json",
        SELECTION_REFERENCE,
        Path(__file__),
    ]
    lines = [
        f"{sha256(path)}  {path.relative_to(ROOT)}"
        for path in manifest_files
        if path.is_file()
    ]
    (ROOT / "manifest.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    args = parser.parse_args()
    if not args.font.is_file():
        raise SystemExit(f"Inter font not found: {args.font}")
    build(args.font.resolve())


if __name__ == "__main__":
    main()
