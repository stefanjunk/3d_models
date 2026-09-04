#!/usr/bin/env python3
"""Apply a reusable texture recipe to planar-faced parts and export printable STL.

Reads a part spec JSON describing solids as vertical prisms/boxes with
explicit per-face texture settings, builds each watertight solid with
texture_lib, optionally unions them with Manifold3D, validates topology,
enforces the recipe triangle budget, and writes STL + report.

Usage:
    python3 apply_texture_patch.py spec.json --output-dir out/

Keep-outs are enforced by the spec: only faces marked textured are displaced.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import texture_lib as tl  # noqa: E402


def load_recipe(spec: dict, spec_path: Path) -> dict:
    recipe_rel = spec.get("recipe")
    if not recipe_rel:
        raise ValueError("spec must name a recipe JSON")
    recipe_path = (spec_path.parent / recipe_rel).resolve()
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    recipe["_path"] = str(recipe_path)
    return recipe


def sampler_from_recipe(recipe: dict) -> tl.TileSampler:
    base = Path(recipe["_path"]).parent
    return tl.TileSampler((base / recipe["master"]["tile"]).resolve())


def rect_polygon(x0: float, y0: float, x1: float, y1: float) -> np.ndarray:
    """CCW rectangle -> outward normals via the wall builder convention."""
    return np.array(
        [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float64
    )


def wall_defaults(spec: dict, recipe: dict, height_span: float) -> dict:
    relief = recipe["relief"]
    return {
        "textured": bool(spec.get("textured", False)),
        "engrave": spec.get("mode", relief["mode"]) == "engrave",
        "depth_mm": float(spec.get("depth_mm", relief["depth_mm"])),
        "pitch_mm": float(spec.get("pitch_mm", relief["mesh_pitch_mm"])),
        "edge_taper_mm": float(spec.get("edge_taper_mm", relief["edge_taper_mm"])),
        "u_period_mm": float(spec.get("u_period_mm", height_span)),
        "v_period_mm": float(spec.get("v_period_mm", height_span)),
        "v_offset_mm": float(spec.get("v_offset_mm", 0.0)),
    }


def cap_defaults(spec: dict, recipe: dict) -> dict:
    relief = recipe["relief"]
    coupon = recipe.get("coupon", {})
    return {
        "textured": bool(spec.get("textured", False)),
        "engrave": spec.get("mode", relief["mode"]) == "engrave",
        "depth_mm": float(spec.get("depth_mm", relief["depth_mm"])),
        "pitch_mm": float(spec.get("pitch_mm", relief["mesh_pitch_mm"])),
        "edge_taper_mm": float(spec.get("edge_taper_mm", relief["edge_taper_mm"])),
        "tile_width_mm": float(spec.get("tile_width_mm", coupon.get("tile_width_mm", 120.0))),
        "tile_height_mm": float(spec.get("tile_height_mm", coupon.get("tile_height_mm", 45.0))),
        "origin": tuple(map(float, spec.get("origin", [0.0, 0.0]))),
    }


def build_prism(
    sampler: tl.TileSampler,
    recipe: dict,
    solid: dict,
) -> tuple[np.ndarray, np.ndarray, dict]:
    polygon = np.asarray(solid["polygon"], dtype=np.float64)
    holes = [np.asarray(h, dtype=np.float64) for h in solid.get("holes", [])]
    z0, z1 = map(float, solid["z_range"])
    height_span = z1 - z0
    if height_span <= 0:
        raise ValueError(f"{solid.get('name', 'solid')}: z_range must be positive")
    walls_spec = solid.get("walls", {})
    top_spec = solid.get("top", {})
    bottom_spec = solid.get("bottom", {})
    wall_cfg = wall_defaults(walls_spec, recipe, height_span)
    top_cfg = cap_defaults(top_spec, recipe)
    bottom_cfg = cap_defaults(bottom_spec, recipe)
    if wall_cfg["textured"] and "v_period_mm" not in walls_spec:
        raise ValueError(f"{solid.get('name', 'solid')}: walls need explicit v_period_mm")

    mesh = tl.MeshBuilder()
    per_segment_enabled = None
    if "segments_textured" in solid:
        per_segment_enabled = [bool(value) for value in solid["segments_textured"]]

    wall_depth = wall_cfg["depth_mm"] if wall_cfg["textured"] else 0.0
    arc_offset = tl.textured_wall_chain(
        mesh,
        sampler,
        polygon,
        z0,
        z1,
        wall_depth,
        wall_cfg["pitch_mm"],
        wall_cfg["edge_taper_mm"],
        wall_cfg["u_period_mm"],
        wall_cfg["v_period_mm"],
        closed=True,
        engrave=wall_cfg["engrave"],
        v_offset_mm=wall_cfg["v_offset_mm"],
        segment_enabled=per_segment_enabled,
    )
    for hole in holes:
        # Hole walls are traversed clockwise so the builder normals point into
        # the cavity; the arc offset continues for uninterrupted grain.
        arc_offset = tl.textured_wall_chain(
            mesh,
            sampler,
            np.asarray(hole, dtype=np.float64)[::-1],
            z0,
            z1,
            wall_depth,
            wall_cfg["pitch_mm"],
            wall_cfg["edge_taper_mm"],
            wall_cfg["u_period_mm"],
            wall_cfg["v_period_mm"],
            closed=True,
            engrave=wall_cfg["engrave"],
            v_offset_mm=wall_cfg["v_offset_mm"] + arc_offset,
        )

    holes_for_tri = list(holes)
    rim_boundary = tl.sampled_chain_boundary(polygon, wall_cfg["pitch_mm"], closed=True)
    for hole in holes_for_tri:
        rim_boundary = np.vstack(
            (rim_boundary, tl.sampled_chain_boundary(hole, wall_cfg["pitch_mm"], closed=True))
        )

    if top_cfg["textured"]:
        tl.textured_planar_polygon(
            mesh, sampler, polygon, holes_for_tri, rim_boundary, z1,
            top_cfg["depth_mm"], top_cfg["pitch_mm"], top_cfg["edge_taper_mm"],
            tile_width_mm=top_cfg["tile_width_mm"],
            tile_height_mm=top_cfg["tile_height_mm"],
            origin=top_cfg["origin"],
            engrave=top_cfg["engrave"],
            facing_up=True,
        )
    else:
        mesh_cap_pitch = max(1.0, wall_cfg["pitch_mm"])
        points, faces = tl.triangulate_cap(polygon, holes_for_tri, rim_boundary, grid_pitch=mesh_cap_pitch)
        mesh.add_triangles(points, faces, z=z1)

    if bottom_cfg["textured"]:
        tl.textured_planar_polygon(
            mesh, sampler, polygon, holes_for_tri, rim_boundary, z0,
            bottom_cfg["depth_mm"], bottom_cfg["pitch_mm"], bottom_cfg["edge_taper_mm"],
            tile_width_mm=bottom_cfg["tile_width_mm"],
            tile_height_mm=bottom_cfg["tile_height_mm"],
            origin=bottom_cfg["origin"],
            engrave=bottom_cfg["engrave"],
            facing_up=False,
        )
    else:
        mesh_cap_pitch = max(1.0, wall_cfg["pitch_mm"])
        points, faces = tl.triangulate_cap(polygon, holes_for_tri, rim_boundary, grid_pitch=mesh_cap_pitch)
        mesh.add_triangles(points, faces, z=z0)

    vertices, faces, report = mesh.finalized()
    return vertices, faces, report


def build_solid(sampler: tl.TileSampler, recipe: dict, solid: dict) -> tuple[np.ndarray, np.ndarray, dict]:
    kind = solid.get("kind", "prism")
    if kind == "rect":
        x0, x1 = map(float, solid["x_range"])
        y0, y1 = map(float, solid["y_range"])
        solid = dict(solid)
        solid["polygon"] = rect_polygon(x0, y0, x1, y1).tolist()
        solid["holes"] = []
        kind = "prism"
    if kind != "prism":
        raise ValueError(f"unknown solid kind: {kind}")
    return build_prism(sampler, recipe, solid)


def union_vertices_faces(parts: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    from manifold3d import Manifold, Mesh, OpType

    manifolds = []
    for vertices, faces in parts:
        mesh = Mesh(
            vert_properties=np.ascontiguousarray(vertices, dtype=np.float32),
            tri_verts=np.ascontiguousarray(faces, dtype=np.uint32),
        )
        manifolds.append(Manifold(mesh=mesh))
    result = Manifold.batch_boolean(manifolds, OpType.Add)
    out = result.to_mesh()
    vertices = np.asarray(out.vert_properties, dtype=np.float64)[:, :3]
    faces = np.asarray(out.tri_verts, dtype=np.int64)
    return vertices, faces


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stl-name", default="textured-part.stl")
    parser.add_argument("--header", default="surface_texture applicator - generated mesh")
    args = parser.parse_args()

    t_start = time.time()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    recipe = load_recipe(spec, args.spec)
    sampler = sampler_from_recipe(recipe)

    parts: list[tuple[np.ndarray, np.ndarray, dict]] = []
    for solid in spec["solids"]:
        vertices, faces, report = build_solid(sampler, recipe, solid)
        tl.require_valid(report, f"solid {solid.get('name', 'unnamed')}")
        parts.append((vertices, faces, report))

    if len(parts) == 1:
        final_vertices, final_faces = parts[0][0], parts[0][1]
        final_report = parts[0][2]
        union_used = False
    else:
        final_vertices, final_faces = union_vertices_faces([p[:2] for p in parts])
        final_faces, orientation_report = tl.orient_mesh(final_vertices, final_faces)
        final_report = tl.mesh_report(final_vertices, final_faces)
        final_report.update(orientation_report)
        tl.require_valid(final_report, "union result")
        union_used = True

    limits = recipe.get("limits", {})
    max_triangles = int(limits.get("max_relief_triangles_per_part", 1_000_000))
    triangles = int(final_report["triangles"])
    if triangles > max_triangles:
        raise RuntimeError(
            f"triangle budget exceeded: {triangles} > {max_triangles}. "
            "Use pitch stepping (secondary_pitch_mm), fewer textured faces, or a coarser pitch."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stl_path = args.output_dir / args.stl_name
    tl.write_binary_stl(stl_path, final_vertices, final_faces, args.header)

    report = {
        "tool": "tools/surface_texture/apply_texture_patch.py",
        "spec": str(args.spec),
        "recipe": {
            "path": recipe["_path"],
            "texture_id": recipe.get("texture_id"),
            "master_sha256": json.loads(
                (Path(recipe["_path"]).parent / recipe["master"]["registration"]).read_text(encoding="utf-8")
            )["master_sha256"],
        },
        "union_used": union_used,
        "solids": [
            {
                "name": solid.get("name", f"solid_{i}"),
                "triangles": parts[i][2]["triangles"],
                "vertices": parts[i][2]["vertices"],
                "bounds_size_mm": parts[i][2]["bounds_size_mm"],
            }
            for i, solid in enumerate(spec["solids"])
        ],
        "final": final_report,
        "budget": {
            "max_relief_triangles_per_part": max_triangles,
            "triangles": triangles,
            "passed": triangles <= max_triangles,
        },
        "elapsed_seconds": round(time.time() - t_start, 3),
    }
    report_path = args.output_dir / (Path(args.stl_name).stem + "-report.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"stl": str(stl_path), "report": str(report_path), "triangles": triangles}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
