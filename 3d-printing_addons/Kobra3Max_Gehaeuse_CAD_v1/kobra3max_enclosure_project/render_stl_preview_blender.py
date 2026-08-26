#!/usr/bin/env python3
"""Blender-side deterministic STL preview renderer.

Run with:
  blender -b --python render_stl_preview_blender.py -- input.stl output.png
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def look_at(obj: bpy.types.Object, point: Vector) -> None:
    direction = point - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    return mat


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :]
    if len(argv) != 2:
        raise SystemExit("Expected input STL and output PNG")
    source = Path(argv[0]).resolve()
    output = Path(argv[1]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.stl_import(filepath=str(source))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise SystemExit(f"No mesh imported from {source}")

    for obj in meshes:
        obj.data.materials.append(material("PETG", (0.93, 0.56, 0.08, 1.0), 0.38))

    corners = []
    for obj in meshes:
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    min_corner = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    max_corner = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    centre = (min_corner + max_corner) / 2
    extent = max_corner - min_corner
    size = max(extent.x, extent.y, extent.z)

    floor_mat = material("Floor", (0.92, 0.92, 0.90, 1.0), 0.65)
    bpy.ops.mesh.primitive_plane_add(size=max(200.0, size * 4), location=(centre.x, centre.y, min_corner.z - 0.2))
    floor = bpy.context.object
    floor.data.materials.append(floor_mat)

    bpy.ops.object.camera_add(location=(centre.x + 1.7 * size, centre.y - 1.9 * size, centre.z + 1.35 * size))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = size * 1.55
    look_at(camera, centre)
    bpy.context.scene.camera = camera

    for location, energy, area_size in [
        ((centre.x - size, centre.y - size, centre.z + 2.5 * size), 1050, size * 1.8),
        ((centre.x + 1.8 * size, centre.y + size, centre.z + 1.2 * size), 700, size * 1.4),
        ((centre.x, centre.y + 0.3 * size, centre.z + 3.0 * size), 650, size * 1.2),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = max(50.0, area_size)
        look_at(lamp, centre)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.show_specular_highlight = True
    scene.render.resolution_x = 900
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output)
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.055, 0.055)
    scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
