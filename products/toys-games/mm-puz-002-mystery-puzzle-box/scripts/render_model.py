#!/usr/bin/env python3
"""Render the actual exported MM-PUZ-002 meshes in closed and exploded views."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports" / "candidate"
BODY = EXPORTS / "DRAFT-mystery-puzzle-box-1.2.0-body-marked.stl"
LID = EXPORTS / "DRAFT-mystery-puzzle-box-1.2.0-lid.stl"
SLIDER = EXPORTS / "DRAFT-mystery-puzzle-box-1.2.0-slider-print-x3.stl"
LEAF = EXPORTS / "DRAFT-mystery-puzzle-box-1.2.0-return-leaf-print-x3.stl"
OUT = ROOT / "renders"


def reset() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_stl(path: Path, name: str):
    try:
        bpy.ops.wm.stl_import(filepath=str(path))
    except Exception:
        bpy.ops.import_mesh.stl(filepath=str(path))
    obj = bpy.context.selected_objects[0]
    obj.name = name
    return obj


def material(name: str, color: tuple[float, float, float, float], roughness: float):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    return mat


def look_at(obj, target=(0.0, 0.0, 42.0)) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(location, target=(0.0, 0.0, 42.0), lens=58.0):
    bpy.ops.object.camera_add(location=location)
    obj = bpy.context.object
    obj.data.lens = lens
    look_at(obj, target)
    bpy.context.scene.camera = obj


def light(location, energy, size, color=(1.0, 1.0, 1.0)):
    bpy.ops.object.light_add(type="AREA", location=location)
    obj = bpy.context.object
    obj.data.energy = energy
    obj.data.shape = "DISK"
    obj.data.size = size
    obj.data.color = color
    look_at(obj)


def floor(mat) -> None:
    bpy.ops.mesh.primitive_plane_add(size=1000, location=(0, 0, -0.35))
    bpy.context.object.data.materials.append(mat)


def setup() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 760
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.045, 0.045, 0.045)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "WORLD"
    OUT.mkdir(parents=True, exist_ok=True)


def add_closed_parts(body_mat, lid_mat, slider_mat, lid_raise=0.0):
    body = import_stl(BODY, "Puzzle_Box_Body")
    body.data.materials.append(body_mat)
    lid = import_stl(LID, "Puzzle_Box_Lid")
    lid.data.materials.append(lid_mat)
    # Reverse the print-orientation transform to recover assembly coordinates.
    lid.matrix_world = Matrix.Translation((0, 0, 75 + lid_raise)) @ Matrix.Rotation(math.pi, 4, "Y")
    placements = {
        "Front": ((-60.0, -37.5, 55.0), math.pi / 2),
        "Rear": ((60.0, 37.5, 55.0), -math.pi / 2),
        "Left": ((-125.0, 0.0, 55.0), 0.0),
    }
    for name, (position, rz) in placements.items():
        slider = import_stl(SLIDER, f"Slider_{name}")
        slider.data.materials.append(slider_mat)
        slider.matrix_world = (
            Matrix.Translation(position)
            @ Matrix.Rotation(rz, 4, "Z")
            @ Matrix.Rotation(math.pi / 2, 4, "Y")
        )
    return body, lid


def render_closed(body_mat, lid_mat, slider_mat, floor_mat) -> None:
    reset()
    add_closed_parts(body_mat, lid_mat, slider_mat)
    floor(floor_mat)
    camera((360, -410, 270), (0, 0, 43), 60)
    light((-230, -230, 380), 1050, 300)
    light((300, 70, 280), 850, 250, (0.82, 0.91, 1.0))
    light((0, 330, 220), 600, 220, (1.0, 0.83, 0.68))
    bpy.context.scene.render.filepath = str(OUT / "actual-model-closed.png")
    bpy.ops.render.render(write_still=True)


def render_exploded(body_mat, lid_mat, slider_mat, leaf_mat, floor_mat) -> None:
    reset()
    add_closed_parts(body_mat, lid_mat, slider_mat, lid_raise=70.0)
    for idx in range(3):
        leaf = import_stl(LEAF, f"Return_Leaf_{idx + 1}")
        leaf.data.materials.append(leaf_mat)
        leaf.location = (-45 + idx * 45, -78, 3)
    floor(floor_mat)
    camera((410, -500, 330), (0, 0, 70), 62)
    light((-250, -250, 440), 1150, 320)
    light((340, 100, 330), 850, 260, (0.82, 0.91, 1.0))
    light((0, 380, 260), 650, 230, (1.0, 0.83, 0.68))
    bpy.context.scene.render.filepath = str(OUT / "actual-model-exploded.png")
    bpy.ops.render.render(write_still=True)


def main() -> None:
    setup()
    body_mat = material("Charcoal PLA", (0.075, 0.085, 0.10, 1), 0.55)
    lid_mat = material("Graphite lid", (0.115, 0.13, 0.15, 1), 0.48)
    slider_mat = material("Brass buttons", (0.62, 0.34, 0.07, 1), 0.42)
    leaf_mat = material("PETG leaves", (0.13, 0.43, 0.53, 1), 0.50)
    floor_mat = material("Warm floor", (0.69, 0.65, 0.57, 1), 0.72)
    render_closed(body_mat, lid_mat, slider_mat, floor_mat)
    render_exploded(body_mat, lid_mat, slider_mat, leaf_mat, floor_mat)


if __name__ == "__main__":
    main()
