#!/usr/bin/env python3
"""NameForm Split-Pair Bookends — MM-PER-001 — revision 0.3.0.

CadQuery B-Rep source of truth. Units are millimetres.

Coordinate convention for an assembled pair:
    X  book-row direction, left to right from the front
    Y  shelf depth, positive away from the front viewer
    Z  up, with the print-bed datum at z=0

The left part has an inward foot along +X and an outward text wing along -X.
The right part has an inward foot along -X and an outward text wing along +X.
Only the structural geometry is mirrored. Text always reads normally from -Y.

The same source builds an unmarked engineering master or, with ``watermark``,
the marked DRAFT candidate. The mandatory product-specific mark is kept as the
last planned solid-geometry operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nameform-matplotlib")
)

import cadquery as cq
from fontTools.ttLib import TTFont
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
import shapely
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon


REVISION = "0.3.0"
PRODUCT_ID = "MM-PER-001"
HERE = Path(__file__).resolve().parent
FONT_PATH = HERE / "assets" / "fonts" / "DejaVuSansCondensed-Bold.ttf"
FONT_LICENSE = HERE / "assets" / "fonts" / "LICENSE-DejaVu.txt"
PROJECT_ROOT = HERE.parents[1]
WATERMARK_DIR = (
    PROJECT_ROOT / "assets" / "metrimade-watermark" / "generated"
    / "MM-PER-001_v0.3.0"
)
WATERMARK_DXF = WATERMARK_DIR / "metrimade-watermark-MM-PER-001-v0.3.0.dxf"
WATERMARK_METADATA = WATERMARK_DIR / "metrimade-watermark-MM-PER-001-v0.3.0.json"
WATERMARK_DEPTH = 0.4
WATERMARK_OVERLAP = 0.01
WATERMARK_ROTATION_DEG = 90.0

# Approved geometry contract.
TOTAL_H = 160.0
SIDE_DEPTH = 115.0
WING_W = 125.0
WING_H = 100.0
FOOT_L = 70.0
PLATE_T = 3.2
FOOT_T = 2.0
FOOT_TIP_T = 0.6
FOOT_TAPER_L = 15.0
RIB_T = 2.4
RIB_PROJECTION = 6.0
WING_CORNER_R = 4.0
TEXT_EDGE_MARGIN_X = 8.0
TEXT_EDGE_MARGIN_Z = 10.0
TEXT_RAISE = 2.0
TEXT_BOOLEAN_OVERLAP = 0.10
GUSSET_X = 20.0
GUSSET_Z = 30.0
GUSSET_Y = 4.0
MESH_TOLERANCE = 0.05
MESH_ANGULAR_TOLERANCE = 0.35

SUPPORTED_EXTRAS = " -'ÄÖÜäöüẞß"
ALLOWED_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    + SUPPORTED_EXTRAS
)
DEFAULT_NAME = "STEFAN"


@dataclass(frozen=True)
class PairText:
    left: str
    right: str
    mode: str
    scale: float
    baseline_z: float
    left_unscaled_bounds: tuple[float, float, float, float]
    right_unscaled_bounds: tuple[float, float, float, float]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value.strip())
    while "  " in value:
        value = value.replace("  ", " ")
    if not value:
        raise ValueError("text must not be empty")
    return value


def _font() -> TTFont:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"bundled font missing: {FONT_PATH}")
    return TTFont(str(FONT_PATH))


def validate_glyphs(text: str) -> None:
    cmap = _font().getBestCmap()
    missing = [f"U+{ord(ch):04X} {ch!r}" for ch in text if ord(ch) not in cmap]
    if missing:
        raise ValueError("font lacks requested glyph(s): " + ", ".join(missing))
    for ch in text:
        if ch not in ALLOWED_CHARS:
            raise ValueError(f"unsupported character U+{ord(ch):04X} {ch!r}")


def _text_path(text: str) -> TextPath:
    validate_glyphs(text)
    return TextPath((0.0, 0.0), text, size=1.0,
                    prop=FontProperties(fname=str(FONT_PATH)))


def text_bounds(text: str) -> tuple[float, float, float, float]:
    bb = _text_path(text).get_extents()
    if not all(math.isfinite(v) for v in (bb.xmin, bb.ymin, bb.xmax, bb.ymax)):
        raise ValueError(f"non-finite text bounds for {text!r}")
    if bb.width <= 0 or bb.height <= 0:
        raise ValueError(f"empty text outline for {text!r}")
    return (float(bb.xmin), float(bb.ymin), float(bb.xmax), float(bb.ymax))


def _rendered_width(text: str) -> float:
    return text_bounds(text)[2] - text_bounds(text)[0]


def auto_split_name(name: str) -> tuple[str, str]:
    """Split at a character boundary to minimize the larger rendered half.

    A one-character name is intentionally repeated so a pair remains useful.
    Spaces adjacent to a split are removed from the visible halves.
    """
    name = normalize_text(name)
    validate_glyphs(name)
    if len(name) == 1:
        return name, name
    candidates: list[tuple[float, float, int, str, str]] = []
    for index in range(1, len(name)):
        left = name[:index].rstrip()
        right = name[index:].lstrip()
        if not left or not right:
            continue
        if right.startswith(("-", "'")) or left.endswith("'"):
            continue
        lw, rw = _rendered_width(left), _rendered_width(right)
        candidates.append((max(lw, rw), abs(lw - rw), index, left, right))
    if not candidates:
        raise ValueError(f"cannot split name {name!r} into two visible halves")
    _, _, _, left, right = min(candidates)
    return left, right


def pair_text(name: str = DEFAULT_NAME, left_text: str | None = None,
              right_text: str | None = None, same_on_both: bool = False) -> PairText:
    if same_on_both and (left_text is not None or right_text is not None):
        raise ValueError("same_on_both cannot be combined with explicit left/right text")
    if same_on_both:
        value = normalize_text(name)
        left, right, mode = value, value, "whole-name-each-side"
    elif left_text is not None or right_text is not None:
        if left_text is None or right_text is None:
            raise ValueError("explicit mode requires both left_text and right_text")
        left, right = normalize_text(left_text), normalize_text(right_text)
        mode = "explicit-pair"
    else:
        left, right = auto_split_name(name)
        mode = "split-name"
    validate_glyphs(left + right)

    lb = text_bounds(left)
    rb = text_bounds(right)
    max_w = max(lb[2] - lb[0], rb[2] - rb[0])
    global_ymin = min(lb[1], rb[1])
    global_ymax = max(lb[3], rb[3])
    max_h = global_ymax - global_ymin
    width_budget = WING_W - 2.0 * TEXT_EDGE_MARGIN_X
    height_budget = WING_H - 2.0 * TEXT_EDGE_MARGIN_Z
    scale = min(width_budget / max_w, height_budget / max_h)
    if scale <= 0:
        raise AssertionError("computed non-positive text scale")
    baseline_z = (WING_H - scale * (global_ymax + global_ymin)) / 2.0

    # Conservative printability proxy: the condensed bold font is accepted only
    # above a cap-height floor; exact thin-wall behavior remains a slicer gate.
    cap_height = scale * max_h
    if cap_height < 18.0:
        raise ValueError(
            f"text pair {left!r} | {right!r} is too small: "
            f"outline height {cap_height:.2f} mm < 18.0 mm"
        )
    return PairText(left, right, mode, scale, baseline_z, lb, rb)


def _polygonal_text(text: str) -> Polygon | MultiPolygon:
    """Convert Matplotlib's closed outline contours with even/odd fill.

    Symmetric difference implements the font outline's nested-contour parity,
    preserving counters in B, D, O, P, Q, R and multi-contour Unicode glyphs.
    """
    paths = _text_path(text).to_polygons(closed_only=True)
    contours: list[Polygon] = []
    for points in paths:
        if len(points) < 4:
            continue
        poly = Polygon(points)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if not poly.is_empty and poly.area > 1e-10:
            contours.append(poly)
    if not contours:
        raise ValueError(f"no closed font contours for {text!r}")
    result = GeometryCollection()
    for poly in sorted(contours, key=lambda item: item.area, reverse=True):
        result = result.symmetric_difference(poly)
    result = result.buffer(0)
    if isinstance(result, Polygon):
        return result
    if isinstance(result, MultiPolygon):
        return result
    polys = [g for g in getattr(result, "geoms", []) if isinstance(g, Polygon)]
    if not polys:
        raise ValueError(f"font outline did not resolve to polygons for {text!r}")
    return MultiPolygon(polys)


def _wire_xy(coords: Iterable[tuple[float, float]], z: float = 0.0) -> cq.Wire:
    points = [(float(x), float(y), z) for x, y in coords]
    if points[0] != points[-1]:
        points.append(points[0])
    return cq.Wire.makePolygon(points)


def _prism_z(face: cq.Face, depth: float) -> cq.Solid:
    maker = BRepPrimAPI_MakePrism(face.wrapped, gp_Vec(0.0, 0.0, depth), True)
    return cq.Solid(maker.Shape())


def _prism_y(face: cq.Face, depth: float) -> cq.Solid:
    maker = BRepPrimAPI_MakePrism(face.wrapped, gp_Vec(0.0, depth, 0.0), True)
    return cq.Solid(maker.Shape())


def _face_from_polygon_xy(poly: Polygon) -> cq.Face:
    outer = _wire_xy(poly.exterior.coords)
    holes = [_wire_xy(ring.coords) for ring in poly.interiors]
    return cq.Face.makeFromWires(outer, holes)


def text_solid(text: str, scale: float, center_x: float,
               baseline_z: float) -> cq.Shape:
    geometry = _polygonal_text(text)
    polys = [geometry] if isinstance(geometry, Polygon) else list(geometry.geoms)
    raw = text_bounds(text)
    center_unscaled = (raw[0] + raw[2]) / 2.0
    solids: list[cq.Solid] = []
    for poly in polys:
        shifted = shapely.affinity.translate(poly, xoff=-center_unscaled)
        shifted = shapely.affinity.scale(shifted, xfact=scale, yfact=scale,
                                         origin=(0.0, 0.0))
        solid = _prism_z(_face_from_polygon_xy(shifted),
                         TEXT_RAISE + TEXT_BOOLEAN_OVERLAP)
        # +Z extrusion becomes -Y; the original +Z-readable outline therefore
        # remains normally readable from the front viewer at -Y.
        solid = solid.rotate((0, 0, 0), (1, 0, 0), 90)
        solid = solid.translate((center_x, TEXT_BOOLEAN_OVERLAP, baseline_z))
        solids.append(solid)
    return cq.Compound.makeCompound(solids)


def _face_xz(points: list[tuple[float, float]], y: float = 0.0) -> cq.Face:
    pts = [(float(x), y, float(z)) for x, z in points]
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    return cq.Face.makeFromWires(cq.Wire.makePolygon(pts))


def _tri_prism_xz(points: list[tuple[float, float]], y0: float,
                  depth: float) -> cq.Solid:
    return _prism_y(_face_xz(points, y0), depth)


def _rounded_wing(inward: int) -> cq.Shape:
    x0, x1 = ((-WING_W, 0.0) if inward == 1 else (0.0, WING_W))
    outline = shapely.box(x0, 0.0, x1, WING_H)
    outline = outline.buffer(-WING_CORNER_R).buffer(WING_CORNER_R)
    if not isinstance(outline, Polygon):
        raise AssertionError("rounded wing outline is not a polygon")
    coords = [(x, z) for x, z in outline.exterior.coords]
    face = _face_xz(coords, 0.0)
    return _prism_y(face, PLATE_T)


def _foot_shape(inward: int) -> cq.Shape:
    full_end = FOOT_L - FOOT_TAPER_L
    if inward == 1:
        points = [(0.0, 0.0), (FOOT_L, 0.0), (FOOT_L, FOOT_TIP_T),
                  (full_end, FOOT_T), (0.0, FOOT_T)]
    else:
        points = [(0.0, 0.0), (-FOOT_L, 0.0), (-FOOT_L, FOOT_TIP_T),
                  (-full_end, FOOT_T), (0.0, FOOT_T)]
    return _prism_y(_face_xz(points, 0.0), SIDE_DEPTH)


@lru_cache(maxsize=1)
def watermark_cutter_centered() -> cq.Shape:
    """Exact generated MM-WM-001-R1 DXF, mirrored for underside reading.

    The selector requires rotation 90 degrees and uniform scale 1.0. The
    cutter is centered after those immutable transforms and spans
    z=[-overlap, depth].
    """
    if not WATERMARK_DXF.is_file() or not WATERMARK_METADATA.is_file():
        raise FileNotFoundError("generated metriMade watermark profile is missing")
    metadata = json.loads(WATERMARK_METADATA.read_text())
    if (metadata.get("asset_revision"), metadata.get("product_id"), metadata.get("version")) != (
        "MM-WM-001-R1", PRODUCT_ID, REVISION
    ):
        raise ValueError("watermark metadata identity does not match the product revision")
    imported = cq.importers.importDXF(str(WATERMARK_DXF))
    solids = imported.extrude(WATERMARK_DEPTH + WATERMARK_OVERLAP,
                              combine=False).solids().vals()
    if len(solids) != 34:
        raise AssertionError(f"expected 34 watermark solids, got {len(solids)}")
    compound = cq.Compound.makeCompound(solids)
    compound = compound.mirror("YZ")
    compound = compound.rotate((0, 0, 0), (0, 0, 1), WATERMARK_ROTATION_DEG)
    bb = compound.BoundingBox()
    compound = compound.translate((-(bb.xmin + bb.xmax) / 2.0,
                                   -(bb.ymin + bb.ymax) / 2.0,
                                   -WATERMARK_OVERLAP))
    bb = compound.BoundingBox()
    expected_volume = float(metadata["digital_validation"]["cutter"]["volume_mm3"])
    expected_area = expected_volume / WATERMARK_DEPTH
    actual_area = compound.Volume() / (WATERMARK_DEPTH + WATERMARK_OVERLAP)
    if abs(actual_area - expected_area) > 0.05:
        raise AssertionError("DXF cutter section does not match generated metadata")
    if abs(bb.xlen - 11.200012) > 0.02 or abs(bb.ylen - 62.039212) > 0.02:
        raise AssertionError(f"unexpected rotated watermark envelope {bb.xlen} x {bb.ylen}")
    return compound


def apply_watermark(part: cq.Workplane, side: str) -> cq.Workplane:
    """Cut the exact mark into the center of the inward-foot underside."""
    center_x = FOOT_L / 2.0 if side == "left" else -FOOT_L / 2.0
    center_y = SIDE_DEPTH / 2.0
    cutter = watermark_cutter_centered().translate((center_x, center_y, 0.0))
    result = part.cut(cq.Workplane("XY").newObject([cutter]))
    solids = result.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError(f"{side}: watermark cut broke the primary body")
    bb = solids[0].BoundingBox()
    if abs(bb.zmin) > 1e-6:
        raise AssertionError(f"{side}: watermark changed bed datum to {bb.zmin}")
    return result


def build_side(side: str, text: str, text_plan: PairText,
               watermark: bool = False) -> cq.Workplane:
    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    inward = 1 if side == "left" else -1
    outward = -inward

    side_blade = (cq.Workplane("XY")
                  .box(PLATE_T, SIDE_DEPTH, TOTAL_H, centered=(True, False, False))
                  .translate((0.0, 0.0, 0.0)))
    foot = cq.Workplane("XY").newObject([_foot_shape(inward)])
    wing = cq.Workplane("XY").newObject([_rounded_wing(inward)])

    part = side_blade.union(foot).union(wing)

    # Continuous bed-rooted outside ribs preserve the book-contact face on the
    # inward side and avoid unsupported horizontal rib shelves.
    rib_x = outward * (PLATE_T / 2.0 + RIB_PROJECTION / 2.0)
    for y in (28.0, 56.0, 84.0, SIDE_DEPTH - RIB_T):
        vertical_rib = (cq.Workplane("XY")
                        .box(RIB_PROJECTION, RIB_T, TOTAL_H,
                             centered=(True, False, False))
                        .translate((rib_x, y, 0.0)))
        part = part.union(vertical_rib)

    # Two self-supporting outside gussets tie the blade to a small outside toe.
    tri = [(0.0, 0.0), (outward * GUSSET_X, 0.0), (0.0, GUSSET_Z)]
    for y0 in (PLATE_T, SIDE_DEPTH - GUSSET_Y):
        part = part.union(cq.Workplane("XY").newObject([
            _tri_prism_xz(tri, y0, GUSSET_Y)
        ]))

    center_x = outward * WING_W / 2.0
    letters = text_solid(text, text_plan.scale, center_x,
                         text_plan.baseline_z)
    part = part.union(cq.Workplane("XY").newObject([letters]))

    if watermark:
        part = apply_watermark(part, side)

    solids = part.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError(f"{side}: expected one non-null solid, got {len(solids)}")
    bb = solids[0].BoundingBox()
    expected_x = WING_W + FOOT_L
    checks = [
        (abs(bb.xlen - expected_x) <= 0.05,
         f"{side}: x envelope {bb.xlen:.3f} != {expected_x:.3f}"),
        (bb.ymin >= -TEXT_RAISE - 0.02,
         f"{side}: text front {bb.ymin:.3f} exceeds relief"),
        (bb.ymax <= SIDE_DEPTH + 0.02,
         f"{side}: depth {bb.ymax:.3f} exceeds {SIDE_DEPTH}"),
        (abs(bb.zmin) <= 1e-6, f"{side}: bed datum {bb.zmin:.6f}"),
        (abs(bb.zmax - TOTAL_H) <= 1e-6,
         f"{side}: height {bb.zmax:.6f} != {TOTAL_H}"),
    ]
    for ok, message in checks:
        if not ok:
            raise AssertionError(message)
    return part


def build_pair(name: str = DEFAULT_NAME, left_text: str | None = None,
               right_text: str | None = None,
               same_on_both: bool = False,
               watermark: bool = False) -> tuple[cq.Workplane, cq.Workplane, PairText]:
    plan = pair_text(name, left_text, right_text, same_on_both)
    left = build_side("left", plan.left, plan, watermark=watermark)
    right = build_side("right", plan.right, plan, watermark=watermark)
    return left, right, plan


def export_step(part: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(part, str(path))
    _normalize_step_header(path)


def export_stl(part: cq.Workplane, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(part, str(path), tolerance=MESH_TOLERANCE,
                        angularTolerance=MESH_ANGULAR_TOLERANCE)


def export_assembly(left: cq.Workplane, right: cq.Workplane, gap: float,
                    path: Path) -> None:
    assembly = cq.Assembly(name=f"NameForm-{PRODUCT_ID}-{REVISION}")
    assembly.add(left, name="left", loc=cq.Location(cq.Vector(-gap / 2.0, 0, 0)))
    assembly.add(right, name="right", loc=cq.Location(cq.Vector(gap / 2.0, 0, 0)))
    path.parent.mkdir(parents=True, exist_ok=True)
    assembly.save(str(path), exportType="STEP", mode="default")
    _normalize_step_header(path)


def _normalize_step_header(path: Path) -> None:
    """Remove the Open CASCADE wall-clock field from an otherwise stable STEP."""
    source = path.read_text(encoding="utf-8")
    normalized, replacements = re.subn(
        r"(FILE_NAME\('Open CASCADE Shape Model',)'[^']*'",
        r"\g<1>'1980-01-01T00:00:00'",
        source,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError(f"could not normalize STEP timestamp in {path}")
    path.write_text(normalized, encoding="utf-8", newline="\n")


def report(left: cq.Workplane, right: cq.Workplane, plan: PairText) -> dict:
    def body(item: cq.Workplane) -> dict:
        solid = item.val()
        bb = solid.BoundingBox()
        return {
            "bbox_mm": [bb.xlen, bb.ylen, bb.zlen],
            "volume_cm3": solid.Volume() / 1000.0,
            "mass_g_at_1_24": solid.Volume() / 1000.0 * 1.24,
            "center_of_mass_mm": [solid.Center().x, solid.Center().y, solid.Center().z],
            "solids": len(item.solids().vals()),
        }
    return {
        "product_id": PRODUCT_ID,
        "revision": REVISION,
        "font": str(FONT_PATH.relative_to(HERE)),
        "font_sha256": sha256(FONT_PATH),
        "text": asdict(plan),
        "left": body(left),
        "right": body(right),
        "pair_mass_g_at_1_24": body(left)["mass_g_at_1_24"] + body(right)["mass_g_at_1_24"],
        "mesh_tolerance_mm": MESH_TOLERANCE,
        "mesh_angular_tolerance_rad": MESH_ANGULAR_TOLERANCE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--left-text")
    parser.add_argument("--right-text")
    parser.add_argument("--same-on-both", action="store_true")
    parser.add_argument("--watermark", action="store_true")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--assembly-gap", type=float, default=240.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    left, right, plan = build_pair(args.name, args.left_text, args.right_text,
                                   args.same_on_both, watermark=args.watermark)
    slug = "-".join((plan.left.replace(" ", "_"), plan.right.replace(" ", "_")))
    export_step(left, args.out_dir / f"nameform-{slug}-left.step")
    export_step(right, args.out_dir / f"nameform-{slug}-right.step")
    export_stl(left, args.out_dir / f"nameform-{slug}-left.stl")
    export_stl(right, args.out_dir / f"nameform-{slug}-right.stl")
    export_assembly(left, right, args.assembly_gap,
                    args.out_dir / f"nameform-{slug}-assembly.step")
    payload = report(left, right, plan)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
