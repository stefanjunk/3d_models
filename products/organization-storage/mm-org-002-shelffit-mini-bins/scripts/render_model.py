#!/usr/bin/env python3
"""Blender headless renders from the actual marked manufacturing STL."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "exports" / "candidate" / "manufacturing" / "DRAFT-shelffit-mini-bin-0.1.0-manufacturing.stl"
OUT = ROOT / "renders"


def reset() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.58):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return mat


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(location, target, lens=54.0, ortho_scale=None):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.data.lens = lens
    if ortho_scale is not None:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = ortho_scale
    look_at(camera, target)
    bpy.context.scene.camera = camera
    return camera


def add_area(location, energy, size, color=(1.0, 1.0, 1.0)):
    bpy.ops.object.light_add(type="AREA", location=location)
    lamp = bpy.context.object
    lamp.data.energy = energy
    lamp.data.shape = "DISK"
    lamp.data.size = size
    lamp.data.color = color
    look_at(lamp, (0.0, 0.0, 70.0))
    return lamp


def import_stl():
    try:
        bpy.ops.wm.stl_import(filepath=str(STL))
    except Exception:
        bpy.ops.import_mesh.stl(filepath=str(STL))
    obj = bpy.context.selected_objects[0]
    obj.name = "ShelfFit_Mini_Bin_MM_ORG_002_v0_1_0"
    return obj


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.055, 0.055, 0.055)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "WORLD"
    OUT.mkdir(parents=True, exist_ok=True)


def render_pair(bin_mat, floor_mat) -> None:
    reset()
    first = import_stl()
    first.data.materials.append(bin_mat)
    first.location.x = -108.5
    second = first.copy()
    second.data = first.data.copy()
    bpy.context.collection.objects.link(second)
    second.location.x = 108.5

    bpy.ops.mesh.primitive_plane_add(size=1200, location=(0.0, 0.0, -0.4))
    floor = bpy.context.object
    floor.data.materials.append(floor_mat)
    bevel = floor.modifiers.new("soft_floor_edge", "BEVEL")
    bevel.width = 2.0

    add_camera((520.0, -610.0, 390.0), (0.0, 0.0, 72.0), lens=56.0)
    add_area((-260.0, -260.0, 480.0), 1150.0, 330.0)
    add_area((340.0, 80.0, 330.0), 800.0, 250.0, (0.86, 0.92, 1.0))
    add_area((0.0, 400.0, 260.0), 650.0, 220.0, (1.0, 0.86, 0.72))
    bpy.context.scene.render.filepath = str(OUT / "actual-model-pair.png")
    bpy.ops.render.render(write_still=True)


def render_underside(bin_mat) -> None:
    reset()
    obj = import_stl()
    obj.data.materials.append(bin_mat)
    # Flip the product over its Y axis. The generated cutter is mirrored in X,
    # so this physical flip produces normal finished-underside reading.
    obj.rotation_euler = (0.0, math.pi, 0.0)
    obj.location.z = 148.0
    camera = add_camera((0.0, 0.0, 520.0), (0.0, 0.0, 148.0), ortho_scale=230.0)
    # A top camera looking down uses identity rotation. Set the roll explicitly
    # so the finished underside, already turned upward, reads normally.
    camera.rotation_euler = (0.0, 0.0, 0.0)
    add_area((-100.0, -120.0, 430.0), 1000.0, 300.0)
    add_area((140.0, 120.0, 360.0), 750.0, 250.0)
    bpy.context.scene.render.resolution_x = 820
    bpy.context.scene.render.resolution_y = 820
    bpy.context.view_layer.update()
    bpy.context.scene.render.filepath = str(OUT / "finished-underside.png")
    bpy.ops.render.render(write_still=True)

    bpy.context.scene.camera.data.ortho_scale = 86.0
    bpy.context.scene.render.resolution_x = 1200
    bpy.context.scene.render.resolution_y = 360
    bpy.context.scene.render.filepath = str(OUT / "watermark-closeup.png")
    bpy.ops.render.render(write_still=True)


def main() -> None:
    configure_scene()
    bin_mat = material("Matte sage PLA", (0.33, 0.45, 0.31, 1.0), 0.62)
    floor_mat = material("Warm studio floor", (0.73, 0.69, 0.61, 1.0), 0.72)
    render_pair(bin_mat, floor_mat)
    render_underside(bin_mat)


if __name__ == "__main__":
    main()
