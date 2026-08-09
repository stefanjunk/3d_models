#!/usr/bin/env python3
"""Generate watertight emboss/engrave relief patches from a height map.

The output is a closed mesh intended for union (emboss) or difference
(engrave) against a base object. Configuration is JSON; see the bundled
schema and reference guide.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import numpy as np
from scipy import ndimage
import trimesh

from heightmap_common import (
    EPS,
    load_image_float,
    normalize_vectors,
    smoothstep01,
    write_json,
)


@dataclass
class SurfaceGrid:
    positions: np.ndarray
    normals: np.ndarray
    u: np.ndarray
    v: np.ndarray
    periodic_u: bool = False
    periodic_v: bool = False
    u_length_mm: float = 1.0
    v_length_mm: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.positions = np.asarray(self.positions, dtype=np.float64)
        self.normals = normalize_vectors(np.asarray(self.normals, dtype=np.float64))
        self.u = np.asarray(self.u, dtype=np.float64)
        self.v = np.asarray(self.v, dtype=np.float64)
        if self.positions.ndim != 3 or self.positions.shape[-1] != 3:
            raise ValueError("positions must have shape (V,U,3)")
        if self.normals.shape != self.positions.shape:
            raise ValueError("normals must match positions")
        if self.u.shape != self.positions.shape[:2] or self.v.shape != self.positions.shape[:2]:
            raise ValueError("u and v must match the first two position dimensions")
        if not np.all(np.isfinite(self.positions)) or not np.all(np.isfinite(self.normals)):
            raise ValueError("surface grid contains non-finite values")

    @property
    def shape(self) -> tuple[int, int]:
        return self.positions.shape[:2]

    @property
    def grid_vertices(self) -> int:
        return int(np.prod(self.positions.shape[:2]))


def _samples(length_mm: float, pitch_mm: float, periodic: bool, minimum: int = 2) -> int:
    if length_mm <= 0 or pitch_mm <= 0:
        raise ValueError("Surface lengths and mesh pitch must be positive")
    count = int(math.ceil(length_mm / pitch_mm))
    if not periodic:
        count += 1
    return max(minimum, count)


def _uv_mesh(nu: int, nv: int, periodic_u: bool, periodic_v: bool) -> tuple[np.ndarray, np.ndarray]:
    u1 = np.linspace(0.0, 1.0, nu, endpoint=not periodic_u, dtype=np.float64)
    v1 = np.linspace(0.0, 1.0, nv, endpoint=not periodic_v, dtype=np.float64)
    return np.meshgrid(u1, v1, indexing="xy")


def _vector3(value: Iterable[float], name: str) -> np.ndarray:
    result = np.asarray(list(value), dtype=np.float64)
    if result.shape != (3,):
        raise ValueError(f"{name} must contain three numbers")
    return result


def _regular_polygon(sides: int, radius: float, start_angle_deg: float) -> np.ndarray:
    if sides < 3 or radius <= 0:
        raise ValueError("A regular polygon needs sides >= 3 and radius > 0")
    angles = np.deg2rad(start_angle_deg) + np.arange(sides, dtype=np.float64) * 2 * math.pi / sides
    return np.column_stack((radius * np.cos(angles), radius * np.sin(angles)))


def _polygon_points(spec: dict[str, Any], prefix: str = "") -> np.ndarray:
    points_key = f"{prefix}points" if prefix else "points"
    if points_key in spec:
        points = np.asarray(spec[points_key], dtype=np.float64)
        if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
            raise ValueError(f"{points_key} must be an array of at least three [x,y] points")
    else:
        sides = int(spec.get("sides", 6))
        radius_key = f"{prefix}radius_mm" if prefix else "radius_mm"
        if radius_key not in spec:
            radius_key = f"{prefix}circumradius_mm" if prefix else "circumradius_mm"
        radius = float(spec[radius_key])
        points = _regular_polygon(sides, radius, float(spec.get("start_angle_deg", 30.0)))
    # Make the path counterclockwise so outward normals are deterministic.
    signed_area = 0.5 * np.sum(points[:, 0] * np.roll(points[:, 1], -1) - np.roll(points[:, 0], -1) * points[:, 1])
    if signed_area < 0:
        points = points[::-1].copy()
    return points


def _polyline_samples(points: np.ndarray, count: int) -> tuple[np.ndarray, np.ndarray, float]:
    closed = np.vstack((points, points[0]))
    edges = np.diff(closed, axis=0)
    lengths = np.linalg.norm(edges, axis=1)
    if np.any(lengths <= EPS):
        raise ValueError("Polygon contains coincident consecutive points")
    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    perimeter = float(cumulative[-1])
    s = np.linspace(0.0, perimeter, count, endpoint=False)
    segment = np.searchsorted(cumulative[1:], s, side="right")
    local = (s - cumulative[segment]) / lengths[segment]
    positions = points[segment] + edges[segment] * local[:, None]
    tangent = edges[segment] / lengths[segment, None]
    outward = np.column_stack((tangent[:, 1], -tangent[:, 0]))
    return positions, outward, perimeter


def _derive_normals(positions: np.ndarray, periodic_u: bool, periodic_v: bool) -> np.ndarray:
    p = np.asarray(positions, dtype=np.float64)
    if periodic_u:
        du = np.roll(p, -1, axis=1) - np.roll(p, 1, axis=1)
    else:
        du = np.gradient(p, axis=1, edge_order=1)
    if periodic_v:
        dv = np.roll(p, -1, axis=0) - np.roll(p, 1, axis=0)
    else:
        dv = np.gradient(p, axis=0, edge_order=1)
    return normalize_vectors(np.cross(du, dv))


def make_plane(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    width = float(spec["width_mm"])
    height = float(spec["height_mm"])
    periodic_u = bool(spec.get("periodic_u", False))
    periodic_v = bool(spec.get("periodic_v", False))
    nu = _samples(width, pitch, periodic_u)
    nv = _samples(height, pitch, periodic_v)
    U, V = _uv_mesh(nu, nv, periodic_u, periodic_v)
    origin = _vector3(spec.get("origin", [0, 0, 0]), "origin")
    axis_u = normalize_vectors(_vector3(spec.get("axis_u", [1, 0, 0]), "axis_u"))
    raw_v = _vector3(spec.get("axis_v", [0, 1, 0]), "axis_v")
    raw_v = raw_v - axis_u * np.dot(raw_v, axis_u)
    axis_v = normalize_vectors(raw_v)
    normal = normalize_vectors(np.cross(axis_u, axis_v)) * float(spec.get("normal_sign", 1.0))
    P = origin + (U * width)[..., None] * axis_u + (V * height)[..., None] * axis_v
    N = np.broadcast_to(normal, P.shape).copy()
    return [SurfaceGrid(P, N, U, V, periodic_u, periodic_v, width, height, {"type": "plane"})]


def make_cylinder(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    radius = float(spec["radius_mm"])
    height = float(spec["height_mm"])
    angle_deg = float(spec.get("angle_deg", 360.0))
    start = math.radians(float(spec.get("start_angle_deg", 0.0)))
    angle = math.radians(angle_deg)
    periodic_u = bool(spec.get("periodic_u", abs(abs(angle_deg) - 360.0) < 1e-8))
    nu = _samples(abs(radius * angle), pitch, periodic_u, 3)
    nv = _samples(height, pitch, False)
    U, V = _uv_mesh(nu, nv, periodic_u, False)
    theta = start + U * angle
    z0 = float(spec.get("z_min_mm", spec.get("z_mm", 0.0)))
    center = np.asarray(spec.get("center_xy", [0.0, 0.0]), dtype=np.float64)
    P = np.stack((center[0] + radius * np.cos(theta), center[1] + radius * np.sin(theta), z0 + V * height), axis=-1)
    N = np.stack((np.cos(theta), np.sin(theta), np.zeros_like(theta)), axis=-1)
    N *= float(spec.get("normal_sign", 1.0))
    return [SurfaceGrid(P, N, U, V, periodic_u, False, abs(radius * angle), height, {"type": "cylinder"})]


def make_cone(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    r0 = float(spec.get("radius_bottom_mm", spec.get("radius0_mm")))
    r1 = float(spec.get("radius_top_mm", spec.get("radius1_mm")))
    height = float(spec["height_mm"])
    angle_deg = float(spec.get("angle_deg", 360.0))
    angle = math.radians(angle_deg)
    start = math.radians(float(spec.get("start_angle_deg", 0.0)))
    periodic_u = bool(spec.get("periodic_u", abs(abs(angle_deg) - 360.0) < 1e-8))
    average_radius = 0.5 * (r0 + r1)
    slant = math.hypot(height, r1 - r0)
    nu = _samples(abs(average_radius * angle), pitch, periodic_u, 3)
    nv = _samples(slant, pitch, False)
    U, V = _uv_mesh(nu, nv, periodic_u, False)
    theta = start + U * angle
    radius = r0 + (r1 - r0) * V
    z0 = float(spec.get("z_min_mm", spec.get("z_mm", 0.0)))
    center = np.asarray(spec.get("center_xy", [0.0, 0.0]), dtype=np.float64)
    P = np.stack((center[0] + radius * np.cos(theta), center[1] + radius * np.sin(theta), z0 + V * height), axis=-1)
    dr_dz = (r1 - r0) / height
    N = np.stack((np.cos(theta), np.sin(theta), np.full_like(theta, -dr_dz)), axis=-1)
    N = normalize_vectors(N) * float(spec.get("normal_sign", 1.0))
    return [SurfaceGrid(P, N, U, V, periodic_u, False, abs(average_radius * angle), slant, {"type": "cone"})]


def _rounded_rect_sample(width: float, depth: float, radius: float, s: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    if width <= 0 or depth <= 0 or radius < 0 or radius > min(width, depth) / 2:
        raise ValueError("Invalid rounded rectangle dimensions")
    straight_x = width - 2 * radius
    straight_y = depth - 2 * radius
    arc = 0.5 * math.pi * radius
    lengths = np.array([straight_x, arc, straight_y, arc, straight_x, arc, straight_y, arc], dtype=np.float64)
    perimeter = float(lengths.sum())
    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    smod = np.mod(s, perimeter)
    segment = np.searchsorted(cumulative[1:], smod, side="right")
    local = np.divide(
        smod - cumulative[segment],
        lengths[segment],
        out=np.zeros_like(smod),
        where=lengths[segment] > EPS,
    )
    x = np.zeros_like(smod)
    y = np.zeros_like(smod)
    nx = np.zeros_like(smod)
    ny = np.zeros_like(smod)
    for idx in range(8):
        m = segment == idx
        t = local[m]
        if not np.any(m):
            continue
        if idx == 0:
            x[m] = -width/2 + radius + t * straight_x; y[m] = -depth/2; nx[m] = 0; ny[m] = -1
        elif idx == 1:
            a = -math.pi/2 + t * math.pi/2
            x[m] = width/2-radius + radius*np.cos(a); y[m] = -depth/2+radius + radius*np.sin(a)
            nx[m] = np.cos(a); ny[m] = np.sin(a)
        elif idx == 2:
            x[m] = width/2; y[m] = -depth/2+radius + t*straight_y; nx[m] = 1; ny[m] = 0
        elif idx == 3:
            a = t * math.pi/2
            x[m] = width/2-radius + radius*np.cos(a); y[m] = depth/2-radius + radius*np.sin(a)
            nx[m] = np.cos(a); ny[m] = np.sin(a)
        elif idx == 4:
            x[m] = width/2-radius - t*straight_x; y[m] = depth/2; nx[m] = 0; ny[m] = 1
        elif idx == 5:
            a = math.pi/2 + t*math.pi/2
            x[m] = -width/2+radius + radius*np.cos(a); y[m] = depth/2-radius + radius*np.sin(a)
            nx[m] = np.cos(a); ny[m] = np.sin(a)
        elif idx == 6:
            x[m] = -width/2; y[m] = depth/2-radius - t*straight_y; nx[m] = -1; ny[m] = 0
        else:
            a = math.pi + t*math.pi/2
            x[m] = -width/2+radius + radius*np.cos(a); y[m] = -depth/2+radius + radius*np.sin(a)
            nx[m] = np.cos(a); ny[m] = np.sin(a)
    return np.column_stack((x, y)), np.column_stack((nx, ny)), perimeter


def make_rounded_rectangle_wall(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    width = float(spec["width_mm"])
    depth = float(spec["depth_mm"])
    radius = float(spec.get("corner_radius_mm", 0.0))
    perimeter = 2*(width+depth-4*radius) + 2*math.pi*radius
    nu = _samples(perimeter, pitch, True, 4)
    height = float(spec["height_mm"])
    nv = _samples(height, pitch, False)
    U, V = _uv_mesh(nu, nv, True, False)
    start_offset = float(spec.get("start_offset_mm", 0.0))
    xy, nxy, perimeter2 = _rounded_rect_sample(width, depth, radius, U[0] * perimeter + start_offset)
    xy_grid = np.broadcast_to(xy[None, :, :], (nv, nu, 2))
    n_grid = np.broadcast_to(nxy[None, :, :], (nv, nu, 2))
    center = np.asarray(spec.get("center_xy", [0.0, 0.0]), dtype=np.float64)
    z0 = float(spec.get("z_min_mm", spec.get("z_mm", 0.0)))
    P = np.concatenate((xy_grid + center, (z0 + V * height)[..., None]), axis=2)
    N = np.concatenate((n_grid, np.zeros((nv, nu, 1))), axis=2) * float(spec.get("normal_sign", 1.0))
    return [SurfaceGrid(P, N, U, V, True, False, perimeter2, height, {"type": "rounded_rectangle_wall"})]


def make_polygon_wall(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    points = _polygon_points(spec)
    perimeter = float(np.linalg.norm(np.roll(points, -1, axis=0) - points, axis=1).sum())
    nu = _samples(perimeter, pitch, True, max(3, len(points)))
    height = float(spec["height_mm"])
    nv = _samples(height, pitch, False)
    U, V = _uv_mesh(nu, nv, True, False)
    xy, nxy, perimeter2 = _polyline_samples(points, nu)
    center = np.asarray(spec.get("center_xy", [0.0, 0.0]), dtype=np.float64)
    xy_grid = np.broadcast_to((xy + center)[None, :, :], (nv, nu, 2))
    n_grid = np.broadcast_to(nxy[None, :, :], (nv, nu, 2))
    z0 = float(spec.get("z_min_mm", spec.get("z_mm", 0.0)))
    P = np.concatenate((xy_grid, (z0 + V * height)[..., None]), axis=2)
    N = np.concatenate((n_grid, np.zeros((nv, nu, 1))), axis=2) * float(spec.get("normal_sign", 1.0))
    return [SurfaceGrid(P, N, U, V, True, False, perimeter2, height, {"type": "polygon_wall"})]


def make_sphere(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    radius = float(spec["radius_mm"])
    lon0 = math.radians(float(spec.get("longitude_start_deg", -180.0)))
    lon_span_deg = float(spec.get("longitude_span_deg", 360.0))
    lon_span = math.radians(lon_span_deg)
    lat0 = math.radians(float(spec.get("latitude_min_deg", -80.0)))
    lat1 = math.radians(float(spec.get("latitude_max_deg", 80.0)))
    periodic_u = bool(spec.get("periodic_u", abs(abs(lon_span_deg) - 360.0) < 1e-8))
    nu = _samples(abs(radius * lon_span), pitch, periodic_u, 3)
    nv = _samples(abs(radius * (lat1-lat0)), pitch, False, 2)
    U, V = _uv_mesh(nu, nv, periodic_u, False)
    lon = lon0 + U*lon_span
    lat = lat0 + V*(lat1-lat0)
    direction = np.stack((np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)), axis=-1)
    center = _vector3(spec.get("center", [0,0,0]), "center")
    P = center + radius*direction
    N = direction * float(spec.get("normal_sign", 1.0))
    return [SurfaceGrid(P, N, U, V, periodic_u, False, abs(radius*lon_span), abs(radius*(lat1-lat0)), {"type":"sphere"})]


def make_torus(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    major = float(spec["major_radius_mm"])
    minor = float(spec["minor_radius_mm"])
    u_span_deg = float(spec.get("major_angle_deg", 360.0))
    v_span_deg = float(spec.get("minor_angle_deg", 360.0))
    u_span = math.radians(u_span_deg)
    v_span = math.radians(v_span_deg)
    periodic_u = bool(spec.get("periodic_u", abs(abs(u_span_deg)-360.0) < 1e-8))
    periodic_v = bool(spec.get("periodic_v", abs(abs(v_span_deg)-360.0) < 1e-8))
    nu = _samples(abs((major+minor)*u_span), pitch, periodic_u, 3)
    nv = _samples(abs(minor*v_span), pitch, periodic_v, 3)
    U,V = _uv_mesh(nu,nv,periodic_u,periodic_v)
    a = math.radians(float(spec.get("major_start_deg",0.0))) + U*u_span
    b = math.radians(float(spec.get("minor_start_deg",0.0))) + V*v_span
    radial = major + minor*np.cos(b)
    center = _vector3(spec.get("center",[0,0,0]),"center")
    P = np.stack((radial*np.cos(a), radial*np.sin(a), minor*np.sin(b)),axis=-1)+center
    N = np.stack((np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)),axis=-1)
    N *= float(spec.get("normal_sign",1.0))
    return [SurfaceGrid(P,N,U,V,periodic_u,periodic_v,abs((major+minor)*u_span),abs(minor*v_span),{"type":"torus"})]


def make_polygon_ring_plane(spec: dict[str, Any], pitch: float) -> list[SurfaceGrid]:
    outer = _polygon_points(spec, "outer_")
    inner = _polygon_points(spec, "inner_")
    if len(outer) != len(inner):
        raise ValueError("outer and inner polygons must have the same number of vertices")
    z = float(spec.get("z_mm", 0.0))
    sign = float(spec.get("normal_sign", 1.0))
    gap = max(0.0, float(spec.get("edge_gap_mm", 0.0)))
    grids: list[SurfaceGrid] = []
    n = len(outer)
    for i in range(n):
        j = (i+1)%n
        oe = outer[j]-outer[i]; ie = inner[j]-inner[i]
        ol = float(np.linalg.norm(oe)); il = float(np.linalg.norm(ie))
        if 2*gap >= min(ol,il):
            raise ValueError("edge_gap_mm is too large for a polygon sector")
        o0 = outer[i] + oe*(gap/ol); o1 = outer[j] - oe*(gap/ol)
        i0 = inner[i] + ie*(gap/il); i1 = inner[j] - ie*(gap/il)
        tangential = max(np.linalg.norm(o1-o0),np.linalg.norm(i1-i0))
        radial = max(np.linalg.norm(o0-i0),np.linalg.norm(o1-i1))
        nu = _samples(float(tangential),pitch,False)
        nv = _samples(float(radial),pitch,False)
        U,V = _uv_mesh(nu,nv,False,False)
        inner_line = i0[None,None,:]*(1-U[...,None]) + i1[None,None,:]*U[...,None]
        outer_line = o0[None,None,:]*(1-U[...,None]) + o1[None,None,:]*U[...,None]
        xy = inner_line*(1-V[...,None]) + outer_line*V[...,None]
        P = np.concatenate((xy,np.full((nv,nu,1),z)),axis=2)
        N = np.zeros_like(P); N[...,2]=sign
        grids.append(SurfaceGrid(P,N,U,V,False,False,float(tangential),float(radial),{"type":"polygon_ring_plane","sector":i}))
    return grids


def make_grid_npz(spec: dict[str, Any], pitch: float, config_dir: Path) -> list[SurfaceGrid]:
    path = Path(spec["npz"])
    if not path.is_absolute():
        path = config_dir/path
    with np.load(path) as data:
        positions = np.asarray(data["positions"],dtype=np.float64)
        periodic_u = bool(spec.get("periodic_u", bool(data["periodic_u"]) if "periodic_u" in data else False))
        periodic_v = bool(spec.get("periodic_v", bool(data["periodic_v"]) if "periodic_v" in data else False))
        normals = np.asarray(data["normals"],dtype=np.float64) if "normals" in data else _derive_normals(positions,periodic_u,periodic_v)
        nv,nu = positions.shape[:2]
        U,V = _uv_mesh(nu,nv,periodic_u,periodic_v)
        ul = float(spec.get("u_length_mm", data["u_length_mm"] if "u_length_mm" in data else 1.0))
        vl = float(spec.get("v_length_mm", data["v_length_mm"] if "v_length_mm" in data else 1.0))
    normals *= float(spec.get("normal_sign",1.0))
    return [SurfaceGrid(positions,normals,U,V,periodic_u,periodic_v,ul,vl,{"type":"grid_npz","npz":str(path)})]


SURFACE_BUILDERS = {
    "plane": make_plane,
    "cylinder": make_cylinder,
    "cone": make_cone,
    "frustum": make_cone,
    "rounded_rectangle_wall": make_rounded_rectangle_wall,
    "polygon_wall": make_polygon_wall,
    "sphere": make_sphere,
    "torus": make_torus,
    "polygon_ring_plane": make_polygon_ring_plane,
}


def build_surface_grids(spec: dict[str, Any], pitch: float, config_dir: Path) -> list[SurfaceGrid]:
    kind = spec.get("type")
    if kind == "grid_npz":
        return make_grid_npz(spec,pitch,config_dir)
    if kind not in SURFACE_BUILDERS:
        raise ValueError(f"Unsupported surface type: {kind!r}")
    return SURFACE_BUILDERS[kind](spec,pitch)


class HeightSampler:
    def __init__(self, image: np.ndarray):
        values = np.asarray(image,dtype=np.float32)
        if values.ndim != 2:
            raise ValueError("Height map must be two-dimensional")
        self.image = values

    @classmethod
    def from_path(cls,path: Path) -> "HeightSampler":
        values,_ = load_image_float(path)
        return cls(values)

    def sample(self,grid: SurfaceGrid,mapping: dict[str,Any]) -> np.ndarray:
        mode = mapping.get("mode","surface_uv")
        if mode == "surface_uv":
            u = grid.u.copy(); v = grid.v.copy()
        elif mode == "planar_axes":
            origin = _vector3(mapping.get("origin",[0,0,0]),"mapping.origin")
            axis_u = normalize_vectors(_vector3(mapping.get("axis_u",[1,0,0]),"mapping.axis_u"))
            axis_v = normalize_vectors(_vector3(mapping.get("axis_v",[0,1,0]),"mapping.axis_v"))
            tile_w = float(mapping["tile_width_mm"]); tile_h = float(mapping["tile_height_mm"])
            delta = grid.positions-origin
            u = np.sum(delta*axis_u,axis=2)/tile_w
            v = np.sum(delta*axis_v,axis=2)/tile_h
        else:
            raise ValueError(f"Unsupported mapping mode: {mode}")

        if mapping.get("swap_uv",False):
            u,v = v,u
        q = int(mapping.get("rotate_quarter_turns",0))%4
        if q == 1:
            u,v = v,1.0-u
        elif q == 2:
            u,v = 1.0-u,1.0-v
        elif q == 3:
            u,v = 1.0-v,u
        if mapping.get("flip_u",False):
            u=1.0-u
        if mapping.get("flip_v",False):
            v=1.0-v
        u = u*float(mapping.get("repeat_u",1.0))+float(mapping.get("offset_u",0.0))
        v = v*float(mapping.get("repeat_v",1.0))+float(mapping.get("offset_v",0.0))
        wrap_u = bool(mapping.get("wrap_u",grid.periodic_u))
        wrap_v = bool(mapping.get("wrap_v",grid.periodic_v))
        if wrap_u: u=np.mod(u,1.0)
        else: u=np.clip(u,0.0,1.0)
        if wrap_v: v=np.mod(v,1.0)
        else: v=np.clip(v,0.0,1.0)

        h,w = self.image.shape
        order=int(mapping.get("interpolation_order",1))
        x = u*w if wrap_u else u*max(w-1,0)
        y = v*h if wrap_v else v*max(h-1,0)
        if wrap_u: x=np.mod(x,w)
        if wrap_v: y=np.mod(y,h)

        # Pad each axis independently so interpolation crosses a periodic seam
        # only on axes explicitly marked as wrapped. A single scipy boundary
        # mode cannot express "wrap U, clamp V".
        pad=max(1,order+1)
        image=self.image
        image=np.pad(
            image,((pad,pad),(0,0)),mode="wrap" if wrap_v else "edge"
        )
        image=np.pad(
            image,((0,0),(pad,pad)),mode="wrap" if wrap_u else "edge"
        )
        x=x+pad; y=y+pad
        sampled = ndimage.map_coordinates(
            image,[y,x],order=order,mode="nearest",prefilter=order>1,
        )
        return np.clip(sampled,0.0,1.0).astype(np.float32)


def _edge_taper(grid: SurfaceGrid, spec: Any) -> np.ndarray:
    if spec is None:
        return np.ones(grid.shape,dtype=np.float32)
    if isinstance(spec,(int,float)):
        tu=tv=float(spec)
    elif isinstance(spec,dict):
        tu=float(spec.get("u",0.0)); tv=float(spec.get("v",0.0))
    else:
        raise ValueError("edge_taper_mm must be a number or {u,v}")
    factor=np.ones(grid.shape,dtype=np.float32)
    if tu>0 and not grid.periodic_u:
        d=np.minimum(grid.u,1.0-grid.u)*grid.u_length_mm
        factor*=smoothstep01(d/tu)
    if tv>0 and not grid.periodic_v:
        d=np.minimum(grid.v,1.0-grid.v)*grid.v_length_mm
        factor*=smoothstep01(d/tv)
    return factor


def _grid_faces(grid: SurfaceGrid, top_offset: int, bottom_offset: int) -> np.ndarray:
    """Vectorized two-skin grid triangulation plus boundary side walls."""
    nv,nu=grid.shape
    v_cells=nv if grid.periodic_v else nv-1
    u_cells=nu if grid.periodic_u else nu-1

    I,J=np.meshgrid(
        np.arange(v_cells,dtype=np.int64),
        np.arange(u_cells,dtype=np.int64),
        indexing="ij",
    )
    a=(I%nv)*nu+(J%nu)
    b=(I%nv)*nu+((J+1)%nu)
    c=((I+1)%nv)*nu+((J+1)%nu)
    d=((I+1)%nv)*nu+(J%nu)
    a=a.ravel(); b=b.ravel(); c=c.ravel(); d=d.ravel()

    flat_p=grid.positions.reshape(-1,3)
    flat_n=grid.normals.reshape(-1,3)
    orientation=np.einsum(
        "ij,ij->i",
        np.cross(flat_p[b]-flat_p[a],flat_p[c]-flat_p[a]),
        flat_n[a]+flat_n[b]+flat_n[c],
    )
    flip=orientation<0
    b1=np.where(flip,c,b)
    c1=np.where(flip,b,c)
    c2=np.where(flip,d,c)
    d2=np.where(flip,c,d)
    tri1=np.column_stack((a,b1,c1))
    tri2=np.column_stack((a,c2,d2))
    top=np.stack((tri1,tri2),axis=1).reshape(-1,3)+top_offset
    bottom=np.stack((tri1[:,::-1],tri2[:,::-1]),axis=1).reshape(-1,3)+bottom_offset
    faces=[top,bottom]

    def idx(i:int,j:int)->int:
        return (i%nv)*nu+(j%nu)

    loops: list[list[int]]=[]
    if not grid.periodic_u and not grid.periodic_v:
        # Counter-clockwise in the native (u,v) parameter domain.
        loop=[idx(0,j) for j in range(nu)]
        loop += [idx(i,nu-1) for i in range(1,nv)]
        loop += [idx(nv-1,j) for j in range(nu-2,-1,-1)]
        loop += [idx(i,0) for i in range(nv-2,0,-1)]
        loops=[loop]
    elif grid.periodic_u and not grid.periodic_v:
        # Bottom boundary runs +u; top boundary runs -u.
        loops=[
            [idx(0,j) for j in range(nu)],
            [idx(nv-1,j) for j in range(nu-1,-1,-1)],
        ]
    elif not grid.periodic_u and grid.periodic_v:
        # Left boundary runs -v; right boundary runs +v.
        loops=[
            [idx(i,0) for i in range(nv-1,-1,-1)],
            [idx(i,nu-1) for i in range(nv)],
        ]

    # If desired surface normals oppose the native parameter orientation,
    # reverse every boundary loop so it still follows the oriented top skin.
    if orientation.size and float(np.median(orientation)) < 0:
        loops=[list(reversed(loop)) for loop in loops]

    side_faces=[]
    for loop in loops:
        values=np.asarray(loop,dtype=np.int64)
        nxt=np.roll(values,-1)
        # For an oriented top boundary, cross(edge, top-normal) points out.
        side_faces.append(np.column_stack((
            values+top_offset,nxt+bottom_offset,nxt+top_offset
        )))
        side_faces.append(np.column_stack((
            values+top_offset,values+bottom_offset,nxt+bottom_offset
        )))
    if side_faces:
        faces.append(np.vstack(side_faces))
    return np.vstack(faces).astype(np.int64,copy=False)


def build_closed_patch(
    grid: SurfaceGrid,
    heights: np.ndarray,
    *,
    mode: str,
    depth_mm: float,
    overlap_mm: float,
) -> trimesh.Trimesh:
    if mode not in {"emboss","engrave"}:
        raise ValueError("mode must be emboss or engrave")
    if depth_mm<=0 or overlap_mm<=0:
        raise ValueError("depth_mm and overlap_mm must be positive")
    h=np.asarray(heights,dtype=np.float64)
    if h.shape!=grid.shape:
        raise ValueError("height array does not match surface grid")
    if mode=="emboss":
        top=grid.positions+grid.normals*(depth_mm*h)[...,None]
        bottom=grid.positions-grid.normals*overlap_mm
    else:
        top=grid.positions+grid.normals*overlap_mm
        bottom=grid.positions-grid.normals*(depth_mm*h)[...,None]
    n=grid.grid_vertices
    vertices=np.vstack((top.reshape(-1,3),bottom.reshape(-1,3)))
    faces=_grid_faces(grid,0,n)
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False,validate=False)
    mesh.remove_unreferenced_vertices()
    # Face winding is constructed analytically. Avoid a global graph traversal
    # here: on million-triangle print meshes it can dominate runtime and memory.
    return mesh


def _merge_dicts(*items: dict[str,Any]) -> dict[str,Any]:
    result: dict[str,Any]={}
    for item in items:
        if item: result.update(item)
    return result


def _mesh_summary(mesh: trimesh.Trimesh) -> dict[str,Any]:
    edges=np.sort(mesh.edges,axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True)
    return {
        "vertices":int(len(mesh.vertices)),
        "triangles":int(len(mesh.faces)),
        "watertight":bool(mesh.is_watertight),
        "winding_consistent":bool(mesh.is_winding_consistent),
        "is_volume":bool(mesh.is_volume),
        "body_count":int(mesh.body_count),
        "boundary_edges":int(np.sum(counts==1)),
        "nonmanifold_edges":int(np.sum(counts>2)),
        "bounds_mm":mesh.bounds.tolist(),
        "extents_mm":mesh.extents.tolist(),
        "volume_mm3":float(mesh.volume),
    }


def generate_from_config(config_path: Path, output_path: Path, report_path: Path|None=None) -> dict[str,Any]:
    config_path=config_path.resolve()
    config=json.loads(config_path.read_text(encoding="utf-8"))
    config_dir=config_path.parent
    surfaces=config.get("surfaces")
    if surfaces is None:
        surfaces=[config["surface"]]
    if not isinstance(surfaces,list) or not surfaces:
        raise ValueError("surface or non-empty surfaces is required")
    default_pitch=float(config.get("mesh_pitch_mm",0.3))
    max_vertices=int(config.get("max_grid_vertices",5_000_000))
    root_mapping=config.get("mapping",{})
    root_relief=config.get("relief",{})
    root_heightmap=config.get("heightmap")
    cache: dict[Path,HeightSampler]={}
    meshes: list[trimesh.Trimesh]=[]
    surface_reports=[]
    total_grid=0
    for si,spec in enumerate(surfaces):
        pitch=float(spec.get("mesh_pitch_mm",default_pitch))
        grids=build_surface_grids(spec,pitch,config_dir)
        for gi,grid in enumerate(grids):
            total_grid+=grid.grid_vertices
            if total_grid>max_vertices:
                raise MemoryError(
                    f"Surface grids require more than max_grid_vertices={max_vertices:,}; "
                    "increase mesh_pitch_mm, split the job, or raise the guard intentionally."
                )
            hm=spec.get("heightmap",root_heightmap)
            if not hm:
                raise ValueError("heightmap is required at root or surface level")
            hm_path=Path(hm)
            if not hm_path.is_absolute(): hm_path=(config_dir/hm_path).resolve()
            if hm_path not in cache: cache[hm_path]=HeightSampler.from_path(hm_path)
            mapping=_merge_dicts(root_mapping,spec.get("mapping",{}))
            relief=_merge_dicts(root_relief,spec.get("relief",{}))
            mode=str(spec.get("mode",config.get("mode","engrave")))
            depth=float(spec.get("relief_depth_mm",relief.get("depth_mm",0.6)))
            overlap=float(spec.get("relief_overlap_mm",relief.get("overlap_mm",0.08)))
            heights=cache[hm_path].sample(grid,mapping)
            if bool(relief.get("invert",False)): heights=1.0-heights
            lo=float(relief.get("input_min",0.0)); hi=float(relief.get("input_max",1.0))
            if hi<=lo: raise ValueError("relief input_max must exceed input_min")
            heights=np.clip((heights-lo)/(hi-lo),0.0,1.0)
            heights=float(relief.get("output_min",0.0))+(float(relief.get("output_max",1.0))-float(relief.get("output_min",0.0)))*heights
            taper=spec.get("edge_taper_mm",config.get("edge_taper_mm"))
            heights=np.clip(heights*_edge_taper(grid,taper),0.0,1.0)
            mesh=build_closed_patch(grid,heights,mode=mode,depth_mm=depth,overlap_mm=overlap)
            meshes.append(mesh)
            surface_reports.append({
                "surface_index":si,"grid_index":gi,"surface":grid.metadata,
                "heightmap":str(hm_path),"mode":mode,"depth_mm":depth,"overlap_mm":overlap,
                "mesh_pitch_mm":pitch,"grid_shape_uv":[grid.shape[1],grid.shape[0]],
                "height_min":float(heights.min()),"height_max":float(heights.max()),
                "mesh":_mesh_summary(mesh),
            })
    combined=trimesh.util.concatenate(meshes)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    combined.export(output_path)
    report={
        "config":str(config_path),"output":str(output_path),
        "surface_parts":surface_reports,"grid_vertices_total":total_grid,
        "combined":_mesh_summary(combined),
    }
    if report_path: write_json(report,report_path)
    return report


def build_parser()->argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("config",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--report",type=Path)
    return p


def main()->int:
    args=build_parser().parse_args()
    report=generate_from_config(args.config,args.output,args.report)
    print(json.dumps(report["combined"],indent=2,sort_keys=True))
    if not report["combined"]["watertight"]:
        print("WARNING: generated mesh is not watertight",file=sys.stderr)
        return 1
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        raise SystemExit(2)
