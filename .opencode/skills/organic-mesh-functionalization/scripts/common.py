#!/usr/bin/env python3
"""Shared helpers for organic-mesh-functionalization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

SKILL_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = SKILL_ROOT / "data"
TEMPLATE_ROOT = SKILL_ROOT / "templates"


def load_structured(path: str | Path) -> Any:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        return json.loads(text)
    if p.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover
            raise SystemExit("PyYAML is required: python -m pip install PyYAML") from exc
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported structured file: {p}")


def dump_json(data: Any, path: str | Path | None = None) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if path is not None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    return text


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mesh(path: str | Path, *, process: bool = True, validate: bool = False):
    try:
        import trimesh
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("trimesh is required: python -m pip install trimesh") from exc
    loaded = trimesh.load(Path(path), force=None, process=process)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if hasattr(g, "faces") and len(g.faces)]
        if not meshes:
            raise ValueError(f"No triangle mesh in scene: {path}")
        loaded = trimesh.util.concatenate(meshes)
    if not hasattr(loaded, "faces"):
        raise ValueError(f"Input is not a triangle mesh: {path}")
    if validate:
        loaded.process(validate=True)
    return loaded


def boundary_edge_count(mesh) -> int:
    if len(mesh.faces) == 0:
        return 0
    counts = np.bincount(mesh.edges_unique_inverse)
    return int(np.count_nonzero(counts == 1))


def body_count(mesh) -> int:
    try:
        return int(len(mesh.split(only_watertight=False)))
    except Exception:
        return int(getattr(mesh, "body_count", 0))


def roi_contains(points: np.ndarray, roi: dict[str, Any], margin: float = 0.0) -> np.ndarray:
    """Return mask of points inside an ROI expanded by margin."""
    p = np.asarray(points, dtype=float)
    kind = str(roi.get("type", "all")).lower()
    if kind == "all":
        return np.ones(len(p), dtype=bool)
    center = np.asarray(roi.get("center_mm", [0.0, 0.0, 0.0]), dtype=float)
    q = p - center
    if kind == "box":
        size = np.asarray(roi["size_mm"], dtype=float) + 2.0 * margin
        return np.all(np.abs(q) <= size / 2.0, axis=1)
    if kind == "sphere":
        radius = float(roi["radius_mm"]) + margin
        return np.einsum("ij,ij->i", q, q) <= radius * radius
    if kind == "cylinder":
        axis_name = str(roi.get("axis", "z")).lower()
        ai = {"x": 0, "y": 1, "z": 2}[axis_name]
        radial_axes = [i for i in range(3) if i != ai]
        radius = float(roi["radius_mm"]) + margin
        height = float(roi["height_mm"]) + 2.0 * margin
        radial2 = np.sum(q[:, radial_axes] ** 2, axis=1)
        return (radial2 <= radius * radius) & (np.abs(q[:, ai]) <= height / 2.0)
    raise ValueError(f"Unsupported ROI type: {kind}")


def mesh_metrics(mesh) -> dict[str, Any]:
    nondegenerate = mesh.nondegenerate_faces() if len(mesh.faces) else np.array([], dtype=bool)
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "body_count": body_count(mesh),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume_mm3_signed": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "bounds_mm": np.asarray(mesh.bounds, dtype=float).tolist(),
        "extents_mm": np.asarray(mesh.extents, dtype=float).tolist(),
        "euler_number": int(mesh.euler_number),
        "boundary_edges": boundary_edge_count(mesh),
        "degenerate_faces": int((~nondegenerate).sum()) if len(nondegenerate) else 0,
    }
