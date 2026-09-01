#!/usr/bin/env python3
"""Inspect a GLB or derive a scaled, oriented geometry-only STL with evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import trimesh
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing numpy/trimesh; install scripts/requirements.txt in the agent environment"
    ) from exc


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def flatten_scene(loaded: Any) -> tuple[trimesh.Trimesh, dict[str, Any]]:
    if isinstance(loaded, trimesh.Trimesh):
        return loaded.copy(), {
            "scene_nodes": 1,
            "geometry_objects": 1,
            "materials": 1 if getattr(loaded.visual, "material", None) else 0,
            "has_uv": getattr(loaded.visual, "uv", None) is not None,
        }
    if not isinstance(loaded, trimesh.Scene):
        raise TypeError(f"unsupported loaded type: {type(loaded).__name__}")
    meshes: list[trimesh.Trimesh] = []
    materials: set[str] = set()
    has_uv = False
    for node_name in loaded.graph.nodes_geometry:
        transform, geometry_name = loaded.graph[node_name]
        geometry = loaded.geometry[geometry_name]
        if not isinstance(geometry, trimesh.Trimesh):
            continue
        candidate = geometry.copy()
        candidate.apply_transform(transform)
        meshes.append(candidate)
        material = getattr(geometry.visual, "material", None)
        if material is not None:
            materials.add(str(getattr(material, "name", type(material).__name__)))
        has_uv = has_uv or getattr(geometry.visual, "uv", None) is not None
    if not meshes:
        raise RuntimeError("GLB scene contains no triangle meshes")
    return trimesh.util.concatenate(meshes), {
        "scene_nodes": len(list(loaded.graph.nodes)),
        "geometry_objects": len(meshes),
        "materials": len(materials),
        "has_uv": has_uv,
    }


def load_mesh(path: Path) -> tuple[trimesh.Trimesh, dict[str, Any]]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"input does not exist: {path}")
    try:
        loaded = trimesh.load(path, force="scene", process=False)
    except Exception as exc:
        raise RuntimeError(f"failed to load {path}: {exc}") from exc
    mesh, scene_info = flatten_scene(loaded)
    if not len(mesh.vertices) or not len(mesh.faces):
        raise RuntimeError("mesh has no vertices or faces")
    vertices = np.asarray(mesh.vertices, dtype=float)
    if not np.isfinite(vertices).all():
        raise RuntimeError("mesh contains non-finite coordinates")
    return mesh, scene_info


def component_count(mesh: trimesh.Trimesh) -> int | None:
    return int(mesh.body_count)


def mesh_facts(mesh: trimesh.Trimesh) -> dict[str, Any]:
    bounds = np.asarray(mesh.bounds, dtype=float)
    extents = np.asarray(mesh.extents, dtype=float)
    watertight = bool(mesh.is_watertight)
    volume = float(mesh.volume) if watertight else None
    return {
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "connected_components": component_count(mesh),
        "bounds": bounds.tolist(),
        "extents": extents.tolist(),
        "watertight": watertight,
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_native_cubed": volume,
    }


def intake_report(
    path: Path, mesh: trimesh.Trimesh, scene: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "captured_at": utc_now(),
        "input": {
            "path": str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "format": path.suffix.lower().lstrip("."),
        },
        "glb_semantics": {
            "declared_linear_unit": "meter",
            "coordinate_system": "right-handed; +Y up; +Z forward",
            "generated_physical_scale_authoritative": False,
            "note": "Step1X does not know the target product dimension; register scale explicitly.",
        },
        "scene": scene,
        "mesh": mesh_facts(mesh),
        "warnings": [
            "Hidden geometry is synthesized from a single image.",
            "Topology, self-intersection, wall thickness and slicer behavior need separate checks.",
        ],
    }


def command_inspect(args: argparse.Namespace) -> int:
    path = args.input.expanduser().resolve()
    mesh, scene = load_mesh(path)
    report = intake_report(path, mesh, scene)
    if args.report:
        atomic_json(args.report.expanduser().resolve(), report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def command_convert(args: argparse.Namespace) -> int:
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != ".stl":
        raise RuntimeError(
            "the explicit print derivative currently supports binary STL only"
        )
    if output.exists():
        raise RuntimeError(f"refusing to overwrite output: {output}")
    mesh, scene = load_mesh(source)
    before = mesh_facts(mesh)
    transform = np.eye(4, dtype=float)

    if args.target_longest_mm is not None:
        longest = float(np.max(mesh.extents))
        if not math.isfinite(longest) or longest <= 0:
            raise RuntimeError("mesh has no positive extent for target scaling")
        scale_factor = args.target_longest_mm / longest
        scale_basis = {
            "method": "target_longest_mm",
            "target_longest_mm": args.target_longest_mm,
            "source_longest_native": longest,
        }
    else:
        scale_factor = args.scale_factor_to_mm
        scale_basis = {
            "method": "explicit_scale_factor_to_mm",
            "scale_factor_to_mm": scale_factor,
        }
    scale_matrix = np.eye(4, dtype=float)
    scale_matrix[:3, :3] *= scale_factor
    mesh.apply_transform(scale_matrix)
    transform = scale_matrix @ transform

    if args.y_up_to_z_up:
        rotation = trimesh.transformations.rotation_matrix(
            math.pi / 2.0, [1.0, 0.0, 0.0]
        )
        mesh.apply_transform(rotation)
        transform = rotation @ transform
        orientation = "glTF +Y up rotated to slicer/CAD +Z up"
    else:
        orientation = "source orientation explicitly retained"

    if args.place_on_bed:
        translation = np.eye(4, dtype=float)
        translation[2, 3] = -float(mesh.bounds[0, 2])
        mesh.apply_transform(translation)
        transform = translation @ transform

    after = mesh_facts(mesh)
    if not after["watertight"] and not args.allow_nonwatertight:
        raise RuntimeError(
            "converted mesh is not watertight; repair/validate it first or use "
            "--allow-nonwatertight only for a diagnostic artifact"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(output, file_type="stl")
    if not output.is_file():
        raise RuntimeError("STL export did not create an output file")

    report = {
        "schema_version": "1.0",
        "captured_at": utc_now(),
        "operation": "GLB scene flatten plus geometry-only STL derivation",
        "input": {
            "path": str(source),
            "sha256": sha256_file(source),
            "bytes": source.stat().st_size,
            "scene": scene,
            "mesh": before,
        },
        "transform": {
            "scale": scale_basis,
            "uniform_scale_factor_to_mm": scale_factor,
            "orientation": orientation,
            "place_min_z_at_zero": bool(args.place_on_bed),
            "matrix_row_major": transform.tolist(),
        },
        "output": {
            "path": str(output),
            "sha256": sha256_file(output),
            "bytes": output.stat().st_size,
            "format": "binary STL",
            "unit_convention": "millimeter (STL itself has no unit metadata)",
            "mesh": after,
        },
        "losses_and_limits": [
            "GLB nodes are flattened into one triangle mesh.",
            "UVs, textures, materials, colors and scene metadata are not represented in STL.",
            "No repair, wall-thickness, self-intersection, functional or slicer validation was performed.",
            "The source GLB remains the immutable appearance/generation evidence.",
        ],
        "diagnostic_nonwatertight_override": bool(args.allow_nonwatertight),
    }
    if args.report:
        atomic_json(args.report.expanduser().resolve(), report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def positive(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("value must be finite and greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    inspect_parser = commands.add_parser(
        "inspect", help="Inspect without modifying GLB"
    )
    inspect_parser.add_argument("input", type=Path)
    inspect_parser.add_argument("--report", type=Path)
    inspect_parser.set_defaults(handler=command_inspect)

    convert_parser = commands.add_parser(
        "convert", help="Create an explicitly scaled geometry-only STL derivative"
    )
    convert_parser.add_argument("input", type=Path)
    convert_parser.add_argument("--output", type=Path, required=True)
    scale = convert_parser.add_mutually_exclusive_group(required=True)
    scale.add_argument("--target-longest-mm", type=positive)
    scale.add_argument("--scale-factor-to-mm", type=positive)
    orientation = convert_parser.add_mutually_exclusive_group(required=True)
    orientation.add_argument("--y-up-to-z-up", action="store_true")
    orientation.add_argument("--keep-orientation", action="store_true")
    convert_parser.add_argument("--place-on-bed", action="store_true")
    convert_parser.add_argument("--allow-nonwatertight", action="store_true")
    convert_parser.add_argument("--report", type=Path)
    convert_parser.set_defaults(handler=command_convert)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return int(args.handler(args))
    except (RuntimeError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
