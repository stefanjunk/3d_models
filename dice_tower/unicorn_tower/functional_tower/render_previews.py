#!/usr/bin/env python3
"""Render polished previews from the actual final STL using Blender."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "exports" / "functional_unicorn_dice_tower.stl"
CUTAWAY = ROOT / "diagnostics" / "actual_final_cutaway.stl"
OUT = ROOT / "previews"
PARAMS = json.loads((ROOT / "parameters.json").read_text(encoding="utf-8"))


def material(name, base, roughness=0.42, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.35
    return mat


def import_stl(path, name, mat):
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.selected_objects[0]
    obj.name = name
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    return obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_camera(location, target, ortho_scale):
    camera = bpy.data.objects.get("Camera")
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
    camera.data.lens = 55
    look_at(camera, target)


def render(filename):
    scene = bpy.context.scene
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


def add_sun(name, location, energy, angle, color):
    data = bpy.data.lights.new(name=name, type="SUN")
    data.energy = energy
    data.angle = angle
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, (0, 0, 90))


def add_area(name, location, energy, size, color):
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, (0, 0, 90))


def add_path_curve(points, mat):
    curve_data = bpy.data.curves.new("Verified 22 mm die center path", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 2
    curve_data.bevel_depth = 2.2
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, xyz in zip(spline.points, points):
        point.co = (*xyz, 1.0)
    obj = bpy.data.objects.new("Verified die center path", curve_data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    for index, xyz in enumerate(points):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=3.2, location=xyz)
        marker = bpy.context.object
        marker.name = f"Path waypoint {index:02d}"
        marker.data.materials.append(mat)
    return obj


bpy.ops.wm.read_factory_settings(use_empty=True)
OUT.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
if scene.world is None:
    scene.world = bpy.data.worlds.new("Preview World")
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.resolution_percentage = 100
scene.view_settings.look = "AgX - Medium High Contrast"
scene.world.color = (0.035, 0.025, 0.055)
scene.world.use_nodes = True
world_bg = scene.world.node_tree.nodes.get("Background")
world_bg.inputs["Color"].default_value = (0.032, 0.020, 0.052, 1.0)
world_bg.inputs["Strength"].default_value = 0.55

body_mat = material("Moonlit lavender", (0.58, 0.34, 0.82), roughness=0.34, metallic=0.04)
cut_mat = material("Cutaway lavender", (0.49, 0.25, 0.72), roughness=0.38, metallic=0.02)
path_mat = material("Verified path orange", (1.0, 0.19, 0.035), roughness=0.3, emission=(1.0, 0.08, 0.01))
ground_mat = material("Ground", (0.055, 0.045, 0.075), roughness=0.62)

bpy.ops.object.camera_add(location=(0, -400, 105))
camera = bpy.context.object
camera.name = "Camera"
scene.camera = camera

add_area("Key", (-180, -220, 300), 1350, 145, (0.84, 0.73, 1.0))
add_area("Fill", (220, -100, 170), 850, 125, (0.65, 0.78, 1.0))
add_area("Rim", (30, 230, 260), 1150, 120, (1.0, 0.55, 0.72))
add_area("Top", (0, 0, 340), 650, 100, (1.0, 0.93, 0.82))
# Sun lights do not attenuate with the millimetre-scaled STL world dimensions.
add_sun("Sun key", (-200, -250, 300), 4.0, 0.20, (0.88, 0.78, 1.0))
add_sun("Sun fill", (250, -80, 180), 2.2, 0.35, (0.60, 0.78, 1.0))
add_sun("Sun rim", (40, 250, 260), 2.8, 0.25, (1.0, 0.50, 0.68))

bpy.ops.mesh.primitive_plane_add(size=420, location=(0, 0, -0.35))
ground = bpy.context.object
ground.name = "Build plane Z=0"
ground.data.materials.append(ground_mat)

full = import_stl(FINAL, "Actual final STL", body_mat)
only = os.environ.get("PREVIEW_ONLY", "all")

if only in ("all", "iso"):
    set_camera((-255, -300, 225), (0, 0, 96), 238)
    render("functional_unicorn_dice_tower_isometric.png")

if only in ("all", "front"):
    set_camera((0, -410, 103), (0, -2, 98), 225)
    render("functional_unicorn_dice_tower_front_minus_y.png")

if only in ("all", "back"):
    set_camera((0, 410, 108), (0, 8, 100), 225)
    render("functional_unicorn_dice_tower_back_plus_y.png")

if only in ("all", "cutaway"):
    full.hide_render = True
    full.hide_set(True)
    cutaway = import_stl(CUTAWAY, "Actual final STL X-half cutaway", cut_mat)
    points = PARAMS["functional_geometry"]["die_path"]["waypoints_mm"]
    add_path_curve(points, path_mat)
    set_camera((-330, -255, 175), (0, 16, 98), 235)
    render("functional_unicorn_dice_tower_cutaway_verified_path.png")

print(json.dumps({
    "rendered_from_actual_final": str(FINAL),
    "cutaway_source": str(CUTAWAY),
    "previews": sorted(str(p) for p in OUT.glob("*.png")),
}, indent=2))
