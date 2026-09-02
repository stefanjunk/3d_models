#!/usr/bin/env python3
"""Rebuild one revision 0.5.0 Berlin composite from four aligned tool STLs.

Tool 4 contains both the original 4.2-4.6 mm accent band and the site-marker
column beginning at 3.0 mm.  Only vertices on the known contact planes are
lowered by 0.02 mm before the Blender Manifold Boolean; the marker floor must
not be mistaken for the ordinary tool-4 band floor.  Tool 4 is split into its
loose components before unioning because one Boolean operand with unrelated
contact planes can leave microscopic shells in Blender's Manifold solver.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bmesh
import bpy

Z_OVERLAP_MM = 0.02
CONTACT_PLANES_BY_TOOL = (
    (),
    (3.0,),
    (3.6,),
    (3.0, 4.2),
)
SNAP_Z_PLANES_MM = (0.0, 2.98, 3.0, 3.58, 3.6, 4.18, 4.2, 4.6, 4.8, 5.2)


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


def lower_contact_planes(obj, nominal_planes: tuple[float, ...]) -> None:
    for vertex in obj.data.vertices:
        for nominal in nominal_planes:
            if abs(vertex.co.z - nominal) <= 0.001:
                vertex.co.z = nominal - Z_OVERLAP_MM
                break
    obj.data.update()


def separate_loose_parts(obj) -> list:
    """Return deterministic loose components while preserving the source object."""

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    before = set(bpy.data.objects)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    result = bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    if "FINISHED" not in result:
        raise RuntimeError(f"could not split loose parts of {obj.name}")
    parts = [obj, *[candidate for candidate in bpy.data.objects if candidate not in before]]
    parts.sort(
        key=lambda candidate: tuple(
            min(
                (
                    candidate.matrix_world @ vertex.co
                    for vertex in candidate.data.vertices
                ),
                key=lambda coordinate: (coordinate.x, coordinate.y, coordinate.z),
            )
        )
    )
    for index, part in enumerate(parts, start=1):
        part.name = f"tool-4-part-{index:02d}"
    print(f"split tool 4 into {len(parts)} loose components")
    return parts


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
        raise SystemExit("expected output plus four tool STL paths")
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
            ("tool-1-base", "tool-2-relief", "tool-3-streets", "tool-4-accent-marker"),
            strict=True,
        )
    ]
    for obj, contact_planes in zip(objects, CONTACT_PLANES_BY_TOOL, strict=True):
        lower_contact_planes(obj, contact_planes)
        print(f"import {obj.name}: {bounds_text(obj)}")

    base = objects[0]
    operands = [objects[1], objects[2], *separate_loose_parts(objects[3])]
    for operand in operands:
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
