#!/usr/bin/env python3
"""Render deterministic V6.2 geometry-review views with Blender."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_stl(path: Path):
    try:
        bpy.ops.wm.stl_import(filepath=str(path))
    except Exception:
        bpy.ops.import_mesh.stl(filepath=str(path))
    obj = bpy.context.selected_objects[0]
    obj.name = "V6_2_FREEFORM_UPPER"
    obj.scale = (0.001, 0.001, 0.001)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def material(name: str, color, roughness: float, metallic: float = 0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    node = mat.node_tree.nodes.get("Principled BSDF") if mat.use_nodes else None
    if node is None:
        mat.use_nodes = True
        node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1.0)
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Metallic"].default_value = metallic
    return mat


def add_camera():
    data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def aim(camera, location, target, ortho_scale=0.34) -> None:
    camera.location = Vector(location)
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale


def add_area(name, location, energy, size, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (0.0, 0.0, 0.0)
    return light


def render(scene, path: Path, camera, location, target, ortho_scale=0.34) -> None:
    aim(camera, location, target, ortho_scale)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    reset_scene()
    obj = import_stl(args.mesh.resolve())
    smooth = material("soft matte black TPU", (0.055, 0.075, 0.095), 0.46)
    obj.data.materials.append(smooth)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

    bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    z_min = min(point.z for point in bounds)
    bpy.ops.mesh.primitive_plane_add(size=1.2, location=(0.0, 0.135, z_min - 0.002))
    floor = bpy.context.active_object
    floor.data.materials.append(material("warm neutral floor", (0.045, 0.040, 0.037), 0.70))

    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.012, 0.014, 0.018, 1.0)
    background.inputs["Strength"].default_value = 0.20

    add_area("Key", (0.20, 0.31, 0.34), 55.0, 0.20, (1.0, 0.90, 0.78))
    add_area("Fill", (-0.22, 0.17, 0.20), 32.0, 0.18, (0.78, 0.88, 1.0))
    add_area("Rim", (0.02, -0.15, 0.28), 48.0, 0.14, (1.0, 1.0, 1.0))

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    camera = add_camera()

    render(
        scene,
        args.output / "production-three-quarter.png",
        camera,
        (0.34, 0.52, 0.27),
        (0.0, 0.145, 0.032),
        0.34,
    )
    render(
        scene,
        args.output / "production-top.png",
        camera,
        (0.0, 0.135, 0.70),
        (0.0, 0.135, 0.025),
        0.33,
    )
    render(
        scene,
        args.output / "production-collar-closeup.png",
        camera,
        (0.22, -0.10, 0.16),
        (0.0, 0.053, 0.036),
        0.12,
    )

    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    obj.data.materials.clear()
    obj.data.materials.append(material("flat geometry evidence", (0.16, 0.20, 0.24), 0.62))
    render(
        scene,
        args.output / "production-flat-shaded.png",
        camera,
        (0.34, 0.52, 0.27),
        (0.0, 0.145, 0.032),
        0.34,
    )


if __name__ == "__main__":
    main()
