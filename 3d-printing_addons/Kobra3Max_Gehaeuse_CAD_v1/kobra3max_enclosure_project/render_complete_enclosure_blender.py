#!/usr/bin/env python3
"""Headless fabrication preview for the complete Kobra 3 Max enclosure.

The OpenSCAD assembly remains the dimensional source of truth. This script
repeats its top-level dimensions only to create a readable material/lighting
preview on systems where OpenSCAD cannot open an off-screen X display.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


W, D, H = 900.0, 1050.0, 900.0
B, PANEL = 20.0, 3.0
SERVICE_BAY_W = 140.0
DOOR_W, DOOR_H = 740.0, 880.0
WINDOW_CX, WINDOW_CZ = 820.0, 590.0


def material(name: str, rgba: tuple[float, float, float, float], metallic: float = 0.0,
             roughness: float = 0.5, emission: tuple[float, float, float, float] | None = None,
             emission_strength: float = 0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Alpha"].default_value = rgba[3]
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if rgba[3] < 1:
        mat.surface_render_method = "DITHERED"
        transmission = bsdf.inputs.get("Transmission Weight")
        if transmission is not None:
            transmission.default_value = 0.55
    return mat


def box(name: str, center: tuple[float, float, float], size: tuple[float, float, float],
        mat: bpy.types.Material, rotation_z_deg: float = 0.0, bevel: float = 0.0) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    obj.rotation_euler[2] = math.radians(rotation_z_deg)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        modifier = obj.modifiers.new("Edge softening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    obj.data.materials.append(mat)
    return obj


def cylinder(name: str, center: tuple[float, float, float], radius: float, depth: float,
             mat: bpy.types.Material, rotation: tuple[float, float, float] = (0, 0, 0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=center,
                                       rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def rod_between(name: str, start: tuple[float, float, float], end: tuple[float, float, float],
                radius: float, mat: bpy.types.Material) -> bpy.types.Object:
    p1, p2 = Vector(start), Vector(end)
    delta = p2 - p1
    obj = cylinder(name, tuple((p1 + p2) / 2), radius, delta.length, mat)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    return obj


def frame(timber: bpy.types.Material) -> None:
    for x in (B / 2, W - B / 2):
        for y in (B / 2, D - B / 2):
            box("Corner post", (x, y, H / 2), (B, B, H), timber)
    for z in (B / 2, H - B / 2):
        for y in (B / 2, D - B / 2):
            box("Front/rear rail", (W / 2, y, z), (W - 2 * B, B, B), timber)
        for x in (B / 2, W - B / 2):
            box("Side rail", (x, D / 2, z), (B, D - 2 * B, B), timber)
    box("Roof centre rail", ((W - B) / 2 + B / 2, D / 2, H - B / 2),
        (B, D - 2 * B, B), timber)
    box("Service stile", (750, B / 2, H / 2), (B, B, H - 2 * B), timber)


def panels(white: bpy.types.Material) -> None:
    box("Left white panel", (B + PANEL / 2, D / 2, H / 2), (PANEL, D, H), white)
    box("Right white panel", (W - B - PANEL / 2, D / 2, H / 2), (PANEL, D, H), white)
    box("Rear white panel", (W / 2, D - B - PANEL / 2, H / 2), (W, PANEL, H), white)

    # Fixed 140 x 880 mm service panel modelled as four bars around 72 x 82 mm cutout.
    panel_left, panel_right = 750.0, 890.0
    cut_left, cut_right = WINDOW_CX - 36, WINDOW_CX + 36
    cut_bottom, cut_top = WINDOW_CZ - 41, WINDOW_CZ + 41
    box("Service panel lower", ((panel_left + panel_right) / 2, -PANEL / 2,
                                (10 + cut_bottom) / 2),
        (panel_right - panel_left, PANEL, cut_bottom - 10), white)
    box("Service panel upper", ((panel_left + panel_right) / 2, -PANEL / 2,
                                (cut_top + 890) / 2),
        (panel_right - panel_left, PANEL, 890 - cut_top), white)
    box("Service panel left", ((panel_left + cut_left) / 2, -PANEL / 2, WINDOW_CZ),
        (cut_left - panel_left, PANEL, 82), white)
    box("Service panel right", ((cut_right + panel_right) / 2, -PANEL / 2, WINDOW_CZ),
        (panel_right - cut_right, PANEL, 82), white)


def front_door(glass: bpy.types.Material, metal: bpy.types.Material) -> None:
    angle = -28.0
    hinge = Vector((10.0, -7.0, 450.0))
    centre_offset = Vector((DOOR_W / 2, 0, 0))
    a = math.radians(angle)
    rotated = Vector((centre_offset.x * math.cos(a), centre_offset.x * math.sin(a), 0))
    centre = hinge + rotated
    box("Open clear door", tuple(centre), (DOOR_W, 4, DOOR_H), glass,
        rotation_z_deg=angle, bevel=3)
    box("Piano hinge", (10, -8, 450), (8, 6, 804), metal, bevel=1)
    box("Door handle", tuple(hinge + Vector((650 * math.cos(a), 650 * math.sin(a), 0))),
        (24, 20, 120), metal, rotation_z_deg=angle, bevel=4)


def roof(timber: bpy.types.Material, diffuser: bpy.types.Material, white: bpy.types.Material,
         metal: bpy.types.Material, led: bpy.types.Material) -> None:
    box("Opal roof diffuser", (W / 2, D / 2, H + 2.5), (W - 2 * B, D - 2 * B, 3), diffuser)
    inset, z = 24.0, H + 22.0
    box("Cassette front", (W / 2, inset + B / 2, z), (W - 2 * inset, B, B), timber)
    box("Cassette rear", (W / 2, D - inset - B / 2, z), (W - 2 * inset, B, B), timber)
    box("Cassette left", (inset + B / 2, D / 2, z), (B, D - 2 * inset, B), timber)
    box("Cassette right", (W - inset - B / 2, D / 2, z), (B, D - 2 * inset, B), timber)
    for x in (120, 252, 384, 516, 648, 780):
        box("Aluminium LED profile", (x + 8.5, D / 2, H + 12), (17, D - 110, 8), metal)
        box("Neutral-white LED", (x + 8.5, D / 2, H + 7.5), (9, D - 112, 2), led)
    box("Cassette lid", (W / 2, D / 2, H + 61.5), (852, 1002, 3), white)


def lighting(metal: bpy.types.Material, led: bpy.types.Material) -> None:
    for x in (33, W - 33):
        box("Fill profile", (x, 33, 425), (10, 14, 610), metal)
        box("Fill LED", (x, 25, 425), (6, 2, 606), led)


def optical_camera(white: bpy.types.Material, black: bpy.types.Material,
                   glass: bpy.types.Material, metal: bpy.types.Material) -> None:
    # Inner white bezel and dark outside wedge/clamp.
    box("White inner optical bezel", (WINDOW_CX, 2.5, WINDOW_CZ), (96, 3, 106), white, bevel=4)
    box("Clear tilted optical pane", (WINDOW_CX, -8, WINDOW_CZ), (80, 2, 90), glass,
        rotation_z_deg=7, bevel=2)
    # Four dark bars make the outside frame legible without hiding the pane.
    box("Window clamp top", (WINDOW_CX, -13, WINDOW_CZ + 49), (96, 8, 8), black, bevel=2)
    box("Window clamp bottom", (WINDOW_CX, -13, WINDOW_CZ - 49), (96, 8, 8), black, bevel=2)
    box("Window clamp left", (WINDOW_CX - 44, -13, WINDOW_CZ), (8, 8, 90), black, bevel=2)
    box("Window clamp right", (WINDOW_CX + 44, -13, WINDOW_CZ), (8, 8, 90), black, bevel=2)

    # Outside rail, slider, short arm and reconstructed camera body.
    box("2020 camera rail", (861, -44, 570), (20, 20, 500), metal, bevel=1)
    box("Camera slider", (850, -58, 565), (44, 12, 90), black, bevel=4)
    rod_between("Short camera arm", (850, -66, 590), (820, -50, 590), 6, black)
    box("New camera enclosure", (WINDOW_CX, -43, WINDOW_CZ), (34, 28, 50), black, bevel=4)
    cylinder("Camera lens", (WINDOW_CX, -27.5, WINDOW_CZ + 5.57), 7.35, 3.0, black,
             rotation=(math.radians(90), 0, 0))


def exhaust(white: bpy.types.Material, black: bpy.types.Material) -> None:
    # Sight baffle inside and 120 mm fan outside the right wall.
    box("White exhaust sight baffle", (W - 30, D - 160, 735), (60, 170, 170), white, bevel=4)
    cylinder("Outside exhaust fan", (W + 16, D - 160, 735), 60, 26, black,
             rotation=(0, math.radians(90), 0))


def printer(black: bpy.types.Material, metal: bpy.types.Material) -> None:
    px, py = (W - 706) / 2, (D - 940) / 2
    box("Printer base", (W / 2, py + 465, 58), (596, 500, 55), black, bevel=8)
    box("Print bed", (W / 2, D / 2, 123), (420, 420, 10), black, bevel=4)
    box("Left Z tower", (px + 113, py + 430, 387), (36, 60, 625), black, bevel=4)
    box("Right Z tower", (px + 593, py + 430, 387), (36, 60, 625), black, bevel=4)
    box("Gantry", (W / 2, py + 430, 663), (516, 36, 36), black, bevel=4)
    box("Toolhead", (W / 2, D / 2, 525), (60, 55, 80), black, bevel=5)
    cylinder("Example print", (W / 2, D / 2, 238), 72, 220, metal)
    box("Display", (835, 28, 120), (92, 25, 94), black, bevel=5)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    timber = material("Timber", (0.48, 0.28, 0.12, 1), roughness=0.68)
    white = material("Matte white", (0.93, 0.94, 0.92, 1), roughness=0.8)
    black = material("Printed dark PETG", (0.035, 0.045, 0.055, 1), roughness=0.48)
    metal = material("Metal", (0.35, 0.38, 0.42, 1), metallic=0.7, roughness=0.3)
    glass = material("Clear PMMA", (0.50, 0.82, 0.94, 0.25), roughness=0.15)
    diffuser = material("Opal diffuser", (0.90, 0.94, 0.96, 0.72), roughness=0.42)
    led = material("Neutral white LED", (1.0, 0.82, 0.28, 1), roughness=0.25,
                   emission=(1.0, 0.78, 0.28, 1), emission_strength=2.0)

    box("Table", (W / 2, D / 2, -12), (W + 250, D + 250, 24),
        material("Table", (0.18, 0.20, 0.23, 1), roughness=0.75), bevel=8)
    frame(timber)
    panels(white)
    front_door(glass, metal)
    roof(timber, diffuser, white, metal, led)
    lighting(metal, led)
    optical_camera(white, black, glass, metal)
    exhaust(white, black)
    printer(black, metal)
    box("Left lift handle", (-8, D / 2, 420), (16, 150, 30), black, bevel=6)
    box("Right lift handle", (W + 8, D / 2, 420), (16, 150, 30), black, bevel=6)

    world = bpy.context.scene.world
    world.color = (0.025, 0.03, 0.04)
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.025, 0.03, 0.04, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8

    bpy.ops.object.light_add(type="AREA", location=(450, -650, 1450))
    key = bpy.context.object
    key.name = "Key light"
    key.data.energy = 85000
    key.data.shape = "RECTANGLE"
    key.data.size = 1000
    key.data.size_y = 800
    look_at(key, (450, 450, 400))

    bpy.ops.object.light_add(type="AREA", location=(1400, 300, 850))
    fill = bpy.context.object
    fill.name = "Fill light"
    fill.data.energy = 55000
    fill.data.size = 900
    look_at(fill, (550, 450, 420))

    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(28), 0, math.radians(-35)))
    sun = bpy.context.object
    sun.name = "Sun fill"
    sun.data.energy = 2.2

    bpy.ops.object.camera_add(location=(1500, -1750, 1220))
    camera = bpy.context.object
    camera.name = "Assembly camera"
    camera.data.lens = 52
    camera.data.sensor_width = 36
    camera.data.clip_end = 6000
    look_at(camera, (455, 475, 435))
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(Path(args.output).resolve())
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 1.2
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
