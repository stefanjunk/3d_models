from __future__ import annotations

import itertools
import math
from pathlib import Path
from typing import Any

from .common import check, finite_number, report


def _load_mesh(path: Path):
    import numpy as np
    import trimesh

    loaded = trimesh.load(path, force="scene", process=False)
    if isinstance(loaded, trimesh.Trimesh):
        mesh = loaded.copy()
    elif isinstance(loaded, trimesh.Scene):
        pieces = []
        for node_name in loaded.graph.nodes_geometry:
            transform, geometry_name = loaded.graph[node_name]
            geometry = loaded.geometry[geometry_name]
            if not isinstance(geometry, trimesh.Trimesh):
                continue
            piece = geometry.copy()
            piece.apply_transform(transform)
            pieces.append(piece)
        if not pieces:
            raise ValueError("scene contains no triangle mesh")
        mesh = trimesh.util.concatenate(pieces)
    else:
        raise ValueError(f"unsupported geometry type {type(loaded).__name__}")
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("mesh contains no vertices or faces")
    if not np.isfinite(mesh.vertices).all():
        raise ValueError("mesh contains non-finite vertices")
    # Use exact coordinate equality for analysis. Trimesh's general merge
    # helper may use digit rounding, which can hide sub-tolerance defects.
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    unique_vertices, inverse = np.unique(vertices, axis=0, return_inverse=True)
    normalized = trimesh.Trimesh(vertices=unique_vertices, faces=inverse[faces], process=False)
    normalized.remove_unreferenced_vertices()
    return mesh, normalized


def _topology(mesh) -> dict[str, Any]:
    import numpy as np

    inverse = mesh.edges_unique_inverse
    counts = np.bincount(inverse, minlength=len(mesh.edges_unique))
    areas = np.asarray(mesh.area_faces, dtype=float)
    threshold = max(float(mesh.area), 1.0) * np.finfo(float).eps * 100.0
    canonical = np.sort(np.asarray(mesh.faces, dtype=np.int64), axis=1)
    duplicate = int(len(canonical) - len(np.unique(canonical, axis=0)))
    try:
        components = len(mesh.split(only_watertight=False, repair=False))
    except TypeError:
        components = len(mesh.split(only_watertight=False))
    return {
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "manifold_edges": int(np.count_nonzero(counts == 2)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
        "degenerate_faces": int(np.count_nonzero(areas <= threshold)),
        "duplicate_faces": duplicate,
        "components": int(components),
    }


def _bed_fit(extents: list[float], bed: list[float], allow_permutation: bool) -> tuple[bool, list[int]]:
    permutations = list(itertools.permutations(range(3))) if allow_permutation else [(0, 1, 2)]
    for order in permutations:
        if all(extents[index] <= bed[axis] + 1e-9 for axis, index in enumerate(order)):
            return True, list(order)
    return False, [0, 1, 2]


def _sample_wall_thickness(mesh, count: int, seed: int, method: str) -> dict[str, Any]:
    import numpy as np
    import trimesh

    if not mesh.is_watertight:
        raise ValueError("wall thickness requires a watertight mesh")
    count = max(8, min(int(count), 100_000))
    points, face_ids = trimesh.sample.sample_surface(mesh, count, seed=seed)
    normals = np.asarray(mesh.face_normals)[face_ids]
    values = trimesh.proximity.thickness(mesh, points, normals=normals, method=method)
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values) & (values >= 0)
    values = values[valid]
    valid_points = np.asarray(points)[valid]
    if len(values) == 0:
        raise ValueError("thickness backend returned no finite values")
    minimum_index = int(np.argmin(values))
    return {
        "method": method,
        "seed": seed,
        "samples_requested": count,
        "samples_valid": int(len(values)),
        "min_mm": float(np.min(values)),
        "p01_mm": float(np.percentile(values, 1)),
        "p05_mm": float(np.percentile(values, 5)),
        "median_mm": float(np.percentile(values, 50)),
        "minimum_sample_point_mm": valid_points[minimum_index].tolist(),
        "limitation": "Sampled local thickness can miss small defects; increase samples and inspect reported regions for critical parts.",
    }


