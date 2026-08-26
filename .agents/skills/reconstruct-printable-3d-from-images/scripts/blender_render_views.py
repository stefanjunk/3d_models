#!/usr/bin/env python3
"""Render repeatable canonical model views in Blender.

Invoke with:
  blender --background --python blender_render_views.py -- --model part.glb ...

The PNG alpha channel is the candidate mask for compare_views.py.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SUPPORTED_VIEWS = ("front", "right", "back", "left", "top", "bottom", "iso")


def arguments_after_separator() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render canonical transparent model views.")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--views",
        default="front,right,back,left,top,iso",
        help="Comma-separated canonical views.",
    )
    parser.add_argument("--resolution", type=int, default=768)
    parser.add_argument(
        "--projection", choices=("orthographic", "perspective"), default="orthographic"
    )
    parser.add_argument("--focal-mm", type=positive, default=70.0)
    parser.add_argument("--ortho-scale", type=positive)
    parser.add_argument("--margin", type=positive, default=1.25)
    parser.add_argument("--color", default="#B8BCC4")
    parser.add_argument("--preserve-materials", action="store_true")
    parser.add_argument("--no-center", action="store_true")
    parser.add_argument(
        "--rotate-deg",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        default=(0.0, 0.0, 0.0),
        help="Rotate imported root before framing.",
    )
    return parser.parse_args(arguments_after_separator())


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def call_operator(primary: tuple[str, str], fallback: tuple[str, str], filepath: str) -> None:
    primary_group = getattr(bpy.ops, primary[0], None)
    primary_op = getattr(primary_group, primary[1], None) if primary_group else None
    if primary_op:
        primary_op(filepath=filepath)
        return
    fallback_group = getattr(bpy.ops, fallback[0], None)
    fallback_op = getattr(fallback_group, fallback[1], None) if fallback_group else None
    if fallback_op:
        fallback_op(filepath=filepath)
        return
    raise RuntimeError(f"No Blender importer found for {filepath}")


def import_model(path: Path) -> list[bpy.types.Object]:
    if not path.is_file():
        raise FileNotFoundError(path)
    before = set(bpy.data.objects)
    suffix = path.suffix.lower()
    if suffix in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif suffix == ".obj":
        call_operator(("wm", "obj_import"), ("import_scene", "obj"), str(path))
    elif suffix == ".stl":
        call_operator(("wm", "stl_import"), ("import_mesh", "stl"), str(path))
    elif suffix == ".ply":
        call_operator(("wm", "ply_import"), ("import_mesh", "ply"), str(path))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise ValueError(f"Unsupported model format: {suffix}")
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not any(obj.type == "MESH" for obj in imported):
        raise RuntimeError("Importer produced no mesh objects")
    return imported


def create_root(imported: list[bpy.types.Object], rotation_deg: tuple[float, float, float]):
    root = bpy.data.objects.new("RenderRoot", None)
    bpy.context.scene.collection.objects.link(root)
    imported_set = set(imported)
    for obj in imported:
        if obj.parent not in imported_set:
            world = obj.matrix_world.copy()
            obj.parent = root
            obj.matrix_world = world
    root.rotation_euler = tuple(math.radians(value) for value in rotation_deg)
    bpy.context.view_layer.update()
    return root


def world_bounds(mesh_objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points: list[Vector] = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in mesh_objects:
        evaluated = obj.evaluated_get(depsgraph)
        points.extend(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def parse_hex_color(value: str) -> tuple[float, float, float, float]:
    text = value.strip().lstrip("#")
    if len(text) != 6:
        raise ValueError("--color must be a six-digit hex RGB value")
    channels = [int(text[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]
    return channels[0], channels[1], channels[2], 1.0


def assign_clay(mesh_objects: list[bpy.types.Object], color: tuple[float, float, float, float]) -> None:
    material = bpy.data.materials.new("ValidationClay")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        if "Base Color" in principled.inputs:
            principled.inputs["Base Color"].default_value = color
        if "Roughness" in principled.inputs:
            principled.inputs["Roughness"].default_value = 0.72
        if "Metallic" in principled.inputs:
            principled.inputs["Metallic"].default_value = 0.0
    for obj in mesh_objects:
        obj.data.materials.clear()
        obj.data.materials.append(material)


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_light(name: str, location: tuple[float, float, float], energy: float, size: float, target: Vector):
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def configure_scene(target: Vector, diagonal: float) -> None:
    scene = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    if scene.world is None:
        scene.world = bpy.data.worlds.new("ValidationWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.8, 0.82, 0.85, 1.0)
        background.inputs["Strength"].default_value = 0.45
    reach = max(diagonal, 1.0)
    create_light(
        "Key",
        tuple(target + Vector((1.5 * reach, -2.0 * reach, 2.0 * reach))),
        900.0,
        reach,
        target,
    )
    create_light(
        "Fill",
        tuple(target + Vector((-1.7 * reach, -0.6 * reach, 0.8 * reach))),
        450.0,
        1.3 * reach,
        target,
    )


def camera_direction(view: str) -> Vector:
    mapping = {
        "front": Vector((0.0, -1.0, 0.0)),
        "right": Vector((1.0, 0.0, 0.0)),
        "back": Vector((0.0, 1.0, 0.0)),
        "left": Vector((-1.0, 0.0, 0.0)),
        "top": Vector((0.0, 0.0, 1.0)),
        "bottom": Vector((0.0, 0.0, -1.0)),
        "iso": Vector((1.0, -1.0, 0.8)).normalized(),
    }
    return mapping[view]


def matrix_as_rows(matrix) -> list[list[float]]:
    return [[float(matrix[row][col]) for col in range(4)] for row in range(4)]


def main() -> int:
    args = parse_args()
    if args.resolution <= 0:
        raise SystemExit("--resolution must be greater than zero")
    views = [value.strip().lower() for value in args.views.split(",") if value.strip()]
    invalid = [view for view in views if view not in SUPPORTED_VIEWS]
    if not views or invalid:
        raise SystemExit(f"Invalid views {invalid}; choose from {SUPPORTED_VIEWS}")

    reset_scene()
    imported = import_model(args.model.resolve())
    mesh_objects = [obj for obj in imported if obj.type == "MESH"]
    root = create_root(imported, tuple(args.rotate_deg))
    minimum, maximum = world_bounds(mesh_objects)
    center = (minimum + maximum) * 0.5
    if not args.no_center:
        root.location -= center
        bpy.context.view_layer.update()
        minimum, maximum = world_bounds(mesh_objects)
        center = (minimum + maximum) * 0.5
    extents = maximum - minimum
    max_extent = max(extents.x, extents.y, extents.z)
    diagonal = max((maximum - minimum).length, 1e-6)

    if not args.preserve_materials:
        assign_clay(mesh_objects, parse_hex_color(args.color))
    configure_scene(center, diagonal)

    camera_data = bpy.data.cameras.new("ValidationCamera")
    camera = bpy.data.objects.new("ValidationCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    camera_data.lens = args.focal_mm
    camera_data.sensor_width = 36.0
    if args.projection == "orthographic":
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = args.ortho_scale or max_extent * args.margin
        distance = diagonal * 3.0
    else:
        camera_data.type = "PERSP"
        half_fov = camera_data.angle / 2.0
        distance = (max_extent * 0.5 * args.margin) / max(math.tan(half_fov), 1e-6)

    scene = bpy.context.scene
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = args.resolution
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "model": str(args.model.resolve()),
        "projection": args.projection,
        "resolution": [args.resolution, args.resolution],
        "bounds_after_rotation_and_centering": {
            "min": list(minimum),
            "max": list(maximum),
            "extents": list(extents),
        },
        "views": [],
        "note": "Canonical cameras are for initial comparison; calibrated source photos require matched cameras.",
    }

    for view in views:
        direction = camera_direction(view)
        camera.location = center + direction * distance
        look_at(camera, center)
        scene.render.filepath = str((args.output_dir / f"{view}.png").resolve())
        bpy.ops.render.render(write_still=True)
        manifest["views"].append(
            {
                "id": view,
                "file": f"{view}.png",
                "camera_location": list(camera.location),
                "camera_matrix_world": matrix_as_rows(camera.matrix_world),
                "ortho_scale": camera_data.ortho_scale
                if camera_data.type == "ORTHO"
                else None,
                "focal_mm": camera_data.lens if camera_data.type == "PERSP" else None,
            }
        )

    (args.output_dir / "render-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
