"""Inspect a returned organic/component mesh against its hybrid design contract.

Requires numpy and trimesh. The keep-out check is deliberately a fast AABB/vertex
screen; use exact CAD/mesh collision and swept-volume checks for acceptance.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import trimesh
except ImportError as exc:  # pragma: no cover - exercised only without optional deps
    raise SystemExit(
        "Missing dependency. Install the versions in scripts/requirements.txt "
        "inside the project environment."
    ) from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Plan not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid plan JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def flatten_scene(loaded: Any) -> trimesh.Trimesh:
    if isinstance(loaded, trimesh.Trimesh):
        return loaded.copy()
    if not isinstance(loaded, trimesh.Scene):
        raise SystemExit(f"Unsupported loaded geometry type: {type(loaded).__name__}")

    meshes = []
    for node_name in loaded.graph.nodes_geometry:
        transform, geometry_name = loaded.graph[node_name]
        geometry = loaded.geometry[geometry_name]
        if not isinstance(geometry, trimesh.Trimesh):
            continue
        candidate = geometry.copy()
        candidate.apply_transform(transform)
        meshes.append(candidate)
    if not meshes:
        raise SystemExit("The scene contains no triangle meshes")
    return trimesh.util.concatenate(meshes)


def load_mesh(path: Path) -> trimesh.Trimesh:
    try:
        # Standard processing merges coincident STL vertices and removes harmless
        # duplicate/degenerate data before topology checks. The raw file remains
        # untouched; report this normalization explicitly in the output.
        loaded = trimesh.load(path, force="scene", process=True)
    except Exception as exc:
        raise SystemExit(f"Failed to load mesh {path}: {exc}") from exc
    mesh = flatten_scene(loaded)
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise SystemExit("Mesh has no vertices or faces")
    return mesh


def find_component(plan: dict[str, Any], component_id: str) -> dict[str, Any]:
    matches = [item for item in plan.get("components", []) if item.get("id") == component_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one component {component_id!r}, found {len(matches)}")
    return matches[0]


def aabb_overlap(a_min: np.ndarray, a_max: np.ndarray, b_min: np.ndarray, b_max: np.ndarray) -> bool:
    return bool(np.all(a_max >= b_min) and np.all(b_max >= a_min))


def finite_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def connected_component_count(mesh: trimesh.Trimesh, max_faces: int = 2_000_000) -> int | None:
    """Count edge-connected face components without optional graph packages."""
    face_count = len(mesh.faces)
    if face_count > max_faces:
        return None
    parent = list(range(face_count))
    rank = bytearray(face_count)

    def find(item: int) -> int:
        root = item
        while parent[root] != root:
            root = parent[root]
        while parent[item] != item:
            next_item = parent[item]
            parent[item] = root
            item = next_item
        return root

    def union(a: int, b: int) -> None:
        root_a = find(a)
        root_b = find(b)
        if root_a == root_b:
            return
        if rank[root_a] < rank[root_b]:
            root_a, root_b = root_b, root_a
        parent[root_b] = root_a
        if rank[root_a] == rank[root_b]:
            rank[root_a] += 1

    for face_a, face_b in np.asarray(mesh.face_adjacency, dtype=np.int64):
        union(int(face_a), int(face_b))
    return len({find(face) for face in range(face_count)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Hybrid design plan JSON")
    parser.add_argument("component_id", help="Component ID in the plan")
    parser.add_argument("mesh", type=Path, help="Returned STL/OBJ/PLY/GLB or other trimesh-supported mesh")
    parser.add_argument("--report", type=Path, help="Write JSON report; otherwise print to stdout")
    parser.add_argument("--no-placement-transform", action="store_true", help="Apply scale but not the recorded placement transform")
    parser.add_argument("--fail-on-keepout", action="store_true", help="Treat detected keep-out vertices as failure")
    args = parser.parse_args()

    plan = load_json(args.plan)
    component = find_component(plan, args.component_id)
    mesh = load_mesh(args.mesh)

    errors: list[str] = []
    warnings: list[str] = []

    source_bounds = np.asarray(mesh.bounds, dtype=float)
    source_extents = np.asarray(mesh.extents, dtype=float)
    source_scale = finite_float(component.get("source_to_mm_scale"), 1.0)
    if source_scale <= 0:
        raise SystemExit("source_to_mm_scale must be positive")
    mesh.apply_scale(source_scale)

    transform = component.get("placement_transform")
    if not args.no_placement_transform:
        if not isinstance(transform, list) or len(transform) != 16:
            raise SystemExit("placement_transform must contain 16 numbers")
        matrix = np.asarray(transform, dtype=float).reshape((4, 4))
        if not np.isfinite(matrix).all():
            raise SystemExit("placement_transform contains non-finite values")
        mesh.apply_transform(matrix)

    processed_bounds = np.asarray(mesh.bounds, dtype=float)
    processed_extents = np.asarray(mesh.extents, dtype=float)
    vertices = np.asarray(mesh.vertices, dtype=float)

    component_count = connected_component_count(mesh)
    if component_count is None:
        warnings.append("Connected-component count skipped above 2,000,000 faces; use a dedicated mesh audit")

    acceptance = component.get("acceptance", {})
    expected_components = acceptance.get("expected_components")
    if component_count is not None and isinstance(expected_components, int) and component_count != expected_components:
        errors.append(f"Expected {expected_components} connected component(s), found {component_count}")

    watertight = bool(mesh.is_watertight)
    if acceptance.get("require_watertight") is True and not watertight:
        errors.append("Mesh is not watertight but the component contract requires watertight input")

    winding_consistent = bool(mesh.is_winding_consistent)
    if not winding_consistent:
        warnings.append("Mesh winding is inconsistent")

    volume = finite_float(mesh.volume)
    if watertight and volume <= 0:
        errors.append(f"Watertight mesh does not have positive volume (reported {volume:g} mm^3)")

    expected_envelope = component.get("envelope_mm", {})
    expected_min = np.asarray(expected_envelope.get("min", []), dtype=float)
    expected_max = np.asarray(expected_envelope.get("max", []), dtype=float)
    bounds_error_tolerance = finite_float(acceptance.get("max_bounds_error_mm"), 0.0)
    if expected_min.shape != (3,) or expected_max.shape != (3,):
        errors.append("Component contract has an invalid envelope_mm")
        lower_excess = upper_excess = np.zeros(3)
    else:
        lower_excess = np.maximum(expected_min - processed_bounds[0], 0.0)
        upper_excess = np.maximum(processed_bounds[1] - expected_max, 0.0)
        max_excess = float(max(lower_excess.max(initial=0.0), upper_excess.max(initial=0.0)))
        if max_excess > bounds_error_tolerance + 1e-9:
            errors.append(
                f"Registered mesh exceeds target envelope by up to {max_excess:g} mm; "
                f"contract allows {bounds_error_tolerance:g} mm"
            )

    related_interfaces = [
        interface
        for interface in plan.get("interfaces", [])
        if args.component_id in {interface.get("a"), interface.get("b")}
    ]
    related_keepout_ids = {
        keepout_id
        for interface in related_interfaces
        for keepout_id in interface.get("keepout_ids", [])
    }
    keepout_by_id = {item.get("id"): item for item in plan.get("keepouts", [])}
    keepout_results = []
    for keepout_id in sorted(related_keepout_ids):
        keepout = keepout_by_id.get(keepout_id)
        if not keepout:
            warnings.append(f"Referenced keep-out {keepout_id} is missing")
            continue
        if keepout.get("type") != "aabb":
            keepout_results.append({"id": keepout_id, "method": "not_evaluated", "reason": "only aabb is screened"})
            continue
        keep_min = np.asarray(keepout.get("min_mm", []), dtype=float)
        keep_max = np.asarray(keepout.get("max_mm", []), dtype=float)
        if keep_min.shape != (3,) or keep_max.shape != (3,):
            warnings.append(f"Keep-out {keepout_id} has invalid AABB")
            continue
        inside = np.all((vertices >= keep_min) & (vertices <= keep_max), axis=1)
        inside_count = int(inside.sum())
        bounds_overlap = aabb_overlap(processed_bounds[0], processed_bounds[1], keep_min, keep_max)
        result = {
            "id": keepout_id,
            "method": "vertex_aabb_screen",
            "bounds_overlap": bounds_overlap,
            "vertices_inside": inside_count,
            "vertex_fraction_inside": float(inside_count / len(vertices)),
        }
        keepout_results.append(result)
        if inside_count:
            message = f"Fast screen found {inside_count} mesh vertices inside keep-out {keepout_id}"
            (errors if args.fail_on_keepout else warnings).append(message)
        elif bounds_overlap:
            warnings.append(
                f"Mesh bounds overlap keep-out {keepout_id}, but no vertices were inside; "
                "triangle crossing remains possible and needs an exact collision check"
            )

    seam_results = []
    for interface in related_interfaces:
        frame = interface.get("local_frame", {})
        origin = np.asarray(frame.get("origin_mm", []), dtype=float)
        normal = np.asarray(frame.get("z_axis", []), dtype=float)
        if origin.shape != (3,) or normal.shape != (3,) or np.linalg.norm(normal) <= 1e-12:
            warnings.append(f"Interface {interface.get('id')} has an invalid seam frame")
            continue
        normal = normal / np.linalg.norm(normal)
        signed = (vertices - origin) @ normal
        band = finite_float(interface.get("seam_band_mm"), 0.0)
        within = np.abs(signed) <= band
        seam_result = {
            "interface_id": interface.get("id"),
            "normal_axis": normal.tolist(),
            "signed_distance_min_mm": float(signed.min()),
            "signed_distance_max_mm": float(signed.max()),
            "seam_band_mm": band,
            "vertices_in_band": int(within.sum()),
            "vertex_fraction_in_band": float(within.mean()),
        }
        seam_results.append(seam_result)
        if band > 0 and not within.any():
            warnings.append(f"No mesh vertices lie in the declared seam band of interface {interface.get('id')}")

    report = {
        "valid": not errors,
        "plan": str(args.plan),
        "component_id": args.component_id,
        "mesh": str(args.mesh),
        "load_processing": "trimesh standard processing enabled; source file unchanged",
        "transform_applied": not args.no_placement_transform,
        "source_to_mm_scale": source_scale,
        "source": {
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
            "bounds_before_scale_and_placement": source_bounds.tolist(),
            "extents_before_scale_and_placement": source_extents.tolist(),
        },
        "registered": {
            "bounds_mm": processed_bounds.tolist(),
            "extents_mm": processed_extents.tolist(),
            "connected_components": component_count,
            "watertight": watertight,
            "winding_consistent": winding_consistent,
            "volume_mm3": volume,
            "target_envelope_mm": expected_envelope,
            "lower_envelope_excess_mm": lower_excess.tolist(),
            "upper_envelope_excess_mm": upper_excess.tolist(),
        },
        "keepout_screen": {
            "limitations": "AABB bounds and mesh vertices only; exact triangle/solid collision and swept-volume checks are still required.",
            "results": keepout_results,
        },
        "seam_plane_screen": seam_results,
        "errors": errors,
        "warnings": warnings,
    }

    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)

    print(f"Mesh contract {'PASS' if not errors else 'FAIL'}: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
    for message in errors:
        print(f"ERROR: {message}", file=sys.stderr)
    for message in warnings:
        print(f"WARNING: {message}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