def audit(path: Path, policy: dict[str, Any] | None = None, profile: str = "release") -> dict[str, Any]:
    policy = policy or {}
    checks: list[dict[str, Any]] = []
    if not path.is_file():
        return report(
            "audit-mesh",
            [check("mesh-file", "FAIL", f"Mesh not found: {path}")],
            inputs=[path],
            profile=profile,
        )
    try:
        raw, mesh = _load_mesh(path)
    except ImportError as exc:
        return report(
            "audit-mesh",
            [check("mesh-capability", "NOT_RUN", f"Mesh capability unavailable: {exc}")],
            inputs=[path],
            profile=profile,
            capabilities=["mesh"],
        )
    except Exception as exc:
        return report(
            "audit-mesh",
            [check("mesh-load", "FAIL", f"Mesh load failed: {type(exc).__name__}: {exc}")],
            inputs=[path],
            profile=profile,
        )

    topo = _topology(mesh)
    extents = [float(value) for value in mesh.extents]
    bounds = [[float(value) for value in row] for row in mesh.bounds]
    metrics: dict[str, Any] = {
        "raw_file_representation": {"vertices": int(len(raw.vertices)), "faces": int(len(raw.faces))},
        "exact_coordinate_welded": {
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "bounds_mm": bounds,
            "extents_mm": extents,
            "surface_area_mm2": float(mesh.area),
            "signed_volume_mm3": float(mesh.volume),
            "watertight": bool(mesh.is_watertight),
            "winding_consistent": bool(mesh.is_winding_consistent),
            "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
            "euler_number": int(mesh.euler_number),
            **topo,
        },
        "file_mib": path.stat().st_size / (1024 * 1024),
    }
    checks.append(check("mesh-load", "PASS", "Mesh loaded without altering the source file"))

    def gate_bool(check_id: str, actual: bool, required_key: str, message: str) -> None:
        required = bool(policy.get(required_key, False))
        status = "PASS" if actual else ("FAIL" if required else "REVIEW_REQUIRED")
        checks.append(check(check_id, status, message, required=required, metrics={"actual": actual}))

    gate_bool("watertight", bool(mesh.is_watertight), "require_watertight", "Watertight topology")
    gate_bool("winding", bool(mesh.is_winding_consistent), "require_winding_consistent", "Consistent face winding")
    gate_bool("positive-volume", bool(mesh.is_volume and mesh.volume > 0), "require_positive_volume", "Positive closed volume")

    expected_components = policy.get("expected_components")
    if expected_components is not None:
        passed = isinstance(expected_components, int) and topo["components"] == expected_components
        checks.append(
            check(
                "component-count",
                "PASS" if passed else "FAIL",
                f"Expected {expected_components} component(s), found {topo['components']}",
                metrics={"expected": expected_components, "actual": topo["components"]},
            )
        )

    for field, policy_key in (
        ("boundary_edges", "max_boundary_edges"),
        ("nonmanifold_edges", "max_nonmanifold_edges"),
        ("degenerate_faces", "max_degenerate_faces"),
        ("duplicate_faces", "max_duplicate_faces"),
    ):
        if policy_key in policy:
            limit = policy[policy_key]
            passed = finite_number(limit) and topo[field] <= float(limit)
            checks.append(
                check(
                    field.replace("_", "-"),
                    "PASS" if passed else "FAIL",
                    f"{field}={topo[field]}, limit={limit}",
                    metrics={"actual": topo[field], "limit": limit},
                )
            )

    if "max_faces" in policy:
        limit = int(policy["max_faces"])
        checks.append(
            check(
                "triangle-budget",
                "PASS" if len(mesh.faces) <= limit else "FAIL",
                f"Triangles {len(mesh.faces)} / {limit}",
                metrics={"actual": int(len(mesh.faces)), "limit": limit},
            )
        )
    if "max_file_mib" in policy:
        limit = float(policy["max_file_mib"])
        actual = metrics["file_mib"]
        checks.append(
            check(
                "file-budget",
                "PASS" if actual <= limit else "FAIL",
                f"Mesh file {actual:.3f} MiB / {limit:g} MiB",
                metrics={"actual_mib": actual, "limit_mib": limit},
            )
        )
    if "bed_mm" in policy:
        bed = policy["bed_mm"]
        if not isinstance(bed, list) or len(bed) != 3 or not all(finite_number(v) and v > 0 for v in bed):
            checks.append(check("bed-fit", "FAIL", "bed_mm must contain three positive numbers"))
        else:
            passed, order = _bed_fit(extents, [float(v) for v in bed], bool(policy.get("allow_axis_permutation", False)))
            checks.append(
                check(
                    "bed-fit",
                    "PASS" if passed else "FAIL",
                    "Mesh fits declared build volume" if passed else "Mesh exceeds declared build volume",
                    metrics={"extents_mm": extents, "bed_mm": bed, "axis_order": order},
                )
            )

    if "min_wall_mm" in policy:
        try:
            thickness = _sample_wall_thickness(
                mesh,
                int(policy.get("wall_samples", 5000)),
                int(policy.get("seed", 42)),
                str(policy.get("wall_method", "ray")),
            )
            metrics["wall_thickness"] = thickness
            passed = thickness["min_mm"] + 1e-9 >= float(policy["min_wall_mm"])
            checks.append(
                check(
                    "minimum-wall",
                    "PASS" if passed else "FAIL",
                    f"Sampled minimum wall {thickness['min_mm']:.6g} mm; required {policy['min_wall_mm']} mm",
                    metrics=thickness,
                )
            )
        except Exception as exc:
            checks.append(
                check(
                    "minimum-wall",
                    "NOT_RUN",
                    f"Wall-thickness check unavailable: {type(exc).__name__}: {exc}",
                    required=True,
                )
            )

    if policy.get("require_self_intersection_check"):
        checks.append(
            check(
                "self-intersection",
                "NOT_RUN",
                "No certified self-intersection backend is configured; run a tool-native or dedicated exact check",
                required=True,
            )
        )

    return report(
        "audit-mesh",
        checks,
        inputs=[path],
        profile=profile,
        metrics=metrics,
        limitations=[
            "STL contains no authoritative units; dimensions are interpreted as millimetres by project contract.",
            "Exact-coordinate vertex welding is used only for analysis and does not rewrite the source.",
            "Sampled wall thickness is not a complete global proof.",
        ],
        capabilities=["mesh"],
    )
