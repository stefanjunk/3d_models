#!/usr/bin/env python3
"""Render the generated coupon with Blender 5.x in a fixed evidence view."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def look_at(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(args.input.resolve()))
    coupon = bpy.context.selected_objects[0]
    coupon.name = "NameForm wood pitch coupon"

    material = bpy.data.materials.new("warm PETG preview")
    material.use_nodes = True
    material.diffuse_color = (0.62, 0.19, 0.045, 1.0)
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
        0.62,
        0.19,
        0.045,
        1.0,
    )
    material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.52
    coupon.data.materials.append(material)

    bpy.ops.mesh.primitive_plane_add(size=500.0, location=(74.5, 8.0, -0.02))
    floor = bpy.context.object
    floor_material = bpy.data.materials.new("neutral build plane")
    floor_material.use_nodes = True
    floor_material.diffuse_color = (0.32, 0.34, 0.37, 1.0)
    floor_material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
        0.32,
        0.34,
        0.37,
        1.0,
    )
    floor_material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    floor.data.materials.append(floor_material)

    bpy.ops.object.light_add(type="AREA", location=(15.0, -70.0, 100.0))
    key = bpy.context.object
    key.data.energy = 2600.0
    key.data.shape = "RECTANGLE"
    key.data.size = 80.0
    key.data.size_y = 55.0
    look_at(key, (72.0, 1.0, 23.0))

    bpy.ops.object.light_add(type="AREA", location=(155.0, -35.0, 65.0))
    fill = bpy.context.object
    fill.data.energy = 1100.0
    fill.data.size = 65.0
    look_at(fill, (95.0, 2.0, 24.0))

    bpy.ops.object.light_add(type="AREA", location=(75.0, 55.0, 75.0))
    rim = bpy.context.object
    rim.data.energy = 1400.0
    rim.data.size = 70.0
    look_at(rim, (75.0, 3.0, 25.0))

    bpy.ops.object.camera_add(location=(74.5, -260.0, 88.0))
    camera = bpy.context.object
    camera.data.lens = 58.0
    look_at(camera, (74.5, 3.0, 22.0))
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("coupon world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.10, 0.11, 0.13, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    scene.world = world
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 2.0
    scene.render.filepath = str(args.output.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
