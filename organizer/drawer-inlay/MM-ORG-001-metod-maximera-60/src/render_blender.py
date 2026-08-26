#!/usr/bin/env python3
"""Blender evidence render for the MM-ORG-001 DRAFT assembly."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


ROOT = Path(__file__).resolve().parent.parent


def srgb(hex_value: str) -> tuple[float, float, float, float]:
    value = hex_value.lstrip("#")
    channels = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return (*linear, 1.0)


def display_rgba(hex_value: str) -> tuple[float, float, float, float]:
    value = hex_value.lstrip("#")
    return (*(int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)), 1.0)


def material(name: str, color: str, roughness: float = 0.46):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = display_rgba(color)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = srgb(color)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def point_camera(camera, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def import_stl(path: Path, name: str, translation: list[float], mat) -> None:
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.active_object
    obj.name = name
    obj.location = translation
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False


def main() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    build = json.loads((ROOT / "reports" / "build-report.json").read_text(encoding="utf-8"))
    mats = {
        0: material("metriMade sand", "#C7AB82", 0.5),
        1: material("metriMade teal", "#08777D", 0.44),
        2: material("metriMade navy", "#112431", 0.4),
        "comb": material("metriMade aqua", "#7FD5D3", 0.42),
        "canvas": material("warm canvas", "#FBFAF7", 0.68),
    }
    for item in build["modules"]:
        import_stl(ROOT / item["manufacturing_file"], item["id"], item["assembly_translation_mm"], mats[item["column"]])
    comb = build["accessories"]["screwdriver_comb"]
    import_stl(ROOT / comb["manufacturing_file"], "screwdriver-comb", comb["assembly_translation_mm"], mats["comb"])

    bpy.ops.mesh.primitive_plane_add(size=1600, location=(256, 245.5, -1.2))
    bpy.context.active_object.data.materials.append(mats["canvas"])

    bpy.ops.object.light_add(type="AREA", location=(-150, -180, 780))
    key = bpy.context.active_object
    key.data.energy = 1450
    key.data.shape = "DISK"
    key.data.size = 520
    point_camera(key, (256, 245.5, 0))
    bpy.ops.object.light_add(type="AREA", location=(760, 180, 520))
    fill = bpy.context.active_object
    fill.data.energy = 950
    fill.data.size = 420
    point_camera(fill, (280, 250, 20))
    bpy.ops.object.light_add(type="AREA", location=(140, 780, 380))
    rim = bpy.context.active_object
    rim.data.energy = 700
    rim.data.size = 360
    point_camera(rim, (256, 245.5, 10))

    bpy.ops.object.camera_add(location=(755, -735, 660))
    camera = bpy.context.active_object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 760
    camera.data.clip_end = 5000
    point_camera(camera, (256, 245.5, 18))
    bpy.context.scene.camera = camera
    bpy.context.view_layer.update()

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = display_rgba("#FBFAF7")[:3]
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1050
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = srgb("#FBFAF7")
    background.inputs["Strength"].default_value = 0.7
    scene.render.filepath = str(ROOT / "reports" / "DRAFT-MM-ORG-001-v0.1.0-draft.1-assembly-blender.png")
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    mesh_objects = [obj for obj in scene.objects if obj.type == "MESH" and obj.name != "Plane"]
    world_points = [obj.matrix_world @ Vector(corner) for obj in mesh_objects for corner in obj.bound_box]
    bounds_min = tuple(min(point[axis] for point in world_points) for axis in range(3))
    bounds_max = tuple(max(point[axis] for point in world_points) for axis in range(3))
    print(f"RENDER_BOUNDS min={bounds_min} max={bounds_max} camera={camera.data.type} ortho={camera.data.ortho_scale}")
    projected_center = world_to_camera_view(scene, camera, Vector((256, 245.5, 25)))
    projected = [world_to_camera_view(scene, camera, point) for point in world_points]
    projected_bounds = tuple((min(point[axis] for point in projected), max(point[axis] for point in projected)) for axis in range(2))
    print(f"PROJECTED_CENTER {tuple(projected_center)} projected_bounds={projected_bounds} camera_loc={tuple(camera.location)} camera_rot={tuple(camera.rotation_euler)}")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
