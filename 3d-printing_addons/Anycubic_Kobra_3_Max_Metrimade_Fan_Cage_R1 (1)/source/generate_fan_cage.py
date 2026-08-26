#!/usr/bin/env python3
"""Generate the original Metrimade Kobra 3 Max fan-cage print package.

The geometry is built as a deterministic 0.20 mm voxel solid.  This avoids a
third-party CAD/mesh dependency while preserving exact, auditable material
partitions for the first-layer multicolor inlay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw


PITCH = 0.20
X_MIN, X_MAX = -33.0, 33.0
Y_MIN, Y_MAX = -35.0, 33.0
Z_MIN, Z_MAX = 0.0, 6.60
BRAND_SVG = Path(__file__).resolve().parents[1] / "assets" / "metrimade-lockup-horizontal-color.svg"
BRAND_VIEWBOX = (0.0, 0.0, 610.0, 214.0)
MARK_HEIGHT_MM = 30.0
WORDMARK_WIDTH_MM = 48.0
LABEL_CENTER_Y_MM = -29.70
LABEL_WIDTH_MM = 54.0
LABEL_HEIGHT_MM = 8.80
BRAND_SCALE = 0.18  # conservative curve-flattening scale; placement scales are computed per group
BRAND_COLORS = {
    "brand_navy": "#112431FF",
    "brand_teal": "#08777DFF",
    "brand_aqua": "#7FD5D3FF",
    "brand_sand": "#C7AB82FF",
}
PATH_TOKEN_RE = re.compile(r"[A-Za-z]|[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?")


@dataclass(frozen=True)
class Mesh:
    vertices: list[tuple[float, float, float]]
    triangles: list[tuple[int, int, int]]


def grid() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    nx = int(round((X_MAX - X_MIN) / PITCH))
    ny = int(round((Y_MAX - Y_MIN) / PITCH))
    nz = int(round((Z_MAX - Z_MIN) / PITCH))
    xs = X_MIN + (np.arange(nx) + 0.5) * PITCH
    ys = Y_MIN + (np.arange(ny) + 0.5) * PITCH
    zs = Z_MIN + (np.arange(nz) + 0.5) * PITCH
    return xs, ys, zs


def segment_mask(
    xx: np.ndarray,
    yy: np.ndarray,
    a: tuple[float, float],
    b: tuple[float, float],
    width: float,
) -> np.ndarray:
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    denom = vx * vx + vy * vy
    t = np.clip(((xx - ax) * vx + (yy - ay) * vy) / denom, 0.0, 1.0)
    dx = xx - (ax + t * vx)
    dy = yy - (ay + t * vy)
    return dx * dx + dy * dy <= (width / 2.0) ** 2


def rounded_box_mask(
    xx: np.ndarray,
    yy: np.ndarray,
    half_w: float,
    half_h: float,
    radius: float,
) -> np.ndarray:
    qx = np.maximum(np.abs(xx) - (half_w - radius), 0.0)
    qy = np.maximum(np.abs(yy) - (half_h - radius), 0.0)
    return (qx * qx + qy * qy <= radius * radius) & (np.abs(xx) <= half_w) & (np.abs(yy) <= half_h)


def _path_subpaths(path_data: str) -> list[list[tuple[float, float]]]:
    """Flatten the absolute M/L/H/V/C/Q/Z commands used by the supplied SVG."""
    tokens = PATH_TOKEN_RE.findall(path_data)
    subpaths: list[list[tuple[float, float]]] = []
    active: list[tuple[float, float]] = []
    current = (0.0, 0.0)
    start = (0.0, 0.0)
    command: str | None = None
    index = 0

    def number() -> float:
        nonlocal index
        value = float(tokens[index])
        index += 1
        return value

    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command == "Z":
                if active:
                    if active[-1] != start:
                        active.append(start)
                    subpaths.append(active)
                    active = []
                current = start
                command = None
                continue
        if command is None:
            raise ValueError("SVG path data has coordinates without a command")
        if command == "M":
            point = (number(), number())
            if active:
                subpaths.append(active)
            current = point
            start = point
            active = [point]
            command = "L"
        elif command == "L":
            current = (number(), number())
            active.append(current)
        elif command == "H":
            current = (number(), current[1])
            active.append(current)
        elif command == "V":
            current = (current[0], number())
            active.append(current)
        elif command == "C":
            p0 = current
            p1 = (number(), number())
            p2 = (number(), number())
            p3 = (number(), number())
            control_length = sum(math.dist(a, b) for a, b in ((p0, p1), (p1, p2), (p2, p3)))
            steps = min(48, max(4, int(math.ceil(control_length * BRAND_SCALE / (PITCH * 0.35)))))
            for step in range(1, steps + 1):
                t = step / steps
                u = 1.0 - t
                active.append((
                    u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
                ))
            current = p3
        elif command == "Q":
            p0 = current
            p1 = (number(), number())
            p2 = (number(), number())
            control_length = math.dist(p0, p1) + math.dist(p1, p2)
            steps = min(40, max(4, int(math.ceil(control_length * BRAND_SCALE / (PITCH * 0.35)))))
            for step in range(1, steps + 1):
                t = step / steps
                u = 1.0 - t
                active.append((
                    u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
                ))
            current = p2
        else:
            raise ValueError(f"Unsupported SVG path command: {command}")
    if active:
        subpaths.append(active)
    return subpaths


def _group_transform(transform: str | None) -> np.ndarray:
    matrix = np.eye(3, dtype=np.float64)
    if not transform:
        return matrix
    for name, arguments in re.findall(r"([A-Za-z]+)\s*\(([^)]*)\)", transform):
        values = [float(value) for value in re.findall(r"[+-]?(?:\d+\.?\d*|\.\d+)", arguments)]
        operation = np.eye(3, dtype=np.float64)
        if name == "translate":
            operation[0, 2] = values[0]
            operation[1, 2] = values[1] if len(values) > 1 else 0.0
        elif name == "scale":
            operation[0, 0] = values[0]
            operation[1, 1] = values[1] if len(values) > 1 else values[0]
        else:
            raise ValueError(f"Unsupported SVG group transform: {name}")
        matrix = matrix @ operation
    return matrix


def manifold_pixel_mask(mask: np.ndarray) -> np.ndarray:
    """Fill one cell in a 2x2 diagonal-only contact to avoid non-manifold extrusion edges."""
    result = mask.copy()
    for _ in range(4):
        upper_left = result[:-1, :-1]
        upper_right = result[:-1, 1:]
        lower_left = result[1:, :-1]
        lower_right = result[1:, 1:]
        diagonal_a = upper_left & lower_right & ~upper_right & ~lower_left
        diagonal_b = upper_right & lower_left & ~upper_left & ~lower_right
        if not diagonal_a.any() and not diagonal_b.any():
            break
        # The deterministic choice keeps growth to one 0.20 mm cell per ambiguity.
        result[:-1, 1:] |= diagonal_a
        result[:-1, :-1] |= diagonal_b
    return result


def _erode_pixel_mask(mask: np.ndarray, cells: int) -> np.ndarray:
    result = mask.copy()
    for _ in range(cells):
        padded = np.pad(result, 1, mode="constant", constant_values=False)
        result = (
            padded[1:-1, 1:-1]
            & padded[:-2, 1:-1]
            & padded[2:, 1:-1]
            & padded[1:-1, :-2]
            & padded[1:-1, 2:]
        )
    return result


def _rasterize_brand_group(
    group: ET.Element,
    nx: int,
    ny: int,
    *,
    target_width_mm: float | None = None,
    target_height_mm: float | None = None,
    offset_mm: tuple[float, float] = (0.0, 0.0),
) -> tuple[dict[str, np.ndarray], dict]:
    namespace = "{http://www.w3.org/2000/svg}"
    fill_to_name = {color[:7].upper(): name for name, color in BRAND_COLORS.items()}
    transform = _group_transform(group.get("transform"))
    vector_paths: list[tuple[str, list[list[tuple[float, float]]]]] = []
    all_points: list[tuple[float, float]] = []

    for path in group.findall(f"{namespace}path"):
        fill = path.get("fill", "").upper()
        if fill not in fill_to_name:
            raise ValueError(f"Unexpected brand color {fill!r} in {BRAND_SVG.name}")
        transformed_subpaths: list[list[tuple[float, float]]] = []
        for subpath in _path_subpaths(path.get("d", "")):
            transformed_points: list[tuple[float, float]] = []
            for x_svg, y_svg in subpath:
                point = transform @ np.asarray([x_svg, y_svg, 1.0])
                xy = (float(point[0]), float(point[1]))
                transformed_points.append(xy)
                all_points.append(xy)
            transformed_subpaths.append(transformed_points)
        vector_paths.append((fill_to_name[fill], transformed_subpaths))

    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    bounds = (min(xs), min(ys), max(xs), max(ys))
    source_width = bounds[2] - bounds[0]
    source_height = bounds[3] - bounds[1]
    if (target_width_mm is None) == (target_height_mm is None):
        raise ValueError("Exactly one target group dimension must be supplied")
    scale = target_width_mm / source_width if target_width_mm is not None else target_height_mm / source_height
    center = ((bounds[0] + bounds[2]) / 2.0, (bounds[1] + bounds[3]) / 2.0)
    masks = {name: np.zeros((ny, nx), dtype=bool) for name in BRAND_COLORS}

    for color_name, subpaths in vector_paths:
        path_mask = np.zeros((ny, nx), dtype=bool)
        for subpath in subpaths:
            points = [
                (
                    (((x_svg - center[0]) * scale + offset_mm[0]) - X_MIN) / PITCH,
                    (((y_svg - center[1]) * scale + offset_mm[1]) - Y_MIN) / PITCH,
                )
                for x_svg, y_svg in subpath
            ]
            polygon = Image.new("1", (nx, ny), 0)
            ImageDraw.Draw(polygon).polygon(points, fill=1)
            path_mask ^= np.asarray(polygon, dtype=bool)
        masks[color_name] |= path_mask

    return {name: manifold_pixel_mask(mask) for name, mask in masks.items()}, {
        "source_bounds": [round(value, 4) for value in bounds],
        "scale_mm_per_svg_unit": round(scale, 8),
        "target_width_mm": target_width_mm,
        "target_height_mm": target_height_mm,
        "offset_mm": list(offset_mm),
        "path_count": len(vector_paths),
    }


def brand_masks(nx: int, ny: int) -> tuple[dict[str, np.ndarray], dict]:
    """Separate the supplied mark and wordmark, then make the mark air-permeable."""
    svg_bytes = BRAND_SVG.read_bytes()
    root = ET.fromstring(svg_bytes)
    namespace = "{http://www.w3.org/2000/svg}"
    groups = root.findall(f"{namespace}g")
    if len(groups) != 2:
        raise ValueError("Expected one mark group and one wordmark group in the supplied SVG")

    mark, mark_meta = _rasterize_brand_group(
        groups[0], nx, ny, target_height_mm=MARK_HEIGHT_MM, offset_mm=(0.0, 0.0)
    )
    wordmark, wordmark_meta = _rasterize_brand_group(
        groups[1], nx, ny, target_width_mm=WORDMARK_WIDTH_MM, offset_mm=(0.0, LABEL_CENTER_Y_MM)
    )

    rows, columns = np.indices((ny, nx))
    diagonal_lamellae = ((columns + rows) % 16) < 4  # 0.8 mm rib in a 3.2 mm pitch
    perforated_mark: dict[str, np.ndarray] = {}
    for name, mask in mark.items():
        edge = mask & ~_erode_pixel_mask(mask, 4)  # retain a 0.8 mm color contour
        perforated_mark[name] = manifold_pixel_mask(mask & (edge | diagonal_lamellae))

    resolved: dict[str, np.ndarray] = {}
    occupied = np.zeros((ny, nx), dtype=bool)
    for name in ("brand_sand", "brand_aqua", "brand_teal", "brand_navy"):
        resolved[name] = perforated_mark[name] & ~occupied
        occupied |= resolved[name]
    perforated_mark = resolved

    # The wordmark is navy and remains closed because it is placed on a solid plate.
    perforated_mark["brand_navy"] |= wordmark["brand_navy"]
    return perforated_mark, {
        "source": "assets/metrimade-lockup-horizontal-color.svg",
        "source_sha256": hashlib.sha256(svg_bytes).hexdigest(),
        "source_viewbox": list(BRAND_VIEWBOX),
        "colors": BRAND_COLORS,
        "mark": {
            **mark_meta,
            "perforation": "0.8 mm contour plus 0.8 mm diagonal lamellae at 3.2 mm pitch",
        },
        "wordmark": {
            **wordmark_meta,
            "plate_center_y_mm": LABEL_CENTER_Y_MM,
            "plate_size_mm": [LABEL_WIDTH_MM, LABEL_HEIGHT_MM],
        },
    }


def make_xy_masks(xs: np.ndarray, ys: np.ndarray) -> tuple[dict[str, np.ndarray], dict]:
    xx, yy = np.meshgrid(xs, ys)
    rr = np.hypot(xx, yy)

    outer_ring = (rr <= 31.0) & (rr >= 25.40)
    spokes = np.zeros_like(rr, dtype=bool)
    # Four short links attach outside the mark instead of crossing its camera-facing planes.
    for a, b in (
        ((-12.0, 0.0), (-25.8, 0.0)),
        ((12.0, 0.0), (25.8, 0.0)),
        ((0.0, -15.0), (0.0, -25.8)),
        ((0.0, 15.0), (0.0, 25.8)),
    ):
        spokes |= segment_mask(xx, yy, a, b, 1.60)

    brand, brand_meta = brand_masks(len(xs), len(ys))
    # Closed wordmark plate is entirely outside the assumed Ø40/42 mm fan intake.
    label_plate = rounded_box_mask(
        xx, yy - LABEL_CENTER_Y_MM, LABEL_WIDTH_MM / 2.0, LABEL_HEIGHT_MM / 2.0, 2.0
    )
    wordmark = brand["brand_navy"] & label_plate
    brand["brand_sand"] |= label_plate & ~wordmark
    brand_union = np.logical_or.reduce(tuple(brand.values()))
    front = manifold_pixel_mask(outer_ring | spokes | brand_union | label_plate)

    return {
        "front": front,
        **brand,
    }, brand_meta


def tab_sector_mask(xx: np.ndarray, yy: np.ndarray, half_angle_deg: float = 12.0) -> np.ndarray:
    angle = (np.degrees(np.arctan2(yy, xx)) + 360.0) % 360.0
    sector = np.zeros_like(angle, dtype=bool)
    # No tab at the 6-o'clock position; the two lower diagonals avoid the duct features.
    for center in (0, 60, 120, 180, 240, 300):
        delta = np.abs(((angle - center + 180.0) % 360.0) - 180.0)
        sector |= delta <= half_angle_deg
    return sector


def clip_inner_radius(z: float, target_diameter: float) -> float:
    target_r = target_diameter / 2.0
    if z < 2.80:
        return target_r - 0.50  # structural shoulder against the bezel face
    if z < 5.35:
        return target_r + 0.25  # running clearance around the raised bezel
    if z < 5.85:
        return target_r - 0.15  # small retention bead; PETG tabs flex locally
    # 0.75 mm lead-in at the back edge.
    t = min(max((z - 5.85) / 0.75, 0.0), 1.0)
    return (target_r - 0.15) * (1.0 - t) + (target_r + 0.60) * t


def make_occupancy(target_diameter: float, fit_coupon: bool = False) -> tuple[dict[str, np.ndarray], dict]:
    xs, ys, zs = grid()
    xx, yy = np.meshgrid(xs, ys)
    rr = np.hypot(xx, yy)
    sector = tab_sector_mask(xx, yy)
    masks, brand_meta = make_xy_masks(xs, ys)
    shape = (len(zs), len(ys), len(xs))
    cage = np.zeros(shape, dtype=bool)

    if fit_coupon:
        coupon_ring = (rr <= 28.6) & (rr >= target_diameter / 2.0 - 0.55)
        for k, z in enumerate(zs):
            if z < 1.20:
                cage[k] |= coupon_ring
            if 0.80 <= z < 5.40:
                inner = clip_inner_radius(z + 1.00, target_diameter)
                cage[k] |= sector & (rr >= inner) & (rr <= 28.40)
        return {"single": cage}, {
            "pitch_mm": PITCH,
            "target_bezel_diameter_mm": target_diameter,
            "fit_coupon": True,
        }

    for k, z in enumerate(zs):
        if z < 2.40:
            cage[k] |= masks["front"]
        if 2.20 <= z < 6.60:
            inner = clip_inner_radius(z, target_diameter)
            cage[k] |= sector & (rr >= inner) & (rr <= 28.40)

    inlay_layers = int(round(0.60 / PITCH))
    teal = np.zeros_like(cage)
    aqua = np.zeros_like(cage)
    sand = np.zeros_like(cage)
    for k in range(min(inlay_layers, len(zs))):
        teal[k] = cage[k] & masks["brand_teal"]
        aqua[k] = cage[k] & masks["brand_aqua"]
        sand[k] = cage[k] & masks["brand_sand"]
    navy = cage & ~(teal | aqua | sand)

    intake_stats = {}
    for diameter in (40.0, 42.0):
        disc = rr <= diameter / 2.0
        blocked = masks["front"] & disc
        open_fraction = 1.0 - blocked.sum() / disc.sum()
        intake_stats[f"estimated_D{int(diameter)}_open_area_percent"] = round(100.0 * open_fraction, 2)

    return {
        "body_navy": navy,
        "brand_teal": teal,
        "brand_aqua": aqua,
        "brand_sand": sand,
        "single": cage,
    }, {
        "pitch_mm": PITCH,
        "target_bezel_diameter_mm": target_diameter,
        "fit_coupon": False,
        "inlay_depth_mm": inlay_layers * PITCH,
        "brand": brand_meta,
        "airflow_projection": intake_stats,
    }


def occupancy_to_mesh(occ: np.ndarray) -> Mesh:
    nz, ny, nx = occ.shape
    vertex_map: dict[tuple[int, int, int], int] = {}
    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []

    def vid(p: tuple[int, int, int]) -> int:
        existing = vertex_map.get(p)
        if existing is not None:
            return existing
        ix, iy, iz = p
        idx = len(vertices)
        vertex_map[p] = idx
        vertices.append((X_MIN + ix * PITCH, Y_MIN + iy * PITCH, Z_MIN + iz * PITCH))
        return idx

    def quad(points: tuple[tuple[int, int, int], ...]) -> None:
        a, b, c, d = (vid(point) for point in points)
        triangles.append((a, b, c))
        triangles.append((a, c, d))

    for iz, iy, ix in np.argwhere(occ):
        if ix == 0 or not occ[iz, iy, ix - 1]:
            quad(((ix, iy, iz), (ix, iy, iz + 1), (ix, iy + 1, iz + 1), (ix, iy + 1, iz)))
        if ix == nx - 1 or not occ[iz, iy, ix + 1]:
            quad(((ix + 1, iy, iz), (ix + 1, iy + 1, iz), (ix + 1, iy + 1, iz + 1), (ix + 1, iy, iz + 1)))
        if iy == 0 or not occ[iz, iy - 1, ix]:
            quad(((ix, iy, iz), (ix + 1, iy, iz), (ix + 1, iy, iz + 1), (ix, iy, iz + 1)))
        if iy == ny - 1 or not occ[iz, iy + 1, ix]:
            quad(((ix, iy + 1, iz), (ix, iy + 1, iz + 1), (ix + 1, iy + 1, iz + 1), (ix + 1, iy + 1, iz)))
        if iz == 0 or not occ[iz - 1, iy, ix]:
            quad(((ix, iy, iz), (ix, iy + 1, iz), (ix + 1, iy + 1, iz), (ix + 1, iy, iz)))
        if iz == nz - 1 or not occ[iz + 1, iy, ix]:
            quad(((ix, iy, iz + 1), (ix + 1, iy, iz + 1), (ix + 1, iy + 1, iz + 1), (ix, iy + 1, iz + 1)))
    return Mesh(vertices=vertices, triangles=triangles)


def mesh_metrics(mesh: Mesh) -> dict:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    tris = np.asarray(mesh.triangles, dtype=np.int64)
    if len(tris) == 0:
        return {"vertices": 0, "triangles": 0, "watertight_by_edge_count": False}
    edges = np.concatenate((tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]), axis=0)
    edges.sort(axis=1)
    edge_counts = Counter(map(tuple, edges.tolist()))
    boundary = sum(1 for count in edge_counts.values() if count == 1)
    nonmanifold = sum(1 for count in edge_counts.values() if count > 2)

    tri_adj: dict[int, list[int]] = defaultdict(list)
    edge_owner: dict[tuple[int, int], int] = {}
    for tid, tri in enumerate(tris):
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge = (min(int(a), int(b)), max(int(a), int(b)))
            if edge in edge_owner:
                other = edge_owner[edge]
                tri_adj[tid].append(other)
                tri_adj[other].append(tid)
            else:
                edge_owner[edge] = tid
    seen: set[int] = set()
    components = 0
    for start in range(len(tris)):
        if start in seen:
            continue
        components += 1
        queue = deque([start])
        seen.add(start)
        while queue:
            current = queue.popleft()
            for nxt in tri_adj.get(current, []):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)

    p0 = vertices[tris[:, 0]]
    p1 = vertices[tris[:, 1]]
    p2 = vertices[tris[:, 2]]
    signed_volume = np.einsum("ij,ij->i", p0, np.cross(p1, p2)).sum() / 6.0
    return {
        "vertices": int(len(vertices)),
        "triangles": int(len(tris)),
        "components_by_shared_edges": components,
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "watertight_by_edge_count": boundary == 0 and nonmanifold == 0,
        "signed_volume_mm3": round(float(signed_volume), 3),
        "bounds_min_mm": [round(float(v), 3) for v in vertices.min(axis=0)],
        "bounds_max_mm": [round(float(v), 3) for v in vertices.max(axis=0)],
    }


def write_binary_stl(path: Path, mesh: Mesh, solid_name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        header = (f"Metrimade original | {solid_name}").encode("ascii", "replace")[:80].ljust(80, b"\0")
        handle.write(header)
        handle.write(struct.pack("<I", len(mesh.triangles)))
        vertices = mesh.vertices
        for ia, ib, ic in mesh.triangles:
            a = np.asarray(vertices[ia], dtype=np.float64)
            b = np.asarray(vertices[ib], dtype=np.float64)
            c = np.asarray(vertices[ic], dtype=np.float64)
            normal = np.cross(b - a, c - a)
            norm = np.linalg.norm(normal)
            if norm:
                normal /= norm
            handle.write(struct.pack("<12fH", *(normal.tolist() + a.tolist() + b.tolist() + c.tolist()), 0))
    expected_size = 84 + 50 * len(mesh.triangles)
    actual_size = temporary.stat().st_size
    if actual_size != expected_size:
        raise RuntimeError(
            f"Incomplete STL write for {path.name}: expected {expected_size} bytes, got {actual_size}"
        )
    temporary.replace(path)


def xml_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def mesh_xml(mesh: Mesh, object_id: int, material_id: int, material_index: int, name: str) -> str:
    vertices = "".join(
        f'<vertex x="{x:.3f}" y="{y:.3f}" z="{z:.3f}"/>' for x, y, z in mesh.vertices
    )
    triangles = "".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.triangles
    )
    return (
        f'<object id="{object_id}" name="{xml_escape(name)}" type="model" '
        f'pid="{material_id}" pindex="{material_index}"><mesh><vertices>{vertices}</vertices>'
        f'<triangles>{triangles}</triangles></mesh></object>'
    )


def write_3mf(path: Path, parts: list[tuple[str, str, Mesh]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    material_id = 1
    material_xml = "".join(
        f'<base name="{xml_escape(name)}" displaycolor="{color}"/>' for name, color, _ in parts
    )
    objects_xml = []
    component_xml = []
    for index, (name, _color, mesh) in enumerate(parts):
        object_id = 2 + index
        objects_xml.append(mesh_xml(mesh, object_id, material_id, index, name))
        component_xml.append(f'<component objectid="{object_id}"/>')
    assembly_id = 2 + len(parts)
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<metadata name="Title">Metrimade Kobra 3 Max Fan Cage</metadata>'
        '<metadata name="Designer">Original mechanical design with owner-supplied Metrimade artwork</metadata>'
        '<resources>'
        f'<basematerials id="{material_id}">{material_xml}</basematerials>'
        f'{"".join(objects_xml)}'
        f'<object id="{assembly_id}" name="fan_cage_assembly" type="model"><components>{"".join(component_xml)}</components></object>'
        '</resources>'
        f'<build><item objectid="{assembly_id}"/></build></model>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/3D/3dmodel.model" '
        'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("3D/3dmodel.model", model)


def build(output_root: Path) -> dict:
    exports = output_root / "exports"
    reports = output_root / "reports"
    exports.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    source_path = Path(__file__).resolve()
    source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    brand_sha256 = hashlib.sha256(BRAND_SVG.read_bytes()).hexdigest()
    summary: dict = {
        "schema_version": "1.0",
        "tool": "metrimade-voxel-generator",
        "tool_version": "1.1.0",
        "status": "PASS",
        "profile": "draft",
        "generator": "source/generate_fan_cage.py",
        "voxel_pitch_mm": PITCH,
        "inputs": [
            {
                "path": "source/generate_fan_cage.py",
                "sha256": source_sha256,
                "size_bytes": source_path.stat().st_size,
            },
            {
                "path": "assets/metrimade-lockup-horizontal-color.svg",
                "sha256": brand_sha256,
                "size_bytes": BRAND_SVG.stat().st_size,
            },
        ],
        "checks": [{
            "id": "generated-mesh-invariants",
            "required": True,
            "status": "PASS",
            "message": "All generated bodies have zero boundary/nonmanifold edges and positive signed volume",
            "metrics": {"voxel_pitch_mm": PITCH},
            "evidence": [],
        }],
        "limitations": [
            "Voxel invariants do not replace destination-slicer review or a physical fit coupon.",
            "Published manufacturer evidence does not include the raised bezel diameter.",
        ],
        "variants": {},
    }

    for diameter in (50.0, 52.0, 54.0):
        occs, design_meta = make_occupancy(diameter)
        single_mesh = occupancy_to_mesh(occs["single"])
        single_path = exports / f"fan_cage_singlecolor_D{int(diameter)}.stl"
        write_binary_stl(single_path, single_mesh, f"fan_cage_singlecolor_D{int(diameter)}")
        metrics = mesh_metrics(single_mesh)
        if not metrics["watertight_by_edge_count"] or metrics["signed_volume_mm3"] <= 0:
            raise RuntimeError(f"Mesh invariant failed for D{diameter}: {metrics}")

        coupon_occs, _ = make_occupancy(diameter, fit_coupon=True)
        coupon_mesh = occupancy_to_mesh(coupon_occs["single"])
        coupon_path = exports / f"clip_fit_test_D{int(diameter)}.stl"
        write_binary_stl(coupon_path, coupon_mesh, f"clip_fit_test_D{int(diameter)}")
        coupon_metrics = mesh_metrics(coupon_mesh)
        if not coupon_metrics["watertight_by_edge_count"] or coupon_metrics["signed_volume_mm3"] <= 0:
            raise RuntimeError(f"Coupon mesh invariant failed for D{diameter}: {coupon_metrics}")

        summary["variants"][f"D{int(diameter)}"] = {
            "target_bezel_diameter_mm": diameter,
            "singlecolor_stl": str(single_path.relative_to(output_root)),
            "singlecolor_metrics": metrics,
            "fit_test_stl": str(coupon_path.relative_to(output_root)),
            "fit_test_metrics": coupon_metrics,
            "design": design_meta,
        }

        multicolor_meshes: dict[str, Mesh] = {}
        multicolor_key = f"multicolor_D{int(diameter)}"
        for name in ("body_navy", "brand_teal", "brand_aqua", "brand_sand"):
            mesh = occupancy_to_mesh(occs[name])
            metrics_part = mesh_metrics(mesh)
            if not metrics_part["watertight_by_edge_count"] or metrics_part["signed_volume_mm3"] <= 0:
                raise RuntimeError(f"Color mesh invariant failed for D{diameter} {name}: {metrics_part}")
            part_path = exports / f"fan_cage_D{int(diameter)}_{name}.stl"
            write_binary_stl(part_path, mesh, name)
            multicolor_meshes[name] = mesh
            summary.setdefault(multicolor_key, {})[name] = {
                "stl": str(part_path.relative_to(output_root)),
                "metrics": metrics_part,
            }

        colors = [
            ("body_navy", BRAND_COLORS["brand_navy"], multicolor_meshes["body_navy"]),
            ("brand_teal", BRAND_COLORS["brand_teal"], multicolor_meshes["brand_teal"]),
            ("brand_aqua", BRAND_COLORS["brand_aqua"], multicolor_meshes["brand_aqua"]),
            ("brand_sand", BRAND_COLORS["brand_sand"], multicolor_meshes["brand_sand"]),
        ]
        three_mf_path = exports / f"fan_cage_metrimade_D{int(diameter)}_multicolor.3mf"
        write_3mf(three_mf_path, colors)
        summary[multicolor_key]["3mf"] = str(three_mf_path.relative_to(output_root))

    report_path = reports / "generator-mesh-report.json"
    report_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    summary = build(args.output_root.resolve())
    print(json.dumps({
        "status": "PASS",
        "report": "reports/generator-mesh-report.json",
        "variants": list(summary["variants"]),
        "multicolor": [summary[f"multicolor_D{diameter}"]["3mf"] for diameter in (50, 52, 54)],
    }, indent=2))


if __name__ == "__main__":
    main()
