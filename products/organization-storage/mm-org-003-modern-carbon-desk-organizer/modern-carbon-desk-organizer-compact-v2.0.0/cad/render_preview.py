#!/usr/bin/env python3
"""Blender-only visual preview; never used as geometric validation evidence."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "exports" / "master"
OUTPUT = ROOT / "renders" / "MM-ORG-003-compact-digital-candidate.png"


def material(name: str, rgba: tuple[float, float, float, float], metallic: float, roughness: float):
    value = bpy.data.materials.new(name)
    value.diffuse_color = rgba
    value.use_nodes = True
    principled = value.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = rgba
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return value


def import_stl(path: Path, name: str, mat, translation=(0.0, 0.0, 0.0)):
    before = set(bpy.context.scene.objects)
    try:
        bpy.ops.wm.stl_import(filepath=str(path))
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=str(path))
    created = list(set(bpy.context.scene.objects) - before)
    if not created:
        raise RuntimeError(f"No object imported from {path}")
    obj = created[0]
    obj.name = name
    obj.location = translation
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Preview edge softness", "BEVEL")
    bevel.width = 0.45
    bevel.segments = 2
    return obj


def look_at(obj, point: tuple[float, float, float]) -> None:
    direction = Vector(point) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 780
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(OUTPUT)
    scene.render.image_settings.color_mode = "RGBA"

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.045, 0.06, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32

    graphite = material("Housing graphite", (0.055, 0.065, 0.078, 1.0), 0.38, 0.29)
    carbon = material("Carbon panels", (0.016, 0.021, 0.028, 1.0), 0.52, 0.22)
    sorter_mat = material("Sorter", (0.075, 0.09, 0.115, 1.0), 0.3, 0.3)
    ground_mat = material("Ground", (0.12, 0.135, 0.155, 1.0), 0.05, 0.42)

    import_stl(MASTER / "DRAFT-MM-ORG-003-compact-housing-2.0.0-draft.1-assembly-source.stl", "Housing", graphite)
    drawer_path = MASTER / "DRAFT-MM-ORG-003-compact-drawer-print-twice-2.0.0-draft.1-assembly-source.stl"
    import_stl(drawer_path, "Lower drawer", carbon, (3.45, 0.0, 3.25))
    import_stl(drawer_path, "Upper drawer", carbon, (3.45, 0.0, 55.75))
    import_stl(MASTER / "DRAFT-MM-ORG-003-compact-top-sorter-2.0.0-draft.1-assembly-source.stl", "Six-bin sorter", sorter_mat, (0.0, 0.0, 108.0))

    bpy.ops.mesh.primitive_plane_add(size=1000, location=(105.0, 95.0, -3.2))
    ground = bpy.context.object
    ground.data.materials.append(ground_mat)

    bpy.ops.object.light_add(type="AREA", location=(-60.0, -120.0, 330.0))
    key = bpy.context.object
    key.data.energy = 1050
    key.data.shape = "DISK"
    key.data.size = 220
    look_at(key, (105.0, 80.0, 80.0))

    bpy.ops.object.light_add(type="AREA", location=(310.0, -40.0, 190.0))
    fill = bpy.context.object
    fill.data.energy = 760
    fill.data.size = 180
    look_at(fill, (105.0, 95.0, 80.0))

    bpy.ops.object.light_add(type="AREA", location=(100.0, 300.0, 250.0))
    rim = bpy.context.object
    rim.data.energy = 950
    rim.data.size = 160
    look_at(rim, (105.0, 100.0, 100.0))

    bpy.ops.object.camera_add(location=(335.0, -355.0, 245.0))
    camera = bpy.context.object
    camera.data.lens = 58
    look_at(camera, (105.0, 92.0, 82.0))
    scene.camera = camera

    scene.view_settings.look = "AgX - Medium High Contrast"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {OUTPUT}")


if __name__ == "__main__":
    main()
