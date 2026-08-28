#!/usr/bin/env python3
"""Generate the MM-SHO-001 V6.2 direct freeform upper.

The visible upper is evaluated directly from C2 longitudinal splines and smooth
cross-sections.  No voxel grid, distance field, marching cubes, global remesh,
or smoothing modifier is used.  The collar opening is part of the parametric
surface domain and its free edge is closed by an explicit rounded cap.  Solid
terminal plugs follow the same analytic outer surface over a controlled blend
length so the heel and toe cannot expose the inner shell tunnel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import scipy
import trimesh
import yaml
from scipy.interpolate import CubicSpline, PchipInterpolator
from shapely.geometry import GeometryCollection, MultiPolygon, Point, Polygon, box
from shapely.ops import triangulate, unary_union
from shapely.prepared import prep


HERE = Path(__file__).resolve().parent
DEFAULT_PARAMETERS = HERE / "parameters.yaml"
V6_1_CONFIG = HERE.parent / "barfussschuh_v6_1_fitfix" / "v6_config.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def smootherstep(value: np.ndarray | float) -> np.ndarray:
    t = np.clip(np.asarray(value, dtype=float), 0.0, 1.0)
    return t**3 * (t * (t * 6.0 - 15.0) + 10.0)


def polygon_parts(geometry) -> Iterable[Polygon]:
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry]
    if isinstance(geometry, MultiPolygon):
        return list(geometry.geoms)
    if isinstance(geometry, GeometryCollection):
        return [item for item in geometry.geoms if isinstance(item, Polygon)]
    return []


def ellipse_polygon(cy: float, ry: float, rr: float, segments: int) -> Polygon:
    angles = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=False)
    return Polygon([(cy + ry * math.cos(a), rr * math.sin(a)) for a in angles])


def mesh_edges(faces: np.ndarray) -> np.ndarray:
    faces = np.asarray(faces, dtype=np.int64)
    return np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))


@dataclass
class DomainMesh:
    parameters: np.ndarray  # columns: y, section parameter r
    faces: np.ndarray
    boundary_edges: np.ndarray


class FreeformUpper:
    def __init__(self, parameters: dict):
        self.p = parameters
        self.length = float(parameters["fit"]["foot_length"] + parameters["fit"]["toe_clearance"])
        self.inset = float(parameters["fit"]["lower_interface_inset_each_side"])
        self.skirt = float(parameters["fit"]["upper_skirt_height"])
        self.heel_taper = float(parameters["fit"]["upper_heel_taper_ratio"])
        self.toe_taper = float(parameters["fit"]["upper_toe_taper_ratio"])
        self.section_exponent = float(parameters["freeform"]["cross_section_exponent"])
        self.collar_cy = float(parameters["freeform"]["collar_center_y_ratio"]) * self.length
        self.collar_ry = float(parameters["freeform"]["collar_radius_y"])
        self.collar_rr = float(parameters["freeform"]["collar_radius_section_parameter"])
        self.band_width = float(parameters["freeform"]["collar_band_width"])
        self.band_target = float(parameters["freeform"]["collar_band_target_wall"])
        self.band_raise = float(parameters["freeform"]["collar_band_outer_raise"])
        self.edge_bulge = float(parameters["freeform"]["collar_edge_round_into_opening"])
        self.edge_segments = int(parameters["freeform"]["collar_edge_segments"])
        self.collar_segments = int(parameters["freeform"]["collar_polygon_segments"])
        self.collar_fairing_width = float(parameters["freeform"]["collar_fairing_width"])
        self.collar_height_front = float(parameters["freeform"]["collar_edge_height_front"])
        self.collar_height_side = float(parameters["freeform"]["collar_edge_height_side"])
        self.collar_height_rear = float(parameters["freeform"]["collar_edge_height_rear"])
        self.end_closure_blend = float(parameters["freeform"]["end_closure_blend_length"])
        self.end_cap_y_step = float(parameters["freeform"]["end_cap_y_step"])
        self.end_cap_r_step = float(parameters["freeform"]["end_cap_section_parameter_step"])
        self.end_cap_overlap = float(parameters["freeform"]["end_cap_boolean_overlap"])
        self.terminal_clip_inset = float(
            parameters["freeform"]["terminal_plane_clip_inset"]
        )

        sole = np.asarray(parameters["sole_stations"]["values"], dtype=float)
        upper = np.asarray(parameters["upper_stations"]["values"], dtype=float)
        self.sole_s = sole[:, 0]
        self.upper_s = upper[:, 0]
        self.sole_splines = {
            name: PchipInterpolator(self.sole_s, sole[:, index])
            for index, name in enumerate(parameters["sole_stations"]["columns"])
            if name != "s"
        }
        self.upper_splines = {
            name: CubicSpline(self.upper_s, upper[:, index], bc_type="natural")
            for index, name in enumerate(parameters["upper_stations"]["columns"])
            if name != "s"
        }
        self._validate_spline_ranges()

    def _validate_spline_ranges(self) -> None:
        samples = np.linspace(0.0, 1.0, 2001)
        sole_width = np.asarray(self.sole_splines["width"](samples))
        upper_width = np.asarray(self.upper_splines["width"](samples))
        height = np.asarray(self.upper_splines["height"](samples))
        if np.min(sole_width) <= 2.0 * self.inset + 2.0:
            raise ValueError("Sole width collapses below the protected interface allowance")
        if np.min(upper_width) <= 2.0:
            raise ValueError("Upper width spline becomes non-positive")
        if np.min(height) < self.skirt:
            raise ValueError("Upper height spline falls below the skirt height")
        if not (0.0 < self.collar_rr < 1.0):
            raise ValueError("Collar section-parameter radius must be inside (0, 1)")
        if self.collar_cy - self.collar_ry <= 0.0 or self.collar_cy + self.collar_ry >= self.length:
            raise ValueError("Collar ellipse must stay inside the longitudinal domain")
        if self.collar_fairing_width <= self.band_width:
            raise ValueError("Collar fairing width must exceed the comfort-band width")
        if not (0.0 < self.end_closure_blend < self.collar_cy - self.collar_ry):
            raise ValueError("End-closure blend must be positive and remain behind the collar")
        if self.end_cap_y_step <= 0.0 or self.end_cap_r_step <= 0.0:
            raise ValueError("End-cap tessellation steps must be positive")
        if not (0.0 < self.end_cap_overlap <= 0.20):
            raise ValueError("End-cap Boolean overlap must stay inside the 0.20 mm interface allowance")
        if not (0.0 < self.terminal_clip_inset <= 0.20):
            raise ValueError("Terminal-plane clip inset must stay inside the 0.20 mm allowance")

    def sole_values(self, s):
        s = np.clip(np.asarray(s, dtype=float), 0.0, 1.0)
        return {name: np.asarray(spline(s)) for name, spline in self.sole_splines.items()}

    def upper_values(self, s):
        s = np.clip(np.asarray(s, dtype=float), 0.0, 1.0)
        return {name: np.asarray(spline(s)) for name, spline in self.upper_splines.items()}

    def tapered_height(self, s, nominal):
        s = np.clip(np.asarray(s, dtype=float), 0.0, 1.0)
        heel = smootherstep(s / max(1.0e-9, self.heel_taper))
        toe = smootherstep((1.0 - s) / max(1.0e-9, self.toe_taper))
        blend = np.minimum(heel, toe)
        return self.skirt + np.maximum(0.0, nominal - self.skirt) * blend

    def _base_surface_point(self, y, r) -> np.ndarray:
        y = np.asarray(y, dtype=float)
        r = np.asarray(r, dtype=float)
        s = np.clip(y / self.length, 0.0, 1.0)
        sole = self.sole_values(s)
        upper = self.upper_values(s)
        base = sole["top"] + 0.55
        height = self.tapered_height(s, upper["height"])
        lower_hw = np.maximum(1.0, sole["width"] * 0.5 - self.inset)
        crown_hw = np.maximum(1.0, upper["width"] * 0.5)

        theta = 0.5 * np.pi * np.clip(r, -1.0, 1.0)
        vertical = np.maximum(0.0, np.cos(theta))
        lateral = np.sin(theta)
        blend = smootherstep(vertical)
        center = sole["shift"] * (1.0 - blend) + upper["shift"] * blend
        half_width = lower_hw * (1.0 - blend) + crown_hw * blend
        x = center + lateral * half_width
        z = base + height * np.power(vertical, self.section_exponent)
        return np.column_stack((x, y, z))

    def collar_target_height(self, angle) -> np.ndarray:
        angle = np.asarray(angle, dtype=float)
        coefficient_1 = 0.5 * (self.collar_height_front - self.collar_height_rear)
        coefficient_0 = 0.25 * (
            self.collar_height_front
            + self.collar_height_rear
            + 2.0 * self.collar_height_side
        )
        coefficient_2 = coefficient_0 - self.collar_height_side
        return coefficient_0 + coefficient_1 * np.cos(angle) + coefficient_2 * np.cos(2.0 * angle)

    def surface_point(self, y, r) -> np.ndarray:
        y = np.asarray(y, dtype=float)
        r = np.asarray(r, dtype=float)
        points = self._base_surface_point(y, r)
        rho = self.collar_rho(y, r)
        safe_rho = np.maximum(rho, 1.0e-9)
        edge_y = self.collar_cy + (y - self.collar_cy) / safe_rho
        edge_r = r / safe_rho
        edge_points = self._base_surface_point(edge_y, edge_r)
        distance = np.linalg.norm(points - edge_points, axis=1)
        weight = smootherstep(1.0 - distance / self.collar_fairing_width)
        angle = np.arctan2(edge_r / self.collar_rr, (edge_y - self.collar_cy) / self.collar_ry)
        height_delta = self.collar_target_height(angle) - edge_points[:, 2]
        points[:, 2] += height_delta * weight
        return points

    def surface_normal(self, y, r) -> np.ndarray:
        y = np.asarray(y, dtype=float)
        r = np.asarray(r, dtype=float)
        yp = np.minimum(self.length, y + 0.05)
        ym = np.maximum(0.0, y - 0.05)
        rp = np.minimum(1.0, r + 0.0005)
        rm = np.maximum(-1.0, r - 0.0005)
        dy = self.surface_point(yp, r) - self.surface_point(ym, r)
        dr = self.surface_point(y, rp) - self.surface_point(y, rm)
        dy /= np.maximum((yp - ym)[:, None], 1.0e-9)
        dr /= np.maximum((rp - rm)[:, None], 1.0e-9)
        normal = np.cross(dr, dy)
        length = np.linalg.norm(normal, axis=1)
        if np.any(length < 1.0e-9):
            raise ValueError("Degenerate freeform surface normal")
        return normal / length[:, None]

    def collar_rho(self, y, r) -> np.ndarray:
        return np.sqrt(((np.asarray(y) - self.collar_cy) / self.collar_ry) ** 2 + (np.asarray(r) / self.collar_rr) ** 2)

    def band_distance(self, y, r, base_points=None) -> np.ndarray:
        y = np.asarray(y, dtype=float)
        r = np.asarray(r, dtype=float)
        rho = np.maximum(self.collar_rho(y, r), 1.0)
        yh = self.collar_cy + (y - self.collar_cy) / rho
        rh = r / rho
        if base_points is None:
            base_points = self.surface_point(y, r)
        edge_points = self.surface_point(yh, rh)
        return np.linalg.norm(base_points - edge_points, axis=1)

    def shell_surfaces(self, domain: DomainMesh, wall: float):
        y = domain.parameters[:, 0]
        r = domain.parameters[:, 1]
        base = self.surface_point(y, r)
        normal = self.surface_normal(y, r)
        s = np.clip(y / self.length, 0.0, 1.0)
        end_weight = np.minimum(
            smootherstep(s / max(self.heel_taper, 1.0e-9)),
            smootherstep((1.0 - s) / max(self.toe_taper, 1.0e-9)),
        )
        # The visible outer envelope retains the full C2 surface.  Suppress
        # only the longitudinal component of the inward offset as each end
        # closes, so the inner shell cannot fold back through an end cap.
        normal[:, 1] *= end_weight
        normal /= np.linalg.norm(normal, axis=1)[:, None]
        end_min_wall = float(self.p["freeform"]["end_closure_min_wall"])
        if wall < end_min_wall - 1.0e-9:
            raise ValueError("Requested shell wall is below the end-closure minimum")
        effective_wall = end_min_wall + (wall - end_min_wall) * end_weight
        distance = self.band_distance(y, r, base)
        # A 4.5 mm inward offset is intentionally retained across the broad
        # infill envelope, but cannot follow the tighter approved collar
        # fairing without locally crossing itself.  Taper only that optional
        # thick envelope to the independently printable comfort-band wall.
        collar_safe_wall = float(self.p["freeform"]["collar_infill_safe_wall"])
        fairing_weight = smootherstep(1.0 - distance / self.collar_fairing_width)
        effective_wall -= np.maximum(0.0, effective_wall - collar_safe_wall) * fairing_weight
        weight = smootherstep(1.0 - distance / self.band_width)
        collar_extra = np.maximum(0.0, self.band_target - effective_wall)
        outer_raise = np.minimum(self.band_raise, 0.40 * collar_extra)
        inward_extra = collar_extra - outer_raise
        outer = base + normal * (outer_raise * weight)[:, None]
        inner = base - normal * (effective_wall + inward_extra * weight)[:, None]
        local_wall = effective_wall + collar_extra * weight
        return outer, inner, local_wall, distance

    def full_domain(self) -> Polygon:
        rectangle = box(0.0, -1.0, self.length, 1.0)
        collar = ellipse_polygon(self.collar_cy, self.collar_ry, self.collar_rr, self.collar_segments)
        return rectangle.difference(collar)

    def _height_band_polygon(self, y_max: float, height_mm: float) -> Polygon:
        count = max(80, int(math.ceil(y_max / 1.5)) + 1)
        ys = np.linspace(0.0, y_max, count)
        s = ys / self.length
        nominal = self.upper_values(s)["height"]
        height = self.tapered_height(s, nominal)
        vertical = np.clip(height_mm / np.maximum(height, 1.0e-6), 0.0, 1.0)
        r_inner = (2.0 / np.pi) * np.arccos(np.power(vertical, 1.0 / self.section_exponent))
        # Keep the medial and lateral reinforcement strips separated by a
        # printable slit instead of allowing them to meet at a zero-width
        # topological pinch near the tapered heel or toe.
        r_inner = np.maximum(
            r_inner,
            float(self.p["variants"]["frame_center_slit_min_parameter"]),
        )
        right = Polygon(
            [(float(y), 1.0) for y in ys]
            + [(float(y), float(r)) for y, r in zip(ys[::-1], r_inner[::-1])]
        )
        left = Polygon(
            [(float(y), float(-r)) for y, r in zip(ys, r_inner)]
            + [(float(y), -1.0) for y in ys[::-1]]
        )
        return unary_union([left, right])

    def frame_domain(self) -> Polygon:
        variants = self.p["variants"]
        lower = self._height_band_polygon(self.length, float(variants["lower_frame_height"]))
        heel_y = float(variants["heel_counter_length_ratio"]) * self.length
        heel = self._height_band_polygon(heel_y, float(variants["heel_counter_height"]))
        outer_rr = self.collar_rr + float(self.p["freeform"]["collar_band_outer_section_parameter_add"])
        collar_outer = ellipse_polygon(
            self.collar_cy,
            self.collar_ry + self.band_width,
            outer_rr,
            self.collar_segments,
        )
        features = unary_union([lower, heel, collar_outer])
        regularization = float(variants["frame_domain_regularization"])
        if regularization > 0.0:
            # Remove zero-width/tangent union seams where the heel counter and
            # collar band meet.  Apply before the full-domain intersection so
            # the protected sole and collar-opening boundaries stay exact.
            features = features.buffer(regularization, join_style="round").buffer(
                -regularization,
                join_style="round",
            )
        return self.full_domain().intersection(features)

    def _adaptive_y_grid(self, physical_step: float) -> np.ndarray:
        """Space longitudinal rows by 3D surface travel, not raw Y distance."""
        fine_count = int(math.ceil(self.length / 0.05)) + 1
        fine_y = np.linspace(0.0, self.length, fine_count)
        sample_r = np.linspace(-1.0, 1.0, 41)
        yy = np.repeat(fine_y, len(sample_r))
        rr = np.tile(sample_r, len(fine_y))
        points = self.surface_point(yy, rr).reshape(len(fine_y), len(sample_r), 3)
        travel = np.max(np.linalg.norm(np.diff(points, axis=0), axis=2), axis=1)
        cumulative = np.concatenate(([0.0], np.cumsum(travel)))
        targets = np.arange(0.0, cumulative[-1], physical_step)
        rows = np.interp(targets, cumulative, fine_y)
        semantic = np.unique(
            np.concatenate(
                (
                    self.sole_s * self.length,
                    self.upper_s * self.length,
                    np.asarray(
                        [
                            0.0,
                            self.length,
                            self.collar_cy,
                        ]
                    ),
                )
            )
        )
        rows = np.unique(np.round(np.concatenate((rows, semantic, [self.length])), 10))
        return rows[(rows >= 0.0) & (rows <= self.length)]

    def build_domain_mesh(self, geometry: Polygon, y_step: float, r_step: float) -> DomainMesh:
        r_count = int(math.ceil(2.0 / r_step)) + 1
        ys = self._adaptive_y_grid(y_step)
        rs = np.linspace(-1.0, 1.0, r_count)
        prepared = prep(geometry)
        vertices: list[tuple[float, float]] = []
        faces: list[tuple[int, int, int]] = []
        vertex_map: dict[tuple[float, float], int] = {}

        def add_vertex(coord) -> int:
            key = (round(float(coord[0]), 10), round(float(coord[1]), 10))
            if key not in vertex_map:
                vertex_map[key] = len(vertices)
                vertices.append(key)
            return vertex_map[key]

        def add_triangle(coords) -> None:
            pts = [(float(item[0]), float(item[1])) for item in coords]
            signed = sum(
                pts[i][0] * pts[(i + 1) % 3][1] - pts[(i + 1) % 3][0] * pts[i][1]
                for i in range(3)
            )
            if abs(signed) < 1.0e-14:
                return
            if signed > 0.0:
                pts[1], pts[2] = pts[2], pts[1]
            faces.append(tuple(add_vertex(pt) for pt in pts))

        for iy in range(len(ys) - 1):
            y0, y1 = float(ys[iy]), float(ys[iy + 1])
            for ir in range(len(rs) - 1):
                r0, r1 = float(rs[ir]), float(rs[ir + 1])
                cell = box(y0, r0, y1, r1)
                if prepared.contains(cell):
                    add_triangle([(y0, r0), (y0, r1), (y1, r1)])
                    add_triangle([(y0, r0), (y1, r1), (y1, r0)])
                    continue
                if not prepared.intersects(cell):
                    continue
                clipped = geometry.intersection(cell)
                for polygon in polygon_parts(clipped):
                    if polygon.area < 1.0e-12:
                        continue
                    for tri in triangulate(polygon):
                        if polygon.covers(tri.representative_point()):
                            coords = list(tri.exterior.coords)[:3]
                            add_triangle(coords)

        param_vertices = np.asarray(vertices, dtype=float)
        domain_faces = np.asarray(faces, dtype=np.int64)
        counts = Counter(tuple(sorted((int(a), int(b)))) for tri in domain_faces for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])))
        boundary = np.asarray([edge for edge, count in counts.items() if count == 1], dtype=np.int64)
        if len(boundary) == 0:
            raise ValueError("Triangulated surface domain has no boundary")
        return DomainMesh(param_vertices, domain_faces, boundary)

    def _collar_edge_loops(self, domain: DomainMesh) -> tuple[list[list[int]], list[tuple[int, int]]]:
        collar_edges: list[tuple[int, int]] = []
        simple_edges: list[tuple[int, int]] = []
        for a, b in domain.boundary_edges:
            midpoint = 0.5 * (domain.parameters[a] + domain.parameters[b])
            rho = float(self.collar_rho(midpoint[0], midpoint[1]))
            if abs(rho - 1.0) <= 0.003:
                collar_edges.append((int(a), int(b)))
            else:
                simple_edges.append((int(a), int(b)))

        adjacency: dict[int, list[int]] = defaultdict(list)
        unused: set[tuple[int, int]] = set()
        for a, b in collar_edges:
            adjacency[a].append(b)
            adjacency[b].append(a)
            unused.add(tuple(sorted((a, b))))
        loops: list[list[int]] = []
        while unused:
            first = next(iter(unused))
            start, current = first
            previous = start
            loop = [start, current]
            unused.remove(first)
            guard = 0
            while current != start:
                options = [item for item in adjacency[current] if item != previous]
                if not options:
                    raise ValueError("Open collar boundary encountered")
                nxt = options[0]
                edge = tuple(sorted((current, nxt)))
                if edge not in unused:
                    raise ValueError("Non-manifold collar boundary encountered")
                unused.remove(edge)
                if nxt == start:
                    break
                loop.append(nxt)
                previous, current = current, nxt
                guard += 1
                if guard > len(collar_edges) + 2:
                    raise ValueError("Collar boundary traversal did not close")
            loops.append(loop)
        return loops, simple_edges

    def _solid_terminal_cap(self, y_start: float, y_end: float) -> trimesh.Trimesh:
        """Create a full solid under the approved outer arch at one end."""
        y_count = int(math.ceil((y_end - y_start) / self.end_cap_y_step)) + 1
        r_count = int(math.ceil(2.0 / self.end_cap_r_step)) + 1
        ys = np.linspace(y_start, y_end, y_count)
        rs = np.linspace(-1.0, 1.0, r_count)
        yy = np.repeat(ys, r_count)
        rr = np.tile(rs, y_count)
        points = self.surface_point(yy, rr)
        # A uniform 0.02 mm outward overlap avoids a tangential/coplanar
        # Boolean between the plug roof and shell skin.  The temporary Y drift
        # is removed by the exact terminal-plane clip after the union.
        points += self.surface_normal(yy, rr) * self.end_cap_overlap
        vertices = points.tolist()
        faces: list[list[int]] = []

        for yi in range(y_count - 1):
            for ri in range(r_count - 1):
                a = yi * r_count + ri
                b = a + 1
                c = (yi + 1) * r_count + ri + 1
                d = (yi + 1) * r_count + ri
                faces.extend(([a, b, c], [a, c, d]))

        # The r=+/-1 hardpoints lie on the protected sole-interface height.
        # Join only those unchanged boundary rails to create the plug floor.
        for yi in range(y_count - 1):
            left_0 = yi * r_count
            right_0 = left_0 + r_count - 1
            left_1 = (yi + 1) * r_count
            right_1 = left_1 + r_count - 1
            faces.extend(
                ([left_0, right_1, right_0], [left_0, left_1, right_1])
            )

        # Close both planar section faces.  A polygon centroid is guaranteed
        # to stay inside the arched section, unlike a bounding-box midpoint.
        for row in (0, y_count - 1):
            indices = [row * r_count + index for index in range(r_count)]
            section = points[np.asarray(indices)]
            centroid_2d = Polygon(section[:, [0, 2]]).centroid
            center_index = len(vertices)
            vertices.append([float(centroid_2d.x), float(ys[row]), float(centroid_2d.y)])
            for index in range(r_count - 1):
                faces.append([center_index, indices[index], indices[index + 1]])
            faces.append([center_index, indices[-1], indices[0]])

        cap = trimesh.Trimesh(
            np.asarray(vertices, dtype=float),
            np.asarray(faces, dtype=np.int64),
            process=True,
        )
        cap.fix_normals(multibody=True)
        if cap.volume < 0.0:
            cap.invert()
        if not cap.is_volume:
            raise ValueError("Parametric terminal cap is not a valid volume")
        return cap

    def _section_area(self, mesh: trimesh.Trimesh, y: float) -> float:
        section = mesh.section(plane_normal=[0.0, 1.0, 0.0], plane_origin=[0.0, y, 0.0])
        if section is None:
            raise ValueError(f"No terminal section found at y={y:.6f} mm")
        planar, _ = section.to_planar()
        return float(sum(polygon.area for polygon in planar.polygons_full))

    def _outer_section_area(self, y: float) -> float:
        r_count = int(math.ceil(2.0 / self.end_cap_r_step)) + 1
        rs = np.linspace(-1.0, 1.0, r_count)
        points = self.surface_point(np.full(r_count, y), rs)
        return float(Polygon(points[:, [0, 2]]).area)

    def _close_terminal_apertures(self, mesh: trimesh.Trimesh) -> tuple[trimesh.Trimesh, dict]:
        heel_cap = self._solid_terminal_cap(0.0, self.end_closure_blend)
        toe_cap = self._solid_terminal_cap(
            self.length - self.end_closure_blend,
            self.length,
        )
        volume_before = float(mesh.volume)
        closed = trimesh.boolean.union(
            [mesh, heel_cap, toe_cap],
            engine="manifold",
            check_volume=True,
        )
        if isinstance(closed, list):
            closed = trimesh.util.concatenate(closed)
        bounds = np.asarray(closed.bounds, dtype=float)
        clip = trimesh.creation.box(
            extents=[
                float(bounds[1, 0] - bounds[0, 0] + 20.0),
                self.length - 2.0 * self.terminal_clip_inset,
                float(bounds[1, 2] - bounds[0, 2] + 20.0),
            ]
        )
        clip.apply_translation(
            [
                float(0.5 * (bounds[0, 0] + bounds[1, 0])),
                0.5 * self.length,
                float(0.5 * (bounds[0, 2] + bounds[1, 2])),
            ]
        )
        closed = trimesh.boolean.intersection(
            [closed, clip],
            engine="manifold",
            check_volume=True,
        )
        if isinstance(closed, list):
            closed = trimesh.util.concatenate(closed)
        vertices = np.asarray(closed.vertices, dtype=float).copy()
        vertices[:, 1] = (
            (vertices[:, 1] - self.terminal_clip_inset)
            * self.length
            / (self.length - 2.0 * self.terminal_clip_inset)
        )
        vertices[:, 1] = np.clip(vertices[:, 1], 0.0, self.length)
        closed.vertices = vertices
        closed.merge_vertices(digits_vertex=8)
        closed.update_faces(closed.unique_faces())
        nondegenerate = closed.nondegenerate_faces(height=1.0e-8)
        discarded_degenerate_faces = int(np.count_nonzero(~nondegenerate))
        if discarded_degenerate_faces > 50:
            raise ValueError(
                "Terminal-cap union emitted too many degenerate faces: "
                f"{discarded_degenerate_faces}"
            )
        closed.update_faces(nondegenerate)
        positive_area = np.asarray(closed.area_faces) > 1.0e-10
        discarded_zero_area_faces = int(np.count_nonzero(~positive_area))
        if discarded_zero_area_faces > 50:
            raise ValueError(
                "Terminal-cap union emitted too many numerical zero-area faces: "
                f"{discarded_zero_area_faces}"
            )
        closed.update_faces(positive_area)
        closed.remove_unreferenced_vertices()
        closed.fix_normals(multibody=True)
        if closed.volume < 0.0:
            closed.invert()
        components = sorted(
            closed.split(only_watertight=False),
            key=lambda component: abs(float(component.volume)),
            reverse=True,
        )
        discarded = components[1:]
        discarded_faces = int(sum(len(component.faces) for component in discarded))
        discarded_volume = float(sum(abs(float(component.volume)) for component in discarded))
        # Manifold may emit a handful of zero-area two-triangle remnants where
        # the sparse reinforcement slit meets the pointed toe.  They are not
        # material bodies.  Remove them explicitly, record the cleanup, and
        # fail closed if the remainder has material volume or meaningful size.
        if discarded and (discarded_faces > 50 or discarded_volume > 1.0e-6):
            raise ValueError(
                "Terminal-cap union emitted nontrivial disconnected geometry: "
                f"faces={discarded_faces}, volume={discarded_volume:.9f} mm3"
            )
        if components:
            closed = components[0].copy()
            final_positive_area = np.asarray(closed.area_faces) > 1.0e-10
            discarded_post_split_zero_area_faces = int(
                np.count_nonzero(~final_positive_area)
            )
            if discarded_post_split_zero_area_faces > 50:
                raise ValueError(
                    "Terminal-cap component retained too many zero-area faces: "
                    f"{discarded_post_split_zero_area_faces}"
                )
            closed.update_faces(final_positive_area)
            closed.remove_unreferenced_vertices()
            closed.fix_normals(multibody=True)
        else:
            discarded_post_split_zero_area_faces = 0
        if not closed.is_volume:
            raise ValueError("Terminal-cap union did not produce one valid upper volume")

        sections = {}
        for name, y in (
            ("heel", 0.5 * self.end_closure_blend),
            ("toe", self.length - 0.5 * self.end_closure_blend),
        ):
            target_area = self._outer_section_area(y)
            material_area = self._section_area(closed, y)
            sections[name] = {
                "sample_y_mm": float(y),
                "outer_section_area_mm2": target_area,
                "material_section_area_mm2": material_area,
                "residual_aperture_area_mm2": float(max(0.0, target_area - material_area)),
            }
        return closed, {
            "method": "parametric-solid-plugs-plus-manifold-union",
            "boolean_engine": "manifold",
            "terminal_plane_clip_source_y_mm": [
                self.terminal_clip_inset,
                self.length - self.terminal_clip_inset,
            ],
            "terminal_plane_clip_output_y_mm": [0.0, self.length],
            "maximum_longitudinal_remap_mm": self.terminal_clip_inset,
            "blend_length_mm": self.end_closure_blend,
            "boolean_overlap_mm": self.end_cap_overlap,
            "minimum_local_wall_mm": float(self.p["freeform"]["end_closure_min_wall"]),
            "volume_before_closure_mm3": volume_before,
            "volume_after_closure_mm3": float(closed.volume),
            "added_material_volume_mm3": float(closed.volume - volume_before),
            "discarded_zero_volume_components": int(len(discarded)),
            "discarded_zero_volume_faces": discarded_faces,
            "discarded_absolute_volume_mm3": discarded_volume,
            "discarded_degenerate_faces": discarded_degenerate_faces,
            "discarded_zero_area_faces": discarded_zero_area_faces,
            "discarded_post_split_zero_area_faces": discarded_post_split_zero_area_faces,
            "sections": sections,
        }

    def create_shell(self, domain: DomainMesh, wall: float) -> tuple[trimesh.Trimesh, dict]:
        outer, inner, local_wall, band_distance = self.shell_surfaces(domain, wall)
        count = len(outer)
        vertices = [*outer.tolist(), *inner.tolist()]
        faces: list[list[int]] = []
        for a, b, c in domain.faces:
            faces.append([int(a), int(b), int(c)])
            faces.append([int(c + count), int(b + count), int(a + count)])

        loops, simple_edges = self._collar_edge_loops(domain)
        for a, b in simple_edges:
            faces.append([a, b, b + count])
            faces.append([a, b + count, a + count])

        collar_edge_lengths: list[float] = []
        for loop in loops:
            params = domain.parameters[np.asarray(loop)]
            y = params[:, 0]
            r = params[:, 1]
            collar_points = outer[np.asarray(loop)]
            collar_edge_lengths.extend(
                np.linalg.norm(collar_points - np.roll(collar_points, -1, axis=0), axis=1).tolist()
            )
            rho_step = 1.002
            y_step = self.collar_cy + (y - self.collar_cy) * rho_step
            r_step = r * rho_step
            material_tangent = self.surface_point(y_step, r_step) - self.surface_point(y, r)
            material_tangent /= np.linalg.norm(material_tangent, axis=1)[:, None]
            center = 0.5 * (outer[loop] + inner[loop])
            half = 0.5 * (outer[loop] - inner[loop])
            ring_indices: list[list[int]] = [[int(index) for index in loop]]
            for segment in range(1, self.edge_segments + 1):
                angle = np.pi * segment / (self.edge_segments + 1)
                points = center + half * math.cos(angle) - material_tangent * (self.edge_bulge * math.sin(angle))
                indices = []
                for point in points:
                    indices.append(len(vertices))
                    vertices.append(point.tolist())
                ring_indices.append(indices)
            ring_indices.append([int(index + count) for index in loop])
            for layer in range(len(ring_indices) - 1):
                ring_a = ring_indices[layer]
                ring_b = ring_indices[layer + 1]
                for i in range(len(loop)):
                    j = (i + 1) % len(loop)
                    faces.append([ring_a[i], ring_a[j], ring_b[j]])
                    faces.append([ring_a[i], ring_b[j], ring_b[i]])

        mesh = trimesh.Trimesh(np.asarray(vertices, dtype=float), np.asarray(faces, dtype=np.int64), process=False)
        mesh.merge_vertices(digits_vertex=8)
        mesh.update_faces(mesh.unique_faces())
        mesh.remove_unreferenced_vertices()
        mesh.fix_normals(multibody=True)
        if mesh.volume < 0.0:
            mesh.invert()
        mesh, terminal_closure = self._close_terminal_apertures(mesh)
        outer_edges = np.unique(np.sort(np.asarray(mesh_edges(domain.faces)), axis=1), axis=0)
        outer_edge_lengths = np.linalg.norm(outer[outer_edges[:, 0]] - outer[outer_edges[:, 1]], axis=1)
        report = {
            "base_wall_mm": wall,
            "constructed_wall_min_mm": float(np.min(local_wall)),
            "constructed_wall_max_mm": float(np.max(local_wall)),
            "collar_constructed_wall_mm": float(np.max(local_wall[band_distance < 0.05])) if np.any(band_distance < 0.05) else None,
            "domain_vertices": int(len(domain.parameters)),
            "domain_faces": int(len(domain.faces)),
            "collar_loops": len(loops),
            "collar_outer_edge_max_mm": float(max(collar_edge_lengths, default=0.0)),
            "visible_outer_edge_max_mm": float(np.max(outer_edge_lengths)),
            "visible_outer_edge_p99_mm": float(np.percentile(outer_edge_lengths, 99.0)),
            "terminal_closure": terminal_closure,
        }
        return mesh, report


def mesh_report(mesh: trimesh.Trimesh, path: Path) -> dict:
    components = mesh.split(only_watertight=False)
    edges = np.asarray(mesh.edges_unique_length)
    degenerate_faces = int(np.count_nonzero(np.asarray(mesh.area_faces) <= 1.0e-10))
    return {
        "path": str(path.relative_to(HERE)),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "components": int(len(components)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "bounds_mm": mesh.bounds.tolist(),
        "edge_length_max_mm": float(np.max(edges)),
        "edge_length_p99_mm": float(np.percentile(edges, 99.0)),
        "euler_number": int(mesh.euler_number),
        "degenerate_faces": degenerate_faces,
    }


def mirrored(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    result = mesh.copy()
    transform = np.eye(4)
    transform[0, 0] = -1.0
    result.apply_transform(transform)
    if result.volume < 0.0:
        result.invert()
    return result


def export_pair(mesh: trimesh.Trimesh, stem: str, output_dir: Path, report: dict) -> None:
    left_path = output_dir / f"{stem}-left.stl"
    right_path = output_dir / f"{stem}-right.stl"
    mesh.export(left_path)
    right = mirrored(mesh)
    right.export(right_path)
    report[left_path.name] = mesh_report(mesh, left_path)
    report[right_path.name] = mesh_report(right, right_path)


def v6_1_sole_reference() -> tuple[dict[str, PchipInterpolator], dict]:
    config = json.loads(V6_1_CONFIG.read_text())
    table = np.asarray(
        [
            [0.00, 0.33 * config["heel_width"], 0.0, 2.00, 6.90, 0.80, 0.08],
            [0.05, 0.88 * config["heel_width"], 0.0, 0.80, 5.70, 0.70, 0.10],
            [0.12, 1.07 * config["heel_width"], -1.0, 0.10, 5.00, 0.58, 0.13],
            [0.22, 1.10 * config["heel_width"], -2.0, 0.00, 4.90, 0.52, 0.15],
            [0.35, 0.99 * config["waist_width"], -4.0, 0.00, 4.90, 0.46, 0.20],
            [0.48, 1.04 * config["waist_width"], -4.0, 0.00, 4.90, 0.46, 0.22],
            [0.62, 0.92 * config["ball_width"], -2.0, 0.00, 4.90, 0.50, 0.18],
            [0.72, 1.05 * config["ball_width"], 0.0, 0.00, 4.90, 0.56, 0.15],
            [0.82, 1.05 * config["toe_box_width"], 2.0, 0.30, 5.20, 0.68, 0.12],
            [0.90, 1.03 * config["toe_box_width"], 4.0, 1.20, 6.10, 0.78, 0.10],
            [0.96, 0.87 * config["toe_box_width"], config["medial_toe_shift"], 3.00, 7.90, 0.88, 0.08],
            [1.00, 0.45 * config["toe_box_width"], config["medial_toe_shift"], 5.00, 9.90, 0.95, 0.05],
        ],
        dtype=float,
    )
    columns = ["s", "width", "shift", "bottom", "top", "edge_rise", "top_crown"]
    splines = {
        name: PchipInterpolator(table[:, 0], table[:, index])
        for index, name in enumerate(columns)
        if name != "s"
    }
    return splines, config


def interface_report(model: FreeformUpper) -> dict:
    reference, config = v6_1_sole_reference()
    if abs(model.length - float(config["foot_length"] + config["toe_clearance"])) > 1.0e-9:
        raise ValueError("V6.2 length no longer matches the protected V6.1 interface reference")
    dense_s = np.linspace(0.0, 1.0, 1001)
    dense_y = dense_s * model.length
    dense_points = model.surface_point(
        np.repeat(dense_y, 2),
        np.tile(np.asarray([-1.0, 1.0]), len(dense_y)),
    ).reshape(len(dense_y), 2, 3)
    target_width = np.asarray(reference["width"](dense_s)) - 2.0 * model.inset
    target_center = np.asarray(reference["shift"](dense_s))
    target_z = np.asarray(reference["top"](dense_s)) + 0.55
    measured_width = dense_points[:, 1, 0] - dense_points[:, 0, 0]
    measured_center = 0.5 * (dense_points[:, 0, 0] + dense_points[:, 1, 0])
    drift_columns = np.column_stack(
        (
            measured_width - target_width,
            measured_center - target_center,
            dense_points[:, 0, 2] - target_z,
            dense_points[:, 1, 2] - target_z,
        )
    )
    maximum_drift = float(np.max(np.abs(drift_columns)))
    stations = [0.0, 0.02, 0.06, 0.12, 0.22, 0.48, 0.62, 0.72, 0.82, 0.90, 0.96, 0.995, 1.0]
    rows = []
    for s in stations:
        index = int(round(s * 1000))
        rows.append(
            {
                "s": s,
                "y_mm": float(dense_y[index]),
                "target_width_mm": float(target_width[index]),
                "measured_width_mm": float(measured_width[index]),
                "width_drift_mm": float(drift_columns[index, 0]),
                "target_center_x_mm": float(target_center[index]),
                "measured_center_x_mm": float(measured_center[index]),
                "center_drift_mm": float(drift_columns[index, 1]),
                "target_z_mm": float(target_z[index]),
                "left_z_drift_mm": float(drift_columns[index, 2]),
                "right_z_drift_mm": float(drift_columns[index, 3]),
            }
        )
    return {
        "reference_path": "../barfussschuh_v6_1_fitfix/v6_config.json",
        "reference_sha256": sha256_file(V6_1_CONFIG),
        "dense_sample_count": int(len(dense_s)),
        "maximum_drift_mm": maximum_drift,
        "semantic_stations": rows,
    }


def create_coupon(mesh: trimesh.Trimesh, model: FreeformUpper, path: Path) -> trimesh.Trimesh:
    point = model.surface_point(np.asarray([model.collar_cy]), np.asarray([model.collar_rr]))[0]
    cutter = trimesh.creation.box(extents=[24.0, 30.0, 26.0])
    cutter.apply_translation(point + np.asarray([0.0, 0.0, -1.5]))
    coupon = trimesh.boolean.intersection([mesh, cutter], engine="manifold", check_volume=True)
    if isinstance(coupon, list):
        coupon = trimesh.util.concatenate(coupon)
    coupon.remove_unreferenced_vertices()
    coupon.fix_normals(multibody=True)
    if coupon.volume < 0.0:
        coupon.invert()
    coupon.export(path)
    return coupon


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=DEFAULT_PARAMETERS)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()

    parameter_path = args.parameters.resolve()
    output = args.output.resolve()
    params = yaml.safe_load(parameter_path.read_text())
    model = FreeformUpper(params)

    master_dir = output / "exports" / "master"
    manufacturing_dir = output / "exports" / "manufacturing"
    coupon_dir = output / "exports" / "coupons"
    validation_dir = output / "validation"
    for directory in (master_dir, manufacturing_dir, coupon_dir, validation_dir):
        directory.mkdir(parents=True, exist_ok=True)

    y_step = float(params["freeform"]["y_grid_step"])
    r_step = float(params["freeform"]["section_parameter_step"])
    print("triangulating full freeform domain", flush=True)
    full_domain = model.build_domain_mesh(model.full_domain(), y_step, r_step)
    print("triangulating reinforcement domain", flush=True)
    frame_domain = model.build_domain_mesh(model.frame_domain(), y_step, r_step)

    variants = params["variants"]
    print("building fuzzy shell", flush=True)
    fuzzy, fuzzy_construct = model.create_shell(full_domain, float(variants["fuzzy_shell_wall"]))
    print("building infill envelope", flush=True)
    infill, infill_construct = model.create_shell(full_domain, float(variants["infill_envelope_wall"]))
    print("building reinforcement frame", flush=True)
    frame, frame_construct = model.create_shell(frame_domain, float(variants["reinforcement_frame_wall"]))

    project_id = str(params["project_id"])
    revision = str(params["revision"])
    if not project_id or not revision or any(
        char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        for char in project_id + revision
    ):
        raise ValueError("Project ID and revision must be non-empty filename-safe identifiers")
    prefix = f"DRAFT-{project_id}-{revision}"
    master_obj = master_dir / f"{prefix}-upper-fuzzy-shell-left-master.obj"
    fuzzy.export(master_obj)

    files: dict[str, dict] = {}
    export_pair(fuzzy, f"{prefix}-upper-fuzzy-shell", manufacturing_dir, files)
    export_pair(infill, f"{prefix}-upper-infill-envelope", manufacturing_dir, files)
    export_pair(frame, f"{prefix}-upper-reinforcement-frame", manufacturing_dir, files)
    coupon_path = coupon_dir / f"{prefix}-collar-comfort-coupon.stl"
    coupon = create_coupon(fuzzy, model, coupon_path)
    files[coupon_path.name] = mesh_report(coupon, coupon_path)
    files[master_obj.name] = mesh_report(fuzzy, master_obj)

    interface = interface_report(model)
    max_interface_drift = float(interface["maximum_drift_mm"])
    v6_1_config = json.loads(V6_1_CONFIG.read_text())
    v6_1_front_boundary = (
        float(v6_1_config["collar_center_y_ratio"]) * model.length
        + float(v6_1_config["collar_radius_y"])
    )
    opening_points = model.surface_point(
        np.asarray([model.collar_cy, model.collar_cy]),
        np.asarray([-model.collar_rr, model.collar_rr]),
    )
    opening_width_center = float(np.linalg.norm(opening_points[1] - opening_points[0]))
    collar_cardinal_y = np.asarray(
        [
            model.collar_cy + model.collar_ry,
            model.collar_cy,
            model.collar_cy - model.collar_ry,
        ]
    )
    collar_cardinal_r = np.asarray([0.0, model.collar_rr, 0.0])
    collar_cardinal_points = model.surface_point(collar_cardinal_y, collar_cardinal_r)
    forward_centerline_y = np.linspace(
        model.collar_cy + model.collar_ry,
        float(params["freeform"]["forward_centerline_end_ratio"]) * model.length,
        4001,
    )
    forward_centerline_z = model.surface_point(
        forward_centerline_y,
        np.zeros_like(forward_centerline_y),
    )[:, 2]
    forward_steps = np.diff(forward_centerline_z)
    report = {
        "schema_version": 1,
        "project_id": params["project_id"],
        "revision": params["revision"],
        "generator": "generate_v6_2.py",
        "method": {
            "name": "direct-c2-freeform-domain-loft",
            "sole_interface_interpolation": "pchip-v6.1-compatible",
            "longitudinal_interpolation": params["freeform"]["interpolation"],
            "upper_height_interpolation": "natural-cubic-c2-with-approved-vamp-stations",
            "voxel_grid": False,
            "distance_field": False,
            "marching_cubes": False,
            "global_remesh": False,
            "collar": "parametric domain opening plus explicit rounded edge cap",
            "terminal_closure": "parametric solid plugs plus exact manifold union",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "trimesh": trimesh.__version__,
        },
        "parameters": {
            "path": str(parameter_path.relative_to(HERE)),
            "sha256": sha256_file(parameter_path),
        },
        "domain": {
            "full_vertices": int(len(full_domain.parameters)),
            "full_faces": int(len(full_domain.faces)),
            "frame_vertices": int(len(frame_domain.parameters)),
            "frame_faces": int(len(frame_domain.faces)),
        },
        "construction": {
            "fuzzy_shell": fuzzy_construct,
            "infill_envelope": infill_construct,
            "reinforcement_frame": frame_construct,
            "collar_band_width_mm": model.band_width,
            "collar_edge_round_into_opening_mm": model.edge_bulge,
            "maximum_opening_reduction_each_side_mm": model.edge_bulge,
            "collar_rear_reserve_mm": model.collar_cy - model.collar_ry,
            "collar_front_boundary_y_mm": model.collar_cy + model.collar_ry,
            "v6_1_collar_front_boundary_y_mm": v6_1_front_boundary,
            "collar_front_boundary_drift_from_v6_1_mm": model.collar_cy + model.collar_ry - v6_1_front_boundary,
            "collar_opening_width_at_center_mm": opening_width_center,
            "collar_edge_height_target_mm": {
                "front": model.collar_height_front,
                "side": model.collar_height_side,
                "rear": model.collar_height_rear,
            },
            "collar_edge_height_measured_mm": {
                "front": float(collar_cardinal_points[0, 2]),
                "side": float(collar_cardinal_points[1, 2]),
                "rear": float(collar_cardinal_points[2, 2]),
            },
            "collar_fairing_width_mm": model.collar_fairing_width,
            "collar_infill_safe_wall_mm": float(params["freeform"]["collar_infill_safe_wall"]),
            "heel_rise_transition_length_mm": model.heel_taper * model.length,
            "heel_rise_transition_ratio": model.heel_taper,
            "end_closure_min_wall_mm": float(params["freeform"]["end_closure_min_wall"]),
            "end_closure_blend_length_mm": model.end_closure_blend,
            "forward_centerline": {
                "start_y_mm": float(forward_centerline_y[0]),
                "end_y_mm": float(forward_centerline_y[-1]),
                "start_z_mm": float(forward_centerline_z[0]),
                "maximum_z_mm": float(np.max(forward_centerline_z)),
                "maximum_z_y_mm": float(forward_centerline_y[int(np.argmax(forward_centerline_z))]),
                "end_z_mm": float(forward_centerline_z[-1]),
                "maximum_positive_sample_step_mm": float(max(0.0, np.max(forward_steps))),
                "sample_count": int(len(forward_centerline_y)),
            },
            "frame_domain_regularization": float(params["variants"]["frame_domain_regularization"]),
            "frame_center_slit_min_parameter": float(params["variants"]["frame_center_slit_min_parameter"]),
        },
        "interface_stations": interface,
        "maximum_interface_drift_mm": max_interface_drift,
        "files": files,
    }
    report_path = validation_dir / f"generation-report-{revision}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(report_path), "files": len(files), "max_interface_drift_mm": max_interface_drift}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
