#!/usr/bin/env python3
"""Build deterministic metriMade logo assets from the selected V10 concept 08."""

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
    "navy": "#112431",
    "teal": "#08777D",
    "aqua": "#7FD5D3",
    "sand": "#C7AB82",
    "canvas": "#FBFAF7",
}

MARK_PATHS = (
    # Left/top spatial plane.
    ("navy", "M8 221C2 213 0 202 0 190V62C0 27 27 0 61 0H157C168 0 177 4 184 11L91 71V174L8 221Z"),
    # Right spatial plane.
    ("teal", "M132 70L195 36V191C195 207 191 217 182 226L132 193V70Z"),
    # Restrained inner-edge strip from V10 concept 08.
    ("aqua", "M132 184L188 218C186 221 184 224 182 226L132 194V184Z"),
    # Warm fitted floor, drawn last so the aqua remains a narrow edge.
    ("sand", "M18 230L92 184L174 231C164 237 154 238 142 238H44C33 238 24 235 18 230Z"),
)

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
DEFAULT_FONT = Path("/usr/share/fonts/inter/InterVariable.ttf")


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
) -> tuple[str, float]:
    """Return font outlines placed at x/y with a fixed visual width."""
    glyph_set = font.getGlyphSet()
    placements, (x_min, y_min, x_max, y_max) = raw_text(font, text, tracking)
    scale = target_width / (x_max - x_min)
    visual_height = (y_max - y_min) * scale
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
    return "".join(fragments), visual_height


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


def mark_body(*, monochrome: bool = False, transform: str | None = None) -> str:
    paths = []
    for color_name, path in MARK_PATHS:
        fill = PALETTE["navy"] if monochrome else PALETTE[color_name]
        paths.append(f'    <path d="{path}" fill="{fill}"/>')
    content = "\n".join(paths)
    if transform:
        return f'  <g transform="{transform}">\n{content}\n  </g>'
    return f'  <g>\n{content}\n  </g>'


def write_svg(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def render_png(svg_path: Path, png_path: Path, width: int) -> None:
    subprocess.run(
        ["magick", "-background", "none", str(svg_path), "-resize", f"{width}x", str(png_path)],
        check=True,
    )


def build(font_path: Path) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    font = load_font(font_path)

    description = (
        "Selected V10 concept 08: spatial M with navy and teal planes, "
        "a fitted sand floor, and a restrained aqua inner edge."
    )

    assets: dict[str, str] = {}
    assets["metrimade-mark-color.svg"] = svg_document(
        "0 0 195 238",
        mark_body(),
        "metriMade color mark",
        description,
    )
    assets["metrimade-mark-mono.svg"] = svg_document(
        "0 0 195 238",
        mark_body(monochrome=True),
        "metriMade monochrome mark",
        "Single-color version of the selected spatial M mark.",
    )

    stacked_word, _ = outlined_text(
        font,
        "metriMade",
        target_width=285,
        x=17.5,
        y=286,
        fill=PALETTE["navy"],
    )
    stacked_mark = mark_body(transform="translate(72.5 12) scale(0.8974)")
    assets["metrimade-lockup-stacked-color.svg"] = svg_document(
        "0 0 340 360",
        f"{stacked_mark}\n  <g>{stacked_word}</g>",
        "metriMade stacked color logo",
        description,
    )
    stacked_word_mono, _ = outlined_text(
        font,
        "metriMade",
        target_width=285,
        x=17.5,
        y=286,
        fill=PALETTE["navy"],
    )
    assets["metrimade-lockup-stacked-mono.svg"] = svg_document(
        "0 0 340 360",
        f'{mark_body(monochrome=True, transform="translate(72.5 12) scale(0.8974)")}\n'
        f"  <g>{stacked_word_mono}</g>",
        "metriMade stacked monochrome logo",
        "Single-color stacked version of the selected spatial M logo.",
    )

    horizontal_word, _ = outlined_text(
        font,
        "metriMade",
        target_width=345,
        x=235,
        y=82,
        fill=PALETTE["navy"],
    )
    horizontal_mark = mark_body(transform="translate(22 9) scale(0.82)")
    assets["metrimade-lockup-horizontal-color.svg"] = svg_document(
        "0 0 610 214",
        f"{horizontal_mark}\n  <g>{horizontal_word}</g>",
        "metriMade horizontal color logo",
        description,
    )
    assets["metrimade-lockup-horizontal-mono.svg"] = svg_document(
        "0 0 610 214",
        f'{mark_body(monochrome=True, transform="translate(22 9) scale(0.82)")}\n'
        f"  <g>{horizontal_word}</g>",
        "metriMade horizontal monochrome logo",
        "Single-color horizontal version of the selected spatial M logo.",
    )

    for filename, content in assets.items():
        write_svg(EXPORTS / filename, content)

    render_png(EXPORTS / "metrimade-lockup-stacked-color.svg", EXPORTS / "metrimade-lockup-stacked-color.png", 1200)
    render_png(EXPORTS / "metrimade-lockup-horizontal-color.svg", EXPORTS / "metrimade-lockup-horizontal-color.png", 1600)
    render_png(EXPORTS / "metrimade-mark-color.svg", EXPORTS / "metrimade-mark-color.png", 768)

    font_hash = sha256(font_path)
    provenance = {
        "asset_family": "metriMade production logo",
        "revision": "MM-BRAND-001-R1",
        "status": "selected-vector-redraw-clearance-pending",
        "intended_rights_owner": "Stefan Junk Holding UG (haftungsbeschränkt)",
        "ownership_status": "to be confirmed in signed BRD-001 brand risk approval",
        "selected_by": "Stefan Junk",
        "selected_at": "2026-08-25",
        "selection": "V10 concept 08",
        "concept_sheet": {
            "path": "../../logo-concepts/metrimade-v7-04-four-color-variations-v10.png",
            "sha256": "9baf6e78a2ae2600861078752e890c464a7b923d95fbba520a857deb26f16d00",
            "generator": "OpenAI built-in image generation",
        },
        "vector_redraw": {
            "method": "deterministic original SVG geometry and outlined wordmark",
            "source": "source/build_brand_assets.py",
            "designer_operator": "OpenAI Codex under Stefan Junk's direction",
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

    manifest_files = sorted(EXPORTS.glob("*")) + [ROOT / "provenance.json", Path(__file__)]
    lines = [f"{sha256(path)}  {path.relative_to(ROOT)}" for path in manifest_files if path.is_file()]
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
