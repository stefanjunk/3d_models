"""Render a deterministic studio preview from the CadQuery GLB assembly."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    args = sys.argv[sys.argv.index("--") + 1 :]
    if len(args) != 2:
        raise SystemExit("usage: blender --background --python render_preview.py -- INPUT.glb OUTPUT.png")
    source = Path(args[0]).resolve()
    output = Path(args[1]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError("GLB contains no mesh objects")

    # The GLB stores physically correct linear colors, but the very dark
    # TrailCam palette loses internal detail in a small documentation render.
    # Remap only the studio materials; the source GLB remains untouched.
    studio_colors = {
        "mat_0": (0.12, 0.16, 0.22, 1.0),  # anthracite printed structure
        "mat_1": (0.08, 0.26, 0.38, 1.0),  # blue-grey service parts
        "mat_2": (1.0, 0.22, 0.015, 1.0),  # orange printed accents
        "mat_3": (0.018, 0.020, 0.025, 1.0),  # tires/camera/antennas
        "mat_4": (0.32, 0.35, 0.40, 1.0),  # motor and bracket metal
        "mat_5": (0.05, 0.06, 0.075, 1.0),  # battery
        "mat_6": (0.015, 0.16, 0.07, 1.0),  # electronics
        "mat_7": (0.95, 0.16, 0.01, 1.0),  # XT60 service disconnect
    }
    for name, color in studio_colors.items():
        material = bpy.data.materials.get(name)
        if material is None:
            continue
        material.diffuse_color = color
        if material.use_nodes:
            shader = material.node_tree.nodes.get("Principled BSDF")
            if shader is not None:
                shader.inputs["Base Color"].default_value = color
                shader.inputs["Roughness"].default_value = 0.58

    # CadQuery writes millimetre-valued GLB geometry. Blender imports its Y-up
    # convention into Z-up, preserving the intended rover orientation.
    bounds = [obj.matrix_world @ Vector(corner) for obj in mesh_objects for corner in obj.bound_box]
    lower = Vector((min(v.x for v in bounds), min(v.y for v in bounds), min(v.z for v in bounds)))
    upper = Vector((max(v.x for v in bounds), max(v.y for v in bounds), max(v.z for v in bounds)))
    centre = (lower + upper) * 0.5

    bpy.ops.mesh.primitive_plane_add(size=650.0, location=(0.0, 0.0, -60.5))
    plane = bpy.context.object
    plane.name = "ground-reference"
    ground = bpy.data.materials.new("ground-matte")
    ground.diffuse_color = (0.32, 0.34, 0.38, 1.0)
    ground.roughness = 0.9
    plane.data.materials.append(ground)

    world = bpy.context.scene.world
    world.color = (0.035, 0.04, 0.055)
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.10, 0.12, 0.16, 1.0)
    background.inputs["Strength"].default_value = 0.80

    def area(name: str, location: tuple[float, float, float], energy: float, size: float) -> None:
        data = bpy.data.lights.new(name=name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        lamp = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(lamp)
        lamp.location = location
        look_at(lamp, Vector((0.0, 0.0, 65.0)))

    area("key", (250.0, -260.0, 330.0), 5000.0, 180.0)
    area("fill", (-250.0, -100.0, 210.0), 3000.0, 150.0)
    area("rim", (40.0, 260.0, 280.0), 4000.0, 130.0)

    camera_data = bpy.data.cameras.new("camera")
    camera = bpy.data.objects.new("camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (450.0, -500.0, 285.0)
    look_at(camera, Vector((centre.x, centre.y, 65.0)))
    camera_data.lens = 52.0
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(output)
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 1.5
    scene.camera.data.dof.use_dof = False
    scene.render.use_file_extension = True
    bpy.ops.render.render(write_still=True)
    print(f"rendered {output} from bounds {tuple(round(v, 3) for v in lower)} -> {tuple(round(v, 3) for v in upper)}")


if __name__ == "__main__":
    main()
