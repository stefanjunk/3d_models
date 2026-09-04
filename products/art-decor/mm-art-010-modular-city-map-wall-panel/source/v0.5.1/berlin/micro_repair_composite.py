#!/usr/bin/env python3
"""Repair only numerical collinear triangles in a watertight composite mesh.

The repair preserves faces and connectivity.  For each face below the same
scale-aware area threshold used by the project gate, it tests one IEEE-754
float32 ULP in X or Y at the face vertices.  The deterministic candidate that
removes the most failed faces with the smallest displacement and volume change
is selected.  Z planes are never changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh


MAX_SHIFT_MM = 5e-5
MAX_VOLUME_DELTA_MM3 = 1e-4
MAX_REPAIRS = 8


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def face_areas(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    points = vertices[faces]
    return np.linalg.norm(
        np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0]),
        axis=1,
    ) * 0.5


def area_threshold(mesh: trimesh.Trimesh) -> float:
    return max(float(mesh.area), 1.0) * np.finfo(float).eps * 100.0


def repair_mesh(source: trimesh.Trimesh) -> tuple[trimesh.Trimesh, dict]:
    mesh = trimesh.Trimesh(
        vertices=np.asarray(source.vertices, dtype=np.float64).copy(),
        faces=np.asarray(source.faces, dtype=np.int64).copy(),
        process=False,
    )
    mesh.remove_unreferenced_vertices()
    if not mesh.is_watertight or not mesh.is_volume or mesh.volume <= 0:
        raise ValueError("micro-repair requires a positive watertight input mesh")

    before_vertices = np.asarray(mesh.vertices, dtype=np.float64).copy()
    faces = np.asarray(mesh.faces, dtype=np.int64)
    before_volume = float(mesh.volume)
    before_bounds = np.asarray(mesh.bounds, dtype=np.float64)
    threshold = area_threshold(mesh)
    initial_bad = np.flatnonzero(face_areas(before_vertices, faces) <= threshold)
    repairs: list[dict] = []

    while True:
        vertices = np.asarray(mesh.vertices, dtype=np.float64)
        areas = face_areas(vertices, faces)
        bad = np.flatnonzero(areas <= threshold)
        if len(bad) == 0:
            break
        if len(repairs) >= MAX_REPAIRS:
            raise ValueError(f"micro-repair exceeded {MAX_REPAIRS} vertex nudges")

        failed_before = len(bad)
        target_face = int(bad[0])
        candidates: list[tuple[tuple, np.ndarray, dict]] = []
        for vertex_index in sorted(int(value) for value in faces[target_face]):
            for axis in (0, 1):
                original = np.float32(vertices[vertex_index, axis])
                for direction_rank, direction in enumerate((-np.inf, np.inf)):
                    replacement = np.nextafter(
                        original, np.float32(direction), dtype=np.float32
                    )
                    displacement = abs(float(replacement) - float(original))
                    if displacement == 0.0 or displacement > MAX_SHIFT_MM:
                        continue
                    candidate_vertices = vertices.copy()
                    candidate_vertices[vertex_index, axis] = float(replacement)
                    candidate_areas = face_areas(candidate_vertices, faces)
                    failed_after = int(np.count_nonzero(candidate_areas <= threshold))
                    if failed_after >= failed_before:
                        continue
                    candidate_mesh = trimesh.Trimesh(
                        vertices=candidate_vertices, faces=faces, process=False
                    )
                    volume_delta = float(candidate_mesh.volume) - before_volume
                    key = (
                        failed_after,
                        displacement,
                        abs(volume_delta),
                        vertex_index,
                        axis,
                        direction_rank,
                    )
                    record = {
                        "target_face": target_face,
                        "vertex_index": vertex_index,
                        "axis": "xy"[axis],
                        "from_mm": float(original),
                        "to_mm": float(replacement),
                        "signed_shift_mm": float(replacement) - float(original),
                        "face_area_before_mm2": float(areas[target_face]),
                        "face_area_after_mm2": float(candidate_areas[target_face]),
                        "failed_faces_before": failed_before,
                        "failed_faces_after": failed_after,
                        "candidate_volume_delta_from_original_mm3": volume_delta,
                    }
                    candidates.append((key, candidate_vertices, record))
        if not candidates:
            raise ValueError(
                f"no topology-preserving one-ULP repair for face {target_face}"
            )
        _, selected_vertices, selected_record = min(candidates, key=lambda item: item[0])
        mesh = trimesh.Trimesh(
            vertices=selected_vertices, faces=faces.copy(), process=False
        )
        repairs.append(selected_record)

    after_volume = float(mesh.volume)
    after_bounds = np.asarray(mesh.bounds, dtype=np.float64)
    shifts = np.linalg.norm(
        np.asarray(mesh.vertices, dtype=np.float64) - before_vertices, axis=1
    )
    final_bad = np.flatnonzero(
        face_areas(np.asarray(mesh.vertices, dtype=np.float64), faces) <= threshold
    )
    checks = {
        "input_watertight": bool(source.is_watertight),
        "output_watertight": bool(mesh.is_watertight),
        "output_positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "face_count_unchanged": len(mesh.faces) == len(source.faces),
        "vertex_count_unchanged": len(mesh.vertices) == len(source.vertices),
        "no_failed_faces_after": len(final_bad) == 0,
        "maximum_shift_within_limit": float(shifts.max(initial=0.0)) <= MAX_SHIFT_MM,
        "volume_delta_within_limit": abs(after_volume - before_volume)
        <= MAX_VOLUME_DELTA_MM3,
        "bounds_unchanged_within_limit": bool(
            np.allclose(after_bounds, before_bounds, atol=MAX_SHIFT_MM, rtol=0.0)
        ),
    }
    if not all(checks.values()):
        raise ValueError(f"micro-repair failed acceptance checks: {checks}")
    trace = {
        "algorithm": "topology-preserving float32 one-ULP XY vertex nudge",
        "area_threshold_mm2": threshold,
        "initial_failed_faces": [int(value) for value in initial_bad],
        "final_failed_faces": [int(value) for value in final_bad],
        "repair_count": len(repairs),
        "repairs": repairs,
        "maximum_vertex_shift_mm": float(shifts.max(initial=0.0)),
        "volume_before_mm3": before_volume,
        "volume_after_mm3": after_volume,
        "signed_volume_delta_mm3": after_volume - before_volume,
        "bounds_before_mm": before_bounds.tolist(),
        "bounds_after_mm": after_bounds.tolist(),
        "checks": checks,
        "status": "PASS",
    }
    return mesh, trace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.report.exists():
        raise SystemExit("refusing destructive overwrite of output or report")
    source = trimesh.load_mesh(args.input, process=True)
    repaired, trace = repair_mesh(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    repaired.export(args.output)
    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "input": {"path": str(args.input.resolve()), "sha256": sha256(args.input)},
        "output": {"path": str(args.output.resolve()), "sha256": sha256(args.output)},
        "trace": trace,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "output": str(args.output), "trace": trace}))


if __name__ == "__main__":
    main()
