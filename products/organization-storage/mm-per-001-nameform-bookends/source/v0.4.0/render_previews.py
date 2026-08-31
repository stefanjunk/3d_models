#!/usr/bin/env python3
"""Render fixed front and grazing-light previews for NameForm 0.4.0 variants."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def material(
    name: str, color: tuple[float, float, float, float], roughness: float
) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = color
    shader = result.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return result


def add_area(
    location: tuple[float, float, float],
    energy: float,
    size: float,
    target: tuple[float, float, float],
) -> None:
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    look_at(light, target)


def add_sun(rotation: tuple[float, float, float], energy: float, angle: float) -> None:
    bpy.ops.object.light_add(type="SUN", rotation=rotation)
    light = bpy.context.object
    light.data.energy = energy
    light.data.angle = angle


def configure(output: Path, width: int, height: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("NameForm evidence world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.025,
        0.032,
        0.045,
        1.0,
    )
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
    scene.world = world
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.8
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output.resolve())


def import_stl(path: Path, name: str, wood: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.wm.stl_import(filepath=str(path.resolve()))
    obj = bpy.context.selected_objects[0]
    obj.name = name
    obj.data.materials.append(wood)
    return obj


def add_floor(location: tuple[float, float, float], size: float = 1000.0) -> None:
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    bpy.context.object.data.materials.append(
        material("charcoal floor", (0.13, 0.15, 0.18, 1.0), 0.94)
    )


def render_coupon(input_path: Path, output: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    wood = material("warm wood filament", (0.43, 0.19, 0.055, 1.0), 0.66)
    import_stl(input_path, "FA process coupon", wood)
    add_floor((69.0, 4.0, -0.03), 450.0)
    target = (69.0, 1.0, 61.0)
    add_area((-35.0, -65.0, 165.0), 3100.0, 42.0, target)
    add_area((185.0, -25.0, 95.0), 1850.0, 35.0, target)
    add_area((65.0, 90.0, 170.0), 1600.0, 65.0, target)
    add_sun((0.88, -0.47, -0.95), 2.8, 0.04)
    bpy.ops.object.camera_add(location=(69.0, -420.0, 70.0))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 165.0
    camera.data.clip_end = 5000.0
    look_at(camera, target)
    bpy.context.scene.camera = camera
    configure(output, 1500, 900)
    bpy.ops.render.render(write_still=True)


def prepare_pair(
    left_path: Path,
    right_path: Path,
    left_label: str,
    right_label: str,
) -> None:
    wood = material("warm wood filament", (0.43, 0.19, 0.055, 1.0), 0.66)
    left = import_stl(left_path, f"left {left_label}", wood)
    right = import_stl(right_path, f"right {right_label}", wood)
    left.location.x -= 120.0
    right.location.x += 120.0
    add_floor((0.0, 55.0, -0.03), 1100.0)


def pair_lighting() -> tuple[float, float, float]:
    target = (10.0, 20.0, 78.0)
    add_area((-330.0, -95.0, 245.0), 5200.0, 78.0, target)
    add_area((360.0, -35.0, 150.0), 3300.0, 64.0, target)
    add_area((0.0, 185.0, 270.0), 2600.0, 110.0, target)
    add_sun((0.84, -0.44, -0.88), 3.2, 0.035)
    add_sun((1.15, 0.52, 1.28), 1.0, 0.12)
    return target


def render_pair_front(
    left_path: Path,
    right_path: Path,
    left_label: str,
    right_label: str,
    output: Path,
) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    prepare_pair(left_path, right_path, left_label, right_label)
    target = pair_lighting()
    bpy.ops.object.camera_add(location=(10.0, -950.0, 110.0))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 800.0
    camera.data.clip_end = 5000.0
    look_at(camera, target)
    bpy.context.scene.camera = camera
    configure(output, 1800, 950)
    bpy.ops.render.render(write_still=True)


def render_pair_three_quarter(
    left_path: Path,
    right_path: Path,
    left_label: str,
    right_label: str,
    output: Path,
) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    prepare_pair(left_path, right_path, left_label, right_label)
    target = pair_lighting()
    bpy.ops.object.camera_add(location=(600.0, -1450.0, 430.0))
    camera = bpy.context.object
    camera.data.lens = 42.0
    camera.data.clip_end = 5000.0
    look_at(camera, target)
    bpy.context.scene.camera = camera
    configure(output, 1800, 1050)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coupon", type=Path)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--coupon-output", type=Path)
    parser.add_argument("--pair-front-output", type=Path, required=True)
    parser.add_argument("--pair-three-quarter-output", type=Path, required=True)
    parser.add_argument("--left-label", default="LEFT")
    parser.add_argument("--right-label", default="RIGHT")
    args = parser.parse_args(argv)
    if (args.coupon is None) != (args.coupon_output is None):
        parser.error("--coupon and --coupon-output must be supplied together")
    outputs = [args.pair_front_output, args.pair_three_quarter_output]
    if args.coupon_output is not None:
        outputs.append(args.coupon_output)
    for output in outputs:
        if output.exists():
            raise FileExistsError(f"refusing to overwrite preview: {output}")
    if args.coupon is not None and args.coupon_output is not None:
        render_coupon(args.coupon, args.coupon_output)
    render_pair_front(
        args.left,
        args.right,
        args.left_label,
        args.right_label,
        args.pair_front_output,
    )
    render_pair_three_quarter(
        args.left,
        args.right,
        args.left_label,
        args.right_label,
        args.pair_three_quarter_output,
    )


if __name__ == "__main__":
    main()
