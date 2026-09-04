#!/usr/bin/env python3
"""Build non-binding metriCreate background and light-ground logo candidates."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "candidates" / "r2-background-light-ground"
PRODUCTION_BUILDER = Path(__file__).with_name("build_brand_assets.py")
DEFAULT_FONT = Path("/usr/share/fonts/inter/InterVariable.ttf")


def load_production_builder():
    spec = importlib.util.spec_from_file_location(
        "metricreate_production_brand_builder", PRODUCTION_BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {PRODUCTION_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRODUCTION = load_production_builder()
PALETTE = PRODUCTION.PALETTE

# Pin the superseded R1 voxel geometry so this historical R2 study remains
# reproducible after the binding production builder moves to v3 concept 01.
VOXEL_LEFT_PATH = (
    "M20 70L72 38V54H90V70H108V86H120V96V150L82 124V204L64 220H20V170H40V150H20Z"
    "M40 100H58V118H40Z"
    "M58 130H76V148H58Z"
    "M40 160H58V178H40Z"
)
VOXEL_RIGHT_PATH = (
    "M120 96H138V78H156V60H174V42H192V58H210V76H228V94H210V112H228V130H210V148"
    "H228V184H210V202H228V220H210L176 204V124L120 150Z"
)
VOXEL_FLOOR_PATH = "M38 220L120 174L204 220L196 228H46Z"


@dataclass(frozen=True)
class Candidate:
    number: str
    slug: str
    label: str
    series: str
    carrier: str
    floor: str
    active: str = PALETTE["orange"]
    floor_stroke: str | None = None
    threshold: str | None = None


CANDIDATES = (
    Candidate("01", "midnight-square", "SQUARE", "carrier", "square", PALETTE["offwhite"]),
    Candidate("02", "midnight-rounded", "ROUNDED", "carrier", "rounded", PALETTE["offwhite"]),
    Candidate("03", "midnight-circle", "CIRCLE", "carrier", "circle", PALETTE["offwhite"]),
    Candidate("04", "midnight-voxel-tile", "VOXEL TILE", "carrier", "voxel", PALETTE["offwhite"]),
    Candidate(
        "05",
        "white-floor-keyline",
        "WHITE FLOOR + KEYLINE",
        "light",
        "light",
        PALETTE["offwhite"],
        floor_stroke=PALETTE["navy"],
    ),
    Candidate("06", "aqua-floor", "AQUA FLOOR", "light", "light", PALETTE["aqua"]),
    Candidate(
        "07",
        "orange-floor",
        "ORANGE FLOOR",
        "light",
        "light",
        PALETTE["orange"],
        active=PALETTE["navy"],
    ),
    Candidate(
        "08",
        "white-floor-aqua-threshold",
        "WHITE FLOOR + AQUA THRESHOLD",
        "light",
        "light",
        PALETTE["offwhite"],
        floor_stroke=PALETTE["navy"],
        threshold=PALETTE["aqua"],
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def carrier_body(kind: str) -> str:
    canvas = PALETTE["canvas"]
    if kind == "square":
        return f'<rect x="20" y="20" width="520" height="520" fill="{canvas}"/>'
    if kind == "rounded":
        return (
            f'<rect x="20" y="20" width="520" height="520" rx="76" '
            f'fill="{canvas}"/>'
        )
    if kind == "circle":
        return f'<circle cx="280" cy="280" r="260" fill="{canvas}"/>'
    if kind == "voxel":
        return (
            f'<path d="M64 20H496V64H540V496H496V540H64V496H20V64H64Z" '
            f'fill="{canvas}"/>'
        )
    if kind == "light":
        return (
            '<rect x="20" y="20" width="520" height="520" rx="30" '
            'fill="#FFFFFF" stroke="#D9E3E5" stroke-width="3"/>'
        )
    raise ValueError(f"Unknown carrier kind: {kind}")


def mark_body(candidate: Candidate, transform: str) -> str:
    floor_outline = ""
    if candidate.floor_stroke:
        floor_outline = (
            f' stroke="{candidate.floor_stroke}" stroke-width="5" '
            'stroke-linejoin="round"'
        )
    threshold = ""
    if candidate.threshold:
        threshold = (
            f'    <path d="{VOXEL_FLOOR_PATH}" transform="translate(0 10)" '
            f'fill="{candidate.threshold}" stroke="{PALETTE["navy"]}" '
            'stroke-width="4" stroke-linejoin="round"/>\n'
        )

    content = "\n".join(
        (
            f'    <path d="{VOXEL_LEFT_PATH}" fill="{PALETTE["navy"]}" fill-rule="evenodd"/>',
            f'    <path d="{VOXEL_RIGHT_PATH}" fill="{PALETTE["teal"]}"/>',
            f'    <rect x="184" y="16" width="18" height="18" fill="{PALETTE["aqua"]}"/>',
            f'    <rect x="188" y="184" width="18" height="18" fill="{PALETTE["aqua"]}"/>',
            f'    <rect x="206" y="184" width="18" height="18" fill="{PALETTE["navy"]}"/>',
            threshold.rstrip(),
            f'    <path d="{VOXEL_FLOOR_PATH}" fill="{candidate.floor}"{floor_outline}/>',
            f'    <rect x="110" y="211" width="20" height="18" fill="{candidate.active}"/>',
        )
    )
    return f'  <g transform="{transform}">\n{content}\n  </g>'


def candidate_body(candidate: Candidate, font) -> str:
    word_color = PALETTE["offwhite"] if candidate.series == "carrier" else PALETTE["navy"]
    word_width = 270 if candidate.carrier == "circle" else 404
    word_x = 145 if candidate.carrier == "circle" else 78
    wordmark = PRODUCTION.outlined_text(
        font,
        "metriCreate",
        target_width=word_width,
        x=word_x,
        y=456,
        fill=word_color,
    )
    return "\n".join(
        (
            carrier_body(candidate.carrier),
            mark_body(candidate, "translate(119 56) scale(1.30)"),
            f"  <g>{wordmark}</g>",
        )
    )


def individual_svg(candidate: Candidate, font) -> str:
    return PRODUCTION.svg_document(
        "0 0 560 560",
        candidate_body(candidate, font),
        f"metriCreate candidate {candidate.number}: {candidate.label.title()}",
        (
            "Non-binding MC-BRAND-001-R2 exploration preserving the selected "
            "M geometry while testing a fixed carrier or a light-ground palette."
        ),
    )


def sheet_svg(font) -> str:
    width = 1920
    height = 1280
    cell_width = 438
    card_height = 486
    gap = 26
    left = 58
    top_rows = (170, 744)
    parts = [
        '<rect width="1920" height="1280" fill="#EEF2F3"/>',
        (
            '<text x="58" y="64" font-family="Inter, sans-serif" font-size="34" '
            'font-weight="700" fill="#112431">metriCreate — background &amp; light-ground study</text>'
        ),
        (
            '<text x="58" y="104" font-family="Inter, sans-serif" font-size="18" '
            'fill="#47616C">MC-BRAND-001-R2 candidates · selected M geometry unchanged</text>'
        ),
        (
            '<text x="58" y="150" font-family="Inter, sans-serif" font-size="20" '
            'font-weight="700" letter-spacing="2" fill="#08777D">A · FIXED MIDNIGHT CARRIER</text>'
        ),
        (
            '<text x="58" y="724" font-family="Inter, sans-serif" font-size="20" '
            'font-weight="700" letter-spacing="2" fill="#08777D">B · LIGHT / WHITE GROUND</text>'
        ),
    ]

    for index, candidate in enumerate(CANDIDATES):
        row = 0 if index < 4 else 1
        col = index % 4
        x = left + col * (cell_width + gap)
        y = top_rows[row]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_width}" height="{card_height}" '
            'rx="22" fill="#FFFFFF" stroke="#D4DEE0" stroke-width="2"/>'
        )
        parts.append(
            f'<g transform="translate({x + 23} {y + 12}) scale(0.70)">'
            f'{candidate_body(candidate, font)}</g>'
        )
        parts.append(
            f'<text x="{x + 22}" y="{y + 456}" font-family="Inter, sans-serif" '
            f'font-size="17" font-weight="700" fill="#112431">{candidate.number} · {candidate.label}</text>'
        )

    parts.append(
        '<text x="58" y="1260" font-family="Inter, sans-serif" font-size="15" '
        'fill="#607780">Review sheet only · SVG candidates are deterministic and non-binding</text>'
    )
    return PRODUCTION.svg_document(
        f"0 0 {width} {height}",
        "\n".join(parts),
        "metriCreate background and light-ground candidate sheet",
        "Eight non-binding variants in two rows: fixed dark carriers and white-ground color treatments.",
    )


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


def build() -> None:
    if not DEFAULT_FONT.is_file():
        raise SystemExit(f"Inter font not found: {DEFAULT_FONT}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    font = PRODUCTION.load_font(DEFAULT_FONT)

    generated: list[Path] = []
    for candidate in CANDIDATES:
        basename = f"metricreate-{candidate.number}-{candidate.slug}"
        svg_path = OUTPUT / f"{basename}.svg"
        png_path = OUTPUT / f"{basename}.png"
        svg_path.write_text(individual_svg(candidate, font), encoding="utf-8")
        render_png(svg_path, png_path, 840)
        generated.extend((svg_path, png_path))

    sheet_svg_path = OUTPUT / "metricreate-background-light-ground-study.svg"
    sheet_png_path = OUTPUT / "metricreate-background-light-ground-study.png"
    sheet_svg_path.write_text(sheet_svg(font), encoding="utf-8")
    render_png(sheet_svg_path, sheet_png_path, 1920)
    generated.extend((sheet_svg_path, sheet_png_path))

    manifest_paths = sorted(generated) + [OUTPUT / "README.md", Path(__file__)]
    lines = [
        f"{sha256(path)}  {os.path.relpath(path, OUTPUT)}"
        for path in manifest_paths
    ]
    (OUTPUT / "manifest.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
