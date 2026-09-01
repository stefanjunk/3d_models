#!/usr/bin/env python3
"""Rebuild one regular composite STL from four aligned color-band STLs.

Run through Blender, for example:
  blender --background --factory-startup --python rebuild_composite_blender.py -- \
    output.stl bone.stl nardo.stl black.stl orange.stl
"""

from __future__ import annotations

import sys
from pathlib import Path

import bmesh
import bpy

Z_OVERLAP_MM = 0.02
LOWER_BAND_Z_MM = (None, 3.0, 3.6, 4.2)
SNAP_Z_PLANES_MM = (0.0, 2.98, 3.0, 3.58, 3.6, 4.18, 4.2, 4.6)


def import_stl(path: Path, name: str):
    before = set(bpy.data.objects)
    result = bpy.ops.wm.stl_import(filepath=str(path))
    if "FINISHED" not in result:
        raise RuntimeError(f"Blender could not import {path}")
    created = [obj for obj in bpy.data.objects if obj not in before]
    if len(created) != 1 or created[0].type != "MESH":
        raise RuntimeError(f"expected one mesh object from {path}, got {created}")
    created[0].name = name
    return created[0]


def lower_band_floor(obj, nominal_floor: float) -> None:
    threshold = nominal_floor + 0.001
    overlap_floor = nominal_floor - Z_OVERLAP_MM
    for vertex in obj.data.vertices:
        if vertex.co.z <= threshold:
            vertex.co.z = overlap_floor
    obj.data.update()


def bounds_text(obj) -> str:
    coordinates = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    minimum = tuple(min(value[index] for value in coordinates) for index in range(3))
    maximum = tuple(max(value[index] for value in coordinates) for index in range(3))
    return f"min={minimum}, max={maximum}, vertices={len(coordinates)}, faces={len(obj.data.polygons)}"


def snap_z_planes(obj) -> None:
    for vertex in obj.data.vertices:
        for plane in SNAP_Z_PLANES_MM:
            if abs(vertex.co.z - plane) <= 0.001:
                vertex.co.z = plane
                break
    obj.data.update()


def boolean_union(base, operand) -> None:
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    operand.select_set(False)
    modifier = base.modifiers.new(name=f"union-{operand.name}", type="BOOLEAN")
    modifier.operation = "UNION"
    modifier.solver = "MANIFOLD"
    modifier.object = operand
    result = bpy.ops.object.modifier_apply(modifier=modifier.name)
    if "FINISHED" not in result:
        raise RuntimeError(f"exact Boolean failed for {operand.name}")
    print(f"union {operand.name}: {bounds_text(base)}")
    bpy.data.objects.remove(operand, do_unlink=True)


def clean_mesh(obj) -> None:
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=1e-4,
        verts=bm.verts,
        edges=bm.edges,
        use_dissolve_boundaries=False,
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(
        bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY"
    )
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(clean_customdata=True)
    mesh.update()


def main() -> None:
    if "--" not in sys.argv:
        raise SystemExit("expected Blender arguments after --")
    args = sys.argv[sys.argv.index("--") + 1 :]
    if len(args) != 5:
        raise SystemExit("expected output plus four color-band STL paths")
    output = Path(args[0]).resolve()
    inputs = [Path(value).resolve() for value in args[1:]]
    if output.exists():
        raise SystemExit(f"refusing destructive overwrite of {output}")
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise SystemExit(f"missing input STL(s): {missing}")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    objects = [
        import_stl(path, name)
        for path, name in zip(
            inputs,
            ("bone-white", "nardo-grey", "black", "orange"),
            strict=True,
        )
    ]
    for obj, nominal_floor in zip(objects, LOWER_BAND_Z_MM, strict=True):
        if nominal_floor is not None:
            lower_band_floor(obj, nominal_floor)
        print(f"import {obj.name}: {bounds_text(obj)}")

    base = objects[0]
    for operand in objects[1:]:
        boolean_union(base, operand)
    snap_z_planes(base)
    clean_mesh(base)

    bpy.ops.object.select_all(action="DESELECT")
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    result = bpy.ops.wm.stl_export(
        filepath=str(output),
        ascii_format=False,
        export_selected_objects=True,
        apply_modifiers=True,
    )
    if "FINISHED" not in result or not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"Blender could not export {output}")


if __name__ == "__main__":
    main()
