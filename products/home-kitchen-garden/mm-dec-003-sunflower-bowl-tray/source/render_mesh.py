#!/usr/bin/env python3
"""Render deterministic review views of a sunflower STL in Blender Workbench."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def import_stl(path: str) -> None:
    try:
        bpy.ops.wm.stl_import(filepath=path)
    except Exception:
        bpy.ops.import_mesh.stl(filepath=path)


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[i] for point in points) for i in range(3))),
        Vector(tuple(max(point[i] for point in points) for i in range(3))),
    )


def look_at(camera: bpy.types.Object, location: Vector, target: Vector) -> None:
    camera.location = location
    camera.rotation_euler = (target - location).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    args = sys.argv[sys.argv.index("--") + 1 :]
    if len(args) not in {2, 3}:
        raise SystemExit("usage: blender -b --python render_mesh.py -- INPUT_STL OUTPUT_PREFIX [components]")
    source, output_prefix = args[:2]
    component_colors = len(args) == 3 and args[2] == "components"

    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_stl(source)
    meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"expected one imported mesh object, got {len(meshes)}")
    active = meshes[0]
    if component_colors:
        bpy.context.view_layer.objects.active = active
        active.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")
        meshes = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]

    palette = [
        (0.95, 0.52, 0.05, 1.0),
        (0.05, 0.45, 0.95, 1.0),
        (0.20, 0.75, 0.25, 1.0),
        (0.75, 0.15, 0.70, 1.0),
    ]
    for index, obj in enumerate(sorted(meshes, key=lambda item: len(item.data.polygons), reverse=True)):
        obj.color = palette[index % len(palette)] if component_colors else (0.95, 0.52, 0.05, 1.0)

    bounds_min, bounds_max = world_bounds(meshes)
    center = (bounds_min + bounds_max) * 0.5
    extents = bounds_max - bounds_min
    span_xy = max(extents.x, extents.y)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = True
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"

    camera_data = bpy.data.cameras.new("ReviewCamera")
    camera = bpy.data.objects.new("ReviewCamera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = "ORTHO"

    output = Path(output_prefix).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    views = {
        "top": (Vector((center.x, center.y, bounds_max.z + span_xy * 1.5)), span_xy * 1.12),
        "front": (Vector((center.x, bounds_min.y - span_xy * 1.5, center.z)), max(extents.x, extents.z) * 1.12),
        "iso": (center + Vector((span_xy, -span_xy, span_xy * 0.72)), max(span_xy, extents.z) * 1.32),
    }
    for name, (location, scale) in views.items():
        camera_data.ortho_scale = float(scale)
        look_at(camera, location, center)
        scene.render.filepath = str(output.with_name(f"{output.name}-{name}.png"))
        bpy.ops.render.render(write_still=True)
        print(f"rendered {name}: {scene.render.filepath}")


if __name__ == "__main__":
    main()
