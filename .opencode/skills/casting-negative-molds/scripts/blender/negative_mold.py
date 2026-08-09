#!/usr/bin/env python3
"""Blender batch baseline for block or conformal-shell negative molds.

Run inside Blender, for example:
  blender --background --python negative_mold.py -- --input master.stl --output-dir build

The script creates a planar two-part split. It does not prove demoldability.
Test in the exact Blender version used for production because import/export
operators change between releases.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


def script_argv() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def deselect_all() -> None:
    bpy.ops.object.select_all(action="DESELECT")


def delete_all() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_mesh(path: Path) -> list[bpy.types.Object]:
    before = set(bpy.data.objects)
    ext = path.suffix.lower()
    if ext == ".stl":
        if hasattr(bpy.ops.wm, "stl_import"):
            bpy.ops.wm.stl_import(filepath=str(path))
        else:
            bpy.ops.import_mesh.stl(filepath=str(path))
    elif ext == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(path))
        else:
            bpy.ops.import_scene.obj(filepath=str(path))
    elif ext == ".ply":
        if hasattr(bpy.ops.wm, "ply_import"):
            bpy.ops.wm.ply_import(filepath=str(path))
        else:
            bpy.ops.import_mesh.ply(filepath=str(path))
    else:
        raise ValueError("Supported inputs are STL, OBJ, and PLY. Convert 3MF or STEP first.")
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not imported:
        raise ValueError("Import produced no mesh objects.")
    return imported


def join_meshes(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    deselect_all()
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    if len(objects) > 1:
        bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    result.name = name
    return result


def apply_transform(obj: bpy.types.Object) -> None:
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def cleanup_mesh(obj: bpy.types.Object, merge_distance: float) -> None:
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if merge_distance > 0:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge_distance)
    bmesh.ops.dissolve_degenerate(bm, dist=max(merge_distance, 1e-9), edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    high = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    return low, high


def center_object(obj: bpy.types.Object) -> None:
    low, high = world_bounds(obj)
    center = (low + high) * 0.5
    obj.location -= center
    apply_transform(obj)


def duplicate_object(obj: bpy.types.Object, name: str) -> bpy.types.Object:
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    bpy.context.collection.objects.link(copy)
    return copy


def add_cube(name: str, dimensions: Vector, center: Vector) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transform(obj)
    return obj


def add_cone(name: str, r1: float, r2: float, depth: float, center: Vector, direction_axis: str = "Z", vertices: int = 48) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=center)
    obj = bpy.context.object
    obj.name = name
    if direction_axis == "X":
        obj.rotation_euler[1] = math.radians(90)
    elif direction_axis == "Y":
        obj.rotation_euler[0] = math.radians(-90)
    apply_transform(obj)
    return obj


def boolean_apply(target: bpy.types.Object, cutter: bpy.types.Object, operation: str) -> None:
    deselect_all()
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    modifier = target.modifiers.new(name=f"BOOL_{operation}_{cutter.name}", type="BOOLEAN")
    modifier.operation = operation
    modifier.object = cutter
    if hasattr(modifier, "solver"):
        modifier.solver = "EXACT"
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except Exception as exc:
        raise RuntimeError(f"Boolean {operation} failed between {target.name} and {cutter.name}: {exc}") from exc


def remove_object(obj: bpy.types.Object) -> None:
    bpy.data.objects.remove(obj, do_unlink=True)


def make_block_negative(master: bpy.types.Object, side: float, bottom: float, top: float) -> tuple[bpy.types.Object, dict[str, float]]:
    low, high = world_bounds(master)
    dims = Vector((high.x - low.x + 2 * side, high.y - low.y + 2 * side, high.z - low.z + bottom + top))
    zmin = low.z - bottom
    center = Vector((0, 0, zmin + dims.z / 2))
    block = add_cube("CompleteMold", dims, center)
    boolean_apply(block, master, "DIFFERENCE")
    return block, {"x": dims.x, "y": dims.y, "z": dims.z, "zmin": zmin, "zmax": zmin + dims.z}


def make_shell_negative(master: bpy.types.Object, thickness: float, flange_extra: float, split_axis: str) -> tuple[bpy.types.Object, dict[str, float]]:
    if thickness <= 0:
        raise ValueError("Shell thickness must be positive.")
    shell = duplicate_object(master, "CompleteMold")
    deselect_all()
    shell.select_set(True)
    bpy.context.view_layer.objects.active = shell
    modifier = shell.modifiers.new(name="OUTWARD_SOLIDIFY", type="SOLIDIFY")
    modifier.thickness = thickness
    modifier.offset = 1.0
    modifier.use_even_offset = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)

    low, high = world_bounds(master)
    sx = high.x - low.x + 2 * (thickness + flange_extra)
    sy = high.y - low.y + 2 * (thickness + flange_extra)
    sz = high.z - low.z + 2 * (thickness + flange_extra)
    if split_axis == "X":
        flange_dims = Vector((max(thickness, 3.0), sy, sz))
    else:
        flange_dims = Vector((sx, max(thickness, 3.0), sz))
    flange = add_cube("PartingFlange", flange_dims, (low + high) * 0.5)
    boolean_apply(flange, master, "DIFFERENCE")
    boolean_apply(shell, flange, "UNION")
    remove_object(flange)
    low_s, high_s = world_bounds(shell)
    return shell, {"x": high_s.x - low_s.x, "y": high_s.y - low_s.y, "z": high_s.z - low_s.z, "zmin": low_s.z, "zmax": high_s.z}


def subtract_vertical_channel(mold: bpy.types.Object, master: bpy.types.Object, dims: dict[str, float], xy: tuple[float, float], r1: float, r2: float, name: str) -> None:
    low, high = world_bounds(master)
    start = high.z - min(1.0, max(0.2, (high.z - low.z) * 0.01))
    depth = dims["zmax"] - start + 2.0
    cutter = add_cone(name, r1, r2, depth, Vector((xy[0], xy[1], start + depth / 2)), "Z")
    boolean_apply(mold, cutter, "DIFFERENCE")
    remove_object(cutter)


def split_mold(complete: bpy.types.Object, dims: dict[str, float], axis: str) -> tuple[bpy.types.Object, bpy.types.Object]:
    pad = 4.0
    a = duplicate_object(complete, "Mold_A")
    b = duplicate_object(complete, "Mold_B")
    if axis == "X":
        clip_dims = Vector((dims["x"] / 2 + pad, dims["y"] + 2 * pad, dims["z"] + 2 * pad))
        clip_a = add_cube("Clip_A", clip_dims, Vector((-dims["x"] / 4 - pad / 2, 0, (dims["zmin"] + dims["zmax"]) / 2)))
        clip_b = add_cube("Clip_B", clip_dims, Vector((dims["x"] / 4 + pad / 2, 0, (dims["zmin"] + dims["zmax"]) / 2)))
    else:
        clip_dims = Vector((dims["x"] + 2 * pad, dims["y"] / 2 + pad, dims["z"] + 2 * pad))
        clip_a = add_cube("Clip_A", clip_dims, Vector((0, -dims["y"] / 4 - pad / 2, (dims["zmin"] + dims["zmax"]) / 2)))
        clip_b = add_cube("Clip_B", clip_dims, Vector((0, dims["y"] / 4 + pad / 2, (dims["zmin"] + dims["zmax"]) / 2)))
    boolean_apply(a, clip_a, "INTERSECT")
    boolean_apply(b, clip_b, "INTERSECT")
    remove_object(clip_a)
    remove_object(clip_b)
    remove_object(complete)
    return a, b


def add_registration_keys(a: bpy.types.Object, b: bpy.types.Object, master: bpy.types.Object, dims: dict[str, float], axis: str,
                          side_margin: float, radius: float, depth: float, clearance: float) -> list[list[float]]:
    low, high = world_bounds(master)
    r = min(radius, side_margin * 0.30)
    if r <= 0.5:
        raise ValueError("Side margin is too small for registration keys.")
    z1 = max(dims["zmin"] + 1.6 * r, low.z + (high.z - low.z) * 0.20)
    z2 = min(dims["zmax"] - 1.6 * r, high.z - (high.z - low.z) * 0.20)
    offset = ((high.y - low.y) / 2 + side_margin * 0.55) if axis == "X" else ((high.x - low.x) / 2 + side_margin * 0.55)
    positions = ([[0, -offset, z1], [0, offset, z1], [0, -offset, z2], [0, offset * 0.72, z2]]
                 if axis == "X" else
                 [[-offset, 0, z1], [offset, 0, z1], [-offset, 0, z2], [offset * 0.72, 0, z2]])
    axis_index = 0 if axis == "X" else 1
    for idx, pos in enumerate(positions):
        male_center = Vector(pos)
        male_center[axis_index] = depth / 2 - 0.2
        male = add_cone(f"MaleKey_{idx}", r, r * 0.82, depth + 0.4, male_center, axis)
        socket = add_cone(f"Socket_{idx}", r + clearance, r * 0.82 + clearance, depth + 0.8, male_center, axis)
        boolean_apply(a, male, "UNION")
        boolean_apply(b, socket, "DIFFERENCE")
        remove_object(male)
        remove_object(socket)
    return positions


def export_selected_stl(obj: bpy.types.Object, path: Path) -> None:
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=str(path), use_selection=True, use_mesh_modifiers=True)


def mesh_stats(obj: bpy.types.Object) -> dict[str, int | bool]:
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    boundary = sum(1 for edge in bm.edges if len(edge.link_faces) == 1)
    nonmanifold = sum(1 for edge in bm.edges if len(edge.link_faces) not in (2,))
    stats = {"vertices": len(bm.verts), "edges": len(bm.edges), "faces": len(bm.faces), "boundary_edges": boundary, "nonmanifold_edges": nonmanifold}
    bm.free()
    return stats


def parse_vent(value: str) -> tuple[float, float]:
    try:
        x, y = value.split(",", 1)
        return float(x), float(y)
    except Exception as exc:
        raise argparse.ArgumentTypeError("Vent must be X,Y") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--mode", choices=("block", "shell"), default="block")
    parser.add_argument("--split-axis", choices=("X", "Y"), default="X")
    parser.add_argument("--shrink", nargs=3, type=float, default=(0.0, 0.0, 0.0))
    parser.add_argument("--side-margin", type=float, default=12.0)
    parser.add_argument("--bottom-margin", type=float, default=10.0)
    parser.add_argument("--top-margin", type=float, default=18.0)
    parser.add_argument("--shell-thickness", type=float, default=3.2)
    parser.add_argument("--flange-extra", type=float, default=10.0)
    parser.add_argument("--sprue", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--sprue-bottom-radius", type=float, default=4.0)
    parser.add_argument("--sprue-top-radius", type=float, default=10.0)
    parser.add_argument("--vent", type=parse_vent, action="append", default=[])
    parser.add_argument("--vent-radius", type=float, default=1.2)
    parser.add_argument("--key-radius", type=float, default=4.0)
    parser.add_argument("--key-depth", type=float, default=3.0)
    parser.add_argument("--key-clearance", type=float, default=0.25)
    parser.add_argument("--merge-distance", type=float, default=1e-5)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(script_argv())
    try:
        source = args.input.expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        out = args.output_dir.expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)

        delete_all()
        scene = bpy.context.scene
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.length_unit = "MILLIMETERS"
        scene.unit_settings.scale_length = 0.001

        master = join_meshes(import_mesh(source), "Master")
        apply_transform(master)
        cleanup_mesh(master, args.merge_distance)
        center_object(master)
        scales = [1.0 / (1.0 - s / 100.0) for s in args.shrink]
        if any(s <= 0 for s in scales):
            raise ValueError("Invalid shrinkage scale.")
        master.scale = scales
        apply_transform(master)

        if args.mode == "block":
            complete, dims = make_block_negative(master, args.side_margin, args.bottom_margin, args.top_margin)
        else:
            complete, dims = make_shell_negative(master, args.shell_thickness, args.flange_extra, args.split_axis)

        channels: list[dict[str, object]] = []
        if args.sprue:
            subtract_vertical_channel(complete, master, dims, (0.0, 0.0), args.sprue_bottom_radius, args.sprue_top_radius, "Sprue")
            channels.append({"type": "sprue", "xy": [0, 0]})
        for idx, xy in enumerate(args.vent):
            subtract_vertical_channel(complete, master, dims, xy, args.vent_radius, args.vent_radius, f"Vent_{idx}")
            channels.append({"type": "vent", "xy": list(xy)})

        mold_a, mold_b = split_mold(complete, dims, args.split_axis)
        positions = add_registration_keys(mold_a, mold_b, master, dims, args.split_axis, args.side_margin,
                                          args.key_radius, args.key_depth, args.key_clearance)
        cleanup_mesh(mold_a, args.merge_distance)
        cleanup_mesh(mold_b, args.merge_distance)

        export_selected_stl(mold_a, out / "mold_A.stl")
        export_selected_stl(mold_b, out / "mold_B.stl")
        export_selected_stl(master, out / "master_adjusted.stl")
        bpy.ops.wm.save_as_mainfile(filepath=str(out / "negative_mold.blend"))

        manifest = {
            "generator": "scripts/blender/negative_mold.py",
            "blender_version": bpy.app.version_string,
            "source": str(source),
            "units": "mm",
            "mode": args.mode,
            "split_axis": args.split_axis,
            "shrinkage_percent_xyz": list(args.shrink),
            "scale_xyz": scales,
            "dimensions": dims,
            "keys": {"positions": positions, "clearance_mm": args.key_clearance},
            "channels": channels,
            "mesh_stats": {"mold_A": mesh_stats(mold_a), "mold_B": mesh_stats(mold_b)},
            "warnings": [
                "Planar splitting does not prove demoldability.",
                "Blender operator names differ by release; validate in the target version.",
                "For conventional ceramic slip casting, route dense printed tooling through an absorbent plaster working mold."
            ]
        }
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output_dir": str(out), "mold_A": manifest["mesh_stats"]["mold_A"], "mold_B": manifest["mesh_stats"]["mold_B"]}, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
