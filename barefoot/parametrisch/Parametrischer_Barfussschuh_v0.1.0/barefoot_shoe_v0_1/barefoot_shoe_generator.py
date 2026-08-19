#!/usr/bin/env python3
"""Parametric barefoot shoe generator.

Creates two variants for left and right feet:
1) TPU outsole plus 1:1 textile cutting pattern.
2) TPU outsole plus an integrated open lattice upper as a multi-object 3MF.

The implementation deliberately uses only Python's standard library and NumPy.
All geometry is generated in millimetres. The reference images establish style,
not scale; the foot parameters in config.json control fit.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
from xml.sax.saxutils import escape

import numpy as np


EPS = 1.0e-9


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def smoothstep(x):
    x = clamp(float(x))
    return x * x * (3.0 - 2.0 * x)


def smootherstep(x):
    x = clamp(float(x))
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


def periodic_distance(value: float, period: float) -> float:
    """Distance to the nearest multiple of period."""
    if period <= 0:
        return 1.0e9
    r = value % period
    return min(r, period - r)


def hermite_interp(xs: Sequence[float], ys: Sequence[float], x: float) -> float:
    """Small monotone-ish cubic Hermite interpolator without SciPy."""
    xa = np.asarray(xs, dtype=float)
    ya = np.asarray(ys, dtype=float)
    x = float(x)
    if x <= xa[0]:
        return float(ya[0])
    if x >= xa[-1]:
        return float(ya[-1])
    k = int(np.searchsorted(xa, x) - 1)
    k = max(0, min(k, len(xa) - 2))
    dx = xa[k + 1] - xa[k]
    t = (x - xa[k]) / dx
    m = np.zeros_like(ya)
    m[0] = (ya[1] - ya[0]) / (xa[1] - xa[0])
    m[-1] = (ya[-1] - ya[-2]) / (xa[-1] - xa[-2])
    for i in range(1, len(ya) - 1):
        m[i] = (ya[i + 1] - ya[i - 1]) / (xa[i + 1] - xa[i - 1])
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return float(h00 * ya[k] + h10 * dx * m[k] + h01 * ya[k + 1] + h11 * dx * m[k + 1])


def normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < EPS:
        return np.array([0.0, 0.0, 1.0], dtype=float)
    return v / n


@dataclass
class Mesh:
    name: str
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    faces: List[Tuple[int, int, int]] = field(default_factory=list)

    def add_vertex(self, p: Iterable[float]) -> int:
        q = tuple(float(x) for x in p)
        self.vertices.append(q)
        return len(self.vertices) - 1

    def add_face(self, a: int, b: int, c: int):
        if a != b and b != c and c != a:
            self.faces.append((int(a), int(b), int(c)))

    def add_mesh(self, other: "Mesh"):
        offset = len(self.vertices)
        self.vertices.extend(other.vertices)
        self.faces.extend((a + offset, b + offset, c + offset) for a, b, c in other.faces)

    def arrays(self):
        return np.asarray(self.vertices, dtype=float), np.asarray(self.faces, dtype=np.int64)

    def cleanup(self):
        if not self.faces:
            return
        used = sorted({i for f in self.faces for i in f})
        remap = {old: new for new, old in enumerate(used)}
        self.vertices = [self.vertices[i] for i in used]
        self.faces = [tuple(remap[i] for i in f) for f in self.faces]
        self._orient_components()

    def _orient_components(self):
        """Make adjacent triangles consistent, then make each closed component positive-volume."""
        if not self.faces:
            return
        faces = [list(f) for f in self.faces]
        edge_map = defaultdict(list)
        for fi, f in enumerate(faces):
            for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
                edge_map[tuple(sorted((a, b)))].append((fi, a, b))
        adj = defaultdict(list)
        for entries in edge_map.values():
            if len(entries) == 2:
                (f0, a0, b0), (f1, a1, b1) = entries
                same = (a0 == a1 and b0 == b1)
                adj[f0].append((f1, same))
                adj[f1].append((f0, same))
        visited = set()
        components = []
        for seed in range(len(faces)):
            if seed in visited:
                continue
            comp = []
            flip = {seed: False}
            q = deque([seed])
            visited.add(seed)
            while q:
                f0 = q.popleft()
                comp.append(f0)
                for f1, same in adj[f0]:
                    wanted = flip[f0] ^ same
                    if f1 not in flip:
                        flip[f1] = wanted
                    if f1 not in visited:
                        visited.add(f1)
                        q.append(f1)
            for fi in comp:
                if flip.get(fi, False):
                    faces[fi][1], faces[fi][2] = faces[fi][2], faces[fi][1]
            components.append(comp)
        verts = np.asarray(self.vertices, dtype=float)
        for comp in components:
            vol = 0.0
            for fi in comp:
                a, b, c = (verts[i] for i in faces[fi])
                vol += float(np.dot(a, np.cross(b, c))) / 6.0
            if vol < 0:
                for fi in comp:
                    faces[fi][1], faces[fi][2] = faces[fi][2], faces[fi][1]
        self.faces = [tuple(f) for f in faces]


def mesh_edge_audit(mesh: Mesh) -> Dict:
    verts, faces = mesh.arrays()
    edge_counts = defaultdict(int)
    degenerates = 0
    area_min = float("inf")
    for f in faces:
        a, b, c = verts[f]
        area = 0.5 * float(np.linalg.norm(np.cross(b - a, c - a)))
        area_min = min(area_min, area)
        if area < 1.0e-8:
            degenerates += 1
        for i, j in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edge_counts[tuple(sorted((int(i), int(j))))] += 1
    boundary = sum(1 for n in edge_counts.values() if n == 1)
    nonmanifold = sum(1 for n in edge_counts.values() if n > 2)
    volume = 0.0
    for f in faces:
        a, b, c = verts[f]
        volume += float(np.dot(a, np.cross(b, c))) / 6.0
    bbox_min = verts.min(axis=0) if len(verts) else np.zeros(3)
    bbox_max = verts.max(axis=0) if len(verts) else np.zeros(3)

    # Face components through shared manifold edges.
    edge_faces = defaultdict(list)
    for fi, f in enumerate(faces):
        for i, j in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edge_faces[tuple(sorted((int(i), int(j))))].append(fi)
    adj = defaultdict(set)
    for fs in edge_faces.values():
        for a in fs:
            for b in fs:
                if a != b:
                    adj[a].add(b)
    seen = set()
    components = 0
    for seed in range(len(faces)):
        if seed in seen:
            continue
        components += 1
        stack = [seed]
        seen.add(seed)
        while stack:
            f0 = stack.pop()
            for f1 in adj[f0]:
                if f1 not in seen:
                    seen.add(f1)
                    stack.append(f1)
    return {
        "name": mesh.name,
        "vertices": int(len(verts)),
        "triangles": int(len(faces)),
        "components": int(components),
        "boundary_edges": int(boundary),
        "nonmanifold_edges": int(nonmanifold),
        "degenerate_triangles": int(degenerates),
        "minimum_triangle_area_mm2": 0.0 if area_min == float("inf") else area_min,
        "watertight_by_edge_count": bool(boundary == 0 and nonmanifold == 0),
        "signed_volume_mm3": volume,
        "bbox_min_mm": bbox_min.tolist(),
        "bbox_max_mm": bbox_max.tolist(),
        "size_mm": (bbox_max - bbox_min).tolist(),
    }


def best_square_bed_fit(mesh: Mesh) -> Dict:
    pts = np.asarray(mesh.vertices, dtype=float)[:, :2]
    best = None
    for angle in np.linspace(0.0, 90.0, 901):
        a = math.radians(float(angle))
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        q = pts @ rot.T
        size = q.max(axis=0) - q.min(axis=0)
        score = float(max(size))
        if best is None or score < best[0]:
            best = (score, float(angle), float(size[0]), float(size[1]))
    return {
        "rotation_deg": best[1],
        "rotated_bbox_xy_mm": [best[2], best[3]],
        "minimum_square_bed_mm_without_brim": best[0],
        "fits_250x250_without_brim": best[0] <= 250.0,
        "fits_220x220_without_brim": best[0] <= 220.0,
    }


def write_binary_stl(mesh: Mesh, path: Path):
    verts, faces = mesh.arrays()
    header = ("Barefoot shoe parametric mesh: " + mesh.name).encode("ascii", "replace")[:80]
    header = header + b" " * (80 - len(header))
    with path.open("wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", len(faces)))
        for f in faces:
            a, b, c = verts[f]
            n = normalize(np.cross(b - a, c - a)).astype(np.float32)
            fh.write(struct.pack("<3f", *n))
            for p in (a, b, c):
                fh.write(struct.pack("<3f", *p.astype(np.float32)))
            fh.write(struct.pack("<H", 0))


def write_obj(meshes: Sequence[Tuple[Mesh, str]], path: Path):
    with path.open("w", encoding="utf-8") as fh:
        fh.write("# Parametric barefoot shoe preview, units mm\n")
        fh.write(f"mtllib {path.with_suffix('.mtl').name}\n")
        offset = 1
        for mesh, material in meshes:
            fh.write(f"o {mesh.name}\nusemtl {material}\n")
            for x, y, z in mesh.vertices:
                fh.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
            for a, b, c in mesh.faces:
                fh.write(f"f {a+offset} {b+offset} {c+offset}\n")
            offset += len(mesh.vertices)
    mtl = path.with_suffix(".mtl")
    with mtl.open("w", encoding="utf-8") as fh:
        fh.write("newmtl orange_tpu\nKd 1.0 0.25 0.015\nKs 0.12 0.12 0.12\nNs 18\n")
        fh.write("newmtl black_tpu\nKd 0.025 0.025 0.028\nKs 0.10 0.10 0.10\nNs 12\n")


def _mesh_xml(mesh: Mesh) -> str:
    verts = "".join(f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in mesh.vertices)
    tris = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
    return f"<mesh><vertices>{verts}</vertices><triangles>{tris}</triangles></mesh>"


def write_3mf(objects: Sequence[Tuple[Mesh, int, str]], path: Path):
    """Write a compact multi-object 3MF. Material index 0=orange, 1=black."""
    resources = [
        '<basematerials id="1"><base name="Orange TPU" displaycolor="#FF6500FF"/>'
        '<base name="Black TPU" displaycolor="#171719FF"/></basematerials>'
    ]
    build = []
    for oid, (mesh, material_index, label) in enumerate(objects, start=2):
        resources.append(
            f'<object id="{oid}" type="model" name="{escape(label)}" pid="1" pindex="{material_index}">'
            f"{_mesh_xml(mesh)}</object>"
        )
        build.append(f'<item objectid="{oid}"/>')
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="de-DE" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        f"<resources>{''.join(resources)}</resources><build>{''.join(build)}</build></model>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("3D/3dmodel.model", model)


class FootGeometry:
    """Parametric foot/sole envelope with an intentionally wide toe box."""

    def __init__(self, side: str, foot: Dict, fit: Dict, sole_cfg: Dict):
        self.side = side
        self.foot = foot
        self.fit = fit
        self.sole_cfg = sole_cfg
        self.foot_length = float(foot["foot_length_mm"])
        self.length = self.foot_length + float(fit["toe_clearance_mm"]) + float(fit["heel_clearance_mm"])
        self.ball_width = float(foot["ball_width_mm"])
        self.heel_width = float(foot["heel_width_mm"])
        self.edge_margin = float(fit["edge_margin_mm"])
        self.hand = 1.0 if side == "left" else -1.0
        self.ball_u = (
            float(fit["toe_clearance_mm"]) + self.foot_length - float(foot["heel_to_ball_mm"])
        ) / self.length

    def raw_bounds(self, u: float) -> Tuple[float, float]:
        """Return lateral/medial y bounds before left/right mirroring."""
        u = clamp(u)
        # Station 0 = toe. The wide early stations preserve toe splay instead of
        # tapering all toes toward a fashion-shoe point.
        bu = clamp(self.ball_u, 0.24, 0.38)
        stations = [0.0, 0.025, 0.085, 0.17, bu, 0.43, 0.56, 0.70, 0.84, 0.94, 1.0]
        ball_half = 0.5 * (self.ball_width + 2.0 * self.edge_margin)
        heel_half = 0.5 * (self.heel_width + 2.0 * self.edge_margin)
        toe_splay = float(self.foot.get("toe_splay_mm", 0.0))
        bias = float(self.foot.get("big_toe_bias_mm", 0.0))
        medial = np.array([
            6.0,
            0.61 * ball_half,
            0.92 * ball_half + 0.7 * toe_splay,
            0.99 * ball_half + toe_splay,
            1.00 * ball_half,
            0.94 * ball_half,
            0.79 * ball_half,
            0.60 * ball_half,
            0.52 * heel_half,
            0.78 * heel_half,
            6.0,
        ])
        lateral = -np.array([
            6.0,
            0.54 * ball_half,
            0.82 * ball_half,
            0.94 * ball_half,
            1.00 * ball_half,
            0.96 * ball_half,
            0.84 * ball_half,
            0.66 * ball_half,
            0.62 * heel_half,
            0.82 * heel_half,
            6.0,
        ])
        # A small medial shift keeps the big-toe line straighter and avoids a
        # symmetric, pointed last. Mirror it for the opposite foot.
        shift = bias * math.exp(-((u - 0.17) / 0.19) ** 2)
        lo = hermite_interp(stations, lateral, u) + shift
        hi = hermite_interp(stations, medial, u) + shift
        if self.hand > 0:
            return lo, hi
        return -hi, -lo

    def bounds(self, x_or_u: float, normalized: bool = False) -> Tuple[float, float]:
        u = float(x_or_u) if normalized else float(x_or_u) / self.length
        return self.raw_bounds(u)

    def center_halfwidth(self, u: float) -> Tuple[float, float]:
        lo, hi = self.raw_bounds(u)
        return 0.5 * (lo + hi), 0.5 * (hi - lo)

    def y_at(self, u: float, t: float) -> float:
        lo, hi = self.raw_bounds(u)
        return lo + clamp(t) * (hi - lo)

    def rim_height(self, u: float) -> float:
        s = self.sole_cfg
        side = float(s["rim_side_height_mm"])
        toe = float(s["rim_toe_height_mm"])
        heel = float(s["rim_heel_height_mm"])
        toe_w = math.exp(-((u - 0.035) / 0.13) ** 2)
        heel_w = math.exp(-((u - 0.97) / 0.13) ** 2)
        return side + (toe - side) * toe_w + (heel - side) * heel_w

    def footbed_base(self, u: float) -> float:
        s = self.sole_cfg
        toe_spring = float(s["toe_spring_mm"]) * (1.0 - smoothstep(u / 0.13))
        return float(s["footbed_thickness_mm"]) + toe_spring

    def top_z(self, u: float, t: float, include_channels: bool = True) -> float:
        s = self.sole_cfg
        edge_proximity = 1.0 - min(clamp(t), 1.0 - clamp(t)) * 2.0  # 1 edge, 0 centre
        rim_frac = clamp((edge_proximity - 0.72) / 0.28)
        z = self.footbed_base(u) + self.rim_height(u) * smootherstep(rim_frac)
        # Shallow curved glue seat inside the foxing wall; this gives textile a
        # repeatable bonding land and gives the printed upper overlap volume.
        if 0.68 < edge_proximity < 0.86:
            q = 1.0 - abs(edge_proximity - 0.77) / 0.09
            z -= float(s["glue_seat_depth_mm"]) * smootherstep(q)
        if include_channels and edge_proximity < 0.60:
            depth = float(s["footbed_channel_depth_mm"])
            # Longitudinal S-channels plus four cross vents. They are shallow,
            # blind grooves: ventilation without perforating the outsole.
            t_curve = t + 0.035 * math.sin(2.0 * math.pi * (u + 0.13))
            channel = 0.0
            for tc in (0.25, 0.41, 0.59, 0.75):
                d = abs(t_curve - tc)
                channel = max(channel, smootherstep((0.020 - d) / 0.020))
            for uc in (0.22, 0.35, 0.49, 0.63):
                d = abs(u - uc - 0.025 * (t - 0.5))
                channel = max(channel, 0.75 * smootherstep((0.012 - d) / 0.012))
            z -= depth * channel
        return z

    def bottom_z(self, u: float, t: float) -> float:
        """Recessed zoned tread. Zero is the broad contact plane."""
        s = self.sole_cfg
        lo, hi = self.raw_bounds(u)
        y = lo + t * (hi - lo)
        edge_proximity = 1.0 - min(clamp(t), 1.0 - clamp(t)) * 2.0
        gate = smoothstep((0.88 - edge_proximity) / 0.20)
        x = u * self.length
        pitch = 8.5
        if u < 0.43:
            d = periodic_distance(0.72 * x + 1.0 * y, pitch)
            d2 = periodic_distance(0.72 * x - 1.0 * y + 0.48 * pitch, pitch * 1.35)
            pattern = max(smootherstep((1.1 - d) / 1.1), 0.45 * smootherstep((0.9 - d2) / 0.9))
        elif u < 0.66:
            d1 = periodic_distance(0.65 * x + y, 7.5)
            d2 = periodic_distance(0.65 * x - y, 7.5)
            pattern = max(smootherstep((0.9 - d1) / 0.9), smootherstep((0.9 - d2) / 0.9))
        else:
            d = periodic_distance(0.70 * x - 0.95 * y, pitch)
            pattern = smootherstep((1.15 - d) / 1.15)
        z = float(s["tread_groove_depth_mm"]) * pattern * gate
        # Flex grooves follow the foot rather than cutting straight across it.
        flex = 0.0
        for uc, slope in ((0.20, 0.028), (self.ball_u, -0.032), (0.72, 0.022)):
            d = abs(u - (uc + slope * (t - 0.5)))
            flex = max(flex, smootherstep((0.010 - d) / 0.010))
        z = max(z, float(s["major_flex_groove_depth_mm"]) * flex * gate)
        return min(z, self.footbed_base(u) - 2.8)

    def upper_height(self, u: float) -> float:
        toe_h = float(self.foot["toe_height_mm"]) + 1.5
        instep_h = float(self.foot["instep_height_mm"]) + float(self.fit["sock_allowance_mm"])
        stations = [0.0, 0.04, 0.16, 0.32, 0.48, 0.60, 0.72, 0.84, 0.94, 1.0]
        heights = [7.0, 0.68 * toe_h, toe_h, 1.18 * toe_h, 0.76 * instep_h,
                   instep_h, 1.04 * instep_h, 0.84 * instep_h, 0.90 * instep_h, 0.58 * instep_h]
        return hermite_interp(stations, heights, clamp(u))

    def throat_gap(self, u: float) -> float:
        """Half gap in normalized cross-foot coordinate v (-1..1)."""
        if u < 0.42:
            return 0.0
        if u < 0.72:
            return 0.32 * smoothstep((u - 0.42) / 0.30)
        if u < 0.82:
            return 0.32 + 0.18 * smoothstep((u - 0.72) / 0.10)
        if u < 0.94:
            return 0.50 - 0.20 * smoothstep((u - 0.82) / 0.12)
        return 0.30 * (1.0 - smoothstep((u - 0.94) / 0.06))


def add_grid_surface(mesh: Mesh, points: np.ndarray, top=True) -> np.ndarray:
    ni, nj, _ = points.shape
    ids = np.empty((ni, nj), dtype=int)
    for i in range(ni):
        for j in range(nj):
            ids[i, j] = mesh.add_vertex(points[i, j])
    for i in range(ni - 1):
        for j in range(nj - 1):
            a, b, c, d = ids[i, j], ids[i + 1, j], ids[i + 1, j + 1], ids[i, j + 1]
            if top:
                mesh.add_face(a, b, c)
                mesh.add_face(a, c, d)
            else:
                mesh.add_face(a, c, b)
                mesh.add_face(a, d, c)
    return ids


def perimeter_normal_xy(geom: FootGeometry, u: float, which: str) -> np.ndarray:
    du = 1.0e-4
    u0, u1 = clamp(u - du), clamp(u + du)
    y0 = geom.raw_bounds(u0)[0 if which == "low" else 1]
    y1 = geom.raw_bounds(u1)[0 if which == "low" else 1]
    tangent = np.array([(u1 - u0) * geom.length, y1 - y0])
    tangent = tangent / max(float(np.linalg.norm(tangent)), EPS)
    if which == "low":
        n = np.array([tangent[1], -tangent[0]])
    else:
        n = np.array([-tangent[1], tangent[0]])
    return n / max(float(np.linalg.norm(n)), EPS)


def generate_sole(geom: FootGeometry) -> Mesh:
    cfg = geom.sole_cfg
    nx, ny = int(cfg["mesh_nx"]), int(cfg["mesh_ny"])
    us = np.linspace(0.0, 1.0, nx)
    ts = np.linspace(0.0, 1.0, ny)
    top = np.zeros((nx, ny, 3), dtype=float)
    bottom = np.zeros_like(top)
    for i, u in enumerate(us):
        lo, hi = geom.raw_bounds(float(u))
        x = float(u) * geom.length
        for j, t in enumerate(ts):
            y = lo + float(t) * (hi - lo)
            top[i, j] = (x, y, geom.top_z(float(u), float(t), True))
            bottom[i, j] = (x, y, geom.bottom_z(float(u), float(t)))
    mesh = Mesh(f"{geom.side}_tpu_outsole")
    top_ids = add_grid_surface(mesh, top, top=True)
    bottom_ids = add_grid_surface(mesh, bottom, top=False)

    # Replace each of the four crude one-quad-thick sides with a curved,
    # subdivided foxing wall. It bulges gently and carries a segmented lower
    # texture inspired by the reference outsole.
    levels = int(cfg.get("sidewall_levels", 5))
    flare = float(cfg["sidewall_bulge_mm"])

    def add_long_side(which: str, j: int):
        rings = np.empty((nx, levels + 1), dtype=int)
        for i, u in enumerate(us):
            base = bottom[i, j].copy()
            cap = top[i, j].copy()
            nxy = perimeter_normal_xy(geom, float(u), which)
            for k in range(levels + 1):
                q = k / levels
                if k == 0:
                    rings[i, k] = bottom_ids[i, j]
                    continue
                if k == levels:
                    rings[i, k] = top_ids[i, j]
                    continue
                p = (1.0 - q) * base + q * cap
                segmented = (0.5 + 0.5 * math.sin(2.0 * math.pi * (22.0 * u + 0.35 * q))) ** 8
                bulge = flare * math.sin(math.pi * q) + 0.42 * segmented * math.exp(-((q - 0.30) / 0.20) ** 2)
                p[:2] += nxy * bulge
                rings[i, k] = mesh.add_vertex(p)
        for i in range(nx - 1):
            for k in range(levels):
                a, b, c, d = rings[i, k], rings[i + 1, k], rings[i + 1, k + 1], rings[i, k + 1]
                mesh.add_face(a, c, b)
                mesh.add_face(a, d, c)
        return rings

    low_rings = add_long_side("low", 0)
    high_rings = add_long_side("high", ny - 1)

    def add_end(i: int, outward_sign: float):
        rings = np.empty((ny, levels + 1), dtype=int)
        for j, t in enumerate(ts):
            base = bottom[i, j].copy()
            cap = top[i, j].copy()
            for k in range(levels + 1):
                q = k / levels
                if k == 0:
                    rings[j, k] = bottom_ids[i, j]
                    continue
                if k == levels:
                    rings[j, k] = top_ids[i, j]
                    continue
                if j == 0:
                    rings[j, k] = low_rings[i, k]
                    continue
                if j == ny - 1:
                    rings[j, k] = high_rings[i, k]
                    continue
                p = (1.0 - q) * base + q * cap
                p[0] += outward_sign * flare * math.sin(math.pi * q)
                rings[j, k] = mesh.add_vertex(p)
        for j in range(ny - 1):
            for k in range(levels):
                a, b, c, d = rings[j, k], rings[j + 1, k], rings[j + 1, k + 1], rings[j, k + 1]
                if i == 0:
                    mesh.add_face(a, b, c)
                    mesh.add_face(a, c, d)
                else:
                    mesh.add_face(a, c, b)
                    mesh.add_face(a, d, c)

    add_end(0, -1.0)
    add_end(nx - 1, 1.0)
    mesh.cleanup()
    return mesh


def surface_point(geom: FootGeometry, u: float, v: float) -> np.ndarray:
    """Approximate shoe-last surface; v=-1..1 from one sole edge to the other."""
    u = clamp(u)
    v = max(-1.0, min(1.0, float(v)))
    center, half = geom.center_halfwidth(u)
    phi = 0.5 * math.pi * v
    y = center + max(half - 1.0, 1.0) * math.sin(phi)
    t = 0.5 * (1.0 + math.sin(phi))
    base = geom.top_z(u, t, include_channels=False) - 0.55
    crown = geom.upper_height(u) * max(0.0, math.cos(phi)) ** 0.72
    return np.array([u * geom.length, y, base + crown], dtype=float)


def surface_frame(geom: FootGeometry, u: float, v: float):
    du, dv = 1.0e-4, 1.0e-4
    pu0 = surface_point(geom, clamp(u - du), v)
    pu1 = surface_point(geom, clamp(u + du), v)
    pv0 = surface_point(geom, u, max(-1.0, v - dv))
    pv1 = surface_point(geom, u, min(1.0, v + dv))
    tu = normalize(pu1 - pu0)
    tv = normalize(pv1 - pv0)
    n = normalize(np.cross(tu, tv))
    if n[2] < 0:
        n = -n
    tv = normalize(np.cross(n, tu))
    return tu, tv, n


def upper_domain(geom: FootGeometry, u: float, v: float) -> bool:
    if u < 0.42:
        return True
    return abs(v) >= geom.throat_gap(u)


def lattice_selected(geom: FootGeometry, cfg: Dict, u: float, v: float) -> bool:
    if not upper_domain(geom, u, v):
        return False
    pitch = float(cfg["lattice_pitch_mm"])
    band = float(cfg["lattice_band_mm"])
    s = u * geom.length
    w = v * 0.52 * (geom.ball_width + 2.0 * geom.edge_margin)
    d1 = periodic_distance(s + 1.28 * w, pitch)
    d2 = periodic_distance(s - 1.28 * w + 0.5 * pitch, pitch)
    lattice = min(d1, d2) <= 0.5 * band
    attach = abs(v) >= 1.0 - float(cfg["attachment_band_fraction"])
    toe_guard = u <= 0.055
    heel_counter = u >= float(cfg["heel_counter_start_fraction"]) and abs(v) >= 0.30
    # Rails connect the diamond field to the closure and make load paths clear.
    rail = abs(abs(v) - 0.62) <= 0.045 and 0.30 <= u <= 0.88
    gap = geom.throat_gap(u)
    border = u >= 0.42 and abs(abs(v) - gap) <= 0.055
    collar = u >= 0.74 and abs(abs(v) - gap) <= 0.075
    heel_cap = u >= 0.965
    return lattice or attach or toe_guard or heel_counter or rail or border or collar or heel_cap


def generate_lattice_upper(geom: FootGeometry, cfg: Dict) -> Mesh:
    nx, nv = int(cfg["mesh_nx"]), int(cfg["mesh_nv"])
    us = np.linspace(0.0, 1.0, nx)
    vs = np.linspace(-1.0, 1.0, nv)
    center = np.empty((nx, nv, 3), dtype=float)
    normals = np.empty_like(center)
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            center[i, j] = surface_point(geom, float(u), float(v))
            normals[i, j] = surface_frame(geom, float(u), float(v))[2]
    thickness = float(cfg["shell_thickness_mm"])
    inner = center - 0.34 * thickness * normals
    outer = center + 0.66 * thickness * normals
    selected = np.zeros((nx - 1, nv - 1), dtype=bool)
    for i in range(nx - 1):
        for j in range(nv - 1):
            uc = 0.5 * (us[i] + us[i + 1])
            vc = 0.5 * (vs[j] + vs[j + 1])
            selected[i, j] = lattice_selected(geom, cfg, float(uc), float(vc))

    # A bitmap lattice can contain two diagonally touching cells. Extruding
    # that exact 2-D topology makes four wall faces meet on one thickness edge,
    # which is non-manifold. Bridge each ambiguous 2x2 case with one cell. The
    # resulting tiny local thickening is below one lattice pitch and improves
    # both mesh validity and physical tear resistance at crossings.
    for _ in range(8):
        additions = []
        for i in range(nx - 2):
            for j in range(nv - 2):
                a = selected[i, j]
                b = selected[i + 1, j]
                c = selected[i, j + 1]
                d = selected[i + 1, j + 1]
                if a and d and not b and not c:
                    additions.append((i + 1, j))
                elif b and c and not a and not d:
                    additions.append((i, j))
        if not additions:
            break
        for i, j in additions:
            selected[i, j] = True

    mesh = Mesh(f"{geom.side}_printed_tpu_lattice_upper")
    outer_ids = np.empty((nx, nv), dtype=int)
    inner_ids = np.empty((nx, nv), dtype=int)
    for i in range(nx):
        for j in range(nv):
            outer_ids[i, j] = mesh.add_vertex(outer[i, j])
            inner_ids[i, j] = mesh.add_vertex(inner[i, j])

    for i in range(nx - 1):
        for j in range(nv - 1):
            if not selected[i, j]:
                continue
            a, b, c, d = outer_ids[i, j], outer_ids[i + 1, j], outer_ids[i + 1, j + 1], outer_ids[i, j + 1]
            mesh.add_face(a, b, c)
            mesh.add_face(a, c, d)
            a, b, c, d = inner_ids[i, j], inner_ids[i + 1, j], inner_ids[i + 1, j + 1], inner_ids[i, j + 1]
            mesh.add_face(a, c, b)
            mesh.add_face(a, d, c)
            # Each boundary between selected/unselected cells is closed with a
            # wall. This yields one real shell with holes, not intersecting rods.
            if i == 0 or not selected[i - 1, j]:
                ao, bo = outer_ids[i, j], outer_ids[i, j + 1]
                ai, bi = inner_ids[i, j], inner_ids[i, j + 1]
                mesh.add_face(ao, bo, bi); mesh.add_face(ao, bi, ai)
            if i == nx - 2 or not selected[i + 1, j]:
                ao, bo = outer_ids[i + 1, j], outer_ids[i + 1, j + 1]
                ai, bi = inner_ids[i + 1, j], inner_ids[i + 1, j + 1]
                mesh.add_face(ao, bi, bo); mesh.add_face(ao, ai, bi)
            if j == 0 or not selected[i, j - 1]:
                ao, bo = outer_ids[i, j], outer_ids[i + 1, j]
                ai, bi = inner_ids[i, j], inner_ids[i + 1, j]
                mesh.add_face(ao, ai, bi); mesh.add_face(ao, bi, bo)
            if j == nv - 2 or not selected[i, j + 1]:
                ao, bo = outer_ids[i, j + 1], outer_ids[i + 1, j + 1]
                ai, bi = inner_ids[i, j + 1], inner_ids[i + 1, j + 1]
                mesh.add_face(ao, bi, ai); mesh.add_face(ao, bo, bi)
    mesh.cleanup()
    return mesh


def generate_eyelet(geom: FootGeometry, cfg: Dict, u: float, sign: float, index: int) -> Mesh:
    gap = geom.throat_gap(u)
    v = sign * min(0.90, gap + 0.075)
    centre = surface_point(geom, u, v)
    tu, tv, n = surface_frame(geom, u, v)
    ro = 0.5 * float(cfg["lace_eyelet_outer_diameter_mm"])
    ri = 0.5 * float(cfg["lace_eyelet_hole_diameter_mm"])
    thick = float(cfg["lace_eyelet_thickness_mm"])
    seg = 24
    mesh = Mesh(f"{geom.side}_eyelet_{index:02d}")
    ids = np.empty((2, 2, seg), dtype=int)  # normal side, inner/outer, angle
    for zside, nz in enumerate((-0.60 * thick, 0.40 * thick)):
        for radial, r in enumerate((ri, ro)):
            for k in range(seg):
                a = 2.0 * math.pi * k / seg
                p = centre + tu * (r * math.cos(a)) + tv * (r * math.sin(a)) + n * nz
                ids[zside, radial, k] = mesh.add_vertex(p)
    for k in range(seg):
        q = (k + 1) % seg
        # outer wall
        a, b, c, d = ids[0, 1, k], ids[0, 1, q], ids[1, 1, q], ids[1, 1, k]
        mesh.add_face(a, b, c); mesh.add_face(a, c, d)
        # inner wall
        a, b, c, d = ids[0, 0, k], ids[1, 0, k], ids[1, 0, q], ids[0, 0, q]
        mesh.add_face(a, b, c); mesh.add_face(a, c, d)
        # bottom and top annulus
        a, b, c, d = ids[0, 0, k], ids[0, 0, q], ids[0, 1, q], ids[0, 1, k]
        mesh.add_face(a, b, c); mesh.add_face(a, c, d)
        a, b, c, d = ids[1, 0, k], ids[1, 1, k], ids[1, 1, q], ids[1, 0, q]
        mesh.add_face(a, b, c); mesh.add_face(a, c, d)
    mesh.cleanup()
    return mesh


def resolve_diagonal_cell_contacts(selected: np.ndarray) -> np.ndarray:
    selected = selected.copy()
    ni, nj = selected.shape
    for _ in range(8):
        additions = []
        for i in range(ni - 1):
            for j in range(nj - 1):
                a, b = selected[i, j], selected[i + 1, j]
                c, d = selected[i, j + 1], selected[i + 1, j + 1]
                if a and d and not b and not c:
                    additions.append((i + 1, j))
                elif b and c and not a and not d:
                    additions.append((i, j))
        if not additions:
            return selected
        for i, j in additions:
            selected[i, j] = True
    return selected


def generate_flat_lattice_coupon(cfg: Dict) -> Mesh:
    """60 x 48 mm coupon for lattice bonding, flex and tear tests."""
    width, height = 60.0, 48.0
    nx, ny = 31, 25
    xs, ys = np.linspace(0, width, nx), np.linspace(0, height, ny)
    selected = np.zeros((nx - 1, ny - 1), dtype=bool)
    pitch = float(cfg["lattice_pitch_mm"])
    band = float(cfg["lattice_band_mm"])
    for i in range(nx - 1):
        for j in range(ny - 1):
            x = 0.5 * (xs[i] + xs[i + 1])
            y = 0.5 * (ys[j] + ys[j + 1])
            d1 = periodic_distance(x + y, pitch)
            d2 = periodic_distance(x - y + 0.5 * pitch, pitch)
            border = min(x, width - x, y, height - y) < 4.2
            selected[i, j] = border or min(d1, d2) <= 0.5 * band
    selected = resolve_diagonal_cell_contacts(selected)
    t = float(cfg["shell_thickness_mm"])
    mesh = Mesh("flat_tpu_lattice_coupon")
    top = np.empty((nx, ny), dtype=int)
    bottom = np.empty((nx, ny), dtype=int)
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            bottom[i, j] = mesh.add_vertex((x, y, 0.0))
            top[i, j] = mesh.add_vertex((x, y, t))
    for i in range(nx - 1):
        for j in range(ny - 1):
            if not selected[i, j]:
                continue
            a, b, c, d = top[i, j], top[i + 1, j], top[i + 1, j + 1], top[i, j + 1]
            mesh.add_face(a, b, c); mesh.add_face(a, c, d)
            a, b, c, d = bottom[i, j], bottom[i + 1, j], bottom[i + 1, j + 1], bottom[i, j + 1]
            mesh.add_face(a, c, b); mesh.add_face(a, d, c)
            if i == 0 or not selected[i - 1, j]:
                ao, bo, ai, bi = top[i, j], top[i, j + 1], bottom[i, j], bottom[i, j + 1]
                mesh.add_face(ao, bo, bi); mesh.add_face(ao, bi, ai)
            if i == nx - 2 or not selected[i + 1, j]:
                ao, bo, ai, bi = top[i + 1, j], top[i + 1, j + 1], bottom[i + 1, j], bottom[i + 1, j + 1]
                mesh.add_face(ao, bi, bo); mesh.add_face(ao, ai, bi)
            if j == 0 or not selected[i, j - 1]:
                ao, bo, ai, bi = top[i, j], top[i + 1, j], bottom[i, j], bottom[i + 1, j]
                mesh.add_face(ao, ai, bi); mesh.add_face(ao, bi, bo)
            if j == ny - 2 or not selected[i, j + 1]:
                ao, bo, ai, bi = top[i, j + 1], top[i + 1, j + 1], bottom[i, j + 1], bottom[i + 1, j + 1]
                mesh.add_face(ao, bi, ai); mesh.add_face(ao, bo, bi)
    mesh.cleanup()
    return mesh


def generate_planar_eyelet_coupon(cfg: Dict) -> Mesh:
    ro = 0.5 * float(cfg["lace_eyelet_outer_diameter_mm"])
    ri = 0.5 * float(cfg["lace_eyelet_hole_diameter_mm"])
    thick = float(cfg["lace_eyelet_thickness_mm"])
    centre = np.array([30.0, 24.0, 0.65 * thick])
    seg = 32
    mesh = Mesh("flat_tpu_eyelet_coupon_reinforcement")
    ids = np.empty((2, 2, seg), dtype=int)
    for zs, z in enumerate((-0.45 * thick, 0.55 * thick)):
        for radial, r in enumerate((ri, ro)):
            for k in range(seg):
                a = 2 * math.pi * k / seg
                ids[zs, radial, k] = mesh.add_vertex(centre + np.array([r * math.cos(a), r * math.sin(a), z]))
    for k in range(seg):
        q = (k + 1) % seg
        for radial, reverse in ((1, False), (0, True)):
            a, b, c, d = ids[0, radial, k], ids[0, radial, q], ids[1, radial, q], ids[1, radial, k]
            if reverse:
                mesh.add_face(a, c, b); mesh.add_face(a, d, c)
            else:
                mesh.add_face(a, b, c); mesh.add_face(a, c, d)
        a, b, c, d = ids[0, 0, k], ids[0, 0, q], ids[0, 1, q], ids[0, 1, k]
        mesh.add_face(a, b, c); mesh.add_face(a, c, d)
        a, b, c, d = ids[1, 0, k], ids[1, 1, k], ids[1, 1, q], ids[1, 0, q]
        mesh.add_face(a, b, c); mesh.add_face(a, c, d)
    mesh.cleanup()
    return mesh


def upper_cross_arc(geom: FootGeometry, u: float, sign: float, v_top: float, samples=80) -> float:
    v_edge = -1.0 if sign < 0 else 1.0
    values = np.linspace(v_edge, v_top, samples)
    pts = np.asarray([surface_point(geom, u, float(v)) for v in values])
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def panel_curves(geom: FootGeometry, sign: float, textile_cfg: Dict):
    us = np.linspace(0.0, 1.0, 121)
    xs, top = [], []
    for u in us:
        gap = geom.throat_gap(float(u))
        if u < 0.42:
            v_top = 0.0
        else:
            v_top = sign * gap
        arc = upper_cross_arc(geom, float(u), sign, float(v_top))
        xs.append(float(u) * geom.length)
        top.append(arc + float(textile_cfg["seam_allowance_mm"]))
    bottom = [-float(textile_cfg["bottom_glue_allowance_mm"])] * len(xs)
    return np.asarray(xs), np.asarray(bottom), np.asarray(top)


def svg_polyline(points, style):
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{p}" style="{style}"/>'


def write_textile_pattern_svg(geom: FootGeometry, cfg: Dict, path: Path):
    spacing = float(cfg["pattern_spacing_mm"])
    panels = []
    max_h = 0.0
    for sign, label in ((-1.0, "Außen/Lateral"), (1.0, "Innen/Medial")):
        xs, bottom, top = panel_curves(geom, sign, cfg)
        poly = list(zip(xs, bottom)) + list(zip(xs[::-1], top[::-1])) + [(xs[0], bottom[0])]
        panels.append((poly, xs, top, sign, label))
        max_h = max(max_h, float(top.max() - bottom.min()))
    tongue_l = float(cfg["tongue_length_mm"])
    tongue_w = max(float(cfg["tongue_width_bottom_mm"]), float(cfg["tongue_width_top_mm"]))
    canvas_w = geom.length + 80.0
    canvas_h = 2 * max_h + tongue_l + 4 * spacing + 90.0
    cut_style = "fill:none;stroke:#d32f2f;stroke-width:0.45"
    sew_style = "fill:none;stroke:#1565c0;stroke-width:0.35;stroke-dasharray:3,2"
    mark_style = "fill:none;stroke:#333;stroke-width:0.3"
    items = []
    items.append(f'<rect x="15" y="15" width="50" height="50" style="{mark_style}"/>')
    items.append('<text x="15" y="78" font-size="5">Kontrollquadrat 50 x 50 mm</text>')
    y0 = 95.0
    eyelet_us = (0.49, 0.57, 0.65, 0.73)
    for poly, xs, top, sign, label in panels:
        shifted = [(x + 35.0, y0 + max_h - y) for x, y in poly]
        items.append(svg_polyline(shifted, cut_style))
        # stitch/glue reference line 8 mm above the lower cut edge
        ref = [(x + 35.0, y0 + max_h - (-4.0)) for x in xs]
        items.append(svg_polyline(ref, sew_style))
        for eu in eyelet_us:
            idx = int(round(eu * (len(xs) - 1)))
            ex = xs[idx] + 35.0
            ey = y0 + max_h - (top[idx] - 9.0)
            items.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="2.0" style="{mark_style}"/>')
        items.append(f'<text x="40" y="{y0 + 8:.2f}" font-size="6">{escape(geom.side.upper())}: {label} – 1x zuschneiden</text>')
        items.append(f'<text x="40" y="{y0 + 16:.2f}" font-size="4.5">Rot = Schnitt, Blau = Klebe-/Nahtreferenz; Pfeilrichtung Zehe → Ferse</text>')
        items.append(f'<line x1="55" y1="{y0 + 24:.2f}" x2="115" y2="{y0 + 24:.2f}" stroke="#111" stroke-width="0.6" marker-end="url(#arrow)"/>')
        y0 += max_h + spacing

    # Rounded trapezoid tongue.
    tb, tt = float(cfg["tongue_width_bottom_mm"]), float(cfg["tongue_width_top_mm"])
    tx, ty = 35.0, y0 + 8.0
    tongue = [(tx + 0.5 * (tt - tb), ty + tongue_l), (tx, ty + 10), (tx + 4, ty),
              (tx + tt - 4, ty), (tx + tt, ty + 10), (tx + 0.5 * (tt + tb), ty + tongue_l),
              (tx + 0.5 * (tt - tb), ty + tongue_l)]
    items.append(svg_polyline(tongue, cut_style))
    items.append(f'<text x="{tx:.2f}" y="{ty - 5:.2f}" font-size="6">Zunge – 1x, optional gedoppelt</text>')
    # Heel counter overlay and pull tab.
    hx = tx + tt + spacing
    heel_w, heel_h = 118.0, 55.0
    heel = [(hx, ty + heel_h), (hx + 8, ty + 7), (hx + 18, ty), (hx + heel_w - 18, ty),
            (hx + heel_w - 8, ty + 7), (hx + heel_w, ty + heel_h), (hx, ty + heel_h)]
    items.append(svg_polyline(heel, cut_style))
    items.append(f'<text x="{hx:.2f}" y="{ty - 5:.2f}" font-size="6">Fersenverstärkung – 1x</text>')
    px = hx + heel_w + spacing
    pl, pw = float(cfg["pull_tab_cut_length_mm"]), float(cfg["pull_tab_width_mm"])
    items.append(f'<rect x="{px:.2f}" y="{ty:.2f}" width="{pw:.2f}" height="{pl:.2f}" rx="4" style="{cut_style}"/>')
    items.append(f'<text x="{px:.2f}" y="{ty - 5:.2f}" font-size="6">Fersenschlaufe – 1x</text>')
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.1f}mm" height="{canvas_h:.1f}mm" viewBox="0 0 {canvas_w:.1f} {canvas_h:.1f}">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#111"/></marker></defs>
<rect width="100%" height="100%" fill="white"/>
<text x="90" y="34" font-size="10" font-weight="bold">Parametrisches Textil-Schnittmuster – {escape(geom.side.upper())}</text>
<text x="90" y="48" font-size="5.5">Druckmaßstab 100 %, Seitenanpassung AUS. Erst Probemodell aus billigem Stoff fertigen.</text>
{''.join(items)}
</svg>'''
    path.write_text(svg, encoding="utf-8")


def write_insole_template_svg(geom: FootGeometry, path: Path):
    n = 180
    us = np.linspace(0.015, 0.985, n)
    low = []
    high = []
    for u in us:
        lo, hi = geom.raw_bounds(float(u))
        # Insole is inset from the raised rim and glue channel.
        low.append((float(u) * geom.length, lo + 6.0))
        high.append((float(u) * geom.length, hi - 6.0))
    pts = low + high[::-1] + [low[0]]
    min_y = min(y for _, y in pts)
    shifted = [(x + 20.0, y - min_y + 30.0) for x, y in pts]
    width = geom.length + 40.0
    height = max(y for _, y in shifted) + 30.0
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}mm" height="{height:.1f}mm" viewBox="0 0 {width:.1f} {height:.1f}">
<rect width="100%" height="100%" fill="white"/>
<text x="20" y="14" font-size="7" font-weight="bold">Einlegesohlen-Schablone {escape(geom.side.upper())} – 100 % drucken</text>
{svg_polyline(shifted, 'fill:none;stroke:#d32f2f;stroke-width:0.45')}
<rect x="{width-70:.1f}" y="8" width="50" height="50" fill="none" stroke="#333" stroke-width="0.3"/>
<text x="{width-70:.1f}" y="64" font-size="4.5">50-mm-Kontrolle</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def write_measurement_svg(geom: FootGeometry, path: Path):
    n = 180
    us = np.linspace(0.0, 1.0, n)
    low, high = [], []
    for u in us:
        lo, hi = geom.raw_bounds(float(u))
        low.append((float(u) * geom.length, lo))
        high.append((float(u) * geom.length, hi))
    min_y = min(y for _, y in low)
    shift_y = -min_y + 45
    pts = [(x + 40, y + shift_y) for x, y in low + high[::-1] + [low[0]]]
    ball_x = geom.ball_u * geom.length + 40
    lo, hi = geom.raw_bounds(geom.ball_u)
    canvas_w, canvas_h = geom.length + 100, 190
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.1f}mm" height="{canvas_h:.1f}mm" viewBox="0 0 {canvas_w:.1f} {canvas_h:.1f}">
<defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="M0,0 L7,3.5 L0,7 z" fill="#1565c0"/></marker></defs>
<rect width="100%" height="100%" fill="white"/><text x="20" y="18" font-size="8" font-weight="bold">Benötigte Fußmaße – beide Füße separat, belastet messen</text>
{svg_polyline(pts, 'fill:#fafafa;stroke:#111;stroke-width:0.6')}
<line x1="40" y1="155" x2="{40+geom.length:.2f}" y2="155" stroke="#1565c0" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>
<text x="{40+0.35*geom.length:.2f}" y="169" font-size="5.5">1 Fußlänge: längster Zeh bis Ferse</text>
<line x1="{ball_x:.2f}" y1="{lo+shift_y:.2f}" x2="{ball_x:.2f}" y2="{hi+shift_y:.2f}" stroke="#1565c0" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>
<text x="{ball_x+5:.2f}" y="{0.5*(lo+hi)+shift_y:.2f}" font-size="5.5">2 Ballenbreite</text>
<text x="20" y="181" font-size="5">Zusätzlich: Fersenbreite, Ferse–Ballen, Ballenumfang, Ristumfang/-höhe, Zehenhöhe, Knöchelöffnung, Fußumrissfoto mit Lineal.</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def render_simple_svg_preview(svg_path: Path, png_path: Path, width_px=1200):
    """Raster preview for the simple SVG primitives emitted by this generator."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle, Rectangle
    except Exception as exc:
        print(f"SVG preview skipped: {exc}")
        return
    root = ET.parse(svg_path).getroot()
    view = [float(v) for v in root.attrib.get("viewBox", "0 0 100 100").split()]
    _, _, w, h = view
    fig_w = 12.0
    fig_h = max(3.0, fig_w * h / w)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=max(80, int(width_px / fig_w)))

    def colour(style, default="#222"):
        for field in style.split(";"):
            if field.startswith("stroke:"):
                return field.split(":", 1)[1]
        return default

    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        style = elem.attrib.get("style", "")
        c = colour(style, elem.attrib.get("stroke", "#222"))
        if tag == "polyline":
            pts = []
            for token in elem.attrib.get("points", "").split():
                x, y = token.split(",")
                pts.append((float(x), float(y)))
            if pts:
                p = np.asarray(pts)
                ax.plot(p[:, 0], p[:, 1], color=c, linewidth=0.8)
        elif tag == "line":
            ax.plot([float(elem.attrib["x1"]), float(elem.attrib["x2"])],
                    [float(elem.attrib["y1"]), float(elem.attrib["y2"])], color=c, linewidth=0.7)
        elif tag == "circle":
            ax.add_patch(Circle((float(elem.attrib["cx"]), float(elem.attrib["cy"])),
                                float(elem.attrib["r"]), fill=False, edgecolor=c, linewidth=0.7))
        elif tag == "rect" and elem.attrib.get("width") not in ("100%", None):
            ax.add_patch(Rectangle((float(elem.attrib.get("x", 0)), float(elem.attrib.get("y", 0))),
                                   float(elem.attrib["width"]), float(elem.attrib["height"]),
                                   fill=False, edgecolor=c, linewidth=0.7))
        elif tag == "text" and elem.text:
            try:
                fs = max(3.0, float(elem.attrib.get("font-size", 5)) * 0.72)
                ax.text(float(elem.attrib.get("x", 0)), float(elem.attrib.get("y", 0)), elem.text,
                        fontsize=fs, color="#222", va="baseline")
            except ValueError:
                pass
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    plt.tight_layout(pad=0.05)
    fig.savefig(png_path, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def render_preview(meshes: Sequence[Tuple[Mesh, str]], path: Path, view="iso"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    except Exception as exc:
        print(f"Preview skipped: {exc}")
        return
    fig = plt.figure(figsize=(12, 6), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    colours = {
        "orange": np.array([1.00, 0.30, 0.015]),
        "black": np.array([0.17, 0.18, 0.20]),
        "textile": np.array([0.12, 0.13, 0.15]),
    }
    light = normalize(np.array([0.35, -0.55, -0.78 if view == "bottom" else 0.76]))
    all_v = []
    for mesh, colour in meshes:
        v, f = mesh.arrays()
        all_v.append(v)
        step = max(1, len(f) // 26000)
        sf = f[::step]
        triangles = v[sf]
        normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        nn = np.linalg.norm(normals, axis=1)
        normals = normals / np.maximum(nn[:, None], EPS)
        intensity = 0.48 + 0.52 * np.maximum(0.0, normals @ light)
        base = colours.get(colour, np.array([0.5, 0.5, 0.5]))
        face_colours = np.clip(base[None, :] * intensity[:, None], 0.0, 1.0)
        poly = Poly3DCollection(triangles, linewidths=0.0, alpha=1.0)
        poly.set_facecolor(face_colours)
        poly.set_edgecolor("none")
        ax.add_collection3d(poly)
    vv = np.vstack(all_v)
    mn, mx = vv.min(axis=0), vv.max(axis=0)
    ctr = 0.5 * (mn + mx)
    span = max(mx[0]-mn[0], 1.75*(mx[1]-mn[1]), 2.1*(mx[2]-mn[2]))
    ax.set_xlim(ctr[0]-0.52*span, ctr[0]+0.52*span)
    ax.set_ylim(ctr[1]-0.34*span, ctr[1]+0.34*span)
    ax.set_zlim(max(-2, mn[2]-2), max(-2, mn[2]-2)+0.34*span)
    if view == "bottom":
        ax.view_init(elev=-88, azim=-90)
    elif view == "top":
        ax.view_init(elev=88, azim=-90)
    elif view == "side":
        ax.view_init(elev=8, azim=-90)
    else:
        ax.view_init(elev=18, azim=-118)
    ax.set_proj_type("ortho")
    ax.set_axis_off()
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    plt.tight_layout(pad=0)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def make_smooth_textile_preview_upper(geom: FootGeometry) -> Mesh:
    """Appearance-only smooth shell used only in the textile concept render."""
    nx, nv, thickness = 90, 39, 0.65
    us, vs = np.linspace(0, 1, nx), np.linspace(-1, 1, nv)
    centre = np.asarray([[surface_point(geom, float(u), float(v)) for v in vs] for u in us])
    normals = np.asarray([[surface_frame(geom, float(u), float(v))[2] for v in vs] for u in us])
    outer = centre + 0.5 * thickness * normals
    inner = centre - 0.5 * thickness * normals
    selected = np.zeros((nx - 1, nv - 1), dtype=bool)
    for i in range(nx - 1):
        for j in range(nv - 1):
            u = 0.5 * (us[i] + us[i + 1])
            v = 0.5 * (vs[j] + vs[j + 1])
            selected[i, j] = upper_domain(geom, float(u), float(v))
    mesh = Mesh(f"{geom.side}_textile_upper_preview_only")
    out_ids = np.empty((nx, nv), dtype=int)
    in_ids = np.empty((nx, nv), dtype=int)
    for i in range(nx):
        for j in range(nv):
            out_ids[i, j] = mesh.add_vertex(outer[i, j])
            in_ids[i, j] = mesh.add_vertex(inner[i, j])
    for i in range(nx - 1):
        for j in range(nv - 1):
            if not selected[i, j]:
                continue
            a, b, c, d = out_ids[i, j], out_ids[i + 1, j], out_ids[i + 1, j + 1], out_ids[i, j + 1]
            mesh.add_face(a, b, c); mesh.add_face(a, c, d)
            a, b, c, d = in_ids[i, j], in_ids[i + 1, j], in_ids[i + 1, j + 1], in_ids[i, j + 1]
            mesh.add_face(a, c, b); mesh.add_face(a, d, c)
            if i == 0 or not selected[i - 1, j]:
                ao, bo, ai, bi = out_ids[i, j], out_ids[i, j + 1], in_ids[i, j], in_ids[i, j + 1]
                mesh.add_face(ao, bo, bi); mesh.add_face(ao, bi, ai)
            if i == nx - 2 or not selected[i + 1, j]:
                ao, bo, ai, bi = out_ids[i + 1, j], out_ids[i + 1, j + 1], in_ids[i + 1, j], in_ids[i + 1, j + 1]
                mesh.add_face(ao, bi, bo); mesh.add_face(ao, ai, bi)
            if j == 0 or not selected[i, j - 1]:
                ao, bo, ai, bi = out_ids[i, j], out_ids[i + 1, j], in_ids[i, j], in_ids[i + 1, j]
                mesh.add_face(ao, ai, bi); mesh.add_face(ao, bi, bo)
            if j == nv - 2 or not selected[i, j + 1]:
                ao, bo, ai, bi = out_ids[i, j + 1], out_ids[i + 1, j + 1], in_ids[i, j + 1], in_ids[i + 1, j + 1]
                mesh.add_face(ao, bi, ai); mesh.add_face(ao, bo, bi)
    mesh.cleanup()
    return mesh


def generate_side(side: str, global_cfg: Dict, out_root: Path) -> Dict:
    foot = global_cfg["feet"][side]
    geom = FootGeometry(side, foot, global_cfg["fit"], global_cfg["sole"])
    side_dir = out_root / side
    side_dir.mkdir(parents=True, exist_ok=True)
    textile_dir = side_dir / "textile_variant"
    printed_dir = side_dir / "printed_mesh_variant"
    textile_dir.mkdir(exist_ok=True)
    printed_dir.mkdir(exist_ok=True)

    sole = generate_sole(geom)
    sole_path = textile_dir / f"{side}_tpu_outsole_textile.stl"
    write_binary_stl(sole, sole_path)
    # Same sole geometry is copied as a named manufacturing export for the
    # printed-upper workflow; the 3MF also includes it at exact origin.
    write_binary_stl(sole, printed_dir / f"{side}_tpu_outsole_printed_upper.stl")

    upper = generate_lattice_upper(geom, global_cfg["printed_upper"])
    write_binary_stl(upper, printed_dir / f"{side}_tpu_lattice_upper.stl")
    eyelets = []
    idx = 1
    for u in (0.49, 0.57, 0.65, 0.73):
        for sign in (-1.0, 1.0):
            e = generate_eyelet(geom, global_cfg["printed_upper"], u, sign, idx)
            eyelets.append(e)
            write_binary_stl(e, printed_dir / f"{side}_eyelet_{idx:02d}.stl")
            idx += 1

    upper_vertices = np.asarray(upper.vertices, dtype=float)
    upper_vertices_inside_sole = 0
    for x, y, z in upper_vertices:
        u = x / geom.length
        if not 0.0 <= u <= 1.0:
            continue
        lo, hi = geom.raw_bounds(float(u))
        if not lo <= y <= hi:
            continue
        t = (y - lo) / max(hi - lo, EPS)
        if geom.bottom_z(float(u), float(t)) - 0.1 <= z <= geom.top_z(float(u), float(t), True) + 0.1:
            upper_vertices_inside_sole += 1
    eyelet_overlap_checks = []
    for eyelet in eyelets:
        ev = np.asarray(eyelet.vertices, dtype=float)
        min_dist = float("inf")
        count_close = 0
        for p in ev:
            distances = np.linalg.norm(upper_vertices - p, axis=1)
            min_dist = min(min_dist, float(distances.min()))
            count_close += int(np.count_nonzero(distances < 1.5)) > 0
        eyelet_overlap_checks.append({
            "eyelet": eyelet.name,
            "minimum_vertex_distance_to_upper_mm": min_dist,
            "eyelet_vertices_with_upper_vertex_within_1_5_mm": int(count_close),
            "overlap_proxy_pass": bool(min_dist < 0.75 and count_close >= 8),
        })

    objects = [(sole, 0, f"{side} outsole"), (upper, 1, f"{side} lattice upper")]
    objects += [(e, 1, e.name) for e in eyelets]
    write_3mf(objects, printed_dir / f"{side}_full_printed_barefoot_shoe.3mf")
    write_obj([(sole, "orange_tpu"), (upper, "black_tpu")] + [(e, "black_tpu") for e in eyelets],
              printed_dir / f"{side}_full_printed_barefoot_shoe.obj")

    write_textile_pattern_svg(geom, global_cfg["textile_upper"], textile_dir / f"{side}_textile_cut_pattern_1to1.svg")
    write_insole_template_svg(geom, textile_dir / f"{side}_insole_template_1to1.svg")
    write_measurement_svg(geom, side_dir / f"{side}_measurement_guide.svg")
    textile_visual = make_smooth_textile_preview_upper(geom)
    write_obj([(sole, "orange_tpu"), (textile_visual, "black_tpu")],
              textile_dir / f"{side}_textile_concept_assembly.obj")

    if side == "left":
        render_preview([(sole, "orange"), (upper, "black")] + [(e, "black") for e in eyelets],
                       out_root / "preview_printed_mesh_variant.png", "iso")
        render_preview([(sole, "orange"), (upper, "black")] + [(e, "black") for e in eyelets],
                       out_root / "preview_top_and_closure.png", "top")
        render_preview([(sole, "orange")], out_root / "preview_outsole_bottom.png", "bottom")
        render_preview([(sole, "orange"), (textile_visual, "textile")],
                       out_root / "preview_textile_variant.png", "iso")
        render_simple_svg_preview(textile_dir / f"{side}_textile_cut_pattern_1to1.svg",
                                  out_root / "preview_textile_cut_pattern.png")
        render_simple_svg_preview(textile_dir / f"{side}_insole_template_1to1.svg",
                                  out_root / "preview_insole_template.png", width_px=1000)
        render_simple_svg_preview(side_dir / f"{side}_measurement_guide.svg",
                                  out_root / "preview_measurement_guide.png", width_px=1000)

    audits = [mesh_edge_audit(sole), mesh_edge_audit(upper)] + [mesh_edge_audit(e) for e in eyelets]
    sole_volume = abs(float(audits[0]["signed_volume_mm3"]))
    solid_volume = sum(abs(float(a["signed_volume_mm3"])) for a in audits)
    return {
        "side": side,
        "assumed_foot_parameters": foot,
        "derived": {
            "sole_length_mm": geom.length,
            "maximum_outsole_width_mm": max(geom.raw_bounds(float(u))[1] - geom.raw_bounds(float(u))[0] for u in np.linspace(0, 1, 501)),
            "ball_station_fraction_from_toe": geom.ball_u,
            "solid_geometry_volume_cm3": solid_volume / 1000.0,
            "solid_tpu_mass_estimate_g_at_1_20_g_cm3": solid_volume / 1000.0 * 1.20,
            "sole_only_solid_volume_cm3": sole_volume / 1000.0,
            "sole_only_mass_estimate_g_at_1_20_g_cm3": sole_volume / 1000.0 * 1.20,
            "best_square_bed_fit": best_square_bed_fit(sole),
            "upper_to_sole_overlap_proxy": {
                "upper_vertices_inside_sole_envelope": int(upper_vertices_inside_sole),
                "pass": bool(upper_vertices_inside_sole >= 100),
                "note": "Proxy only; exact slicer union still must be inspected."
            },
            "eyelet_to_upper_overlap_proxies": eyelet_overlap_checks,
        },
        "meshes": audits,
    }


def validate_3mf(path: Path) -> Dict:
    with zipfile.ZipFile(path, "r") as zf:
        names = sorted(zf.namelist())
        model = zf.read("3D/3dmodel.model")
    return {
        "path": str(path),
        "zip_entries": names,
        "model_xml_bytes": len(model),
        "has_core_files": all(x in names for x in ("[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model")),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate parametric barefoot-shoe prototypes")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--output", default="generated")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    out_root = Path(args.output).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    reports = [generate_side(side, cfg, out_root) for side in ("left", "right")]
    coupon_dir = out_root / "test_coupons"
    coupon_dir.mkdir(exist_ok=True)
    coupon = generate_flat_lattice_coupon(cfg["printed_upper"])
    coupon_eyelet = generate_planar_eyelet_coupon(cfg["printed_upper"])
    write_binary_stl(coupon, coupon_dir / "tpu_lattice_coupon.stl")
    write_binary_stl(coupon_eyelet, coupon_dir / "tpu_eyelet_reinforcement_coupon.stl")
    write_3mf([(coupon, 1, coupon.name), (coupon_eyelet, 1, coupon_eyelet.name)],
              coupon_dir / "tpu_lattice_and_eyelet_coupon.3mf")
    coupon_audits = [mesh_edge_audit(coupon), mesh_edge_audit(coupon_eyelet)]
    threemf = []
    for side in ("left", "right"):
        threemf.append(validate_3mf(out_root / side / "printed_mesh_variant" / f"{side}_full_printed_barefoot_shoe.3mf"))
    report = {
        "project": cfg["project"],
        "units": "millimetres",
        "validation_scope": [
            "binary STL structure written deterministically",
            "undirected edge count for watertightness",
            "degenerate-triangle check",
            "signed volume and bounding box",
            "3MF ZIP/core-file check"
        ],
        "not_validated_without_user_profile": [
            "exact slicer toolpaths and print time",
            "TPU bridge/support behaviour",
            "skin comfort, fatigue, abrasion and wet grip",
            "final anatomical fit"
        ],
        "sides": reports,
        "test_coupons": coupon_audits,
        "three_mf": threemf,
    }
    (out_root / "validation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    failed = []
    for sr in reports:
        for m in sr["meshes"]:
            if not m["watertight_by_edge_count"] or m["degenerate_triangles"]:
                failed.append(m["name"])
    for m in coupon_audits:
        if not m["watertight_by_edge_count"] or m["degenerate_triangles"]:
            failed.append(m["name"])
    print(json.dumps({"output": str(out_root), "failed_mesh_checks": failed, "sides": reports}, indent=2, ensure_ascii=False))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
