#!/usr/bin/env python3
"""Render fixed grazing-light evidence views for the transfer coupon and pair."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = color
    result.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    result.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = roughness
    return result


def add_area(location: tuple[float, float, float], energy: float, size: float,
             target: tuple[float, float, float]) -> None:
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.data.size = size
    look_at(light, target)


def add_sun(rotation: tuple[float, float, float], energy: float, angle: float) -> None:
    bpy.ops.object.light_add(type="SUN", rotation=rotation)
    light = bpy.context.object
    light.data.energy = energy
    light.data.angle = angle


def configure_scene(output: Path, width: int, height: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("evidence world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.065, 0.08, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 1.0
    scene.render.filepath = str(output.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)


def render_coupon(input_path: Path, output: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(input_path.resolve()))
    coupon = bpy.context.selected_objects[0]
    coupon.name = "Direct sampled wood transfer coupon A B C D"
    coupon.data.materials.append(material("light clay", (0.62, 0.39, 0.19, 1.0), 0.58))
    bpy.ops.mesh.primitive_plane_add(size=500.0, location=(92.0, 8.0, -0.02))
    bpy.context.object.data.materials.append(material("floor", (0.24, 0.27, 0.31, 1.0), 0.92))
    target = (92.0, 0.5, 25.0)
    add_area((-20.0, -45.0, 70.0), 3200.0, 38.0, target)
    add_area((205.0, -20.0, 45.0), 1700.0, 28.0, target)
    add_area((92.0, 45.0, 85.0), 1400.0, 65.0, target)
    add_sun((0.92, -0.45, -0.92), 3.2, 0.05)
    add_sun((1.18, 0.55, 1.32), 1.3, 0.12)
    bpy.ops.object.camera_add(location=(92.0, -305.0, 92.0))
    camera = bpy.context.object
    camera.data.lens = 58.0
    look_at(camera, target)
    bpy.context.scene.camera = camera
    configure_scene(output, 1600, 760)
    bpy.ops.render.render(write_still=True)


def render_pair(left_path: Path, right_path: Path, output: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    wood = material("wood clay", (0.52, 0.30, 0.13, 1.0), 0.62)
    for path, offset, name in ((left_path, -120.0, "left STE"), (right_path, 120.0, "right FAN")):
        bpy.ops.wm.stl_import(filepath=str(path.resolve()))
        obj = bpy.context.selected_objects[0]
        obj.name = name
        obj.location.x += offset
        obj.data.materials.append(wood)
    bpy.ops.mesh.primitive_plane_add(size=900.0, location=(0.0, 55.0, -0.02))
    bpy.context.object.data.materials.append(material("floor", (0.22, 0.24, 0.28, 1.0), 0.9))
    target = (0.0, 1.0, 78.0)
    add_area((-285.0, -80.0, 185.0), 4700.0, 72.0, target)
    add_area((285.0, -30.0, 125.0), 3000.0, 60.0, target)
    add_area((0.0, 150.0, 235.0), 2200.0, 100.0, target)
    add_sun((0.88, -0.42, -0.88), 3.0, 0.05)
    add_sun((1.12, 0.48, 1.25), 1.2, 0.14)
    bpy.ops.object.camera_add(location=(0.0, -900.0, 225.0))
    camera = bpy.context.object
    camera.data.lens = 58.0
    look_at(camera, target)
    bpy.context.scene.camera = camera
    configure_scene(output, 1700, 900)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coupon", type=Path, required=True)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    render_coupon(args.coupon, args.output_dir / "DRAFT-nameform-wood-direct-transfer-coupon-v0.2.0.png")
    render_pair(args.left, args.right, args.output_dir / "DRAFT-nameform-STE-FAN-wood-direct-v0.3.0-tx0.2.0.png")


if __name__ == "__main__":
    main()
