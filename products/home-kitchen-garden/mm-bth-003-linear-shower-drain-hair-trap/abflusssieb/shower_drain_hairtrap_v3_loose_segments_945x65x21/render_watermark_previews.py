#!/usr/bin/env python3
"""Render the actual marked STL from inside the double segment with Blender."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "exports" / "master" / "DRAFT-MM-BTH-003-3.1.0-draft.1-double-105mm-marked-master.stl"
OUTPUT = ROOT / "validation" / "previews" / "DRAFT-MM-BTH-003-3.1.0-draft.1-watermark-inner-side-render.png"


def point_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def add_area_light(name: str, location: tuple[float, float, float], energy: float, size: float, target: tuple[float, float, float]) -> None:
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "RECTANGLE"
    data.size = size
    data.size_y = size / 2.0
    light = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(light)
    light.location = location
    point_camera(light, target)


def main() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.stl_import(filepath=str(MODEL))
    model = bpy.context.selected_objects[0]
    model.name = "MM-BTH-003-marked-double"

    material = bpy.data.materials.new("PETG inspection grey")
    material.diffuse_color = (0.30, 0.38, 0.43, 1.0)
    material.metallic = 0.0
    material.roughness = 0.58
    model.data.materials.append(material)

    camera_data = bpy.data.cameras.new("Interior orthographic camera")
    camera = bpy.data.objects.new("Interior orthographic camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (52.5, 42.0, 8.4)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 96.0
    camera_data.lens = 52.0
    camera_data.clip_start = 0.1
    camera_data.clip_end = 500.0
    point_camera(camera, (52.5, 2.8, 8.4))
    bpy.context.scene.camera = camera

    add_area_light("Grazing top", (52.5, 24.0, 15.5), 850.0, 55.0, (52.5, 2.8, 8.0))
    add_area_light("Grazing left", (15.0, 25.0, 5.0), 500.0, 30.0, (45.0, 2.8, 8.0))
    add_area_light("Fill", (92.0, 28.0, 10.0), 300.0, 35.0, (60.0, 2.8, 8.0))

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = str(OUTPUT)
    scene.render.image_settings.color_depth = "8"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.42, 0.58, 0.68)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.curvature_ridge_factor = 2.0
    scene.display.shading.curvature_valley_factor = 2.0
    scene.display.shading.show_object_outline = True
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = (0.96, 0.96, 0.96)
    scene.view_settings.look = "AgX - Medium High Contrast"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
