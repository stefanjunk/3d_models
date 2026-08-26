#!/usr/bin/env python3
"""Inspect a mesh before using it as a casting master or mold operand.

The report is intentionally conservative. A passing report does not prove that a
mold can be demolded; it only screens common mesh problems.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene", process=False)
    if isinstance(loaded, trimesh.Scene):
        if not loaded.geometry:
            raise ValueError("The file contains no mesh geometry.")
        try:
            mesh = loaded.to_mesh()
        except Exception:
            dumped = loaded.dump(concatenate=False)
            meshes = [g for g in dumped if isinstance(g, trimesh.Trimesh)]
            if not meshes:
                raise ValueError("The scene contains no triangle meshes.")
            mesh = trimesh.util.concatenate(meshes)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        raise TypeError(f"Unsupported loaded object: {type(loaded).__name__}")

    if mesh.vertices.size == 0 or mesh.faces.size == 0:
        raise ValueError("The mesh has no vertices or faces.")
    # STL commonly repeats identical vertices per triangle. Weld exact/near-exact
    # coordinates for meaningful topology checks without filling holes or remeshing.
    mesh.merge_vertices(digits_vertex=12)
    mesh.remove_unreferenced_vertices()
    return mesh


def safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def edge_topology(mesh: trimesh.Trimesh) -> dict[str, int]:
    inverse = np.asarray(mesh.edges_unique_inverse, dtype=np.int64)
    counts = np.bincount(inverse, minlength=len(mesh.edges_unique))
    return {
        "unique_edges": int(len(counts)),
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "manifold_edges": int(np.count_nonzero(counts == 2)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
        "max_face_uses_per_edge": int(counts.max(initial=0)),
    }


def face_quality(mesh: trimesh.Trimesh) -> dict[str, int]:
    try:
        nondegenerate = np.asarray(mesh.nondegenerate_faces(), dtype=bool)
        degenerate = int(len(mesh.faces) - np.count_nonzero(nondegenerate))
    except Exception:
        degenerate = -1

    try:
        unique = np.asarray(mesh.unique_faces(), dtype=bool)
        duplicate = int(len(mesh.faces) - np.count_nonzero(unique))
    except Exception:
        duplicate = -1

    return {"degenerate_faces": degenerate, "duplicate_faces": duplicate}


def edge_length_stats(mesh: trimesh.Trimesh) -> dict[str, float | None]:
    lengths = np.asarray(mesh.edges_unique_length, dtype=float)
    lengths = lengths[np.isfinite(lengths)]
    if lengths.size == 0:
        return {key: None for key in ("min", "p01", "p05", "median", "p95", "max")}
    q = np.percentile(lengths, [0, 1, 5, 50, 95, 100])
    return {
        "min": float(q[0]),
        "p01": float(q[1]),
        "p05": float(q[2]),
        "median": float(q[3]),
        "p95": float(q[4]),
        "max": float(q[5]),
    }


def draft_screen(mesh: trimesh.Trimesh, vector: np.ndarray, threshold_deg: float) -> dict[str, Any]:
    norm = float(np.linalg.norm(vector))
    if norm <= 0:
        raise ValueError("Pull vector must be non-zero.")
    direction = vector / norm
    normals = np.asarray(mesh.face_normals, dtype=float)
    dot = normals @ direction
    threshold = math.sin(math.radians(threshold_deg))
    areas = np.asarray(mesh.area_faces, dtype=float)
    total_area = float(areas.sum()) or 1.0

    categories = {
        "faces_with_pull": dot > threshold,
        "near_parallel_to_pull": np.abs(dot) <= threshold,
        "faces_against_pull": dot < -threshold,
    }
    result: dict[str, Any] = {
        "pull_vector": [float(x) for x in direction],
        "threshold_degrees_from_parallel_band": threshold_deg,
        "warning": "Face-normal classification is only a draft screen; it does not prove global removability or detect all undercuts.",
    }
    for name, mask in categories.items():
        result[name] = {
            "faces": int(np.count_nonzero(mask)),
            "area_fraction": float(areas[mask].sum() / total_area),
        }
    return result


def build_report(mesh: trimesh.Trimesh, path: Path, pull: np.ndarray, draft_band_deg: float) -> dict[str, Any]:
    bounds = np.asarray(mesh.bounds, dtype=float)
    extents = np.asarray(mesh.extents, dtype=float)
    components = mesh.split(only_watertight=False)
    component_faces = sorted((int(len(c.faces)) for c in components), reverse=True)

    report: dict[str, Any] = {
        "file": {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "mesh": {
            "units_metadata": getattr(mesh, "units", None),
            "vertices": int(len(mesh.vertices)),
            "faces": int(len(mesh.faces)),
            "connected_components": int(len(components)),
            "component_face_counts": component_faces[:50],
            "watertight": bool(mesh.is_watertight),
            "winding_consistent": bool(mesh.is_winding_consistent),
            "is_volume": bool(mesh.is_volume),
            "euler_number": int(mesh.euler_number),
            "bounds_min": [float(x) for x in bounds[0]],
            "bounds_max": [float(x) for x in bounds[1]],
            "extents": [float(x) for x in extents],
            "surface_area": safe_float(mesh.area),
            "signed_volume": safe_float(mesh.volume),
            "center_mass": [safe_float(x) for x in np.asarray(mesh.center_mass)] if mesh.is_volume else None,
        },
        "topology": edge_topology(mesh),
        "face_quality": face_quality(mesh),
        "edge_length": edge_length_stats(mesh),
        "draft_screen": draft_screen(mesh, pull, draft_band_deg),
        "limitations": [
            "Self-intersections are not exhaustively tested by this lightweight report.",
            "Thin-wall, trapped-volume, and demolding analysis require process-specific geometry checks.",
            "STL usually does not encode trustworthy units; verify dimensions against a known measurement."
        ],
    }

    warnings: list[str] = []
    if not mesh.is_watertight:
        warnings.append("Mesh is not watertight; a solid boolean or cavity subtraction may fail.")
    if not mesh.is_winding_consistent:
        warnings.append("Face winding is inconsistent; repair normals before boolean operations.")
    if len(components) > 1:
        warnings.append(f"Mesh has {len(components)} connected components; confirm that all are intentional.")
    if report["topology"]["nonmanifold_edges"] > 0:
        warnings.append("Non-manifold edges are present.")
    if report["face_quality"]["degenerate_faces"] not in (0, -1):
        warnings.append("Degenerate faces are present.")
    if report["face_quality"]["duplicate_faces"] not in (0, -1):
        warnings.append("Duplicate faces are present.")
    if np.any(extents <= 0):
        warnings.append("One or more bounding-box dimensions are zero or negative.")
    if min(extents) > 0 and max(extents) / min(extents) > 1000:
        warnings.append("Extreme aspect ratio detected; verify units and accidental distant geometry.")
    report["warnings"] = warnings
    report["status"] = "review_required" if warnings else "screen_passed"
    return report


def clean_mesh(mesh: trimesh.Trimesh, merge_tolerance: float | None) -> trimesh.Trimesh:
    cleaned = mesh.copy()
    try:
        cleaned.update_faces(cleaned.nondegenerate_faces())
    except Exception:
        pass
    try:
        cleaned.update_faces(cleaned.unique_faces())
    except Exception:
        pass
    cleaned.remove_unreferenced_vertices()

    if merge_tolerance is not None:
        if merge_tolerance <= 0:
            raise ValueError("--merge-tolerance must be greater than zero.")
        digits = max(0, int(math.ceil(-math.log10(merge_tolerance))))
        cleaned.merge_vertices(digits_vertex=digits)

    try:
        trimesh.repair.fix_normals(cleaned, multibody=True)
    except Exception:
        pass
    cleaned.remove_unreferenced_vertices()
    return cleaned


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input STL/OBJ/PLY/3MF or other trimesh-supported mesh")
    parser.add_argument("--json", dest="json_path", type=Path, help="Write the full report as JSON")
    parser.add_argument("--cleaned", type=Path, help="Write a conservative cleaned copy; original remains unchanged")
    parser.add_argument("--merge-tolerance", type=float, default=None, help="Optional approximate vertex merge tolerance in model units")
    parser.add_argument("--pull-vector", nargs=3, type=float, default=(0.0, 0.0, 1.0), metavar=("X", "Y", "Z"))
    parser.add_argument("--draft-band-deg", type=float, default=2.0, help="Near-parallel face-normal classification band")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        path = args.input.expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        mesh = load_mesh(path)
        report = build_report(mesh, path, np.asarray(args.pull_vector, dtype=float), args.draft_band_deg)

        if args.cleaned:
            cleaned = clean_mesh(mesh, args.merge_tolerance)
            out = args.cleaned.expanduser().resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            cleaned.export(out)
            report["cleaned_output"] = str(out)

        if args.json_path:
            json_path = args.json_path.expanduser().resolve()
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        m = report["mesh"]
        t = report["topology"]
        print(f"Status: {report['status']}")
        print(f"File: {path}")
        print(f"Vertices/faces: {m['vertices']:,} / {m['faces']:,}")
        print(f"Extents: {m['extents'][0]:.4g} × {m['extents'][1]:.4g} × {m['extents'][2]:.4g} model units")
        print(f"Components: {m['connected_components']} | watertight: {m['watertight']} | winding consistent: {m['winding_consistent']}")
        print(f"Boundary edges: {t['boundary_edges']:,} | non-manifold edges: {t['nonmanifold_edges']:,}")
        if report["warnings"]:
            print("Warnings:")
            for warning in report["warnings"]:
                print(f"  - {warning}")
        print("Draft screen is indicative only; run collision-based pull tests for the actual mold parts.")
        return 0 if report["status"] == "screen_passed" else 2
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
