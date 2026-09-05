#!/usr/bin/env python3
"""Blender-only visual preview; never used as geometric validation evidence."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "exports" / "master"
REVISION = "2.0.0-draft.2"
OUTPUTS = {
    "hero": ROOT / "renders" / "MM-ORG-003-compact-digital-candidate-draft.2.png",
    "rear": ROOT / "renders" / "MM-ORG-003-compact-rear-corner-review-draft.2.png",
    "top": ROOT / "renders" / "MM-ORG-003-compact-top-corner-review-draft.2.png",
}


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
    scene.render.image_settings.color_mode = "RGBA"

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.16, 0.20, 0.28, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8

    graphite = material("Housing graphite", (0.34, 0.39, 0.48, 1.0), 0.12, 0.31)
    carbon = material("Carbon panels", (0.16, 0.21, 0.30, 1.0), 0.22, 0.23)
    sorter_mat = material("Sorter", (0.40, 0.47, 0.58, 1.0), 0.10, 0.32)
    ground_mat = material("Ground", (0.08, 0.10, 0.14, 1.0), 0.02, 0.46)

    import_stl(MASTER / f"DRAFT-MM-ORG-003-compact-housing-{REVISION}-assembly-source.stl", "Housing", graphite)
    drawer_path = MASTER / f"DRAFT-MM-ORG-003-compact-drawer-print-twice-{REVISION}-assembly-source.stl"
    import_stl(drawer_path, "Lower drawer", carbon, (3.45, 0.0, 3.25))
    import_stl(drawer_path, "Upper drawer", carbon, (3.45, 0.0, 55.75))
    import_stl(MASTER / f"DRAFT-MM-ORG-003-compact-top-sorter-{REVISION}-assembly-source.stl", "Six-bin sorter", sorter_mat, (0.0, 0.0, 108.0))

    bpy.ops.mesh.primitive_plane_add(size=1000, location=(105.0, 95.0, -3.2))
    ground = bpy.context.object
    ground.data.materials.append(ground_mat)

    bpy.ops.object.light_add(type="AREA", location=(-60.0, -120.0, 330.0))
    key = bpy.context.object
    key.data.energy = 2400
    key.data.shape = "DISK"
    key.data.size = 220
    look_at(key, (105.0, 80.0, 80.0))

    bpy.ops.object.light_add(type="AREA", location=(310.0, -40.0, 190.0))
    fill = bpy.context.object
    fill.data.energy = 1800
    fill.data.size = 180
    look_at(fill, (105.0, 95.0, 80.0))

    bpy.ops.object.light_add(type="AREA", location=(100.0, 300.0, 250.0))
    rim = bpy.context.object
    rim.data.energy = 2100
    rim.data.size = 160
    look_at(rim, (105.0, 100.0, 100.0))

    bpy.ops.object.camera_add(location=(335.0, -355.0, 245.0))
    camera = bpy.context.object
    camera.data.lens = 58
    scene.camera = camera

    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 1.6
    for output in OUTPUTS.values():
        output.parent.mkdir(parents=True, exist_ok=True)
    views = {
        "hero": ((455.0, -525.0, 330.0), (105.0, 92.0, 82.0), 62),
        "rear": ((-315.0, 520.0, 330.0), (105.0, 100.0, 86.0), 65),
        "top": ((105.0, -360.0, 590.0), (105.0, 95.0, 82.0), 68),
    }
    for name, (location, target, lens) in views.items():
        camera.location = location
        camera.data.lens = lens
        look_at(camera, target)
        scene.render.filepath = str(OUTPUTS[name])
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {OUTPUTS[name]}")


if __name__ == "__main__":
    main()
