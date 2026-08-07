#!/usr/bin/env python3
"""Functional validation of the reloaded final unicorn dice-tower STL (spiral v2)."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
PARAMS = json.loads((ROOT / "parameters.json").read_text(encoding="utf-8"))
FINAL = ROOT / "exports" / "functional_unicorn_dice_tower.stl"
REPORT = ROOT / "reports" / "functional_validation.json"
PATH_REPORT = ROOT / "reports" / "die_path_clearance.json"
PATH_LOG = ROOT / "reports" / "die_path_clearance.log"
COLLISION = ROOT / "diagnostics" / "final_die_path_collision.stl"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ray_hits(mesh, origin, direction, max_distance=math.inf) -> np.ndarray:
    """Brute-force Moller-Trumbore ray/triangle intersections (deterministic)."""
    origin = np.asarray(origin, dtype=float)
    direction = np.asarray(direction, dtype=float)
    direction /= np.linalg.norm(direction)
    tri = np.asarray(mesh.triangles, dtype=float)
    v0 = tri[:, 0]
    e1 = tri[:, 1] - v0
    e2 = tri[:, 2] - v0
    h = np.cross(np.broadcast_to(direction, e2.shape), e2)
    a = np.einsum("ij,ij->i", e1, h)
    valid = np.abs(a) > 1e-9
    f = np.zeros_like(a)
    f[valid] = 1.0 / a[valid]
    s = np.broadcast_to(origin, v0.shape) - v0
    u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    v = f * np.einsum("j,ij->i", direction, q)
    t = f * np.einsum("ij,ij->i", e2, q)
    valid &= (u >= -1e-8) & (v >= -1e-8) & (u + v <= 1.0 + 1e-8)
    valid &= (t >= -1e-7) & (t <= max_distance + 1e-7)
    values = np.sort(t[valid])
    if len(values) == 0:
        return values
    unique = [float(values[0])]
    for value in values[1:]:
        if abs(float(value) - unique[-1]) > 1e-5:
            unique.append(float(value))
    return np.asarray(unique)


def segment_hits(mesh, start, end):
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    delta = end - start
    return ray_hits(mesh, start, delta, float(np.linalg.norm(delta)))


def line_coordinates(mesh, origin, direction, axis_index, max_distance):
    hits = ray_hits(mesh, origin, direction, max_distance)
    o = np.asarray(origin, dtype=float)
    d = np.asarray(direction, dtype=float)
    d /= np.linalg.norm(d)
    return np.round(o[axis_index] + hits * d[axis_index], 6)


def nearest(values, target):
    values = np.asarray(values, dtype=float)
    return float(values[np.argmin(np.abs(values - target))])


def elliptic_radius(fg, x, y):
    rx = float(fg["core_radius_x_mm"])
    ry = float(fg["core_radius_y_mm"])
    cy = float(fg["core_center_y_mm"])
    return math.sqrt((x / rx) ** 2 + ((y - cy) / ry) ** 2)


def spiral_evidence(mesh, fg) -> dict:
    """Discrete spiral staircase evidence: zone faces, shell/inner reach,
    per-step slab thickness rays, multi-turn stacking, and vertical
    enclosed-gap sampling between stair surfaces."""
    sp = fg["spiral"]
    t0 = float(sp["first_step_high_end_azimuth_deg"])
    idx = float(sp["step_index_angle_deg"])
    arc = float(sp["step_arc_deg"])
    z_first = float(sp["z_first_step_high_end_mm"])
    descent = float(sp["descent_per_step_mm"])
    n = int(sp["step_count"])
    rx_c = float(fg["core_radius_x_mm"]); ry_c = float(fg["core_radius_y_mm"])
    cy = float(fg["core_center_y_mm"])

    def elliptic_radius(x, y):
        return math.sqrt((x / rx_c) ** 2 + ((y - cy) / ry_c) ** 2)

    centroids = np.asarray(mesh.triangles_center)
    rho = np.array([elliptic_radius(c[0], c[1]) for c in centroids])
    zone = (
        (centroids[:, 2] >= 19.0) & (centroids[:, 2] <= 120.0)
        & (rho >= 0.36) & (rho <= 1.20)
    )
    zone_faces = int(np.count_nonzero(zone))
    zone_rho = rho[zone]
    reaches_shell = bool(zone_faces > 0 and float(zone_rho.max()) >= 0.99)
    reaches_inner = bool(zone_faces > 0 and float(zone_rho.min()) <= 0.60)

    # Slab thickness rays through three stair midpoints (different turns).
    thickness_rays = []
    for step_i in [1, 4, 7]:
        t_mid = math.radians(t0 + step_i * idx + arc / 2.0)
        x = 28.0 * math.cos(t_mid); y = cy + 13.0 * math.sin(t_mid)
        coords = line_coordinates(mesh, [x, y, 125.0], [0.0, 0.0, -1.0], 2, 108.0)
        diffs = np.diff(coords)
        pairs = [round(float(d), 6) for d in diffs if 4.2 <= d <= 4.8]
        thickness_rays.append({
            "step_index": step_i,
            "azimuth_deg": round(math.degrees(t_mid) % 360, 2),
            "point_xy_mm": [round(x, 3), round(y, 3)],
            "z_intersections_mm": coords.tolist(),
            "measured_slab_pairs_mm": pairs,
        })
    thickness_ok = all(len(r["measured_slab_pairs_mm"]) >= 1 for r in thickness_rays)

    # Multi-turn stacking: an azimuth covered by two stair turns.
    theta_check = 150.0
    rad = math.degrees and math.radians(theta_check)
    x = 28.0 * math.cos(rad); y = cy + 13.0 * math.sin(rad)
    turns_coords = line_coordinates(mesh, [x, y, 125.0], [0.0, 0.0, -1.0], 2, 108.0)
    turns_diffs = np.diff(turns_coords)
    slab_hits = int(np.count_nonzero((turns_diffs >= 4.2) & (turns_diffs <= 4.8)))

    # Enclosed-gap sampling: vertical rays across the spiral; every gap between
    # surfaces above the floor band that is thicker than a slab must be >= 30 mm.
    gap_samples = []
    for theta_deg in range(100, 350, 30):
        t_rad = math.radians(theta_deg)
        rmax = 1.0 / math.sqrt(
            (math.cos(t_rad) / rx_c) ** 2 + (math.sin(t_rad) / ry_c) ** 2
        )
        for frac in (0.50, 0.78):
            x = frac * rmax * math.cos(t_rad)
            y = cy + frac * rmax * math.sin(t_rad)
            coords = line_coordinates(mesh, [x, y, 125.0], [0.0, 0.0, -1.0], 2, 108.0)
            diffs = np.diff(coords)
            lows = coords[:-1]
            for low, d in zip(lows, diffs):
                if float(low) >= 27.0 and float(d) >= 6.0:
                    gap_samples.append({
                        "azimuth_deg": theta_deg,
                        "xy_mm": [round(x, 2), round(y, 2)],
                        "lower_surface_z_mm": round(float(low), 3),
                        "gap_mm": round(float(d), 3),
                    })
    min_gap = min(g["gap_mm"] for g in gap_samples) if gap_samples else None
    gaps_ok = bool(min_gap is not None and min_gap >= 29.5)

    passed = bool(
        zone_faces >= 2500
        and reaches_shell
        and reaches_inner
        and thickness_ok
        and slab_hits >= 2
        and gaps_ok
        and mesh.body_count == 1
    )
    return {
        "method": "Actual-STL evidence: staircase-zone faces by elliptic radius/height; vertical thickness rays through three stair midpoints; a two-turn stacking ray; and vertical enclosed-gap sampling between all stair surfaces above the floor.",
        "declared_shell_radial_overlap_mm": sp["shell_radial_overlap_mm"],
        "zone_face_count": zone_faces,
        "zone_normalized_radius_min": None if zone_faces == 0 else round(float(zone_rho.min()), 6),
        "zone_normalized_radius_max": None if zone_faces == 0 else round(float(zone_rho.max()), 6),
        "reaches_shell_overlap_band": reaches_shell,
        "reaches_inner_edge": reaches_inner,
        "thickness_rays": thickness_rays,
        "thickness_ok": thickness_ok,
        "two_turn_stacking_azimuth_deg": theta_check,
        "slab_hits_at_two_turn_azimuth": slab_hits,
        "enclosed_gap_samples": gap_samples,
        "minimum_enclosed_gap_mm": min_gap,
        "enclosed_gaps_ok": gaps_ok,
        "global_final_mesh_body_count": int(mesh.body_count),
        "passed": passed,
    }


def run_path_check(final_sha: str) -> dict:
    COLLISION.parent.mkdir(parents=True, exist_ok=True)
    COLLISION.unlink(missing_ok=True)
    command = [
        "openscad",
        "-o",
        str(COLLISION),
        str(ROOT / "validate_die_path.scad"),
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    combined = (completed.stdout or "") + (completed.stderr or "")
    PATH_LOG.write_text(combined, encoding="utf-8")
    collision_exists = COLLISION.exists() and COLLISION.stat().st_size > 0
    collision_volume = 0.0
    if collision_exists:
        collision_mesh = trimesh.load_mesh(COLLISION, process=True)
        collision_mesh.merge_vertices()
        collision_volume = float(abs(collision_mesh.volume))
    empty_message = "Current top level object is empty" in combined
    passed = bool(completed.returncode == 1 and empty_message and not collision_exists)
    evidence = {
        "actual_final_stl": str(FINAL),
        "actual_final_sha256": final_sha,
        "proxy": PARAMS["functional_geometry"]["die_path"]["proxy"],
        "cube_size_mm": PARAMS["functional_geometry"]["die_path"]["cube_size_mm"],
        "waypoints_mm": PARAMS["functional_geometry"]["die_path"]["waypoints_mm"],
        "method": "OpenSCAD CGAL intersection of the actual final STL reloaded from disk with the hull-swept axis-aligned die cube along spiral waypoints.",
        "command": command,
        "openscad_exit_code": completed.returncode,
        "empty_intersection_message_seen": empty_message,
        "collision_output_exists": collision_exists,
        "collision_volume_mm3": collision_volume,
        "physics_simulation": False,
        "interpretation": "A pass proves this conservative prescribed 22 mm geometric path is collision-free; it does not simulate gravity, bounce, rotation, or jamming.",
        "passed": passed,
    }
    PATH_REPORT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    return evidence


def main() -> int:
    fg = PARAMS["functional_geometry"]
    source = (ROOT / PARAMS["source"]["path"]).resolve()
    source_sha = sha256(source)
    source_unchanged = source_sha == PARAMS["source"]["sha256"]
    final_sha = sha256(FINAL)

    mesh = trimesh.load_mesh(FINAL, process=True)
    mesh.merge_vertices()

    bottom_mask = (
        (mesh.triangles_center[:, 2] <= 0.2)
        & (mesh.face_normals[:, 2] < -0.90)
    )
    bottom_area = float(mesh.area_faces[bottom_mask].sum())
    floor_samples = []
    for x, y in [(0.0, 25.0), (0.0, -40.0), (-35.0, -25.0), (35.0, -25.0)]:
        coords = line_coordinates(mesh, [x, y, -5.0], [0, 0, 1], 2, 230.0)
        first = float(coords[0]) if len(coords) else None
        floor_samples.append({
            "xy_mm": [x, y],
            "z_intersections_mm": coords[:8].tolist(),
            "first_hit_is_z0": bool(first is not None and abs(first) <= 0.1),
        })
    center_hits = line_coordinates(mesh, [0.0, 25.0, -5.0], [0, 0, 1], 2, 230.0)
    measured_base = float(center_hits[1] - center_hits[0]) if len(center_hits) >= 2 else None
    underside_pass = bool(
        mesh.is_watertight
        and abs(float(mesh.bounds[0, 2])) <= 1e-5
        and bottom_area > 1000.0
        and all(s["first_hit_is_z0"] for s in floor_samples)
        and measured_base is not None
        and abs(measured_base - fg["base_floor_min_thickness_mm"]) <= 0.1
    )

    opening_tests = {}
    opening_specs = {
        "inlet_back_plus_y": {
            "xs": [-15.0, 0.0, 15.0], "zs": [126.0, 139.0, 152.0],
            "start_y": 65.0, "end_y": 37.0,
            "declared_clear_width_mm": fg["inlet"]["clear_width_mm"],
            "declared_clear_height_mm": fg["inlet"]["clear_height_mm"],
        },
        "outlet_front_minus_y": {
            "xs": [-15.0, 0.0, 15.0], "zs": [30.0, 41.0, 52.0],
            "start_y": -28.0, "end_y": 17.0,
            "declared_clear_width_mm": fg["outlet"]["clear_width_mm"],
            "declared_clear_height_mm": fg["outlet"]["clear_height_mm"],
        },
    }
    for name, spec in opening_specs.items():
        rays = []
        for x in spec["xs"]:
            for z in spec["zs"]:
                hits = segment_hits(mesh, [x, spec["start_y"], z], [x, spec["end_y"], z])
                rays.append({
                    "x_z_mm": [x, z],
                    "segment_y_mm": [spec["start_y"], spec["end_y"]],
                    "intersection_count": int(len(hits)),
                    "hit_distances_mm": np.round(hits, 6).tolist(),
                    "clear": bool(len(hits) == 0),
                })
        opening_tests[name] = {
            "declared_clear_width_mm": spec["declared_clear_width_mm"],
            "declared_clear_height_mm": spec["declared_clear_height_mm"],
            "clear_test_rays": len(rays),
            "clear_rays": int(sum(r["clear"] for r in rays)),
            "rays": rays,
            "method": "Nine center-region line segments run from outside through the wall to a point analytically inside the elliptical core on the actual STL.",
            "passed": bool(all(r["clear"] for r in rays)),
        }

    x_mid = line_coordinates(mesh, [-80, 25, 115], [1, 0, 0], 0, 160)
    x_top = line_coordinates(mesh, [-80, 25, 149], [1, 0, 0], 0, 160)
    y_mid = line_coordinates(mesh, [30, -50, 115], [0, 1, 0], 1, 130)
    x_mid_targets = [-49.0, -42.0, 42.0, 49.0]
    x_mid_pick = [nearest(x_mid, t) for t in x_mid_targets]
    x_top_targets = [-46.0, -42.0, 42.0, 46.0]
    x_top_pick = [nearest(x_top, t) for t in x_top_targets]
    dy = fg["core_radius_y_mm"] * math.sqrt(1.0 - (30.0 / fg["core_radius_x_mm"]) ** 2)
    y_inner_front = fg["core_center_y_mm"] - dy
    y_inner_back = fg["core_center_y_mm"] + dy
    y_front_inner = nearest(y_mid, y_inner_front)
    y_back_inner = nearest(y_mid, y_inner_back)
    y_front_outer_candidates = [v for v in y_mid if v < y_front_inner - 0.5]
    y_back_outer_candidates = [v for v in y_mid if v > y_back_inner + 0.5]
    y_front_outer = float(max(y_front_outer_candidates)) if y_front_outer_candidates else None
    y_back_outer = float(min(y_back_outer_candidates)) if y_back_outer_candidates else None
    wall = {
        "mid_height_z_mm": 115.0,
        "x_axis_intersections_mm": x_mid.tolist(),
        "x_wall_samples_mm": {
            "negative_x": round(x_mid_pick[1] - x_mid_pick[0], 6),
            "positive_x": round(x_mid_pick[3] - x_mid_pick[2], 6),
        },
        "top_core_z_mm": 149.0,
        "top_x_axis_intersections_mm": x_top.tolist(),
        "top_x_wall_samples_mm": {
            "negative_x": round(x_top_pick[1] - x_top_pick[0], 6),
            "positive_x": round(x_top_pick[3] - x_top_pick[2], 6),
        },
        "mid_height_y_line_at_x30_intersections_mm": y_mid.tolist(),
        "y_wall_samples_mm": {
            "front": None if y_front_outer is None else round(y_front_inner - y_front_outer, 6),
            "back": None if y_back_outer is None else round(y_back_outer - y_back_inner, 6),
        },
    }
    wall_values = list(wall["x_wall_samples_mm"].values()) + list(wall["top_x_wall_samples_mm"].values())
    wall_values += [v for v in wall["y_wall_samples_mm"].values() if v is not None]
    wall["minimum_measured_sample_mm"] = round(float(min(wall_values)), 6)
    wall["note"] = "Samples exclude through-openings and include the narrow core-to-dome transition at Z=149; decorative relief can only add local thickness at these lines."
    wall["passed"] = bool(wall["minimum_measured_sample_mm"] >= 3.0)

    spiral = spiral_evidence(mesh, fg)
    path = run_path_check(final_sha)

    report = {
        "actual_final_stl": str(FINAL),
        "actual_final_sha256": final_sha,
        "source_stl": str(source),
        "source_sha256_expected": PARAMS["source"]["sha256"],
        "source_sha256_actual": source_sha,
        "source_unchanged": source_unchanged,
        "mesh_reloaded_from_disk": True,
        "interior_generation": "spiral_stairs_v3",
        "mesh_summary": {
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "watertight": bool(mesh.is_watertight),
            "winding_consistent": bool(mesh.is_winding_consistent),
            "is_volume": bool(mesh.is_volume),
            "body_count": int(mesh.body_count),
            "volume_mm3": float(mesh.volume),
            "bounds_xyz_mm": np.round(mesh.bounds, 6).tolist(),
            "extents_xyz_mm": np.round(mesh.extents, 6).tolist(),
            "z_min_mm": float(mesh.bounds[0, 2]),
        },
        "closed_underside": {
            "method": "Watertight topology plus downward bed-contact area and four independent +Z rays from below. The core-center ray measures the solid floor between its first two surface hits.",
            "downward_near_bed_face_area_within_0_2mm_mm2": bottom_area,
            "bed_surface_planarity_band_mm": 0.2,
            "ray_samples": floor_samples,
            "core_center_z_intersections_mm": center_hits[:12].tolist(),
            "measured_core_floor_thickness_mm": measured_base,
            "declared_floor_thickness_mm": fg["base_floor_min_thickness_mm"],
            "passed": underside_pass,
        },
        "opening_penetration": opening_tests,
        "wall_measurements": wall,
        "spiral_fusion_and_geometry": spiral,
        "die_path_clearance_report": str(PATH_REPORT),
        "die_path_passed": bool(path["passed"]),
    }
    report["passed"] = bool(
        source_unchanged
        and mesh.is_watertight
        and mesh.is_winding_consistent
        and mesh.is_volume
        and mesh.body_count == 1
        and mesh.volume > 0
        and abs(float(mesh.bounds[0, 2])) <= 1e-5
        and underside_pass
        and all(v["passed"] for v in opening_tests.values())
        and wall["passed"]
        and spiral["passed"]
        and path["passed"]
    )
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
