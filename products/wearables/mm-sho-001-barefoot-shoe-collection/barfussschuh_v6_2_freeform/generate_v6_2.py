#!/usr/bin/env python3
"""Generate the MM-SHO-001 V6.2 direct freeform upper.

The visible upper is evaluated directly from C2 longitudinal splines and smooth
cross-sections.  No voxel grid, distance field, marching cubes, global remesh,
or smoothing modifier is used.  The collar opening is part of the parametric
surface domain and its free edge is closed by an explicit rounded cap.
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
from scipy.interpolate import CubicSpline
from shapely.geometry import GeometryCollection, MultiPolygon, Point, Polygon, box
from shapely.ops import triangulate, unary_union
from shapely.prepared import prep


HERE = Path(__file__).resolve().parent
DEFAULT_PARAMETERS = HERE / "parameters.yaml"


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

        sole = np.asarray(parameters["sole_stations"]["values"], dtype=float)
        upper = np.asarray(parameters["upper_stations"]["values"], dtype=float)
        self.sole_s = sole[:, 0]
        self.upper_s = upper[:, 0]
        self.sole_splines = {
            name: CubicSpline(self.sole_s, sole[:, index], bc_type="natural")
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

    def surface_point(self, y, r) -> np.ndarray:
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
        distance = self.band_distance(y, r, base)
        weight = smootherstep(1.0 - distance / self.band_width)
        extra = max(0.0, self.band_target - wall)
        outer_raise = min(self.band_raise, 0.40 * extra) if extra > 0.0 else 0.0
        inward_extra = max(0.0, extra - outer_raise)
        outer = base + normal * (outer_raise * weight)[:, None]
        inner = base - normal * (wall + inward_extra * weight)[:, None]
        local_wall = wall + extra * weight
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
        r_inner = np.maximum(r_inner, 0.015)
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
        return self.full_domain().intersection(unary_union([lower, heel, collar_outer]))

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

        for loop in loops:
            params = domain.parameters[np.asarray(loop)]
            y = params[:, 0]
            r = params[:, 1]
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
            "visible_outer_edge_max_mm": float(np.max(outer_edge_lengths)),
            "visible_outer_edge_p99_mm": float(np.percentile(outer_edge_lengths, 99.0)),
        }
        return mesh, report


def mesh_report(mesh: trimesh.Trimesh, path: Path) -> dict:
    components = mesh.split(only_watertight=False)
    edges = np.asarray(mesh.edges_unique_length)
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


def interface_report(model: FreeformUpper) -> list[dict]:
    stations = [0.0, 0.02, 0.06, 0.12, 0.22, 0.48, 0.62, 0.72, 0.82, 0.90, 0.96, 0.995, 1.0]
    rows = []
    for s in stations:
        y = s * model.length
        points = model.surface_point(np.asarray([y, y]), np.asarray([-1.0, 1.0]))
        sole = model.sole_values(np.asarray([s]))
        target_width = float(sole["width"][0] - 2.0 * model.inset)
        measured_width = float(points[1, 0] - points[0, 0])
        target_center = float(sole["shift"][0])
        measured_center = float(0.5 * (points[0, 0] + points[1, 0]))
        target_z = float(sole["top"][0] + 0.55)
        rows.append(
            {
                "s": s,
                "y_mm": y,
                "target_width_mm": target_width,
                "measured_width_mm": measured_width,
                "width_drift_mm": measured_width - target_width,
                "target_center_x_mm": target_center,
                "measured_center_x_mm": measured_center,
                "center_drift_mm": measured_center - target_center,
                "target_z_mm": target_z,
                "left_z_drift_mm": float(points[0, 2] - target_z),
                "right_z_drift_mm": float(points[1, 2] - target_z),
            }
        )
    return rows


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

    prefix = "DRAFT-MM-SHO-001-6.2.0-draft.1"
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
    max_interface_drift = max(
        max(abs(row["width_drift_mm"]), abs(row["center_drift_mm"]), abs(row["left_z_drift_mm"]), abs(row["right_z_drift_mm"]))
        for row in interface
    )
    report = {
        "schema_version": 1,
        "project_id": params["project_id"],
        "revision": params["revision"],
        "generator": "generate_v6_2.py",
        "method": {
            "name": "direct-c2-freeform-domain-loft",
            "longitudinal_interpolation": params["freeform"]["interpolation"],
            "voxel_grid": False,
            "distance_field": False,
            "marching_cubes": False,
            "global_remesh": False,
            "collar": "parametric domain opening plus explicit rounded edge cap",
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
        },
        "interface_stations": interface,
        "maximum_interface_drift_mm": max_interface_drift,
        "files": files,
    }
    report_path = validation_dir / "generation-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(report_path), "files": len(files), "max_interface_drift_mm": max_interface_drift}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
