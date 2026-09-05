"""Rigid/uniform visual registration of immutable Step1X geometry.

Uses the SAME physical studio and cameras as parametric Run 002. No sculpt,
repair, non-uniform scaling, smoothing modifier or image overpaint is applied.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--model", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("--rotation-z", type=float, default=0)
ap.add_argument("--views", default="hero,side,back,front")
args = ap.parse_args(sys.argv[sys.argv.index("--")+1:])
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=False)
template = ROOT / "runs/002/fluent-parametric-study.blend"
bpy.ops.wm.open_mainfile(filepath=str(template))
scene = bpy.context.scene
for ob in list(scene.objects):
    if ob.type == "MESH" and ob.name != "Render studio floor":
        bpy.data.objects.remove(ob, do_unlink=True)
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(args.model.resolve()))
imported = [ob for ob in bpy.data.objects if ob not in before and ob.type == "MESH"]
bpy.context.view_layer.update()

def points():
    return np.array([tuple(ob.matrix_world @ v.co) for ob in imported for v in ob.data.vertices])

original_matrices = {ob.name: [list(row) for row in ob.matrix_world] for ob in imported}
xyz = points()
extent = np.ptp(xyz, axis=0)
up_axis = int(np.argmax(extent))
if up_axis != 2:
    raise ValueError(f"Imported longest axis {up_axis} is not Z. Inspect semantic pose before rendering.")
scale = 0.240 / extent[2]
rotate = Matrix.Rotation(math.radians(args.rotation_z), 4, "Z")
mid = (xyz.min(axis=0) + xyz.max(axis=0)) / 2
translate = Matrix.Translation(Vector((-float(mid[0]), -float(mid[1]), -float(xyz[:,2].min()))))
registration = rotate @ Matrix.Scale(scale, 4) @ translate
ivory = next(m for m in bpy.data.materials if m.name.startswith("Ivory |"))
for ob in imported:
    ob.matrix_world = registration @ ob.matrix_world
    ob.data.materials.clear()
    ob.data.materials.append(ivory)
    for f in ob.data.polygons:
        f.use_smooth = True
    ob["use"] = "Generated appearance proposal, not hollowed or print-ready"
bpy.context.view_layer.update()
xyz_after = points()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = {
    "schema_version":"1.0", "status":"REVIEW_REQUIRED",
    "source": {"path":str(args.model.resolve()),"sha256":sha(args.model)},
    "render_script_sha256":sha(Path(__file__)),
    "studio_template_sha256":sha(template),
    "source_frame":"glTF +Y up; Blender importer performs standard +Y to +Z basis conversion",
    "original_imported_object_matrices":original_matrices,
    "registration_blender_world_meters":[list(row) for row in registration],
    "uniform_scale_after_import":float(scale),
    "rotation_z_degrees":args.rotation_z,
    "height_requested_mm":240,
    "bounds_mm":(np.stack((xyz_after.min(axis=0),xyz_after.max(axis=0))) * 1000).tolist(),
    "dimensions_mm":(np.ptp(xyz_after,axis=0)*1000).tolist(),
    "raw_geometry_modified":False,
    "render_processing":"constant clay material, smooth vertex normals; no geometry smoothing or imagegen",
    "limitations":["Unseen back synthesized; pose visually reviewed, not calibrated to a measured object.",
                   "Uniform 240 mm height is a design choice, not a source measurement.",
                   "No hollowing, fit, component removal or manufacturing validation."],
}
(out/"registration.json").write_text(json.dumps(report,indent=2)+"\n")
bpy.ops.object.select_all(action="DESELECT")
for ob in imported:
    ob.select_set(True)
bpy.context.view_layer.objects.active = imported[0]
bpy.ops.export_scene.gltf(filepath=str(out/"fluent-step1x-240mm-visual.glb"),
                          export_format="GLB",use_selection=True,export_apply=True)
# Millimetre inspection derivative, deliberately OBJ rather than print-ready STL.
with (out/"fluent-step1x-visual-mm.obj").open("w") as f:
    f.write("# mm; registered visual proposal; not hollowed, NOT FOR PRINT\n")
    offset = 0
    for ob in imported:
        for v in ob.data.vertices:
            f.write("v %.7f %.7f %.7f\n" % tuple((ob.matrix_world @ v.co)*1000))
        ob.data.calc_loop_triangles()
        for tri in ob.data.loop_triangles:
            f.write("f %d %d %d\n" % tuple(i+1+offset for i in tri.vertices))
        offset += len(ob.data.vertices)
views = {
    "hero":((0.16,-0.60,0.29),(0,0,0.123)),
    "front":((0,-0.65,0.125),(0,0,0.125)),
    "back":((-0.16,0.60,0.29),(0,0,0.123)),
    "side":((0.65,0,0.15),(0,0,0.123)),
}
scene.cycles.samples = 24
scene.render.resolution_x,scene.render.resolution_y = 800,1000
for view in args.views.split(","):
    scene.camera.location,target = views[view]
    scene.camera.rotation_euler = (Vector(target)-scene.camera.location).to_track_quat("-Z","Y").to_euler()
    scene.render.filepath = str(out/f"fluent-step1x-{view}.png")
    if view == "hero":
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"fluent-step1x-study.blend"))
    bpy.ops.render.render(write_still=True)
print("REGISTERED_VISUAL_DIMENSIONS_MM",report["dimensions_mm"])
