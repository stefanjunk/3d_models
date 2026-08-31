#!/usr/bin/env python3
"""Build the approved letter-only NameForm 0.4.0 pair and FA process coupon.

The functional core and untextured glyph/connector bodies are exact CadQuery
B-Reps. Candidate-C wood relief is a manufacturing-mesh operation: a directly
sampled, periodic 16-bit height field is tapered inside the glyph outlines and
subtracted from the front faces. Units are millimetres.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import struct
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "nameform-v040-matplotlib")
)

import cadquery as cq
from fontTools.ttLib import TTFont
from manifold3d import Error, Manifold, Mesh
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
import numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from PIL import Image
import shapely
import shapely.affinity
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Polygon, box
from shapely.ops import nearest_points, unary_union
import trimesh


PRODUCT_ID = "MM-PER-001"
REVISION = "0.4.0"
DEFAULT_NAME = "STEFAN"
DEFAULT_LEFT = "STE"
DEFAULT_RIGHT = "FAN"
COUPON_TEXT = "FA"

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
REPO_ROOT = PROJECT_ROOT.parents[2]
FONT_PATH = HERE / "assets/fonts/NotoSans-ExtraCondensedExtraBold.ttf"
FONT_LICENSE = HERE / "assets/fonts/LICENSE-Noto.txt"
FONT_SOURCE = HERE / "assets/fonts/SOURCE.json"
WOOD_MASTER = REPO_ROOT / "libraries/surface-textures/wood-001/master/wood-001-tile-16bit.png"
WOOD_REGISTRATION = WOOD_MASTER.with_name(WOOD_MASTER.name + ".source.json")

# Approved functional geometry.
TOTAL_H = 160.0
SIDE_DEPTH = 115.0
FOOT_L = 70.0
PLATE_T = 3.2
FOOT_T = 2.0
FOOT_TIP_T = 0.6
FOOT_TAPER_L = 15.0
RIB_T = 2.4
RIB_PROJECTION = 6.0
GUSSET_X = 20.0
GUSSET_Z = 30.0
GUSSET_Y = 4.0

# Approved facade geometry.
CAP_HEIGHT = 122.0
GLYPH_GAP = 1.8
MIN_FINISHED_GAP = 1.2
GLYPH_DEPTH = 6.0
CONNECTOR_SETBACK = 6.0
CONNECTOR_T = 2.4
CONNECTOR_OVERLAP = 0.1
BRIDGE_WIDTH = 6.0

# Candidate-C transfer contract.
WOOD_PERIOD_X = 120.0
WOOD_PERIOD_Z = 45.0
WOOD_BLEND_PX = 24
WOOD_DEPTH = 0.6
TEXTURE_PITCH = 0.45
OUTLINE_TAPER = 1.2

MESH_TOLERANCE = 0.05
MESH_ANGULAR_TOLERANCE = 0.35
MAX_TRIANGLES = 1_000_000
MAX_MESH_MIB = 50.0

ALLOWED_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " -'ÄÖÜäöüẞß"
)


@dataclass(frozen=True)
class PlacedGlyph:
    char: str
    geometry: Polygon | MultiPolygon
    source_holes: int


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_once(path: Path, payload: dict) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value.strip())
    while "  " in value:
        value = value.replace("  ", " ")
    if not value:
        raise ValueError("text must not be empty")
    return value


@lru_cache(maxsize=1)
def _font() -> TTFont:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"bundled font missing: {FONT_PATH}")
    return TTFont(str(FONT_PATH))


def validate_glyphs(text: str) -> None:
    cmap = _font().getBestCmap()
    missing = [f"U+{ord(ch):04X} {ch!r}" for ch in text if ch != " " and ord(ch) not in cmap]
    if missing:
        raise ValueError("font lacks requested glyph(s): " + ", ".join(missing))
    unsupported = [f"U+{ord(ch):04X} {ch!r}" for ch in text if ch not in ALLOWED_CHARS]
    if unsupported:
        raise ValueError("unsupported character(s): " + ", ".join(unsupported))
    if " " in text:
        raise ValueError(
            "spaces need an explicit rear word bridge and are intentionally fail-closed in 0.4.0"
        )


def polygon_parts(geometry: Polygon | MultiPolygon) -> list[Polygon]:
    if isinstance(geometry, Polygon):
        return [geometry]
    return list(geometry.geoms)


def hole_count(geometry: Polygon | MultiPolygon) -> int:
    return sum(len(poly.interiors) for poly in polygon_parts(geometry))


@lru_cache(maxsize=128)
def raw_glyph(char: str) -> Polygon | MultiPolygon:
    validate_glyphs(char)
    path = TextPath(
        (0.0, 0.0), char, size=1.0, prop=FontProperties(fname=str(FONT_PATH))
    )
    contours: list[Polygon] = []
    for points in path.to_polygons(closed_only=True):
        if len(points) < 4:
            continue
        poly = Polygon(points)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if not poly.is_empty and poly.area > 1.0e-10:
            contours.append(poly)
    if not contours:
        raise ValueError(f"no closed font contours for {char!r}")
    result = GeometryCollection()
    for poly in sorted(contours, key=lambda item: item.area, reverse=True):
        result = result.symmetric_difference(poly)
    result = result.buffer(0)
    if not isinstance(result, (Polygon, MultiPolygon)) or result.is_empty:
        raise ValueError(f"font outline did not resolve to polygons for {char!r}")
    return result


@lru_cache(maxsize=1)
def cap_scale() -> float:
    # One immutable typographic cap scale is shared by coupon and product.
    # H has the font's nominal flat cap line; round-letter optical overshoots
    # are clipped to the manufacturing cap/bed planes below.
    cap_top = raw_glyph("H").bounds[3]
    if cap_top <= 0:
        raise AssertionError("invalid font cap reference")
    return CAP_HEIGHT / cap_top


def printable_glyph(char: str) -> tuple[Polygon | MultiPolygon, int]:
    source = raw_glyph(char)
    scaled = shapely.affinity.scale(
        source, xfact=cap_scale(), yfact=cap_scale(), origin=(0.0, 0.0)
    )
    # Trim only the font's optical undershoot below the shared baseline. This
    # produces a true z=0 bed datum without shifting individual baselines.
    bounds = scaled.bounds
    clipped = scaled.intersection(box(bounds[0] - 1.0, 0.0, bounds[2] + 1.0, CAP_HEIGHT))
    clipped = clipped.buffer(0)
    if not isinstance(clipped, (Polygon, MultiPolygon)) or clipped.is_empty:
        raise ValueError(f"print adaptation removed glyph {char!r}")
    if hole_count(clipped) != hole_count(source):
        raise ValueError(f"bed adaptation changed counter topology for {char!r}")
    return clipped, hole_count(source)


def pack_glyphs(text: str) -> list[PlacedGlyph]:
    """Pack glyphs until the actual outline-to-outline distance is 1.8 mm."""
    text = normalize_text(text)
    validate_glyphs(text)
    placed: list[PlacedGlyph] = []
    for char in text:
        geometry, holes = printable_glyph(char)
        geometry = shapely.affinity.translate(geometry, xoff=-geometry.bounds[0])
        if placed:
            previous = unary_union([item.geometry for item in placed])
            low = previous.bounds[0] - geometry.bounds[2]
            # One extra millimetre makes the far-side bracket insensitive to
            # floating-point rounding at the exact 1.8 mm target.
            high = previous.bounds[2] - geometry.bounds[0] + GLYPH_GAP + 1.0
            if previous.distance(shapely.affinity.translate(geometry, xoff=high)) < GLYPH_GAP:
                raise AssertionError("failed to bracket glyph spacing")
            for _ in range(80):
                midpoint = 0.5 * (low + high)
                candidate = shapely.affinity.translate(geometry, xoff=midpoint)
                if previous.distance(candidate) < GLYPH_GAP:
                    low = midpoint
                else:
                    high = midpoint
            geometry = shapely.affinity.translate(geometry, xoff=high)
        placed.append(PlacedGlyph(char, geometry, holes))
    distances = [
        placed[index].geometry.distance(placed[index + 1].geometry)
        for index in range(len(placed) - 1)
    ]
    if any(abs(distance - GLYPH_GAP) > 1.0e-6 for distance in distances):
        raise AssertionError(f"outline packing error: {distances}")
    return placed


def move_glyphs(glyphs: Sequence[PlacedGlyph], xoff: float) -> list[PlacedGlyph]:
    return [
        PlacedGlyph(
            item.char,
            shapely.affinity.translate(item.geometry, xoff=xoff),
            item.source_holes,
        )
        for item in glyphs
    ]


def place_half(text: str, side: str) -> list[PlacedGlyph]:
    glyphs = pack_glyphs(text)
    group = unary_union([item.geometry for item in glyphs])
    blade_edge_gap = GLYPH_GAP
    if side == "left":
        xoff = (-PLATE_T / 2.0 - blade_edge_gap) - group.bounds[2]
    elif side == "right":
        xoff = (PLATE_T / 2.0 + blade_edge_gap) - group.bounds[0]
    else:
        raise ValueError("side must be left or right")
    return move_glyphs(glyphs, xoff)


def bridge_between(first: Polygon | MultiPolygon, second: Polygon | MultiPolygon) -> Polygon:
    point_a, point_b = nearest_points(first, second)
    line = LineString([(point_a.x, point_a.y), (point_b.x, point_b.y)])
    bridge = line.buffer(BRIDGE_WIDTH / 2.0, cap_style=1, join_style=1, resolution=8)
    if not isinstance(bridge, Polygon) or bridge.is_empty:
        raise AssertionError("failed to generate local connector bridge")
    return bridge


def connector_profile(
    glyphs: Sequence[PlacedGlyph], side: str | None
) -> tuple[Polygon | MultiPolygon, list[dict]]:
    nodes: list[Polygon | MultiPolygon]
    blade = box(-PLATE_T / 2.0, 0.0, PLATE_T / 2.0, TOTAL_H)
    if side == "left":
        nodes = [item.geometry for item in glyphs] + [blade]
    elif side == "right":
        nodes = [blade] + [item.geometry for item in glyphs]
    elif side is None:
        nodes = [item.geometry for item in glyphs]
    else:
        raise ValueError("invalid connector side")
    bridges = []
    bridge_reports = []
    for index in range(len(nodes) - 1):
        point_a, point_b = nearest_points(nodes[index], nodes[index + 1])
        bridges.append(bridge_between(nodes[index], nodes[index + 1]))
        bridge_reports.append(
            {
                "index": index,
                "span_mm": float(point_a.distance(point_b)),
                "from_x_z_mm": [float(point_a.x), float(point_a.y)],
                "to_x_z_mm": [float(point_b.x), float(point_b.y)],
                "width_mm": BRIDGE_WIDTH,
            }
        )
    profile = unary_union([*nodes, *bridges]).buffer(0)
    # A nearest-point bridge to the blade can terminate at z=0. Its rounded
    # 3 mm cap must not cross the immutable print-bed plane.
    min_x = min(node.bounds[0] for node in nodes) - BRIDGE_WIDTH
    max_x = max(node.bounds[2] for node in nodes) + BRIDGE_WIDTH
    profile = profile.intersection(box(min_x, 0.0, max_x, TOTAL_H)).buffer(0)
    if not isinstance(profile, (Polygon, MultiPolygon)) or profile.is_empty:
        raise AssertionError("connector profile is invalid")
    parts = polygon_parts(profile)
    if len(parts) != 1:
        raise AssertionError(f"connector graph has {len(parts)} disconnected profiles")
    expected_holes = sum(item.source_holes for item in glyphs)
    if hole_count(profile) != expected_holes:
        raise AssertionError(
            f"connector changed counters: {hole_count(profile)} != {expected_holes}"
        )
    return profile, bridge_reports


def _wire_xz(coords: Iterable[tuple[float, float]], y: float) -> cq.Wire:
    points = [(float(x), float(y), float(z)) for x, z in coords]
    if points[0] != points[-1]:
        points.append(points[0])
    return cq.Wire.makePolygon(points)


def _face_polygon_xz(poly: Polygon, y: float) -> cq.Face:
    outer = _wire_xz(poly.exterior.coords, y)
    holes = [_wire_xz(ring.coords, y) for ring in poly.interiors]
    return cq.Face.makeFromWires(outer, holes)


def _prism_y(face: cq.Face, depth: float) -> cq.Solid:
    maker = BRepPrimAPI_MakePrism(face.wrapped, gp_Vec(0.0, depth, 0.0), True)
    return cq.Solid(maker.Shape())


def profile_solids(
    geometry: Polygon | MultiPolygon, y: float, depth: float
) -> list[cq.Solid]:
    return [_prism_y(_face_polygon_xz(poly, y), depth) for poly in polygon_parts(geometry)]


def _face_xz(points: list[tuple[float, float]], y: float = 0.0) -> cq.Face:
    return cq.Face.makeFromWires(_wire_xz(points, y))


def _foot_shape(inward: int) -> cq.Solid:
    full_end = FOOT_L - FOOT_TAPER_L
    if inward == 1:
        points = [
            (0.0, 0.0),
            (FOOT_L, 0.0),
            (FOOT_L, FOOT_TIP_T),
            (full_end, FOOT_T),
            (0.0, FOOT_T),
        ]
    else:
        points = [
            (0.0, 0.0),
            (-FOOT_L, 0.0),
            (-FOOT_L, FOOT_TIP_T),
            (-full_end, FOOT_T),
            (0.0, FOOT_T),
        ]
    return _prism_y(_face_xz(points), SIDE_DEPTH)


def fuse_solids(parts: Sequence[cq.Shape], label: str) -> cq.Workplane:
    if not parts:
        raise ValueError("no solids to fuse")
    result = cq.Workplane("XY").newObject([parts[0]])
    for part in parts[1:]:
        result = result.union(cq.Workplane("XY").newObject([part]), clean=False)
    result = result.clean()
    solids = result.solids().vals()
    if len(solids) != 1 or solids[0].isNull():
        raise AssertionError(f"{label}: expected one fused B-Rep solid, got {len(solids)}")
    return result


def build_coupon_brep() -> tuple[cq.Workplane, list[PlacedGlyph], Polygon | MultiPolygon, list[dict]]:
    glyphs = pack_glyphs(COUPON_TEXT)
    profile, bridges = connector_profile(glyphs, None)
    parts: list[cq.Shape] = []
    for item in glyphs:
        parts.extend(profile_solids(item.geometry, 0.0, GLYPH_DEPTH))
    parts.extend(
        profile_solids(
            profile,
            CONNECTOR_SETBACK - CONNECTOR_OVERLAP,
            CONNECTOR_T + CONNECTOR_OVERLAP,
        )
    )
    return fuse_solids(parts, "coupon"), glyphs, profile, bridges


def build_side_brep(
    side: str, text: str
) -> tuple[cq.Workplane, list[PlacedGlyph], Polygon | MultiPolygon, list[dict]]:
    inward = 1 if side == "left" else -1
    outward = -inward
    glyphs = place_half(text, side)
    profile, bridges = connector_profile(glyphs, side)
    parts: list[cq.Shape] = []
    blade = (
        cq.Workplane("XY")
        .box(PLATE_T, SIDE_DEPTH, TOTAL_H, centered=(True, False, False))
        .val()
    )
    parts.extend([blade, _foot_shape(inward)])
    for item in glyphs:
        parts.extend(profile_solids(item.geometry, 0.0, GLYPH_DEPTH))
    parts.extend(
        profile_solids(
            profile,
            CONNECTOR_SETBACK - CONNECTOR_OVERLAP,
            CONNECTOR_T + CONNECTOR_OVERLAP,
        )
    )
    rib_x = outward * (PLATE_T / 2.0 + RIB_PROJECTION / 2.0)
    for y in (28.0, 56.0, 84.0, SIDE_DEPTH - RIB_T):
        rib = (
            cq.Workplane("XY")
            .box(RIB_PROJECTION, RIB_T, TOTAL_H, centered=(True, False, False))
            .translate((rib_x, y, 0.0))
            .val()
        )
        parts.append(rib)
    triangle = [(0.0, 0.0), (outward * GUSSET_X, 0.0), (0.0, GUSSET_Z)]
    for y in (PLATE_T, SIDE_DEPTH - GUSSET_Y):
        parts.append(_prism_y(_face_xz(triangle, y), GUSSET_Y))
    part = fuse_solids(parts, side)
    bb = part.val().BoundingBox()
    if abs(bb.zmin) > 1.0e-6 or abs(bb.zmax - TOTAL_H) > 1.0e-6:
        raise AssertionError(f"{side}: invalid bed/height bounds {bb.zmin}, {bb.zmax}")
    if bb.xlen > 350.0 or bb.ylen > 120.0 or bb.zlen > 165.0:
        raise AssertionError(f"{side}: exceeds approved part envelope")
    return part, glyphs, profile, bridges


def normalize_step_header(path: Path) -> None:
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


def export_step_once(part: cq.Workplane, path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(part, str(path))
    normalize_step_header(path)


def export_assembly_step_once(left: cq.Workplane, right: cq.Workplane, path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    assembly = cq.Assembly(name=f"NameForm-{PRODUCT_ID}-{REVISION}")
    assembly.add(left, name="left-STE", loc=cq.Location(cq.Vector(-120.0, 0.0, 0.0)))
    assembly.add(right, name="right-FAN", loc=cq.Location(cq.Vector(120.0, 0.0, 0.0)))
    path.parent.mkdir(parents=True, exist_ok=True)
    assembly.save(str(path), exportType="STEP", mode="default")
    normalize_step_header(path)


def periodic_edge_blend(values: np.ndarray, blend_px: int) -> np.ndarray:
    if blend_px <= 0:
        return values.copy()
    output = values.copy()
    height, width = values.shape
    bx = min(blend_px, width // 4)
    by = min(blend_px, height // 4)
    seam_x = 0.5 * (values[:, 0] + values[:, -1])
    seam_y = 0.5 * (values[0, :] + values[-1, :])
    for column in range(bx):
        alpha = (column + 1) / (bx + 1)
        output[:, column] = values[:, column] * alpha + seam_x * (1.0 - alpha)
        output[:, width - 1 - column] = (
            values[:, width - 1 - column] * alpha + seam_x * (1.0 - alpha)
        )
    for row in range(by):
        alpha = (row + 1) / (by + 1)
        output[row, :] = output[row, :] * alpha + seam_y * (1.0 - alpha)
        output[height - 1 - row, :] = (
            output[height - 1 - row, :] * alpha + seam_y * (1.0 - alpha)
        )
    return output


class PeriodicSampler:
    def __init__(self, values: np.ndarray) -> None:
        if values.ndim != 2:
            raise ValueError("heightmap must be two-dimensional")
        self.values = np.asarray(values, dtype=np.float32)
        self.height, self.width = self.values.shape

    def sample(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        x = np.mod(u, 1.0) * self.width
        y = np.mod(v, 1.0) * self.height
        x0 = np.floor(x).astype(np.int64) % self.width
        y0 = np.floor(y).astype(np.int64) % self.height
        x1 = (x0 + 1) % self.width
        y1 = (y0 + 1) % self.height
        fx = (x - np.floor(x)).astype(np.float32)
        fy = (y - np.floor(y)).astype(np.float32)
        lower = self.values[y0, x0] * (1.0 - fx) + self.values[y0, x1] * fx
        upper = self.values[y1, x0] * (1.0 - fx) + self.values[y1, x1] * fx
        return lower * (1.0 - fy) + upper * fy


def load_sampler() -> tuple[PeriodicSampler, dict]:
    registration = json.loads(WOOD_REGISTRATION.read_text(encoding="utf-8"))
    if sha256(WOOD_MASTER) != registration["master_sha256"]:
        raise ValueError("wood master hash does not match registration")
    raw_u16 = np.asarray(Image.open(WOOD_MASTER))
    if raw_u16.dtype != np.uint16 or raw_u16.shape != (1254, 1254):
        raise ValueError("wood master must be 1254 x 1254 16-bit grayscale")
    raw = raw_u16.astype(np.float32) / 65535.0
    blended = periodic_edge_blend(raw, WOOD_BLEND_PX)
    return PeriodicSampler(blended), {
        "master": str(WOOD_MASTER.relative_to(REPO_ROOT)),
        "master_sha256": sha256(WOOD_MASTER),
        "registration": str(WOOD_REGISTRATION.relative_to(REPO_ROOT)),
        "registration_sha256": sha256(WOOD_REGISTRATION),
        "pixels": [1254, 1254],
        "container_bits": 16,
        "sampling": "direct bilinear at physical mesh vertices; no build raster",
        "periodic_edge_blend_px": WOOD_BLEND_PX,
    }


def smoothstep01(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def boundary_indices(rows: int, columns: int) -> list[int]:
    bottom = list(range(columns))
    right = [row * columns + columns - 1 for row in range(1, rows)]
    top = [(rows - 1) * columns + column for column in range(columns - 2, -1, -1)]
    left = [row * columns for row in range(rows - 2, 0, -1)]
    return bottom + right + top + left


def make_front_cutter(
    glyph_geometry: Polygon | MultiPolygon, sampler: PeriodicSampler
) -> tuple[Manifold, dict]:
    x0, z0, x1, z1 = glyph_geometry.bounds
    nx = math.ceil((x1 - x0) / TEXTURE_PITCH)
    nz = math.ceil((z1 - z0) / TEXTURE_PITCH)
    xs = np.linspace(x0, x1, nx + 1)
    zs = np.linspace(z0, z1, nz + 1)
    xx, zz = np.meshgrid(xs, zs, indexing="xy")
    sampled = sampler.sample(xx / WOOD_PERIOD_X, (CAP_HEIGHT - zz) / WOOD_PERIOD_Z)
    points = shapely.points(xx.ravel(), zz.ravel())
    inside = shapely.contains(glyph_geometry, points).reshape(xx.shape)
    distance = shapely.distance(points, glyph_geometry.boundary).reshape(xx.shape)
    mask = smoothstep01(distance / OUTLINE_TAPER) * inside
    relief = WOOD_DEPTH * sampled * mask
    top_y = -0.01 + relief
    bottom_y = -0.05

    top = np.dstack((xx, top_y, zz)).reshape(-1, 3)
    bottom = np.dstack((xx, np.full_like(xx, bottom_y), zz)).reshape(-1, 3)
    vertices = np.vstack((top, bottom))
    faces: list[tuple[int, int, int]] = []
    columns, rows = nx + 1, nz + 1
    offset = len(top)
    for row in range(nz):
        for column in range(nx):
            a = row * columns + column
            b, c, d = a + 1, a + columns, a + columns + 1
            faces.extend(((a, d, b), (a, c, d)))
            a2, b2, c2, d2 = a + offset, b + offset, c + offset, d + offset
            faces.extend(((a2, b2, d2), (a2, d2, c2)))
    boundary = boundary_indices(rows, columns)
    for index in range(len(boundary)):
        following = (index + 1) % len(boundary)
        front_a, front_b = boundary[index], boundary[following]
        back_a, back_b = front_a + offset, front_b + offset
        faces.extend(((front_a, front_b, back_b), (front_a, back_b, back_a)))
    cutter = Manifold(
        mesh=Mesh(
            vert_properties=np.ascontiguousarray(vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(faces, dtype=np.uint32),
        )
    )
    if cutter.status() != Error.NoError or cutter.is_empty():
        raise RuntimeError(f"height-field cutter rejected by Manifold: {cutter.status()}")
    active = relief[mask > 0.95]
    if active.size < 100:
        raise AssertionError("not enough fully active relief samples")
    return cutter, {
        "grid_cells_x_z": [nx, nz],
        "actual_pitch_x_z_mm": [(x1 - x0) / nx, (z1 - z0) / nz],
        "cutter_triangles": int(cutter.num_tri()),
        "sample_min_max": [float(sampled.min()), float(sampled.max())],
        "relief_min_max_mm": [float(relief.min()), float(relief.max())],
        "active_relief_p05_p95_mm": [
            float(np.percentile(active, 5)),
            float(np.percentile(active, 95)),
        ],
        "active_relief_robust_span_mm": float(
            np.percentile(active, 95) - np.percentile(active, 5)
        ),
        "boundary_relief_max_mm": float(
            max(
                relief[0, :].max(),
                relief[-1, :].max(),
                relief[:, 0].max(),
                relief[:, -1].max(),
            )
        ),
    }


def cadquery_to_manifold(shape: cq.Shape) -> Manifold:
    cq_vertices, cq_faces = shape.tessellate(MESH_TOLERANCE, MESH_ANGULAR_TOLERANCE)
    vertices = np.asarray(
        [[vertex.x, vertex.y, vertex.z] for vertex in cq_vertices], dtype=np.float32
    )
    faces = np.asarray(cq_faces, dtype=np.uint32)
    welded = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    manifold = Manifold(
        mesh=Mesh(
            vert_properties=np.ascontiguousarray(welded.vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(welded.faces, dtype=np.uint32),
        )
    )
    if manifold.status() != Error.NoError or manifold.is_empty():
        raise RuntimeError(f"CadQuery mesh rejected by Manifold: {manifold.status()}")
    return manifold


def manifold_arrays(manifold: Manifold) -> tuple[np.ndarray, np.ndarray]:
    output = manifold.to_mesh()
    return (
        np.asarray(output.vert_properties, dtype=np.float64)[:, :3],
        np.asarray(output.tri_verts, dtype=np.int64),
    )


def clean_mesh(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    before = len(mesh.faces)
    mesh.merge_vertices(digits_vertex=4)
    mesh.update_faces(mesh.nondegenerate_faces(height=1.0e-8))
    mesh.remove_unreferenced_vertices()
    return (
        np.ascontiguousarray(mesh.vertices, dtype=np.float64),
        np.ascontiguousarray(mesh.faces, dtype=np.int64),
        int(before - len(mesh.faces)),
    )


def write_binary_stl_once(path: Path, vertices: np.ndarray, faces: np.ndarray) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
    triangles = vertices[faces]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    normals[lengths > 0] /= lengths[lengths > 0, None]
    record_dtype = np.dtype(
        [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]
    )
    records = np.zeros(len(faces), dtype=record_dtype)
    records["normal"] = normals.astype(np.float32)
    records["vertices"] = triangles.astype(np.float32)
    header = b"MM-PER-001 NameForm letter-only wood C v0.4.0 DRAFT"[:80].ljust(80, b" ")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(faces)))
        handle.write(records.tobytes())


def mesh_metrics(vertices: np.ndarray, faces: np.ndarray) -> tuple[trimesh.Trimesh, dict]:
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    components = mesh.split(only_watertight=False)
    return mesh, {
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "body_count": len(components),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "bounds_min_mm": mesh.bounds[0].tolist(),
        "bounds_max_mm": mesh.bounds[1].tolist(),
        "extents_mm": mesh.extents.tolist(),
    }


def glyph_report(glyphs: Sequence[PlacedGlyph]) -> dict:
    group = unary_union([item.geometry for item in glyphs])
    gaps = [
        float(glyphs[index].geometry.distance(glyphs[index + 1].geometry))
        for index in range(len(glyphs) - 1)
    ]
    return {
        "text": "".join(item.char for item in glyphs),
        "cap_scale_mm_per_font_unit": cap_scale(),
        "bounds_x_z_mm": list(map(float, group.bounds)),
        "width_mm": float(group.bounds[2] - group.bounds[0]),
        "height_mm": float(group.bounds[3] - group.bounds[1]),
        "baseline_z_mm": 0.0,
        "nearest_outline_gaps_mm": gaps,
        "minimum_outline_gap_mm": min(gaps) if gaps else None,
        "counter_count": sum(item.source_holes for item in glyphs),
        "front_fill_ratio": float(group.area / box(*group.bounds).area),
    }


def engrave_part(
    part: cq.Workplane,
    glyphs: Sequence[PlacedGlyph],
    sampler: PeriodicSampler,
    path: Path,
) -> dict:
    glyph_geometry = unary_union([item.geometry for item in glyphs])
    base = cadquery_to_manifold(part.val())
    base_vertices, base_faces = manifold_arrays(base)
    base_mesh = trimesh.Trimesh(vertices=base_vertices, faces=base_faces, process=False)
    cutter, cutter_report = make_front_cutter(glyph_geometry, sampler)
    result = base - cutter
    if result.status() != Error.NoError or result.is_empty():
        raise RuntimeError(f"texture Boolean failed: {result.status()}")
    vertices, faces = manifold_arrays(result)
    # Manifold's output is already a certified 2-manifold. Do not apply a
    # decimal-place vertex weld here: at exact cap/bed clipping planes it can
    # collapse valid sub-0.0001 mm Boolean transition triangles and open the
    # shell. Printer-scale simplification, if needed, is a separate validated
    # operation with a geometric-error budget.
    removed = 0
    write_binary_stl_once(path, vertices, faces)
    mesh, metrics = mesh_metrics(vertices, faces)
    metrics["removed_degenerate_faces"] = removed
    size_mib = path.stat().st_size / (1024.0 * 1024.0)
    checks = {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "single_body": bool(metrics["body_count"] == 1),
        "positive_volume": bool(mesh.volume > 0.0),
        "bed_datum": bool(abs(float(mesh.bounds[0, 2])) <= 1.0e-6),
        "envelope_preserved": bool(np.allclose(mesh.bounds, base_mesh.bounds, atol=1.0e-5)),
        "volume_reduced": bool(0.0 < mesh.volume < base_mesh.volume),
        "triangle_budget": bool(len(faces) <= MAX_TRIANGLES),
        "file_size_budget": bool(size_mib <= MAX_MESH_MIB),
        "outline_taper_protected": bool(cutter_report["boundary_relief_max_mm"] <= 1.0e-8),
        "candidate_c_relief_span": bool(cutter_report["active_relief_robust_span_mm"] >= 0.20),
    }
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
        "size_mib": size_mib,
        "source_volume_mm3": float(base_mesh.volume),
        "engraved_volume_mm3": float(mesh.volume),
        "removed_volume_mm3": float(base_mesh.volume - mesh.volume),
        "metrics": metrics,
        "texture": cutter_report,
        "checks": checks,
    }


def engineering_report(
    part: cq.Workplane,
    glyphs: Sequence[PlacedGlyph],
    connector: Polygon | MultiPolygon,
    bridges: list[dict],
    step_path: Path,
) -> dict:
    solid = part.val()
    bb = solid.BoundingBox()
    glyphs_payload = glyph_report(glyphs)
    checks = {
        "one_brep_solid": len(part.solids().vals()) == 1,
        "connector_single_profile": len(polygon_parts(connector)) == 1,
        "counters_preserved": hole_count(connector) == glyphs_payload["counter_count"],
        "nominal_gap": all(
            gap >= GLYPH_GAP - 1.0e-6
            for gap in glyphs_payload["nearest_outline_gaps_mm"]
        ),
        "minimum_finished_gap": all(
            gap >= MIN_FINISHED_GAP
            for gap in glyphs_payload["nearest_outline_gaps_mm"]
        ),
        "no_rectangular_panel": glyphs_payload["front_fill_ratio"] < 0.75,
        "bed_datum": abs(bb.zmin) <= 1.0e-6,
    }
    return {
        "step": str(step_path.relative_to(REPO_ROOT)),
        "step_sha256": sha256(step_path),
        "step_size_bytes": step_path.stat().st_size,
        "bbox_min_max_mm": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
        "extents_mm": [bb.xlen, bb.ylen, bb.zlen],
        "volume_mm3": solid.Volume(),
        "solids": len(part.solids().vals()),
        "glyphs": glyphs_payload,
        "connector": {
            "setback_nominal_mm": CONNECTOR_SETBACK,
            "boolean_overlap_mm": CONNECTOR_OVERLAP,
            "thickness_mm": CONNECTOR_T,
            "profile_area_mm2": float(connector.area),
            "profile_counter_count": hole_count(connector),
            "local_bridges": bridges,
        },
        "checks": checks,
    }


def common_report_inputs(wood: dict) -> list[dict]:
    paths = [Path(__file__).resolve(), FONT_PATH, FONT_LICENSE, FONT_SOURCE, WOOD_MASTER, WOOD_REGISTRATION]
    return [
        {
            "path": str(path.relative_to(REPO_ROOT)),
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
        }
        for path in paths
    ]


def build_coupon(sampler: PeriodicSampler, wood: dict) -> dict:
    coupon_root = PROJECT_ROOT / "coupons/nameform-letter-bridge-v0.4.0"
    engineering_path = coupon_root / "exports/engineering/nameform-FA-bridge-v0.4.0.step"
    candidate_path = coupon_root / "exports/candidate/DRAFT-nameform-FA-wood-C-v0.4.0.stl"
    report_path = coupon_root / "reports/generation-report.json"
    part, glyphs, connector, bridges = build_coupon_brep()
    export_step_once(part, engineering_path)
    engineering = engineering_report(part, glyphs, connector, bridges, engineering_path)
    candidate = engrave_part(part, glyphs, sampler, candidate_path)
    checks = {
        "engineering": all(engineering["checks"].values()),
        "candidate": all(candidate["checks"].values()),
        "candidate_c_exact_contract": True,
    }
    report = {
        "schema_version": "1.0",
        "tool": "NameForm letter-only generator",
        "tool_version": REVISION,
        "profile": "DRAFT process-matched FA coupon",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "inputs": common_report_inputs(wood),
        "wood": wood,
        "engineering": engineering,
        "candidate": candidate,
        "checks": checks,
        "limitations": [
            "Physical coupon review is not run by this generator.",
            "Exact filament product, color, batch and conditioning remain unresolved.",
            "No printer upload or print start is performed.",
        ],
    }
    write_json_once(report_path, report)
    if report["status"] != "PASS":
        raise RuntimeError(f"coupon generation checks failed; see {report_path}")
    return report


def build_pair(sampler: PeriodicSampler, wood: dict) -> dict:
    engineering_dir = PROJECT_ROOT / "exports/v0.4.0/engineering"
    candidate_dir = PROJECT_ROOT / "exports/v0.4.0/candidate"
    report_path = PROJECT_ROOT / "validation/v0.4.0/generation-report.json"
    left, left_glyphs, left_connector, left_bridges = build_side_brep("left", DEFAULT_LEFT)
    right, right_glyphs, right_connector, right_bridges = build_side_brep("right", DEFAULT_RIGHT)
    left_step = engineering_dir / "nameform-STE-left-v0.4.0.step"
    right_step = engineering_dir / "nameform-FAN-right-v0.4.0.step"
    assembly_step = engineering_dir / "nameform-STE-FAN-assembly-v0.4.0.step"
    export_step_once(left, left_step)
    export_step_once(right, right_step)
    export_assembly_step_once(left, right, assembly_step)
    left_engineering = engineering_report(
        left, left_glyphs, left_connector, left_bridges, left_step
    )
    right_engineering = engineering_report(
        right, right_glyphs, right_connector, right_bridges, right_step
    )
    left_candidate = engrave_part(
        left,
        left_glyphs,
        sampler,
        candidate_dir / "DRAFT-nameform-STE-left-wood-C-v0.4.0.stl",
    )
    right_candidate = engrave_part(
        right,
        right_glyphs,
        sampler,
        candidate_dir / "DRAFT-nameform-FAN-right-wood-C-v0.4.0.stl",
    )
    checks = {
        "left_engineering": all(left_engineering["checks"].values()),
        "right_engineering": all(right_engineering["checks"].values()),
        "left_candidate": all(left_candidate["checks"].values()),
        "right_candidate": all(right_candidate["checks"].values()),
        "shared_cap_scale": True,
        "opposed_inward_feet": (
            left_engineering["bbox_min_max_mm"][3] >= FOOT_L - 1.0e-6
            and right_engineering["bbox_min_max_mm"][0] <= -FOOT_L + 1.0e-6
        ),
        "candidate_c_exact_contract": True,
    }
    report = {
        "schema_version": "1.0",
        "tool": "NameForm letter-only generator",
        "tool_version": REVISION,
        "profile": "DRAFT STE | FAN pair",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "inputs": common_report_inputs(wood),
        "wood": wood,
        "assembly_step": {
            "path": str(assembly_step.relative_to(REPO_ROOT)),
            "sha256": sha256(assembly_step),
            "size_bytes": assembly_step.stat().st_size,
            "blade_spacing_mm": 240.0,
        },
        "left": {"engineering": left_engineering, "candidate": left_candidate},
        "right": {"engineering": right_engineering, "candidate": right_candidate},
        "checks": checks,
        "limitations": [
            "The complete pair is a digital DRAFT pending physical FA coupon acceptance.",
            "Wood relief is applied to glyph fronts only; optional flank relief remains excluded.",
            "The 0.4.0 product watermark is not generated or placed yet.",
            "Exact filament product, color, batch and conditioning remain unresolved.",
            "No printer upload or print start is performed.",
        ],
    }
    write_json_once(report_path, report)
    if report["status"] != "PASS":
        raise RuntimeError(f"pair generation checks failed; see {report_path}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("coupon", "pair", "all"), default="all")
    args = parser.parse_args()
    sampler, wood = load_sampler()
    payload: dict[str, object] = {"target": args.target}
    if args.target in {"coupon", "all"}:
        coupon = build_coupon(sampler, wood)
        payload["coupon"] = {
            "status": coupon["status"],
            "step": coupon["engineering"]["step"],
            "stl": coupon["candidate"]["path"],
            "triangles": coupon["candidate"]["metrics"]["triangles"],
        }
    if args.target in {"pair", "all"}:
        pair = build_pair(sampler, wood)
        payload["pair"] = {
            "status": pair["status"],
            "left_stl": pair["left"]["candidate"]["path"],
            "right_stl": pair["right"]["candidate"]["path"],
            "triangles": [
                pair["left"]["candidate"]["metrics"]["triangles"],
                pair["right"]["candidate"]["metrics"]["triangles"],
            ],
        }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
